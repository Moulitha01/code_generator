"""
Planner Agent - Analyzes requirements and creates development plan
"""

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.llm import get_gemini_llm


class PlannerOutput(BaseModel):
    """Output schema for the Planner agent."""
    project_overview: str = Field(description="Brief overview of what needs to be built")
    key_features: list[str] = Field(description="List of key features to implement")
    approach: str = Field(description="High-level approach to implementation")
    considerations: str = Field(description="Important considerations or constraints")


class PlannerAgent:
    """
    Planner Agent - Analyzes requirements and creates a development plan.
    """
    
    def __init__(self):
        self.llm = get_gemini_llm(temperature=0.7)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert software architect and planner.
Your role is to analyze user requirements and create a clear, concise development plan.

Focus on:
- Understanding the core problem
- Identifying key features needed
- Suggesting a practical approach
- Noting important considerations

Keep the plan minimal and focused on what's truly necessary."""),
            ("user", """Create a development plan for the following request:

Description: {description}
Programming Language: {language}

Provide a structured plan that will guide the design and implementation.""")
        ])
    
    def plan(self, description: str, language: str) -> PlannerOutput:
        """
        Create a development plan based on user requirements.
        
        Args:
            description: What the user wants to build
            language: The programming language to use
            
        Returns:
            PlannerOutput with the development plan
        """
        chain = self.prompt | self.llm
        
        response = chain.invoke({
            "description": description,
            "language": language
        })
        
        # Parse the response into structured output
        content = response.content
        if isinstance(content, list):
            content = "\n".join(
               item.get("text", str(item)) if isinstance(item, dict) else str(item)
               for item in content
            )

        
        # Simple parsing
        lines = content.split('\n')
        
        overview = ""
        features = []
        approach = ""
        considerations = ""
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "overview" in line.lower() or "summary" in line.lower():
                current_section = "overview"
            elif "feature" in line.lower() or "requirement" in line.lower():
                current_section = "features"
            elif "approach" in line.lower() or "strategy" in line.lower():
                current_section = "approach"
            elif "consideration" in line.lower() or "note" in line.lower():
                current_section = "considerations"
            elif line.startswith('-') or line.startswith('*') or line.startswith('•'):
                if current_section == "features":
                    features.append(line.lstrip('-*• '))
            else:
                if current_section == "overview":
                    overview += line + " "
                elif current_section == "approach":
                    approach += line + " "
                elif current_section == "considerations":
                    considerations += line + " "
        
        # Fallback if parsing doesn't work well
        if not overview:
            overview = content[:200] + "..."
        if not features:
            features = ["Core functionality as described", "Error handling", "User-friendly interface"]
        if not approach:
            approach = f"Implement using {language} with clean, modular code structure"
        if not considerations:
            considerations = "Focus on code quality, readability, and maintainability"
        
        return PlannerOutput(
            project_overview=overview.strip(),
            key_features=features,
            approach=approach.strip(),
            considerations=considerations.strip()
        )