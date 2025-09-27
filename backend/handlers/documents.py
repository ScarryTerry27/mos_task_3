from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from service.db import schema
from service.db.db import get_db
from service.db.service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=schema.Document, status_code=status.HTTP_201_CREATED)
def create_document(
    document_in: schema.DocumentCreate, db: Session = Depends(get_db)
) -> schema.Document:
    service = DocumentService(db)
    document = service.create_document(document_in)
    return schema.Document.model_validate(document)


@router.get("/", response_model=List[schema.Document])
def list_documents(db: Session = Depends(get_db)) -> List[schema.Document]:
    service = DocumentService(db)
    documents = service.list_documents()
    return [schema.Document.model_validate(item) for item in documents]


@router.get("/{document_id}", response_model=schema.Document)
def get_document(document_id: int, db: Session = Depends(get_db)) -> schema.Document:
    service = DocumentService(db)
    document = service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return schema.Document.model_validate(document)


@router.put("/{document_id}", response_model=schema.Document)
def update_document(
    document_id: int, document_in: schema.DocumentUpdate, db: Session = Depends(get_db)
) -> schema.Document:
    service = DocumentService(db)
    document = service.update_document(document_id, document_in)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return schema.Document.model_validate(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)) -> None:
    service = DocumentService(db)
    deleted = service.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

