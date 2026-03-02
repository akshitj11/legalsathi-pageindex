"""
Upload route - Handles file upload (PDF, images, text) and triggers processing.
"""

import os
import uuid
import asyncio
from typing import Dict

from fastapi import APIRouter, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from services.pageindex_service import PageIndexService
from services.file_processor import FileProcessor

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Supported file types
SUPPORTED_EXTENSIONS = {
    ".pdf": "pdf",
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".webp": "image",
    ".bmp": "image",
    ".txt": "text",
    ".doc": "text",
    ".docx": "text",
}

# In-memory store for document processing status
# In production, use Redis or a database
processing_status: Dict[str, dict] = {}
document_trees: Dict[str, dict] = {}
document_metadata: Dict[str, dict] = {}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Receives a PDF, image, or text file, saves it with a unique doc_id,
    and starts processing in the background.
    """
    if not file.filename:
        return JSONResponse(
            status_code=400,
            content={"error": "No filename provided"},
        )

    # Get file extension
    ext = os.path.splitext(file.filename.lower())[1]
    file_type = SUPPORTED_EXTENSIONS.get(ext)

    if not file_type:
        supported = ", ".join(SUPPORTED_EXTENSIONS.keys())
        return JSONResponse(
            status_code=400,
            content={"error": f"Unsupported file type. Accepted: {supported}"},
        )

    doc_id = str(uuid.uuid4())[:8]
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}{ext}")

    # Save uploaded file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Store metadata
    document_metadata[doc_id] = {
        "file_type": file_type,
        "extension": ext,
        "original_name": file.filename,
        "file_path": file_path,
    }

    # Initialize status
    processing_status[doc_id] = {
        "status": "processing",
        "progress": 0,
        "nodes_built": 0,
        "current_node": None,
        "tree_ascii": "",
    }

    # Start processing in background
    asyncio.create_task(_process_document(doc_id, file_path, file_type))

    return {"doc_id": doc_id, "file_type": file_type}


async def _process_document(doc_id: str, file_path: str, file_type: str):
    """Background task to process a document."""
    try:
        processor = FileProcessor()

        # For non-PDF files, convert to text first, then build tree
        if file_type == "image":
            processing_status[doc_id]["current_node"] = "Extracting text from image..."
            processing_status[doc_id]["progress"] = 10
            text = await processor.extract_text_from_image(file_path)
            processing_status[doc_id]["progress"] = 30

            # Save extracted text for later use
            text_path = os.path.join(UPLOAD_DIR, f"{doc_id}_extracted.txt")
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(text)
            document_metadata[doc_id]["extracted_text"] = text
            document_metadata[doc_id]["text_path"] = text_path

        elif file_type == "text":
            processing_status[doc_id]["current_node"] = "Reading text file..."
            processing_status[doc_id]["progress"] = 10
            text = await processor.read_text_file(file_path)
            processing_status[doc_id]["progress"] = 30
            document_metadata[doc_id]["extracted_text"] = text

        # Build tree using PageIndex (for PDFs) or Gemini (for text/images)
        service = PageIndexService()

        if file_type == "pdf":
            tree = await service.index_document(
                pdf_path=file_path,
                doc_id=doc_id,
                status_store=processing_status,
            )
        else:
            # For non-PDF files, use Gemini to build a document tree from text
            extracted_text = document_metadata[doc_id].get("extracted_text", "")
            tree = await service.index_from_text(
                text=extracted_text,
                doc_id=doc_id,
                status_store=processing_status,
            )

        document_trees[doc_id] = tree
        processing_status[doc_id]["status"] = "completed"
        processing_status[doc_id]["progress"] = 100

    except Exception as e:
        processing_status[doc_id]["status"] = "error"
        processing_status[doc_id]["error"] = str(e)


@router.websocket("/ws/status/{doc_id}")
async def websocket_status(websocket: WebSocket, doc_id: str):
    """
    WebSocket endpoint that streams processing progress.
    Sends tree nodes one by one as they are built.
    """
    await websocket.accept()

    try:
        while True:
            if doc_id not in processing_status:
                await websocket.send_json({"error": "Document not found"})
                break

            status = processing_status[doc_id]

            # Send update
            await websocket.send_json(
                {
                    "status": status["status"],
                    "progress": status.get("progress", 0),
                    "nodes_built": status.get("nodes_built", 0),
                    "current_node": status.get("current_node"),
                    "tree_ascii": status.get("tree_ascii", ""),
                }
            )

            if status["status"] in ("completed", "error"):
                break

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass


def get_processing_status():
    """Expose processing status to other modules."""
    return processing_status


def get_document_trees():
    """Expose document trees to other modules."""
    return document_trees


def get_document_metadata():
    """Expose document metadata to other modules."""
    return document_metadata
