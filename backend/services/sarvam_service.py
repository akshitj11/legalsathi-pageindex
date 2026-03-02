"""
Sarvam AI Service - Handles Hindi/English voice (STT + TTS) and translation.

Sarvam AI provides Indian-language-first AI models for:
- Speech-to-Text (STT) in Hindi/English
- Text-to-Speech (TTS) in Hindi/English
- Translation between Hindi and English
"""

import os
import base64
import asyncio
from typing import Optional

import httpx

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
SARVAM_BASE_URL = "https://api.sarvam.ai"


class SarvamService:
    """Service wrapper for Sarvam AI API."""

    def __init__(self):
        self.api_key = SARVAM_API_KEY
        self.headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json",
        }

    async def speech_to_text(
        self,
        audio_data: bytes,
        language: str = "hi-IN",
    ) -> str:
        """
        Convert speech audio to text using Sarvam AI STT.

        Args:
            audio_data: Raw audio bytes (WAV format preferred)
            language: Language code (hi-IN, en-IN)

        Returns:
            Transcribed text string
        """
        try:
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{SARVAM_BASE_URL}/speech-to-text",
                    headers=self.headers,
                    json={
                        "input": audio_base64,
                        "language_code": language,
                        "model": "saarika:v2",
                        "with_timestamps": False,
                    },
                )
                response.raise_for_status()
                result = response.json()
                return result.get("transcript", "")

        except httpx.HTTPError as e:
            raise Exception(f"Sarvam STT API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Speech-to-text failed: {str(e)}")

    async def text_to_speech(
        self,
        text: str,
        language: str = "hi",
        speaker: str = "meera",
    ) -> Optional[str]:
        """
        Convert text to speech using Sarvam AI TTS.

        Args:
            text: Text to convert to speech
            language: Language code (hi/en)
            speaker: Voice name (meera, arvind, etc.)

        Returns:
            Base64 encoded audio string, or None on failure
        """
        try:
            lang_code = "hi-IN" if language == "hi" else "en-IN"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{SARVAM_BASE_URL}/text-to-speech",
                    headers=self.headers,
                    json={
                        "input": text[:500],  # Limit text length
                        "target_language_code": lang_code,
                        "speaker": speaker,
                        "model": "bulbul:v1",
                        "pitch": 0,
                        "pace": 1.0,
                        "loudness": 1.0,
                        "enable_preprocessing": True,
                    },
                )
                response.raise_for_status()
                result = response.json()

                # Return base64 audio
                audio_base64 = result.get("audios", [None])[0]
                if audio_base64:
                    return f"data:audio/wav;base64,{audio_base64}"
                return None

        except httpx.HTTPError as e:
            raise Exception(f"Sarvam TTS API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Text-to-speech failed: {str(e)}")

    async def translate(
        self,
        text: str,
        source_language: str = "en",
        target_language: str = "hi",
    ) -> str:
        """
        Translate text between Hindi and English using Sarvam AI.

        Args:
            text: Text to translate
            source_language: Source language (en/hi)
            target_language: Target language (hi/en)

        Returns:
            Translated text
        """
        try:
            source_code = (
                "hi-IN" if source_language == "hi" else "en-IN"
            )
            target_code = (
                "hi-IN" if target_language == "hi" else "en-IN"
            )

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{SARVAM_BASE_URL}/translate",
                    headers=self.headers,
                    json={
                        "input": text,
                        "source_language_code": source_code,
                        "target_language_code": target_code,
                        "mode": "formal",
                        "model": "mayura:v1",
                        "enable_preprocessing": True,
                    },
                )
                response.raise_for_status()
                result = response.json()
                return result.get("translated_text", text)

        except httpx.HTTPError as e:
            raise Exception(f"Sarvam Translation API error: {str(e)}")
        except Exception as e:
            # Fallback: return original text
            return text

    async def transliterate(
        self,
        text: str,
        source_script: str = "latin",
        target_script: str = "devanagari",
    ) -> str:
        """
        Transliterate text between scripts.

        Args:
            text: Text to transliterate
            source_script: Source script (latin/devanagari)
            target_script: Target script (devanagari/latin)

        Returns:
            Transliterated text
        """
        try:
            source_lang = (
                "en-IN" if source_script == "latin" else "hi-IN"
            )
            target_lang = (
                "hi-IN" if target_script == "devanagari" else "en-IN"
            )

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{SARVAM_BASE_URL}/transliterate",
                    headers=self.headers,
                    json={
                        "input": text,
                        "source_language_code": source_lang,
                        "target_language_code": target_lang,
                    },
                )
                response.raise_for_status()
                result = response.json()
                return result.get("transliterated_text", text)

        except Exception:
            return text
