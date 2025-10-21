"""
Schemas for PDF export responses.
"""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class PdfExportResponse(BaseModel):
    """Metadata returned to the client after generating a PDF export."""

    file_name: str
    download_url: str
    storage_path: str
    expires_at: datetime | None = None
