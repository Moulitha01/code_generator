"""
Orchestrator - Coordinates all agents in the code generation pipeline
"""

import os
import sys
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.planner import PlannerAgent, PlannerOutput
from agents.designer import DesignerAgent, DesignerOutput
from agents.code_generator import CodeGeneratorAgent, CodeGeneratorOutput
from agents.tester import TesterAgent, TesterOutput


class CodeGenerationOrchestrator:
    """
    Orchestrator - Coordinates all agents in the code generation pipeline.
    
    This class manages the workflow:
    1. Planner creates development plan
    2. Designer creates technical design
    3. Code Generator writes the code
    4. Tester validates the code
    """
    
    def __init__(self):
        """Initialize the orchestrator with all agents."""
        print(" Initializing agents...")
        self.planner = PlannerAgent()
        self.designer = DesignerAgent()
        self.code_generator = CodeGeneratorAgent()
        self.tester = TesterAgent()
        print("All agents initialized successfully\n")
    
    def generate_code(self, description: str, language: str) -> Dict[str, Any]:
        """
        Execute the complete code generation pipeline.
        
        Args:
            description: What the user wants to build
            language: Programming language to use
            
        Returns:
            Dictionary containing all outputs from each agent
        """
        results = {
            "description": description,
            "language": language
        }
        
        # Stage 1: Planning
        print("=" * 70)
        print(" STAGE 1: PLANNING")
        print("=" * 70)
        print(f"Analyzing requirements and creating development plan...\n")
        
        plan = self.planner.plan(description, language)
        results["plan"] = plan
        
        print(" Planning Complete!")
        print(f"\nProject Overview: {plan.project_overview}")
        print(f"\nKey Features:")
        for i, feature in enumerate(plan.key_features, 1):
            print(f"  {i}. {feature}")
        print(f"\nApproach: {plan.approach}")
        print(f"\nConsiderations: {plan.considerations}\n")
        
        # Stage 2: Design
        print("=" * 70)
        print(" STAGE 2: DESIGN")
        print("=" * 70)
        print(f"Creating technical design from the plan...\n")
        
        design = self.designer.design(plan, language)
        results["design"] = design
        
        print(" Design Complete!")
        print(f"\nArchitecture: {design.architecture}")
        print(f"\nComponents:")
        for i, component in enumerate(design.components, 1):
            print(f"  {i}. {component}")
        print(f"\nData Structures: {design.data_structures}")
        print(f"\nFunction Signatures: {design.function_signatures}\n")
        
        # Stage 3: Code Generation
        print("=" * 70)
        print(" STAGE 3: CODE GENERATION")
        print("=" * 70)
        print(f"Generating {language} code...\n")
        
        code_output = self.code_generator.generate(description, plan, design, language)
        results["code"] = code_output
        
        print(" Code Generation Complete!")
        print(f"\nFilename: {code_output.filename}")
        print(f"Explanation: {code_output.explanation}")
        print(f"\n--- Generated Code ({len(code_output.code)} characters) ---")
        print(code_output.code)
        print("--- End of Code ---\n")
        
        # Stage 4: Testing
        print("=" * 70)
        print(" STAGE 4: TESTING & VALIDATION")
        print("=" * 70)
        print(f"Reviewing and testing the generated code...\n")
        
        test_results = self.tester.test(description, code_output, language)
        results["test_results"] = test_results
        
        print("Testing Complete!")
        print(f"\nOverall Quality: {test_results.overall_quality}")
        print(f"\nTest Results:")
        for i, test in enumerate(test_results.test_results, 1):
            status = "PASS" if test.passed else "❌ FAIL"
            print(f"  {i}. {test.test_name}: {status}")
            print(f"     {test.details}")
        
        print(f"\nIssues Found:")
        for i, issue in enumerate(test_results.issues_found, 1):
            print(f"  {i}. {issue}")
        
        print(f"\nSuggestions:")
        for i, suggestion in enumerate(test_results.suggestions, 1):
            print(f"  {i}. {suggestion}")
        
        status = " YES" if test_results.is_production_ready else "⚠️  NEEDS WORK"
        print(f"\nProduction Ready: {status}\n")
        
        # Final Summary
        print("=" * 70)
        print(" PIPELINE SUMMARY")
        print("=" * 70)
        print(f"Description: {description}")
        print(f"Language: {language}")
        print(f"Generated File: {code_output.filename}")
        print(f"Code Length: {len(code_output.code)} characters")
        print(f"Production Ready: {'Yes' if test_results.is_production_ready else 'No'}")
        print("=" * 70 + "\n")
        
        return results
    
    def save_code(self, code_output: CodeGeneratorOutput, output_path: str = None) -> str:
        """
        Save the generated code to a file.
        
        Args:
            code_output: The code output from CodeGeneratorAgent
            output_path: Optional custom path, otherwise uses suggested filename
            
        Returns:
            Path where the file was saved
        """
        if output_path is None:
            output_path = code_output.filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(code_output.code)
        
        print(f"💾 Code saved to: {output_path}")
        return output_path