"""
File Processor Service - Handles text extraction from images and text files.

Uses Gemini 1.5 Pro vision for image OCR and standard file reading for text.
"""

import os
import asyncio
import base64
from typing import Optional


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# MIME types for image files
IMAGE_MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
}


class FileProcessor:
    """Service for extracting text from images and reading text files."""

    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self._model = None

    @property
    def model(self):
        """Lazy-initialize the Gemini model for vision tasks."""
        if self._model is None:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel("gemini-1.5-pro")
        return self._model

    async def extract_text_from_image(self, file_path: str) -> str:
        """
        Extract text from an image using Gemini 1.5 Pro vision.

        Args:
            file_path: Path to the image file

        Returns:
            Extracted text from the image
        """
        ext = os.path.splitext(file_path.lower())[1]
        mime_type = IMAGE_MIME_TYPES.get(ext, "image/jpeg")

        # Read image and encode as base64
        with open(file_path, "rb") as f:
            image_data = f.read()

        image_b64 = base64.b64encode(image_data).decode("utf-8")

        prompt = """Extract ALL text from this image of a legal document.
Maintain the original structure and formatting as much as possible.
Include headers, paragraphs, bullet points, and any fine print.
If the text is in Hindi or any Indian language, transcribe it as-is.
If there are tables, represent them in a readable text format.
Return ONLY the extracted text, no commentary."""

        try:
            import google.generativeai as genai

            # Create image part for Gemini
            image_part = {
                "mime_type": mime_type,
                "data": image_b64,
            }

            response = await asyncio.to_thread(
                self.model.generate_content, [prompt, image_part]
            )
            return response.text.strip()

        except Exception as e:
            # Fallback: try basic OCR description
            return f"[Image text extraction failed: {str(e)}]"

    async def read_text_file(self, file_path: str) -> str:
        """
        Read text from a text file (.txt, .doc, .docx).

        Args:
            file_path: Path to the text file

        Returns:
            Text content of the file
        """
        ext = os.path.splitext(file_path.lower())[1]

        if ext == ".txt":
            return await self._read_plain_text(file_path)
        elif ext in (".doc", ".docx"):
            return await self._read_docx(file_path)
        else:
            return await self._read_plain_text(file_path)

    async def _read_plain_text(self, file_path: str) -> str:
        """Read a plain text file with encoding detection."""
        # Try UTF-8 first, then fall back to latin-1
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue

        # Last resort: read as bytes and decode with errors replaced
        with open(file_path, "rb") as f:
            return f.read().decode("utf-8", errors="replace")

    async def _read_docx(self, file_path: str) -> str:
        """
        Read text from a .docx file.
        Falls back to raw XML parsing if python-docx is not available.
        """
        try:
            import docx

            doc = await asyncio.to_thread(docx.Document, file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)

        except ImportError:
            # Fallback: extract text from docx XML (docx is a zip of XML files)
            return await self._read_docx_raw(file_path)

    async def _read_docx_raw(self, file_path: str) -> str:
        """Extract text from .docx by parsing the raw XML inside the zip."""
        import zipfile
        import xml.etree.ElementTree as ET

        try:
            with zipfile.ZipFile(file_path, "r") as z:
                with z.open("word/document.xml") as f:
                    tree = ET.parse(f)

            # Extract all text elements
            ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
            paragraphs = []

            for para in tree.iter(ns + "p"):
                texts = []
                for run in para.iter(ns + "r"):
                    for text_elem in run.iter(ns + "t"):
                        if text_elem.text:
                            texts.append(text_elem.text)
                if texts:
                    paragraphs.append("".join(texts))

            return "\n\n".join(paragraphs)

        except Exception as e:
            return f"[Failed to read .docx file: {str(e)}]"

    async def get_image_as_base64(self, file_path: str) -> Optional[str]:
        """
        Get an image file as a base64-encoded data URL.
        Used for serving images to the frontend viewer.

        Args:
            file_path: Path to the image file

        Returns:
            Base64 data URL string or None
        """
        ext = os.path.splitext(file_path.lower())[1]
        mime_type = IMAGE_MIME_TYPES.get(ext)

        if not mime_type:
            return None

        try:
            with open(file_path, "rb") as f:
                data = f.read()
            b64 = base64.b64encode(data).decode("utf-8")
            return f"data:{mime_type};base64,{b64}"
        except Exception:
            return None
