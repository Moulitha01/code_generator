"""
Orchestrator - Coordinates all agents in the code generation pipeline
"""

import os
import sys
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.planner import PlannerAgent
from agents.designer import DesignerAgent
from agents.code_generator import CodeGeneratorAgent
from agents.tester import TesterAgent


class CodeGenerationOrchestrator:
    """
    Orchestrator - Coordinates all agents in the code generation pipeline.

    Workflow:
    1. Planner creates development plan
    2. Designer creates technical design
    3. Code Generator writes the code
    4. Tester validates the code
    """

    def __init__(self):
        print(" Initializing agents...")
        self.planner = PlannerAgent()
        self.designer = DesignerAgent()
        self.code_generator = CodeGeneratorAgent()
        self.tester = TesterAgent()
        print("All agents initialized successfully\n")

    def generate_code(self, description: str, language: str) -> Dict[str, Any]:
        """
        Execute the complete code generation pipeline.
        Returns clean, frontend-friendly data.
        """

        # ---------------- STAGE 1: PLANNING ----------------
        print(" STAGE 1: PLANNING")
        print("Analyzing requirements and creating development plan...\n")

        plan = self.planner.plan(description, language)

        planner_text = (
            f"Project Overview:\n{plan.project_overview}\n\n"
            f"Key Features:\n" +
            "\n".join([f"- {f}" for f in plan.key_features]) +
            f"\n\nApproach:\n{plan.approach}\n\n"
            f"Considerations:\n{plan.considerations}"
        )

        print(" Planning Complete!\n")
        print(planner_text + "\n")

        # ---------------- STAGE 2: DESIGN ----------------
        print(" STAGE 2: DESIGN")
        print("Creating technical design from the plan...\n")

        design = self.designer.design(plan, language)

        designer_text = (
            f"Architecture:\n{design.architecture}\n\n"
            f"Components:\n" +
            "\n".join([f"- {c}" for c in design.components]) +
            f"\n\nData Structures:\n{design.data_structures}\n\n"
            f"Function Signatures:\n{design.function_signatures}"
        )

        print(" Design Complete!\n")
        print(designer_text + "\n")

        # ---------------- STAGE 3: CODE GENERATION ----------------
        print(" STAGE 3: CODE GENERATION")
        print(f"Generating {language} code...\n")

        code_output = self.code_generator.generate(
            description, plan, design, language
        )

        print(" Code Generation Complete!")
        print(f"\nFilename: {code_output.filename}")
        print(f"Explanation: {code_output.explanation}")
        print(f"\n--- Generated Code ---")
        print(code_output.code)
        print("--- End of Code ---\n")

        # ---------------- STAGE 4: TESTING ----------------
        print(" STAGE 4: TESTING & VALIDATION")
        print("Reviewing and testing the generated code...\n")

        test_results = self.tester.test(description, code_output, language)

        tester_text = (
            f"Overall Quality: {test_results.overall_quality}\n\n"
            f"Test Results:\n" +
            "\n".join([
                f"- {t.test_name}: {'PASS' if t.passed else 'FAIL'} ({t.details})"
                for t in test_results.test_results
            ]) +
            f"\n\nIssues Found:\n" +
            "\n".join(test_results.issues_found or ["None"]) +
            f"\n\nSuggestions:\n" +
            "\n".join(test_results.suggestions or ["None"]) +
            f"\n\nProduction Ready: "
            f"{'YES' if test_results.is_production_ready else 'NO'}"
        )

        print("Testing Complete!\n")
        print(tester_text + "\n")

        # ---------------- FINAL RETURN (FOR WEBSITE) ----------------
        return {
            "planner": planner_text,
            "designer": designer_text,
            "code": code_output.code,
            "tester": tester_text
        }
