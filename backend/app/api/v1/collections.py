import uuid
from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from app.api.deps import get_collection_service, get_current_user
from app.models.user import User
from app.schemas.collection import CollectionCreate, CollectionResponse, CollectionUpdate
from app.schemas.response import APIResponse
from app.services.collection_service import CollectionService

router = APIRouter(prefix="/collections", tags=["Collections"])


@router.get("", response_model=APIResponse[List[CollectionResponse]])
async def list_collections(
    current_user: Annotated[User, Depends(get_current_user)],
    collection_service: Annotated[CollectionService, Depends(get_collection_service)],
):
    collections = await collection_service.list_collections(current_user.id)
    return APIResponse.ok(data=[CollectionResponse.model_validate(c) for c in collections])


@router.post("", response_model=APIResponse[CollectionResponse], status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection_in: CollectionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    collection_service: Annotated[CollectionService, Depends(get_collection_service)],
):
    collection = await collection_service.create_collection(current_user.id, collection_in)
    return APIResponse.ok(data=CollectionResponse.model_validate(collection))


@router.get("/{collection_id}", response_model=APIResponse[CollectionResponse])
async def get_collection(
    collection_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    collection_service: Annotated[CollectionService, Depends(get_collection_service)],
):
    collection = await collection_service.get_collection(current_user.id, collection_id)
    return APIResponse.ok(data=CollectionResponse.model_validate(collection))


@router.patch("/{collection_id}", response_model=APIResponse[CollectionResponse])
async def update_collection(
    collection_id: uuid.UUID,
    update_in: CollectionUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    collection_service: Annotated[CollectionService, Depends(get_collection_service)],
):
    collection = await collection_service.update_collection(current_user.id, collection_id, update_in)
    return APIResponse.ok(data=CollectionResponse.model_validate(collection))


@router.delete("/{collection_id}", response_model=APIResponse[dict])
async def delete_collection(
    collection_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    collection_service: Annotated[CollectionService, Depends(get_collection_service)],
):
    await collection_service.delete_collection(current_user.id, collection_id)
    return APIResponse.ok(data={"message": "Collection deleted successfully"})
