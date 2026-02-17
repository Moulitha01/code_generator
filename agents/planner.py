"""
Planner Agent - Analyzes requirements and creates a concise development plan
"""

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.llm import get_gemini_llm


class PlannerOutput(BaseModel):
    """Output schema for the Planner agent."""
    project_overview: str = Field(description="Brief overview of what needs to be built")
    key_features: List[str] = Field(description="Essential features only")
    approach: str = Field(description="High-level implementation approach")
    considerations: str = Field(description="Critical constraints or notes")


class PlannerAgent:
    """
    Planner Agent - Produces a minimal, high-signal development plan.
    Optimized for speed, clarity, and downstream code generation.
    """

    def __init__(self):
        # Lower temperature = more deterministic, less verbose
        self.llm = get_gemini_llm(temperature=0.4)

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a senior software architect.

Rules:
- Be concise
- Focus only on what is REQUIRED to build the system
- Avoid fluff, repetition, or optional ideas
- Prefer practical, implementable decisions
- Output should guide code generation directly
"""
            ),
            (
                "user",
                """Create a SHORT, STRUCTURED development plan.

PROJECT DESCRIPTION:
{description}

LANGUAGE:
{language}

Return content in this format ONLY:

Overview:
<1–2 sentences>

Key Features:
- <feature 1>
- <feature 2>
- <feature 3>

Approach:
<short paragraph>

Considerations:
<critical constraints only>
"""
            )
        ])

    def plan(self, description: str, language: str) -> PlannerOutput:
        """
        Create a concise development plan based on user requirements.
        """
        chain = self.prompt | self.llm

        response = chain.invoke({
            "description": description,
            "language": language
        })

        content = response.content
        if isinstance(content, list):
            content = "\n".join(
                item.get("text", str(item)) if isinstance(item, dict) else str(item)
                for item in content
            )

        lines = [line.strip() for line in content.split("\n") if line.strip()]

        overview = ""
        features: List[str] = []
        approach = ""
        considerations = ""

        section = None

        for line in lines:
            lower = line.lower()

            if lower.startswith("overview"):
                section = "overview"
                continue
            if lower.startswith("key features"):
                section = "features"
                continue
            if lower.startswith("approach"):
                section = "approach"
                continue
            if lower.startswith("considerations"):
                section = "considerations"
                continue

            if line.startswith(("-", "*", "•")) and section == "features":
                features.append(line.lstrip("-*• ").strip())
            else:
                if section == "overview":
                    overview += line + " "
                elif section == "approach":
                    approach += line + " "
                elif section == "considerations":
                    considerations += line + " "

        # Hard fallbacks (never fail downstream)
        if not overview:
            overview = f"Build the requested system using {language}."
        if not features:
            features = ["Core functionality", "Input handling", "Output generation"]
        if not approach:
            approach = f"Implement using clean, modular {language} code."
        if not considerations:
            considerations = "Ensure correctness, performance, and maintainability."

        return PlannerOutput(
            project_overview=overview.strip(),
            key_features=features[:8],  # hard cap to avoid token bloat
            approach=approach.strip(),
            considerations=considerations.strip()
        )