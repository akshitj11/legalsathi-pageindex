"""
Query route - Handles user queries against the document tree.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal

from routes.upload import get_document_trees
from services.pageindex_service import PageIndexService
from services.sarvam_service import SarvamService

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    node_id: Optional[str] = None
    language: Literal["hi", "en"] = "hi"
    input_mode: Literal["text", "voice"] = "text"
    output_mode: Literal["text", "voice"] = "text"


class SourceInfo(BaseModel):
    page: int
    section: str
    node_id: str


class QueryResponse(BaseModel):
    exact_quote: str
    simple_explanation: str
    source: SourceInfo
    follow_up_suggestions: list[str]
    audio_url: Optional[str] = None


@router.post("/query/{doc_id}", response_model=QueryResponse)
async def query_document(doc_id: str, request: QueryRequest):
    """
    Runs PageIndex tree search with Gemini.
    Returns structured response with exact quote, simple explanation,
    source reference, and follow-up suggestions.
    """
    trees = get_document_trees()

    if doc_id not in trees:
        raise HTTPException(status_code=404, detail="Document not found")

    tree_data = trees[doc_id]

    try:
        # Run PageIndex query
        pi_service = PageIndexService()
        result = await pi_service.query_tree(
            tree=tree_data,
            query=request.query,
            node_id=request.node_id,
            language=request.language,
        )

        response = QueryResponse(
            exact_quote=result["exact_quote"],
            simple_explanation=result["simple_explanation"],
            source=SourceInfo(
                page=result["source"]["page"],
                section=result["source"]["section"],
                node_id=result["source"]["node_id"],
            ),
            follow_up_suggestions=result["follow_up_suggestions"],
        )

        # If voice output is requested, generate TTS audio
        if request.output_mode == "voice":
            sarvam = SarvamService()
            audio_url = await sarvam.text_to_speech(
                text=result["simple_explanation"],
                language=request.language,
            )
            response.audio_url = audio_url

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}",
        )


@router.post("/voice-to-text")
async def voice_to_text(audio_data: bytes):
    """
    Converts voice audio to text using Sarvam AI STT.
    """
    try:
        sarvam = SarvamService()
        text = await sarvam.speech_to_text(audio_data)
        return {"text": text}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Voice-to-text failed: {str(e)}",
        )
