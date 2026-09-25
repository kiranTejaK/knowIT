import uuid
from typing import Annotated, Any, Dict, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user, get_rag_service
from app.models.user import User
from app.schemas.response import APIResponse
from app.services.rag_service import RAGService

router = APIRouter(tags=["Search"])


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


@router.post("/collections/{collection_id}/search", response_model=APIResponse[List[Dict[str, Any]]])
async def semantic_search_debug(
    collection_id: uuid.UUID,
    search_in: SearchRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    rag_service: Annotated[RAGService, Depends(get_rag_service)],
):
    results = await rag_service.semantic_search_debug(
        user_id=current_user.id,
        collection_id=collection_id,
        query=search_in.query,
        top_k=search_in.top_k,
    )
    return APIResponse.ok(data=results)
