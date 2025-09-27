from __future__ import annotations

from datetime import date, timedelta
from typing import List, Tuple
from uuid import uuid4

from services.db import schema


def analyze_photo(image_bytes: bytes) -> Tuple[schema.DocumentBase, List[schema.MaterialBase]]:
    """Mock photo analysis services that returns document and material metadata."""

    today = date.today()
    document_data = schema.DocumentBase(
        doc_type=schema.DocTypeEnum.TTN,
        doc_number=f"DOC-{uuid4().hex[:8].upper()}",
        doc_date_start=today,
        doc_date_end=today + timedelta(days=30),
        doc_image_id=uuid4().hex,
    )

    materials_data = [
        schema.MaterialBase(
            name="Generic Construction Material",
            okpd="12.34.56",
            amount=100.0,
            uom="kg",
            to_be_certified=True,
            certificate="Generated certificate data",
        )
    ]

    return document_data, materials_data
