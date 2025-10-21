"""
PDF rendering infrastructure backed by Playwright (Chromium / Puppeteer compatible).
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from ...config.settings import settings


class PdfRenderError(RuntimeError):
    """Base error for PDF rendering operations."""


class PdfBrowserStartupError(PdfRenderError):
    """Raised when the headless browser could not be launched."""


class _BrowserPool:
    """Simple async pool that reuses Chromium browser instances."""

    def __init__(self, size: int, launch_timeout: int) -> None:
        self._size = max(1, size)
        self._launch_timeout = launch_timeout * 1000  # Playwright expects milliseconds
        self._playwright: Playwright | None = None
        self._queue: asyncio.Queue[Browser] | None = None
        self._start_lock = asyncio.Lock()
        self._is_started = False

    async def _ensure_started(self) -> None:
        if self._is_started:
            return
        async with self._start_lock:
            if self._is_started:
                return
            try:
                self._playwright = await async_playwright().start()
                self._queue = asyncio.Queue(maxsize=self._size)
                for _ in range(self._size):
                    browser = await self._playwright.chromium.launch(
                        headless=True,
                        timeout=self._launch_timeout,
                        args=[
                            "--no-sandbox",
                            "--disable-setuid-sandbox",
                            "--disable-dev-shm-usage",
                            "--disable-gpu",
                        ],
                    )
                    await self._queue.put(browser)
                self._is_started = True
            except Exception as exc:  # pragma: no cover - startup is environment specific
                raise PdfBrowserStartupError("Failed to start headless browser for PDF rendering.") from exc

    async def acquire(self) -> Browser:
        await self._ensure_started()
        if self._queue is None:
            raise PdfBrowserStartupError("Browser pool not initialized.")
        return await self._queue.get()

    async def release(self, browser: Browser) -> None:
        if self._queue is None:
            # Pool was not initialized; close browser defensively.
            await browser.close()
            return
        await self._queue.put(browser)

    async def shutdown(self) -> None:
        if not self._is_started:
            return
        if self._queue is not None:
            while not self._queue.empty():
                browser = await self._queue.get()
                await browser.close()
        if self._playwright is not None:
            await self._playwright.stop()
        self._is_started = False
        self._queue = None
        self._playwright = None

    @asynccontextmanager
    async def page(self) -> AsyncIterator[Page]:
        browser = await self.acquire()
        context: BrowserContext | None = None
        try:
            context = await browser.new_context(locale=settings.PDF_TEMPLATE_LOCALE or "en-US")
            page = await context.new_page()
            yield page
        finally:
            if context is not None:
                await context.close()
            await self.release(browser)


class PdfRenderer:
    """Render HTML content into PDF bytes."""

    def __init__(self, pool: _BrowserPool) -> None:
        self._pool = pool

    async def render(  # noqa: PLR0913 - explicit parameters aid clarity
        self,
        html: str,
        *,
        wait_until: str = "networkidle",
        prefer_css_page_size: bool = True,
        landscape: bool = False,
        format: str = "A4",
    ) -> bytes:
        try:
            async with self._pool.page() as page:
                await page.set_content(html, wait_until=wait_until)
                pdf = await page.pdf(
                    format=format,
                    print_background=True,
                    prefer_css_page_size=prefer_css_page_size,
                    landscape=landscape,
                    margin={
                        "top": "25mm",
                        "bottom": "20mm",
                        "left": "15mm",
                        "right": "15mm",
                    },
                )
        except Exception as exc:  # pragma: no cover - rendering depends on runtime browser
            raise PdfRenderError("Failed to render PDF from HTML content.") from exc
        return pdf


_pool: _BrowserPool | None = None
_renderer: PdfRenderer | None = None
_pool_lock = asyncio.Lock()


async def get_pdf_renderer() -> PdfRenderer:
    """Return a singleton PDF renderer."""
    global _pool, _renderer
    if _renderer is not None:
        return _renderer
    async with _pool_lock:
        if _renderer is None:
            timeout = max(5, settings.PDF_RENDER_TIMEOUT)
            pool_size = max(1, settings.PDF_POOL_SIZE)
            _pool = _BrowserPool(size=pool_size, launch_timeout=timeout)
            _renderer = PdfRenderer(_pool)
    return _renderer


async def shutdown_pdf_renderer() -> None:
    """Dispose the browser pool (useful for tests or application shutdown)."""
    global _pool, _renderer
    if _pool is not None:
        await _pool.shutdown()
    _pool = None
    _renderer = None
