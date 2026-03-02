"""
Tree route - Returns the PageIndex document tree.
"""

from fastapi import APIRouter, HTTPException

from routes.upload import get_document_trees, get_processing_status
from utils.tree_to_ascii import tree_to_ascii

router = APIRouter()


@router.get("/tree/{doc_id}")
async def get_tree(doc_id: str):
    """
    Returns the full PageIndex tree as JSON.
    Also provides an ASCII markdown string representation.
    """
    trees = get_document_trees()
    status_store = get_processing_status()

    if doc_id not in trees:
        # Check if still processing
        if doc_id in status_store:
            status = status_store[doc_id]
            if status["status"] == "processing":
                raise HTTPException(
                    status_code=202,
                    detail="Document is still being processed",
                )
            elif status["status"] == "error":
                raise HTTPException(
                    status_code=500,
                    detail=f"Processing failed: {status.get('error', 'Unknown error')}",
                )
        raise HTTPException(status_code=404, detail="Document tree not found")

    tree_data = trees[doc_id]
    ascii_repr = tree_to_ascii(tree_data)

    return {
        "doc_id": doc_id,
        "tree": tree_data,
        "ascii": ascii_repr,
    }
