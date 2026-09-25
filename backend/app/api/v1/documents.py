import uuid
from typing import Annotated, List
from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status
from app.api.deps import get_current_user, get_document_service
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentStatusResponse
from app.schemas.response import APIResponse
from app.services.document_service import DocumentService

router = APIRouter(tags=["Documents"])


@router.post(
    "/collections/{collection_id}/documents",
    response_model=APIResponse[DocumentResponse],
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    collection_id: uuid.UUID,
    file: Annotated[UploadFile, File(...)],
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    file_bytes = await file.read()
    document = await document_service.upload_document(
        user_id=current_user.id,
        collection_id=collection_id,
        file_bytes=file_bytes,
        filename=file.filename or "uploaded_file",
        content_type=file.content_type or "application/octet-stream",
        background_tasks=background_tasks,
    )
    return APIResponse.ok(data=DocumentResponse.model_validate(document))


@router.get("/collections/{collection_id}/documents", response_model=APIResponse[List[DocumentResponse]])
async def list_documents(
    collection_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    documents = await document_service.list_documents(current_user.id, collection_id)
    return APIResponse.ok(data=[DocumentResponse.model_validate(d) for d in documents])


@router.get("/documents/{document_id}", response_model=APIResponse[DocumentResponse])
async def get_document(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    document = await document_service.get_document(current_user.id, document_id)
    return APIResponse.ok(data=DocumentResponse.model_validate(document))


@router.get("/documents/{document_id}/status", response_model=APIResponse[DocumentStatusResponse])
async def get_document_status(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    doc = await document_service.get_document_status(current_user.id, document_id)
    status_resp = DocumentStatusResponse(
        document_id=doc.id,
        status=doc.status,
        progress=doc.progress,
        current_step=doc.current_step,
        total_chunks=doc.total_chunks,
        total_pages=doc.total_pages,
        error_message=doc.error_message,
    )
    return APIResponse.ok(data=status_resp)


@router.delete("/documents/{document_id}", response_model=APIResponse[dict])
async def delete_document(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    await document_service.delete_document(current_user.id, document_id)
    return APIResponse.ok(data={"message": "Document deleted successfully"})


@router.post("/documents/{document_id}/retry", response_model=APIResponse[DocumentResponse])
async def retry_document_processing(
    document_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    document = await document_service.retry_processing(current_user.id, document_id, background_tasks)
    return APIResponse.ok(data=DocumentResponse.model_validate(document))
