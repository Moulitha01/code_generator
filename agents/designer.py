"""
Designer Agent - Creates detailed technical design from the plan
"""

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.llm import get_gemini_llm
from agents.planner import PlannerOutput


class DesignerOutput(BaseModel):
    """Output schema for the Designer agent."""
    architecture: str = Field(description="System architecture and structure")
    components: list[str] = Field(description="List of main components/modules")
    data_structures: str = Field(description="Key data structures or models")
    function_signatures: str = Field(description="Main functions/methods to implement")


class DesignerAgent:
    """
    Designer Agent - Creates detailed technical design from the plan.
    """
    
    def __init__(self):
        self.llm = get_gemini_llm(temperature=0.5)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert software designer.
Your role is to create detailed technical designs from high-level plans.

Focus on:
- Clear architecture and component structure
- Key data structures needed
- Main function/method signatures
- How components interact

Keep the design minimal but complete."""),
            ("user", """Based on this development plan, create a detailed technical design:

PROJECT OVERVIEW:
{overview}

KEY FEATURES:
{features}

APPROACH:
{approach}

LANGUAGE: {language}

Provide a technical design that includes architecture, components, data structures, and function signatures.""")
        ])
    
    def design(self, plan: PlannerOutput, language: str) -> DesignerOutput:
        """
        Create a technical design from the development plan.
        
        Args:
            plan: The development plan from PlannerAgent
            language: The programming language to use
            
        Returns:
            DesignerOutput with the technical design
        """
        features_text = "\n".join([f"- {f}" for f in plan.key_features])
        
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
        
        # Simple parsing
        lines = content.split('\n')
        
        architecture = ""
        components = []
        data_structures = ""
        function_signatures = ""
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "architecture" in line.lower() or "structure" in line.lower():
                current_section = "architecture"
            elif "component" in line.lower() or "module" in line.lower():
                current_section = "components"
            elif "data" in line.lower() or "structure" in line.lower() or "model" in line.lower():
                current_section = "data"
            elif "function" in line.lower() or "method" in line.lower() or "signature" in line.lower():
                current_section = "functions"
            elif line.startswith('-') or line.startswith('*') or line.startswith('•'):
                if current_section == "components":
                    components.append(line.lstrip('-*• '))
            else:
                if current_section == "architecture":
                    architecture += line + " "
                elif current_section == "data":
                    data_structures += line + " "
                elif current_section == "functions":
                    function_signatures += line + " "
        
        # Fallback values
        if not architecture:
            architecture = f"Modular {language} application with clear separation of concerns"
        if not components:
            components = ["Main module", "Helper functions", "Data processing"]
        if not data_structures:
            data_structures = "Standard data structures appropriate for the task"
        if not function_signatures:
            function_signatures = "Core functions as needed by the requirements"
        
        return DesignerOutput(
            architecture=architecture.strip(),
            components=components,
            data_structures=data_structures.strip(),
            function_signatures=function_signatures.strip()
        )