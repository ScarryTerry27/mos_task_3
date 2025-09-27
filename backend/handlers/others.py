from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from services.db import schema
from services.db.db import get_db
from services.db.service import DocumentService, MaterialService
from services.others.photo_client import analyze_photo

router = APIRouter(prefix="/others", tags=["others"])


@router.post(
    "/process-photo",
    response_model=schema.PhotoProcessingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def process_photo(
    user_id: int = Form(...),
    object_id: int = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> schema.PhotoProcessingResponse:
    """Accept a photo, forward it to the external services and persist the results."""

    if photo.content_type not in {"image/jpeg", "image/png", "image/jpg"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only JPEG and PNG are allowed.",
        )

    image_bytes = await photo.read()
    document_data, materials_data = analyze_photo(image_bytes)

    document_service = DocumentService(db)
    material_service = MaterialService(db)

    document_create = schema.DocumentCreate(
        user_id=user_id,
        object_id=object_id,
        doc_type=document_data.doc_type,
        doc_number=document_data.doc_number,
        doc_date_start=document_data.doc_date_start,
        doc_date_end=document_data.doc_date_end,
        doc_image_id=document_data.doc_image_id,
    )
    document = document_service.create_document(document_create)

    saved_materials: List[schema.Material] = []
    for material_data in materials_data:
        material_create = schema.MaterialCreate(
            name=material_data.name,
            okpd=material_data.okpd,
            amount=material_data.amount,
            uom=material_data.uom,
            to_be_certified=material_data.to_be_certified,
            certificate=material_data.certificate,
            doc_id=document.document_id,
        )
        material = material_service.create_material(material_create)
        saved_materials.append(schema.Material.model_validate(material))

    response = schema.PhotoProcessingResponse(
        document=schema.Document.model_validate(document),
        materials=saved_materials,
    )
    return response
