from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from trustlens_pipeline import CaseInput, run_trustlens
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="TrustLens APAC API",
    version="0.1.0",
    description="Bounded Gemini-based scam analysis prototype for Cloud Run.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "https://trustlens-dashboard-993487022253.us-central1.run.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_BYTES = 8 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


class AnalyzeTextRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20_000)
    language: str = Field(default="en", min_length=2, max_length=16)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "trustlens", "status": "running", "docs": "/docs"}


def _run(message: str, language: str, image_path: str | None = None) -> JSONResponse:
    if not message.strip():
        raise HTTPException(status_code=400, detail="message must not be empty")
    try:
        result = run_trustlens(
            CaseInput(
                message=message,
                image_path=image_path,
                requested_language=language,
            )
        )
        return JSONResponse(result.model_dump(mode="json"))
    except Exception as exc:
        # Do not expose provider prompts, credentials, or stack traces to callers.
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=502, detail="AI analysis failed; please retry") from exc
    
@app.post("/v1/analyze/text")
def analyze_text(request: AnalyzeTextRequest) -> JSONResponse:
    return _run(request.message, request.language)


@app.post("/v1/analyze/multipart")
async def analyze_multipart(
    message: Annotated[str, Form()],
    language: Annotated[str, Form()] = "en",
    screenshot: Annotated[UploadFile | None, File()] = None,
) -> JSONResponse:
    temporary_path: str | None = None
    try:
        if screenshot is not None:
            if screenshot.content_type not in ALLOWED_IMAGE_TYPES:
                raise HTTPException(status_code=415, detail="Only JPEG, PNG, and WebP are accepted")
            data = await screenshot.read(MAX_UPLOAD_BYTES + 1)
            if len(data) > MAX_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="Screenshot exceeds 8 MB limit")
            suffix = Path(screenshot.filename or "upload.jpg").suffix.lower() or ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
                handle.write(data)
                temporary_path = handle.name
        return _run(message, language, temporary_path)
    finally:
        if temporary_path:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass
    
@app.exception_handler(413)
async def request_too_large_handler(_, __):
    return JSONResponse(status_code=413, content={"detail": "request too large"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", "8080")))

# Example requests:
# curl -X POST "$SERVICE_URL/v1/analyze/text" \
#   -H 'Content-Type: application/json' \
#   -d '{"message":"Your refund is pending. Share your OTP.","language":"en"}'
#
# curl -X POST "$SERVICE_URL/v1/analyze/multipart" \
#   -F 'message=Your refund is pending. Share your OTP.' \
#   -F 'language=en' \
#   -F 'screenshot=@./screenshot.png'

