"""
PageIndex Service - Handles document indexing and querying using PageIndex.

PageIndex uses Gemini 1.5 Pro for reasoning-based document tree construction,
providing structured hierarchical understanding of legal documents.
"""

import os
import asyncio
import json
from typing import Dict, Optional

from utils.tree_to_ascii import tree_to_ascii

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


class PageIndexService:
    """Service wrapper around the PageIndex library."""

    def __init__(self):
        self.api_key = GEMINI_API_KEY

    async def index_document(
        self,
        pdf_path: str,
        doc_id: str,
        status_store: Dict[str, dict],
    ) -> dict:
        """
        Index a PDF document using PageIndex.
        Updates status_store with real-time progress for WebSocket streaming.

        Args:
            pdf_path: Path to the PDF file
            doc_id: Unique document identifier
            status_store: Shared dict for progress updates

        Returns:
            PageIndex tree as a dictionary
        """
        try:
            from pageindex import PageIndex

            pi = PageIndex(api_key=self.api_key, model="gemini-1.5-pro")

            # Update status: starting indexing
            status_store[doc_id]["current_node"] = "Initializing PageIndex..."
            status_store[doc_id]["progress"] = 10

            # Run the blocking index call in a thread pool
            tree = await asyncio.to_thread(pi.index, pdf_path=pdf_path)

            # Convert tree to serializable format
            tree_data = self._serialize_tree(tree)

            # Update progress with built tree
            status_store[doc_id]["progress"] = 90
            status_store[doc_id]["nodes_built"] = self._count_nodes(tree_data)
            status_store[doc_id]["tree_ascii"] = tree_to_ascii(tree_data)
            status_store[doc_id]["current_node"] = "Finalizing..."

            return tree_data

        except ImportError:
            # PageIndex not installed — return a demo tree for development
            return await self._generate_demo_tree(pdf_path, doc_id, status_store)

    async def query_tree(
        self,
        tree: dict,
        query: str,
        node_id: Optional[str] = None,
        language: str = "hi",
    ) -> dict:
        """
        Query the document tree using PageIndex and Gemini.

        Args:
            tree: The PageIndex tree dictionary
            query: User's question
            node_id: Optional specific node to query
            language: Response language (hi/en)

        Returns:
            Structured response with quote, explanation, source, suggestions
        """
        try:
            from pageindex import PageIndex

            pi = PageIndex(api_key=self.api_key, model="gemini-1.5-pro")

            # Run query in thread pool
            result = await asyncio.to_thread(
                pi.query, tree=tree, query=query
            )

            # Structure the response
            return self._format_query_result(result, query, language)

        except ImportError:
            # PageIndex not installed — return demo response
            return self._generate_demo_response(query, language)

    def _serialize_tree(self, tree) -> dict:
        """Convert PageIndex tree object to a JSON-serializable dictionary."""
        if isinstance(tree, dict):
            return tree

        # Handle PageIndex tree object serialization
        try:
            if hasattr(tree, "to_dict"):
                return tree.to_dict()
            elif hasattr(tree, "__dict__"):
                return self._deep_serialize(tree.__dict__)
            else:
                return {"raw": str(tree)}
        except Exception:
            return {"raw": str(tree)}

    def _deep_serialize(self, obj) -> dict:
        """Recursively serialize an object to a dictionary."""
        if isinstance(obj, dict):
            return {k: self._deep_serialize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_serialize(item) for item in obj]
        elif hasattr(obj, "__dict__"):
            return self._deep_serialize(obj.__dict__)
        else:
            return obj

    def _count_nodes(self, tree_data: dict) -> int:
        """Count total nodes in the tree."""
        count = 1
        for child in tree_data.get("children", []):
            count += self._count_nodes(child)
        return count

    def _format_query_result(
        self, result, query: str, language: str
    ) -> dict:
        """Format a PageIndex query result into our response structure."""
        # Extract information from PageIndex result
        if isinstance(result, dict):
            exact_quote = result.get("quote", result.get("text", ""))
            page = result.get("page", 1)
            section = result.get("section", "General")
            node_id = result.get("node_id", "0001")
        else:
            exact_quote = str(result)
            page = 1
            section = "General"
            node_id = "0001"

        # Generate simple explanation using Gemini
        explanation = self._generate_explanation(exact_quote, query, language)

        # Generate follow-up suggestions
        suggestions = self._generate_follow_ups(query, section, language)

        return {
            "exact_quote": exact_quote,
            "simple_explanation": explanation,
            "source": {
                "page": page,
                "section": section,
                "node_id": node_id,
            },
            "follow_up_suggestions": suggestions,
        }

    def _generate_explanation(
        self, quote: str, query: str, language: str
    ) -> str:
        """Generate a simple explanation of the quote."""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel("gemini-1.5-pro")

            lang_instruction = (
                "simple Hindi (Hinglish is OK)"
                if language == "hi"
                else "simple English"
            )

            prompt = f"""You are a legal document explainer for common Indians with no legal knowledge.

Given this exact quote from a legal document:
"{quote}"

The user asked: "{query}"

Explain what this means in {lang_instruction}. Keep it very simple,
like explaining to someone who has never read a legal document.
Maximum 2-3 sentences. Be direct and practical."""

            response = model.generate_content(prompt)
            return response.text.strip()

        except Exception:
            if language == "hi":
                return f'Yeh clause kehta hai: "{quote}"'
            return f'This clause says: "{quote}"'

    def _generate_follow_ups(
        self, query: str, section: str, language: str
    ) -> list:
        """Generate contextual follow-up suggestions."""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel("gemini-1.5-pro")

            lang = "Hindi/Hinglish" if language == "hi" else "English"

            prompt = f"""Generate exactly 3 natural follow-up questions in {lang}
that a common Indian person might ask after asking "{query}" about the
"{section}" section of a legal document.

Keep questions simple, practical, and in everyday language.
Return only the 3 questions, one per line, no numbering."""

            response = model.generate_content(prompt)
            lines = [
                line.strip()
                for line in response.text.strip().split("\n")
                if line.strip()
            ]
            return lines[:3]

        except Exception:
            if language == "hi":
                return [
                    "Isme aur kya likha hai?",
                    "Yeh mujh par kaise apply hota hai?",
                    "Koi risk hai isme?",
                ]
            return [
                "What else does this say?",
                "How does this apply to me?",
                "Are there any risks?",
            ]

    async def _generate_demo_tree(
        self, pdf_path: str, doc_id: str, status_store: Dict[str, dict]
    ) -> dict:
        """
        Generate a realistic demo tree for development when PageIndex
        is not installed. Simulates the tree-building process with delays.
        """
        demo_nodes = [
            {
                "id": "root",
                "label": "Legal Document",
                "label_hi": "Kanuni Dastavez",
                "pages": "1-15",
                "children": [
                    {
                        "id": "0001",
                        "label": "Financial Terms",
                        "label_hi": "Paise se Related",
                        "pages": "1-5",
                        "summary": "Tenant shall pay Rs 8,000 by 5th of every month",
                        "children": [
                            {
                                "id": "0002",
                                "label": "Rent Amount",
                                "label_hi": "Kiraya Kitna Dena Hai",
                                "pages": "1-2",
                                "children": [],
                            },
                            {
                                "id": "0003",
                                "label": "Late Payment Rules",
                                "label_hi": "Late Payment Rules",
                                "pages": "2-3",
                                "children": [],
                            },
                            {
                                "id": "0004",
                                "label": "Security Deposit",
                                "label_hi": "Security Deposit",
                                "pages": "4-5",
                                "children": [],
                            },
                        ],
                    },
                    {
                        "id": "0005",
                        "label": "Property Terms",
                        "label_hi": "Ghar se Related",
                        "pages": "6-10",
                        "children": [
                            {
                                "id": "0006",
                                "label": "Lock-in Period",
                                "label_hi": "Lock-in Period",
                                "pages": "6-7",
                                "children": [],
                            },
                            {
                                "id": "0007",
                                "label": "Occupancy Rules",
                                "label_hi": "Rehne ke Niyam",
                                "pages": "8-9",
                                "children": [],
                            },
                            {
                                "id": "0008",
                                "label": "Maintenance",
                                "label_hi": "Ghar ki Dekhbhal",
                                "pages": "9-10",
                                "children": [],
                            },
                        ],
                    },
                    {
                        "id": "0009",
                        "label": "Important Clauses",
                        "label_hi": "Zaruri Baatein",
                        "pages": "11-15",
                        "children": [
                            {
                                "id": "0010",
                                "label": "Deposit Refund",
                                "label_hi": "Deposit Wapsi",
                                "pages": "11-12",
                                "children": [],
                            },
                            {
                                "id": "0011",
                                "label": "Termination Rules",
                                "label_hi": "Agreement Khatam Karna",
                                "pages": "13-15",
                                "children": [],
                            },
                        ],
                    },
                ],
            }
        ]

        # Simulate progressive tree building
        total_steps = 8
        for step in range(total_steps):
            await asyncio.sleep(0.8)
            progress = int((step + 1) / total_steps * 90)
            status_store[doc_id]["progress"] = progress
            status_store[doc_id]["nodes_built"] = step + 1
            status_store[doc_id]["current_node"] = f"Building node {step + 1}..."

            # Incrementally build ASCII tree
            partial_tree = demo_nodes[0].copy()
            status_store[doc_id]["tree_ascii"] = tree_to_ascii(partial_tree)

        return demo_nodes[0]

    def _generate_demo_response(self, query: str, language: str) -> dict:
        """Generate a demo response for development."""
        if language == "hi":
            return {
                "exact_quote": "Tenant shall pay rent of Rs 8,000 by the 5th of every calendar month",
                "simple_explanation": "Aapko har mahine ki 5 tarikh tak 8,000 rupaye kiraya dena hoga. Agar late diye toh penalty lag sakti hai.",
                "source": {
                    "page": 2,
                    "section": "Kiraya Kitna Dena Hai",
                    "node_id": "0002",
                },
                "follow_up_suggestions": [
                    "Late dene par kya hoga?",
                    "Kiraya kaise dena hai - cash ya online?",
                    "Kiraya badhega kya har saal?",
                ],
            }
        return {
            "exact_quote": "Tenant shall pay rent of Rs 8,000 by the 5th of every calendar month",
            "simple_explanation": "You must pay Rs 8,000 as rent by the 5th of every month. Late payment may attract penalties.",
            "source": {
                "page": 2,
                "section": "Rent Amount",
                "node_id": "0002",
            },
            "follow_up_suggestions": [
                "What happens if I pay late?",
                "How should I pay - cash or online?",
                "Will rent increase every year?",
            ],
        }
