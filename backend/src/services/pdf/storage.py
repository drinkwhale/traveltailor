"""
Supabase Storage integration for PDF exports.
"""

from __future__ import annotations

import asyncio
import datetime as dt
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Optional
from uuid import UUID

from supabase import Client, create_client

from ...config.settings import settings


class PdfStorageError(RuntimeError):
    """Raised when storing the generated PDF fails."""


@dataclass(slots=True)
class StoredPdf:
    """Metadata about an uploaded PDF document."""

    url: str
    path: str
    expires_at: Optional[dt.datetime]


class SupabasePdfStorage:
    """Uploads generated PDFs to Supabase Storage and returns signed URLs."""

    def __init__(
        self,
        *,
        client: Optional[Client] = None,
        bucket_name: Optional[str] = None,
        folder: Optional[str] = None,
        signed_url_ttl: Optional[int] = None,
    ) -> None:
        self._client = client or create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        self._bucket = bucket_name or settings.PDF_BUCKET_NAME
        self._folder = folder or settings.PDF_STORAGE_FOLDER
        self._signed_url_ttl = max(60, signed_url_ttl or settings.PDF_SIGNED_URL_TTL)

    def _object_path(self, plan_id: UUID, file_name: str) -> str:
        base_path = PurePosixPath(self._folder.strip("/")) if self._folder else PurePosixPath()
        return str(base_path / str(plan_id) / file_name)

    async def upload_pdf(self, plan_id: UUID, file_name: str, content: bytes) -> StoredPdf:
        """Persist the PDF in Storage and return an accessible URL."""
        path = self._object_path(plan_id, file_name)
        storage = self._client.storage.from_(self._bucket)

        async def _upload() -> StoredPdf:
            try:
                storage.upload(
                    path,
                    content,
                    {
                        "content-type": "application/pdf",
                        "cache-control": "public, max-age=3600",
                        "upsert": True,
                    },
                )
            except Exception as exc:  # pragma: no cover - depends on Supabase runtime
                raise PdfStorageError(f"Failed to upload PDF to Supabase Storage: {exc}") from exc

            url: Optional[str] = None
            expires_at: Optional[dt.datetime] = None
            try:
                if settings.PDF_PUBLIC_BASE_URL:
                    url = f"{settings.PDF_PUBLIC_BASE_URL.rstrip('/')}/{path}"
                else:
                    signed = storage.create_signed_url(path, self._signed_url_ttl)
                    if isinstance(signed, dict):
                        url = signed.get("signedURL") or signed.get("signed_url")
                    else:
                        url = getattr(signed, "signed_url", None) or getattr(signed, "signedURL", None)
                    expires_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=self._signed_url_ttl)

                if not url:
                    url = storage.get_public_url(path)
                    expires_at = None
            except Exception as exc:  # pragma: no cover - thin wrapper around SDK behaviour
                raise PdfStorageError(f"Failed to generate public URL for PDF: {exc}") from exc

            return StoredPdf(url=url, path=path, expires_at=expires_at)

        return await asyncio.to_thread(_upload)
