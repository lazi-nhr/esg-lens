"""
Document endpoints: add and list documents.
"""
from fastapi import APIRouter, HTTPException

from app.api.schemas import DocumentCreateRequest
from app.db.repositories.documents_repo import DocumentRepository
from app.retrieval.embedder import create_embedding

router = APIRouter()


@router.post("/documents")
async def add_document(request: DocumentCreateRequest):
    """Add a document with embedding."""
    try:
        embedding = create_embedding(request.content)
        doc_id = DocumentRepository.add(request.content, embedding)
        return {"id": doc_id, "message": "Document added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def list_documents():
    """List all documents."""
    try:
        documents = DocumentRepository.list_all()
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
