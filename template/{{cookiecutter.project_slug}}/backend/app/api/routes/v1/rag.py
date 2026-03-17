{%- if cookiecutter.enable_rag %}
"""RAG API routes for collection management, search, and document deletion.

Document ingestion is handled via CLI commands (rag-ingest, rag-sync-gdrive, rag-sync-s3).
"""

import logging

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import IngestionSvc, RetrievalSvc, VectorStoreSvc
{%- if cookiecutter.use_jwt %}
from app.api.deps import CurrentUser
{%- endif %}
from app.schemas.rag import (
    RAGCollectionInfo,
    RAGCollectionList,
    RAGDocumentItem,
    RAGDocumentList,
    RAGSearchRequest,
    RAGSearchResponse,
    RAGSearchResult,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/collections", response_model=RAGCollectionList)
async def list_collections(
    vector_store: VectorStoreSvc,
{%- if cookiecutter.use_jwt %}
    current_user: CurrentUser,
{%- endif %}
):
    """List all available collections in the vector store."""
    names = await vector_store.list_collections()
    return RAGCollectionList(items=names)


@router.post("/collections/{name}", status_code=status.HTTP_201_CREATED)
async def create_collection(
    name: str,
    vector_store: VectorStoreSvc,
{%- if cookiecutter.use_jwt %}
    current_user: CurrentUser,
{%- endif %}
):
    """Create and initialize a new collection."""
    await vector_store._ensure_collection(name)
    return {"message": f"Collection '{name}' created successfully."}


@router.delete("/collections/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def drop_collection(
    name: str,
    vector_store: VectorStoreSvc,
{%- if cookiecutter.use_jwt %}
    current_user: CurrentUser,
{%- endif %}
):
    """Drop an entire collection and all its vectors."""
    await vector_store.delete_collection(name)


@router.get("/collections/{name}/info", response_model=RAGCollectionInfo)
async def get_collection_info(
    name: str,
    vector_store: VectorStoreSvc,
{%- if cookiecutter.use_jwt %}
    current_user: CurrentUser,
{%- endif %}
):
    """Retrieve stats for a specific collection."""
    return await vector_store.get_collection_info(name)


@router.get("/collections/{name}/documents", response_model=RAGDocumentList)
async def list_documents(
    name: str,
    vector_store: VectorStoreSvc,
{%- if cookiecutter.use_jwt %}
    current_user: CurrentUser,
{%- endif %}
):
    """List all documents in a specific collection."""
    documents = await vector_store.get_documents(name)
    return RAGDocumentList(
        items=[
            RAGDocumentItem(
                document_id=doc.document_id,
                filename=doc.filename,
                filesize=doc.filesize,
                filetype=doc.filetype,
                chunk_count=doc.chunk_count,
                additional_info=doc.additional_info,
            )
            for doc in documents
        ],
        total=len(documents),
    )


@router.post("/search", response_model=RAGSearchResponse)
async def search_documents(
    request: RAGSearchRequest,
    retrieval_service: RetrievalSvc,
    {%- if cookiecutter.use_jwt %}
    current_user: CurrentUser,
    {%- endif %}
    use_reranker: bool = Query(False, description="Whether to use reranking (if configured)"),
):
    """Search for relevant document chunks. Supports multi-collection search."""
    if request.collection_names and len(request.collection_names) > 1:
        results = await retrieval_service.retrieve_multi(
            query=request.query,
            collection_names=request.collection_names,
            limit=request.limit,
            min_score=request.min_score,
            use_reranker=use_reranker,
        )
    else:
        collection = (request.collection_names[0] if request.collection_names else request.collection_name)
        results = await retrieval_service.retrieve(
            query=request.query,
            collection_name=collection,
            limit=request.limit,
            min_score=request.min_score,
            filter=request.filter or "",
            use_reranker=use_reranker,
        )
    api_results = [
        RAGSearchResult(**hit.model_dump())
        for hit in results
    ]
    return RAGSearchResponse(results=api_results)


@router.delete("/collections/{name}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    name: str,
    document_id: str,
    ingestion_service: IngestionSvc,
{%- if cookiecutter.use_jwt %}
    current_user: CurrentUser,
{%- endif %}
):
    """Delete a specific document by its ID from a collection."""
    success = await ingestion_service.remove_document(name, document_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

{%- else %}
"""RAG routes - not configured."""
{%- endif %}
