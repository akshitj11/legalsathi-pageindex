"""
Pages route - Serves document pages/content for the viewer.

Handles PDFs (rendered as images), images (served directly),
and text files (returned as text content).
"""

import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, JSONResponse

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")


def _get_document_metadata(doc_id: str) -> dict:
    """Get document metadata from the upload module."""
    from routes.upload import get_document_metadata

    metadata = get_document_metadata()
    return metadata.get(doc_id, {})


@router.get("/page/{doc_id}/{page_number}")
async def get_page(doc_id: str, page_number: int):
    """
    Returns a document page as content.
    - PDF: renders page as PNG image
    - Image: serves the original image file
    - Text: returns the text content as JSON
    """
    meta = _get_document_metadata(doc_id)
    file_type = meta.get("file_type", "pdf")
    file_path = meta.get("file_path", "")

    # Fallback: try to find a PDF with this doc_id (backward compatibility)
    if not file_path or not os.path.exists(file_path):
        file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.pdf")
        file_type = "pdf"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document not found")

    if file_type == "pdf":
        return _serve_pdf_page(file_path, page_number)
    elif file_type == "image":
        return _serve_image(file_path)
    elif file_type == "text":
        return await _serve_text_content(doc_id, meta)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")


def _serve_pdf_page(file_path: str, page_number: int) -> Response:
    """Render a PDF page as a PNG image."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)

        if page_number < 1 or page_number > len(doc):
            doc.close()
            raise HTTPException(
                status_code=400,
                detail=f"Page number must be between 1 and {len(doc)}",
            )

        # Render page at 2x resolution for clarity on mobile
        page = doc[page_number - 1]
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")

        doc.close()

        return Response(
            content=img_bytes,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=3600",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to render page: {str(e)}",
        )


def _serve_image(file_path: str) -> Response:
    """Serve an image file directly."""
    ext = os.path.splitext(file_path.lower())[1]
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
    }
    mime_type = mime_types.get(ext, "image/jpeg")

    try:
        with open(file_path, "rb") as f:
            img_bytes = f.read()

        return Response(
            content=img_bytes,
            media_type=mime_type,
            headers={
                "Cache-Control": "public, max-age=3600",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to serve image: {str(e)}",
        )


async def _serve_text_content(doc_id: str, meta: dict) -> JSONResponse:
    """Return text content as JSON."""
    extracted_text = meta.get("extracted_text", "")

    if not extracted_text:
        # Try reading from the extracted text file
        text_path = meta.get("text_path", "")
        if text_path and os.path.exists(text_path):
            with open(text_path, "r", encoding="utf-8") as f:
                extracted_text = f.read()

    if not extracted_text:
        # Try reading the original file
        file_path = meta.get("file_path", "")
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    extracted_text = f.read()
            except Exception:
                extracted_text = "[Could not read file content]"

    return JSONResponse(
        content={"text": extracted_text, "file_type": "text"},
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/page-count/{doc_id}")
async def get_page_count(doc_id: str):
    """
    Returns the total number of pages in the document.
    - PDF: actual page count
    - Image: always 1
    - Text: always 1
    """
    meta = _get_document_metadata(doc_id)
    file_type = meta.get("file_type", "pdf")
    file_path = meta.get("file_path", "")

    # Fallback for backward compatibility
    if not file_path or not os.path.exists(file_path):
        file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.pdf")
        file_type = "pdf"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document not found")

    if file_type == "pdf":
        try:
            import fitz

            doc = fitz.open(file_path)
            count = len(doc)
            doc.close()
            return {"doc_id": doc_id, "page_count": count, "file_type": "pdf"}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get page count: {str(e)}",
            )
    else:
        # Images and text files are single-page
        return {"doc_id": doc_id, "page_count": 1, "file_type": file_type}


@router.get("/document-info/{doc_id}")
async def get_document_info(doc_id: str):
    """
    Returns metadata about the document (type, name, etc.).
    Used by the frontend to determine how to display the document.
    """
    meta = _get_document_metadata(doc_id)

    if not meta:
        # Fallback: check if a PDF exists
        pdf_path = os.path.join(UPLOAD_DIR, f"{doc_id}.pdf")
        if os.path.exists(pdf_path):
            return {
                "doc_id": doc_id,
                "file_type": "pdf",
                "original_name": f"{doc_id}.pdf",
            }
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "doc_id": doc_id,
        "file_type": meta.get("file_type", "pdf"),
        "original_name": meta.get("original_name", "unknown"),
        "extension": meta.get("extension", ".pdf"),
    }
