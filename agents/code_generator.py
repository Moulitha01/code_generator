"""
Code Generator Agent - Generates actual code from technical design
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
    """Output schema for the Code Generator agent."""
    code: str = Field(description="The generated source code")
    filename: str = Field(description="Suggested filename for the code")
    explanation: str = Field(description="Brief explanation of the code")


class CodeGeneratorAgent:
    """
    Code Generator Agent - Generates actual code from the technical design.
    """
    
    def __init__(self):
        self.llm = get_gemini_llm(temperature=0.3)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert programmer.
Your role is to generate clean, working code based on technical designs.

Focus on:
- Writing clean, readable code
- Following best practices for the language
- Including comments for clarity
- Ensuring the code is complete and functional

Generate production-quality code that works."""),
            ("user", """Generate complete, working code based on this design:

DESCRIPTION: {description}

ARCHITECTURE:
{architecture}

COMPONENTS:
{components}

DATA STRUCTURES:
{data_structures}

FUNCTION SIGNATURES:
{function_signatures}

LANGUAGE: {language}

Generate the complete code with appropriate comments and structure.
Make it clean, minimal, and functional.""")
        ])
    
    def generate(self, description: str, plan: PlannerOutput, 
                design: DesignerOutput, language: str) -> CodeGeneratorOutput:
        """
        Generate code from the technical design.
        
        Args:
            description: Original user description
            plan: The development plan
            design: The technical design
            language: The programming language
            
        Returns:
            CodeGeneratorOutput with the generated code
        """
        components_text = "\n".join([f"- {c}" for c in design.components])
        
        chain = self.prompt | self.llm
        
        response = chain.invoke({
            "description": description,
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

        
        # Extract code blocks
        code = ""
        explanation = ""
        
        if "```" in content:
            # Extract code from markdown code blocks
            parts = content.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Odd indices are code blocks
                    # Remove language identifier if present
                    lines = part.strip().split('\n')
                    if lines[0].strip().lower() in ['python', 'javascript', 'java', 'cpp', 'c++', 'c', 'go', 'rust', language.lower()]:
                        code = '\n'.join(lines[1:])
                    else:
                        code = part.strip()
                    break
            
            # Get explanation from before the code block
            if parts[0].strip():
                explanation = parts[0].strip()
        else:
            code = content
            explanation = f"Generated {language} code as per requirements"
        
        # Determine filename based on language
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
        
        if not explanation:
            explanation = f"Complete {language} implementation based on the requirements"
        
        return CodeGeneratorOutput(
            code=code.strip(),
            filename=filename,
            explanation=explanation[:500]  # Limit explanation length
        )