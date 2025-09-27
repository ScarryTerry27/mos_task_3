"""Stub client for processing inspection videos."""

from __future__ import annotations

from typing import List, Tuple

from services.db import schema


def analyze_video(video_bytes: bytes) -> Tuple[schema.CheckBase, List[schema.IncidentBase]]:
    """Mock video analysis that returns check and incident metadata.

    This function pretends to forward the provided video to an external
    detection service. Until the real integration is implemented we return
    deterministic metadata that can be stored in the database.
    """

    check_data = schema.CheckBase(
        info="Automatically generated inspection from video",
        location="Video stream location",
        status_check=schema.CheckStatusEnum.INCIDENT,
    )

    incidents_data = [
        schema.IncidentBase(
            photo="video_frame_reference",
            incident_status=True,
            incident_info="Potential safety violation detected in the video",
            prescription_type=schema.PrescriptionTypeEnum.TYPE_1,
        )
    ]

    return check_data, incidents_data

