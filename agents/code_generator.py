"""
Code Generator Agent - Generates full runnable code (supports complex programs)
"""

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.llm import get_gemini_llm
from agents.designer import DesignerOutput
from agents.planner import PlannerOutput


class CodeGeneratorOutput(BaseModel):
    code: str = Field(description="The generated source code")
    filename: str = Field(description="Suggested filename for the code")
    explanation: str = Field(description="Brief explanation of the code")


class CodeGeneratorAgent:
    """
    Code Generator Agent - Generates full, production-style code.
    Designed to handle complex programs (games, apps, long scripts).
    """

    def __init__(self):
        self.llm = get_gemini_llm(
            temperature=0.3,
            
        )

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an expert and senior software engineer. "
                "You MUST generate full-scale, production-style implementations. "
                "NEVER simplify. NEVER generate toy or demo examples. "
                "If the task is a game or application, include the complete game loop, "
                 "No explanations. No markdown. No comments outside code.\n"
                "Never truncate output. Never summarize.\n"
                "If the program is complex, generate the FULL implementation."
                "state management, input handling, rendering, and cleanup. "
                "Assume the user expects a fully working, end-to-end program."
            ),
            (
                "user",
                """Generate FULL, COMPLETE, RUNNABLE code.

STRICT RULES:
- Return ONLY code
-FULLY RUNNABLE
- NO explanations
- NO markdown
- NO summaries
- SINGLE FILE
- Do NOT omit any part
- If code is long, DO NOT stop early; continue until complete

DESCRIPTION:
{description}

DEVELOPMENT PLAN:
{plan}

ARCHITECTURE:
{architecture}

COMPONENTS:
{components}

DATA STRUCTURES:
{data_structures}

FUNCTION SIGNATURES:
{function_signatures}

LANGUAGE: {language}
"""
            )
        ])

    def generate(
        self,
        description: str,
        plan: PlannerOutput,
        design: DesignerOutput,
        language: str
    ) -> CodeGeneratorOutput:

        components_text = "\n".join(f"- {c}" for c in design.components)

        plan_text = (
            f"Overview: {plan.project_overview}\n"
            f"Approach: {plan.approach}\n"
            f"Considerations: {plan.considerations}"
        )

        chain = self.prompt | self.llm

        response = chain.invoke({
            "description": description,
            "plan": plan_text,
            "architecture": design.architecture,
            "components": components_text,
            "data_structures": design.data_structures,
            "function_signatures": design.function_signatures,
            "language": language
        })

        content = response.content
        if isinstance(content, list):
            content = "\n".join(
                item.get("text", str(item)) if isinstance(item, dict) else str(item)
                for item in content
            )

        # Robust code extraction (handles accidental markdown)
        if "```" in content:
            parts = content.split("```")
            code_blocks = []

            for i, part in enumerate(parts):
                if i % 2 == 1:
                    lines = part.strip().split("\n")
                    if lines and lines[0].strip().lower() == language.lower():
                        code_blocks.append("\n".join(lines[1:]))
                    else:
                        code_blocks.append(part.strip())

            code = "\n\n".join(code_blocks)
        else:
            code = content

        extension_map = {
            "python": ".py",
            "javascript": ".js",
            "java": ".java",
            "cpp": ".cpp",
            "c++": ".cpp",
            "c": ".c",
            "go": ".go",
            "rust": ".rs",
            "ruby": ".rb",
            "php": ".php",
            "typescript": ".ts",
            "swift": ".swift",
            "kotlin": ".kt",
        }

        extension = extension_map.get(language.lower(), ".txt")
        filename = f"generated_code{extension}"

        return CodeGeneratorOutput(
            code=code.strip(),
            filename=filename,
            explanation=" runnable code"
        )