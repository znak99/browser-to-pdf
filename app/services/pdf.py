from __future__ import annotations

import asyncio
import os

from playwright.async_api import Browser, Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright


class PDFRenderError(RuntimeError):
    """Raised when a target URL cannot be converted to PDF."""


class PDFRenderer:
    def __init__(self, timeout_ms: int | None = None) -> None:
        self.timeout_ms = timeout_ms or int(os.getenv("BROWSER_TO_PDF_TIMEOUT_MS", "45000"))
        self._playwright = None
        self._browser: Browser | None = None

    async def start(self) -> None:
        if self._browser is not None:
            return

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--font-render-hinting=medium",
                "--no-sandbox",
            ],
        )

    async def close(self) -> None:
        if self._browser is not None:
            await self._browser.close()
            self._browser = None

        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None

    async def render(self, url: str) -> bytes:
        if self._browser is None:
            raise PDFRenderError("PDF 엔진이 아직 준비되지 않았습니다.")

        page = await self._browser.new_page(
            viewport={"width": 1440, "height": 2200},
            locale="ko-KR",
        )

        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
            if response is not None and response.status >= 400:
                raise PDFRenderError(f"대상 페이지가 {response.status} 상태 코드를 반환했습니다.")

            try:
                await page.wait_for_load_state("networkidle", timeout=15000)
            except PlaywrightTimeoutError:
                pass

            await self._warm_up_lazy_content(page)

            try:
                await page.emulate_media(media="screen")
            except PlaywrightError:
                pass

            return await page.pdf(
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                margin={
                    "top": "14mm",
                    "right": "12mm",
                    "bottom": "14mm",
                    "left": "12mm",
                },
            )
        except PlaywrightTimeoutError as exc:
            raise PDFRenderError("페이지 로딩 시간이 초과되었습니다. 더 단순한 페이지나 응답이 빠른 URL을 시도하세요.") from exc
        except PlaywrightError as exc:
            raise PDFRenderError("브라우저 렌더링 중 오류가 발생했습니다.") from exc
        finally:
            await page.close()

    async def _warm_up_lazy_content(self, page) -> None:
        await page.evaluate(
            """
            async () => {
              const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
              let lastHeight = 0;

              for (let index = 0; index < 8; index += 1) {
                window.scrollTo(0, document.body.scrollHeight);
                await delay(250);
                const nextHeight = document.body.scrollHeight;

                if (nextHeight === lastHeight) {
                  break;
                }

                lastHeight = nextHeight;
              }

              window.scrollTo(0, 0);
              await delay(150);
            }
            """
        )
        await asyncio.sleep(0.15)
