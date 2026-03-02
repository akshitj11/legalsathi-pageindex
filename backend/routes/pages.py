"""
Pages route - Serves PDF pages as images for the viewer.
"""

import os

import fitz  # PyMuPDF
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")


@router.get("/page/{doc_id}/{page_number}")
async def get_page(doc_id: str, page_number: int):
    """
    Returns a PDF page rendered as a PNG image.
    Used by the PDF viewer panel in the frontend.
    """
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.pdf")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document not found")

    try:
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


@router.get("/page-count/{doc_id}")
async def get_page_count(doc_id: str):
    """Returns the total number of pages in the document."""
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.pdf")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        doc = fitz.open(file_path)
        count = len(doc)
        doc.close()
        return {"doc_id": doc_id, "page_count": count}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get page count: {str(e)}",
        )
