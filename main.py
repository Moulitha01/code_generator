"""
Main entry point for the multi-agent code generation system
"""

import sys
import os

# Ensure project root is in Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

from orchestrator import CodeGenerationOrchestrator


def main():
    print("MULTI-AGENT CODE GENERATOR")

    try:
        description = input(
            "What do you want to build?\n"
            "(e.g., 'Addition of two integers'): "
        ).strip()

        if not description:
            print(" Description cannot be empty")
            return

        language = input(
            "Programming language?\n"
            "(e.g., Python, JavaScript, Java): "
        ).strip()

        if not language:
            print("Language cannot be empty")
            return

        print("\n Starting code generation pipeline...\n")

        orchestrator = CodeGenerationOrchestrator()
        results = orchestrator.generate_code(
            description=description,
            language=language
        )

        # Ask user if they want to save the file
        save = input("\n Save generated code to file? (y/n): ").lower().strip()
        if save == "y":
            orchestrator.save_code(results["code"])

        print("\n Done!")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print("\n Fatal error occurred:")
        print(str(e))


if __name__ == "__main__":
    main()
