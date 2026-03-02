"""
Upload route - Handles PDF file upload and triggers PageIndex processing.
"""

import os
import uuid
import asyncio
from typing import Dict

from fastapi import APIRouter, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from services.pageindex_service import PageIndexService

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory store for document processing status
# In production, use Redis or a database
processing_status: Dict[str, dict] = {}
document_trees: Dict[str, dict] = {}


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Receives a PDF file, saves it with a unique doc_id,
    and starts PageIndex processing in the background.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        return JSONResponse(
            status_code=400,
            content={"error": "Only PDF files are accepted"},
        )

    doc_id = str(uuid.uuid4())[:8]
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.pdf")

    # Save uploaded file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Initialize status
    processing_status[doc_id] = {
        "status": "processing",
        "progress": 0,
        "nodes_built": 0,
        "current_node": None,
        "tree_ascii": "",
    }

    # Start PageIndex processing in background
    asyncio.create_task(_process_document(doc_id, file_path))

    return {"doc_id": doc_id}


async def _process_document(doc_id: str, file_path: str):
    """Background task to process a document with PageIndex."""
    try:
        service = PageIndexService()
        tree = await service.index_document(
            pdf_path=file_path,
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
    WebSocket endpoint that streams PageIndex tree building progress.
    Sends tree nodes one by one as they are built.
    """
    await websocket.accept()

    try:
        last_nodes_built = 0
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

            last_nodes_built = status.get("nodes_built", 0)
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass


def get_processing_status():
    """Expose processing status to other modules."""
    return processing_status


def get_document_trees():
    """Expose document trees to other modules."""
    return document_trees
