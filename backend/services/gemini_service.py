"""
Gemini Service - Handles direct interactions with Google's Gemini API
for document explanation and language processing.
"""

import os
from typing import Optional

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


class GeminiService:
    """Service for Gemini 1.5 Pro API interactions."""

    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self._model = None

    @property
    def model(self):
        """Lazy-initialize the Gemini model."""
        if self._model is None:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel("gemini-1.5-pro")
        return self._model

    async def explain_clause(
        self,
        clause_text: str,
        language: str = "hi",
        context: Optional[str] = None,
    ) -> str:
        """
        Explain a legal clause in simple language.

        Args:
            clause_text: The legal text to explain
            language: Target language (hi/en)
            context: Optional surrounding context

        Returns:
            Simple explanation string
        """
        lang_instruction = (
            "simple Hindi (Hinglish is fine, use everyday language)"
            if language == "hi"
            else "simple English (use everyday words, avoid legal jargon)"
        )

        context_section = ""
        if context:
            context_section = f"\nContext from the document: {context}\n"

        prompt = f"""You are LegalSaathi, a friendly legal document explainer for common Indians.
Your job is to explain legal clauses so that even someone with no education can understand them.

Rules:
- Use {lang_instruction}
- Maximum 3 sentences
- Give practical implications (what does this mean for the person?)
- Never use legal jargon
- Be direct and reassuring
{context_section}
Legal clause to explain:
"{clause_text}"

Simple explanation:"""

        import asyncio

        response = await asyncio.to_thread(
            self.model.generate_content, prompt
        )
        return response.text.strip()

    async def generate_document_summary(
        self,
        document_text: str,
        language: str = "hi",
    ) -> str:
        """
        Generate a brief summary of the entire document.

        Args:
            document_text: Full document text (first few pages)
            language: Target language

        Returns:
            Brief document summary
        """
        lang = "Hindi/Hinglish" if language == "hi" else "English"

        prompt = f"""You are LegalSaathi. Summarize this legal document in {lang}
in 3-4 bullet points. Keep it very simple for someone with no legal knowledge.
Focus on: What type of document is this? Who are the parties? What are the key obligations?

Document text:
{document_text[:5000]}

Summary:"""

        import asyncio

        response = await asyncio.to_thread(
            self.model.generate_content, prompt
        )
        return response.text.strip()

    async def translate_tree_labels(
        self,
        labels: list[str],
        target_language: str = "hi",
    ) -> list[str]:
        """
        Translate tree node labels to the target language.
        Uses Gemini for natural-sounding translations.

        Args:
            labels: List of English labels
            target_language: Target language code

        Returns:
            List of translated labels
        """
        if target_language == "en":
            return labels

        labels_text = "\n".join(f"- {label}" for label in labels)

        prompt = f"""Translate these legal document section headings to simple Hindi/Hinglish.
Make them sound natural, like how a common Indian person would describe these topics.
Keep translations short (2-4 words max).

English headings:
{labels_text}

Return ONLY the Hindi translations, one per line, in the same order. No bullets or numbering."""

        import asyncio

        response = await asyncio.to_thread(
            self.model.generate_content, prompt
        )

        translated = [
            line.strip()
            for line in response.text.strip().split("\n")
            if line.strip()
        ]

        # Ensure we have the same number of translations
        while len(translated) < len(labels):
            translated.append(labels[len(translated)])

        return translated[: len(labels)]

    async def detect_language(self, text: str) -> str:
        """
        Detect if the input text is Hindi or English.

        Args:
            text: Input text

        Returns:
            Language code ('hi' or 'en')
        """
        # Simple heuristic: check for Devanagari characters
        devanagari_count = sum(
            1 for char in text if "\u0900" <= char <= "\u097F"
        )
        total_alpha = sum(1 for char in text if char.isalpha())

        if total_alpha == 0:
            return "hi"  # Default to Hindi

        if devanagari_count / total_alpha > 0.3:
            return "hi"

        # Check for common Hindi words written in Roman script (Hinglish)
        hindi_markers = [
            "kya", "hai", "kab", "kaise", "kitna", "dena", "lena",
            "hoga", "mein", "par", "se", "ka", "ki", "ke",
            "nahi", "aur", "ya", "toh", "bhi", "wala",
            "kiraya", "paisa", "ghar", "baatein", "zaruri",
        ]

        words = text.lower().split()
        hindi_word_count = sum(1 for w in words if w in hindi_markers)

        if hindi_word_count >= 2 or (
            len(words) <= 5 and hindi_word_count >= 1
        ):
            return "hi"

        return "en"
