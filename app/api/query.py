from fastapi import APIRouter, Depends
from model.query import QueryRequest, QueryResponse
from services.llm_generator import generate_response
from core.security import get_current_user
from schema.users import Users

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    current_user: Users = Depends(get_current_user),
):
    """
    Query the authenticated user's indexed financial documents using
    the hybrid (BM25 + dense vector) RAG pipeline.
    Results are strictly scoped to the user's own Qdrant collection.
    """
    res = await generate_response(query=request.query, user_id=current_user.id)
    return {"message": res}