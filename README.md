# LegalSaathi — AI Legal Document Analyzer

**Helping common Indians understand their legal documents without any legal knowledge.**

Upload any document — rent agreement, job contract, loan paper, court notice — and get simple Hindi/English explanations powered by AI. Speak your questions, hear the answers. No legal jargon, no confusion.

LegalSathi uses PageIndex as its core document intelligence engine, replacing traditional vector based RAG with a reasoning first approach that's far better suited for structured legal documents. When a PDF is uploaded, PageIndex analyzes the full document and constructs a hierarchical tree mirroring the natural structure of legal texts like sections, clauses, sub-clauses, and schedules which is then rendered as an interactive ASCII tree in the left panel of the UI. When a user asks a question in Hindi or English, PageIndex doesn't do a fuzzy similarity search across random text chunks; instead, it reasons through the document tree to locate the most relevant node, enabling LegalSathi to return the exact quote from the precise clause and page number rather than a vague approximate match. This makes the system especially powerful for legal documents where context, hierarchy, and precision matter a clause in Section 4.2 means something very different from a similar-sounding phrase in an appendix, and PageIndex respects that distinction naturally.

---

## What It Does

LegalSaathi takes a legal document and makes it understandable for anyone. It builds an interactive document tree showing the structure of the document, lets you view the original, and answers your questions in plain Hindi or English — with voice support.

**Target users:** Common Indians with zero legal knowledge, primarily on mobile, often on slow connections.

### Key Features

- **Multi-format upload** — PDF, images (JPG/PNG/WEBP/BMP), and text files (TXT/DOC/DOCX)
- **Document tree** — AI-generated hierarchical breakdown of the document structure
- **Simple explanations** — Legal jargon converted to plain Hindi/English that anyone can understand
- **Voice input/output** — Ask questions by speaking, hear answers read aloud (Sarvam AI)
- **Bilingual** — Responds in the same language as your input (Hindi or English)
- **Source citations** — Every answer points to the exact clause and page in the original document
- **Follow-up suggestions** — Contextual next questions so you know what else to ask
- **Real-time processing** — WebSocket-based progress updates as the document tree is built

---

## Architecture

```
┌─────────────────┬──────────────────┬─────────────────┐
│   TREE PANEL    │  DOCUMENT VIEWER │   CHAT PANEL    │
│                 │                  │                 │
│ ASCII markdown  │  PDF page image  │ Query input     │
│ tree rendered   │  / image file    │ (text + voice)  │
│ in code block   │  / text content  │                 │
│                 │                  │ exact quote     │
│ Each node is    │  zoom controls   │ + simple hindi  │
│ clickable       │  page navigation │ explanation     │
│                 │                  │ + follow ups    │
└─────────────────┴──────────────────┴─────────────────┘
```

### How It Works

1. **Upload** — User uploads a PDF, image, or text file
2. **Process** — For PDFs, PageIndex builds a reasoning-based tree. For images, Gemini 1.5 Pro extracts text via vision. For text files, content is read directly.
3. **Index** — Gemini analyzes the document and creates a hierarchical tree structure (streamed via WebSocket)
4. **Explore** — Interactive ASCII tree + document viewer + chat in a 3-panel layout
5. **Ask** — Type or speak a question in Hindi or English
6. **Understand** — Get the exact quote from the document + a simple explanation + follow-up suggestions
7. **Listen** — Optionally hear the answer read aloud via Sarvam AI TTS

---

## Tech Stack

| Layer      | Technology                                              |
| ---------- | ------------------------------------------------------- |
| Frontend   | Next.js 14 (App Router), Tailwind CSS, react-markdown   |
| Backend    | FastAPI, Python 3.11+                                    |
| Document AI| PageIndex (PDF tree building), Gemini 1.5 Pro            |
| Voice & i18n| Sarvam AI (STT + TTS + Translation)                    |
| PDF        | PyMuPDF (page rendering)                                 |
| Image OCR  | Gemini 1.5 Pro Vision                                    |
| DOCX       | python-docx (with raw XML fallback)                      |
| Design     | Neobrutalism                                             |
| Deployment | Vercel (frontend) + Railway (backend)                    |

---

## Project Structure

```
legalsaathi/
├── frontend/                          # Next.js 14 application
│   ├── app/
│   │   ├── page.tsx                   # Landing page + file upload
│   │   ├── analyze/[doc_id]/page.tsx  # Main 3-panel analysis interface
│   │   ├── layout.tsx                 # Root layout (Space Grotesk font)
│   │   └── globals.css                # Neobrutalism design system CSS
│   ├── components/
│   │   ├── UploadZone.tsx             # Drag-and-drop multi-format upload
│   │   ├── PDFViewer.tsx              # Document viewer (PDF/image/text)
│   │   ├── TreeViewer.tsx             # Interactive ASCII tree renderer
│   │   ├── ChatPanel.tsx              # Query input + AI response display
│   │   └── VoiceInput.tsx             # Voice recording with Sarvam STT
│   ├── lib/
│   │   └── api.ts                     # Backend API client functions
│   ├── tailwind.config.js             # Neobrutalism design tokens
│   ├── next.config.js                 # Remote patterns for Railway
│   ├── tsconfig.json                  # TypeScript config (es5 target)
│   ├── package.json                   # Dependencies
│   └── .env.example                   # Environment variable template
│
├── backend/                           # FastAPI application
│   ├── main.py                        # App entry point, CORS, route registration
│   ├── routes/
│   │   ├── upload.py                  # POST /upload + WebSocket status stream
│   │   ├── tree.py                    # GET /tree/{doc_id}
│   │   ├── query.py                   # POST /query/{doc_id} + POST /voice-to-text
│   │   └── pages.py                   # GET /page, /page-count, /document-info
│   ├── services/
│   │   ├── pageindex_service.py       # PageIndex indexing + Gemini tree building
│   │   ├── gemini_service.py          # Gemini 1.5 Pro explanations + translation
│   │   ├── sarvam_service.py          # Sarvam AI STT / TTS / translate
│   │   └── file_processor.py          # Image OCR (Gemini vision) + text reading
│   ├── utils/
│   │   └── tree_to_ascii.py           # JSON tree -> ASCII art converter
│   ├── requirements.txt               # Python dependencies
│   ├── Procfile                       # Railway deployment config
│   └── .env.example                   # Environment variable template
│
├── .gitignore
└── README.md
```

---

## Setup

### Prerequisites

- **Python 3.11+** (backend)
- **Node.js 18+** (frontend)
- **Gemini API Key** — [Get from Google AI Studio](https://aistudio.google.com/app/apikey)
- **Sarvam AI API Key** — [Get from Sarvam Dashboard](https://dashboard.sarvam.ai)

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env` and add your keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here
```

## Supported File Formats

| Format | Extensions | How It's Processed |
| ------ | ---------- | ------------------ |
| PDF    | `.pdf`     | PageIndex tree building + PyMuPDF page rendering |
| Images | `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp` | Gemini 1.5 Pro Vision OCR -> text -> tree building |
| Text   | `.txt`     | Direct text reading with encoding detection |
| Word   | `.doc`, `.docx` | python-docx parsing (with raw XML fallback) -> tree building |


