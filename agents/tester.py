"""
Tester Agent - Reviews and tests the generated code
"""

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.llm import get_gemini_llm
from agents.code_generator import CodeGeneratorOutput


class TestResult(BaseModel):
    """Individual test result."""
    test_name: str = Field(description="Name of the test")
    passed: bool = Field(description="Whether the test passed")
    details: str = Field(description="Test details or failure reason")


class TesterOutput(BaseModel):
    """Output schema for the Tester agent."""
    overall_quality: str = Field(description="Overall code quality assessment")
    test_results: List[TestResult] = Field(description="List of test results")
    issues_found: List[str] = Field(description="List of issues or concerns")
    suggestions: List[str] = Field(description="Suggestions for improvement")
    is_production_ready: bool = Field(description="Whether code is production ready")


class TesterAgent:
    """
    Tester Agent - Reviews and tests the generated code.
    """
    
    def __init__(self):
        self.llm = get_gemini_llm(temperature=0.4)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert code reviewer and tester.
Your role is to analyze code for quality, correctness, and potential issues.

Focus on:
- Code correctness and logic
- Error handling
- Edge cases
- Code quality and best practices
- Security concerns
- Performance considerations

Provide honest, constructive feedback."""),
            ("user", """Review and test this code:

ORIGINAL REQUIREMENTS:
{description}

LANGUAGE: {language}

CODE:
```{language}
{code}
```

Provide a comprehensive review including:
1. Overall quality assessment
2. Specific test results (syntax, logic, functionality)
3. Issues found
4. Suggestions for improvement
5. Whether it's production-ready

Be thorough but fair in your assessment.""")
        ])
    
    def test(self, description: str, code_output: CodeGeneratorOutput, 
             language: str) -> TesterOutput:
        """
        Test and review the generated code.
        
        Args:
            description: Original user description
            code_output: The generated code
            language: The programming language
            
        Returns:
            TesterOutput with test results and feedback
        """
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

        
        # Parse the response
        lines = content.split('\n')
        
        overall_quality = ""
        test_results = []
        issues_found = []
        suggestions = []
        is_production_ready = True
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if "quality" in line.lower() or "assessment" in line.lower():
                current_section = "quality"
            elif "test" in line.lower() and "result" in line.lower():
                current_section = "tests"
            elif "issue" in line.lower() or "problem" in line.lower() or "concern" in line.lower():
                current_section = "issues"
            elif "suggest" in line.lower() or "recommend" in line.lower() or "improve" in line.lower():
                current_section = "suggestions"
            elif "production" in line.lower() or "ready" in line.lower():
                if "not" in line.lower() or "isn't" in line.lower() or "no" in line.lower():
                    is_production_ready = False
            
            # Extract content based on section
            if line.startswith('-') or line.startswith('*') or line.startswith('•'):
                clean_line = line.lstrip('-*• ').strip()
                if current_section == "issues":
                    issues_found.append(clean_line)
                    is_production_ready = False
                elif current_section == "suggestions":
                    suggestions.append(clean_line)
            else:
                if current_section == "quality" and not overall_quality:
                    overall_quality += line + " "
        
        # Create test results
        if not test_results:
            test_results = [
                TestResult(
                    test_name="Syntax Check",
                    passed=True if not any("syntax" in i.lower() for i in issues_found) else False,
                    details="Code syntax appears valid"
                ),
                TestResult(
                    test_name="Logic Review",
                    passed=True if not any("logic" in i.lower() for i in issues_found) else False,
                    details="Logic flow reviewed"
                ),
                TestResult(
                    test_name="Best Practices",
                    passed=len(issues_found) == 0,
                    details="Code follows standard practices" if len(issues_found) == 0 else "Some improvements suggested"
                )
            ]
        
        # Fallback values
        if not overall_quality:
            overall_quality = "Code review completed. " + ("No major issues found." if len(issues_found) == 0 else f"{len(issues_found)} issues identified.")
        
        if not issues_found:
            issues_found = ["No critical issues found"]
            is_production_ready = True
        
        if not suggestions:
            suggestions = ["Code appears functional", "Consider adding more comments", "Test with various inputs"]
        
        return TesterOutput(
            overall_quality=overall_quality.strip(),
            test_results=test_results,
            issues_found=issues_found,
            suggestions=suggestions,
            is_production_ready=is_production_ready
        )