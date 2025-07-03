from __future__ import annotations

import io
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.services.pdf import PDFRenderError, PDFRenderer
from app.utils import build_download_filename, normalize_target_url

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

WORKFLOW = [
    "URL을 입력하면 서버가 허용 스킴과 호스트를 먼저 검증합니다.",
    "브라우저가 페이지를 연 뒤 네트워크 안정화와 지연 로딩 콘텐츠를 정리합니다.",
    "A4 PDF를 생성해 첨부 파일로 바로 내려줍니다.",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    renderer = PDFRenderer()
    await renderer.start()
    app.state.pdf_renderer = renderer
    yield
    await renderer.close()


app = FastAPI(title="browser-to-pdf", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def render_index(
    request: Request,
    *,
    target_url: str = "",
    error: str | None = None,
    status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
    context = {
        "request": request,
        "target_url": target_url,
        "error": error,
        "workflow": WORKFLOW,
    }
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
        status_code=status_code,
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return render_index(request)


@app.post("/download", response_model=None)
async def download_pdf(request: Request, target_url: str = Form(...)) -> Response:
    try:
        normalized_url = normalize_target_url(target_url)
    except ValueError as exc:
        return render_index(
            request,
            target_url=target_url,
            error=str(exc),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    renderer: PDFRenderer = request.app.state.pdf_renderer

    try:
        pdf_bytes = await renderer.render(normalized_url)
    except PDFRenderError as exc:
        return render_index(
            request,
            target_url=normalized_url,
            error=str(exc),
            status_code=status.HTTP_502_BAD_GATEWAY,
        )

    filename = build_download_filename(normalized_url)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})
