"""
Designer Agent - Produces a precise technical design ready for code generation
"""

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.llm import get_gemini_llm
from agents.planner import PlannerOutput


class DesignerOutput(BaseModel):
    """Output schema for the Designer agent."""
    architecture: str = Field(description="Overall system architecture")
    components: List[str] = Field(description="Concrete modules/classes/files")
    data_structures: str = Field(description="Key data structures and models")
    function_signatures: str = Field(description="Important functions or methods")


class DesignerAgent:
    """
    Designer Agent - Converts a plan into a concrete, implementable design.
    Optimized for complex programs (games, apps, systems).
    """

    def __init__(self):
        # Lower temperature = stable, implementation-focused output
        self.llm = get_gemini_llm(temperature=0.4)

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a senior software engineer.

Rules:
- Design MUST be implementable directly in code
- Prefer explicit modules, classes, and responsibilities
- Avoid vague statements
- Think like you are preparing for coding immediately
- Assume the next agent will generate FULL WORKING CODE
"""
            ),
            (
                "user",
                """Create a TECHNICAL DESIGN based on the plan below.

PROJECT OVERVIEW:
{overview}

KEY FEATURES:
{features}

APPROACH:
{approach}

LANGUAGE:
{language}

Return output in EXACTLY this format:

Architecture:
<clear description>

Components:
- <module/class 1>
- <module/class 2>
- <module/class 3>

Data Structures:
<key data models / structures>

Function Signatures:
<important functions or class methods>
"""
            )
        ])

    def design(self, plan: PlannerOutput, language: str) -> DesignerOutput:
        """
        Generate a concrete technical design from the planner output.
        """
        features_text = "\n".join(f"- {f}" for f in plan.key_features)

        chain = self.prompt | self.llm

        response = chain.invoke({
            "overview": plan.project_overview,
            "features": features_text,
            "approach": plan.approach,
            "language": language
        })

        content = response.content
        if isinstance(content, list):
            content = "\n".join(
                item.get("text", str(item)) if isinstance(item, dict) else str(item)
                for item in content
            )

        lines = [line.strip() for line in content.split("\n") if line.strip()]

        architecture = ""
        components: List[str] = []
        data_structures = ""
        function_signatures = ""

        section = None

        for line in lines:
            lower = line.lower()

            if lower.startswith("architecture"):
                section = "architecture"
                continue
            if lower.startswith("components"):
                section = "components"
                continue
            if lower.startswith("data structures"):
                section = "data"
                continue
            if lower.startswith("function signatures"):
                section = "functions"
                continue

            if line.startswith(("-", "*", "•")) and section == "components":
                components.append(line.lstrip("-*• ").strip())
            else:
                if section == "architecture":
                    architecture += line + " "
                elif section == "data":
                    data_structures += line + " "
                elif section == "functions":
                    function_signatures += line + " "

        # HARD FAIL-SAFES (critical for complex programs)
        if not architecture:
            architecture = f"Modular {language} application with separated logic, state, and execution layers."

        if not components:
            components = [
                "main entry point",
                "core logic module",
                "state/data manager",
                "input handling",
                "rendering/output module"
            ]

        if not data_structures:
            data_structures = "Core state objects, configuration structures, and runtime data containers."

        if not function_signatures:
            function_signatures = (
                "initialize(), run_loop(), update_state(), handle_input(), render_output(), cleanup()"
            )

        return DesignerOutput(
            architecture=architecture.strip(),
            components=components[:10],  # cap size to prevent token explosion
            data_structures=data_structures.strip(),
            function_signatures=function_signatures.strip()
        )