from fastapi import APIRouter
from pydantic import BaseModel
from orchestrator import CodeGenerationOrchestrator

router = APIRouter()
orchestrator = CodeGenerationOrchestrator()


class CodeRequest(BaseModel):
    description: str
    language: str


@router.post("/generate")
def generate_code(request: CodeRequest):
    result = orchestrator.generate_code(
        description=request.description,
        language=request.language
    )

    # IMPORTANT: return exactly what orchestrator gives
    return {
        "planning": result.get("planner", ""),
        "design": result.get("designer", ""),
        "code": result.get("code", ""),
        "testing": result.get("tester", "")
    }
