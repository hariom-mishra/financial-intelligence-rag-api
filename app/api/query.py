from fastapi import APIRouter
from model.query import QueryRequest, QueryResponse
from services.llm_generator import generate_response

router = APIRouter(prefix="/query", tags=["query"])

@router.post("/", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    res = await generate_response(request.query)
    return {"message": res}