"""
Tester Agent - Reviews and validates generated code
Only CRITICAL failures block production readiness
"""

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
import sys
import os
import re

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.llm import get_gemini_llm
from agents.code_generator import CodeGeneratorOutput


class TestResult(BaseModel):
    test_name: str
    passed: bool
    details: str


class TesterOutput(BaseModel):
    overall_quality: str
    test_results: List[TestResult]
    issues_found: List[str]
    suggestions: List[str]
    is_production_ready: bool


class TesterAgent:
    """
    Tester Agent - Validates correctness and runtime safety.
    """

    def __init__(self):
        self.llm = get_gemini_llm(temperature=0.2)

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a strict automated code validator.\n"
                "ONLY identify CRITICAL problems:\n"
                "- Syntax errors\n"
                "- Guaranteed runtime crashes\n"
                "- Infinite loops\n"
                "- Missing entry points\n\n"
                "DO NOT comment on style, formatting, or optimizations.\n"
                "DO NOT fail code for improvements or best practices.\n"
                "If no critical issue exists, say: NO_CRITICAL_ISSUES"
            ),
            (
                "user",
                """LANGUAGE: {language}

REQUIREMENTS:
{description}

CODE:
{code}

Return ONLY:
- CRITICAL_ISSUES (if any)
- OPTIONAL_SUGGESTIONS (if any)
"""
            )
        ])

    def _basic_static_checks(self, code: str, language: str) -> List[str]:
        """Fast deterministic checks without LLM."""
        issues = []

        if not code.strip():
            issues.append("Empty source code")

        if language.lower() == "python":
            # Accept either a main() function or direct __main__ run
            if "if __name__ == '__main__'" not in code and "if __name__ == \"__main__\"" not in code:
                if "def main" not in code:
                    issues.append("Missing Python entry point")

        if language.lower() == "java":
            if "public static void main" not in code:
                issues.append("Missing Java main method")

        # Simple infinite loop check
        if re.search(r"while\s*\(\s*true\s*\)", code) and "break" not in code:
            issues.append("Potential infinite loop")

        return issues

    def test(
        self,
        description: str,
        code_output: CodeGeneratorOutput,
        language: str
    ) -> TesterOutput:

        critical_issues = self._basic_static_checks(
            code_output.code, language
        )

        llm_issues = []
        suggestions = []

        chain = self.prompt | self.llm
        response = chain.invoke({
            "description": description,
            "language": language,
            "code": code_output.code
        })

        content = response.content
        if isinstance(content, list):
            content = "\n".join(
                item.get("text", str(item)) if isinstance(item, dict) else str(item)
                for item in content
            )

        if "NO_CRITICAL_ISSUES" not in content:
            for line in content.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if "critical" in line.lower() or "error" in line.lower():
                    llm_issues.append(line)
                else:
                    suggestions.append(line)

        critical_issues.extend(llm_issues)

        is_production_ready = len(critical_issues) == 0

        test_results = [
            TestResult(
                test_name="Syntax & Structure",
                passed=len(critical_issues) == 0,
                details="No syntax or structural errors detected"
                if is_production_ready else "Critical issues detected"
            ),
            TestResult(
                test_name="Runtime Safety",
                passed=is_production_ready,
                details="No guaranteed runtime crashes found"
                if is_production_ready else "Potential runtime failures"
            )
        ]

        if not critical_issues:
            critical_issues = ["No critical issues found"]

        if not suggestions:
            suggestions = ["Optional improvements may be applied if desired"]

        overall_quality = (
            "Production-ready code."
            if is_production_ready
            else "Critical issues must be resolved before production use."
        )

        return TesterOutput(
            overall_quality=overall_quality,
            test_results=test_results,
            issues_found=critical_issues,
            suggestions=suggestions,
            is_production_ready=is_production_ready
        )