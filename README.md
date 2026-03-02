# LegalSaathi — AI Legal Document Analyzer

**Helping common Indians understand their legal documents without any legal knowledge.**

Upload any document — rent agreement, job contract, loan paper, court notice — and get simple Hindi/English explanations powered by AI. Speak your questions, hear the answers. No legal jargon, no confusion.

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
FRONTEND_URL=http://localhost:3000
```

Start the server:

```bash
uvicorn main:app --reload --port 8000
```

The API will be running at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive Swagger UI.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
```

Edit `frontend/.env.local`:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Start the dev server:

```bash
npm run dev
```

Open `http://localhost:3000` in your browser.

---

## API Reference

### Document Upload & Processing

| Method    | Route                        | Description                              |
| --------- | ---------------------------- | ---------------------------------------- |
| POST      | `/upload`                    | Upload a file (PDF/image/text), returns `doc_id` and `file_type` |
| WebSocket | `/ws/status/{doc_id}`        | Real-time tree building progress stream  |

### Document Retrieval

| Method | Route                        | Description                                |
| ------ | ---------------------------- | ------------------------------------------ |
| GET    | `/tree/{doc_id}`             | Full document tree (JSON + ASCII)          |
| GET    | `/page/{doc_id}/{page_num}`  | PDF page as PNG / image file / text as JSON|
| GET    | `/page-count/{doc_id}`       | Total page count + file type               |
| GET    | `/document-info/{doc_id}`    | Document metadata (type, name, extension)  |

### Querying & Voice

| Method | Route                        | Description                              |
| ------ | ---------------------------- | ---------------------------------------- |
| POST   | `/query/{doc_id}`            | Query document, returns structured explanation |
| POST   | `/voice-to-text`             | Convert audio to text (Sarvam AI STT)    |

### Query Request Body

```json
{
  "query": "Kiraya kitna dena hai?",
  "node_id": null,
  "language": "hi",
  "input_mode": "text",
  "output_mode": "text"
}
```

### Query Response

```json
{
  "exact_quote": "Tenant shall pay rent of Rs 8,000 by the 5th of every calendar month",
  "simple_explanation": "Aapko har mahine ki 5 tarikh tak 8,000 rupaye kiraya dena hoga.",
  "source": {
    "page": 2,
    "section": "Kiraya Kitna Dena Hai",
    "node_id": "0002"
  },
  "follow_up_suggestions": [
    "Late dene par kya hoga?",
    "Kiraya kaise dena hai - cash ya online?",
    "Kiraya badhega kya har saal?"
  ],
  "audio_url": null
}
```

---

## Supported File Formats

| Format | Extensions | How It's Processed |
| ------ | ---------- | ------------------ |
| PDF    | `.pdf`     | PageIndex tree building + PyMuPDF page rendering |
| Images | `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp` | Gemini 1.5 Pro Vision OCR -> text -> tree building |
| Text   | `.txt`     | Direct text reading with encoding detection |
| Word   | `.doc`, `.docx` | python-docx parsing (with raw XML fallback) -> tree building |

---

## Environment Variables

### Backend (`backend/.env`)

| Variable        | Required | Description                                    |
| --------------- | -------- | ---------------------------------------------- |
| `GEMINI_API_KEY`| Yes      | Google Gemini API key for document AI           |
| `SARVAM_API_KEY`| Yes      | Sarvam AI key for voice + translation           |
| `FRONTEND_URL`  | No       | Frontend URL for CORS (default: `http://localhost:3000`) |

### Frontend (`frontend/.env.local`)

| Variable                  | Required | Description                              |
| ------------------------- | -------- | ---------------------------------------- |
| `NEXT_PUBLIC_BACKEND_URL` | Yes      | Backend API URL (default: `http://localhost:8000`) |

---

## Deployment

### Frontend on Vercel

1. Connect the GitHub repo to Vercel
2. Set **Root Directory** to `frontend` in Vercel project settings
3. Add environment variable: `NEXT_PUBLIC_BACKEND_URL` = your Railway backend URL
4. Deploy — Vercel auto-detects Next.js

**Important:** Do not add a `vercel.json` file. The Root Directory setting in Vercel UI is sufficient and a `vercel.json` will conflict with it.

### Backend on Railway

1. Connect the GitHub repo to Railway
2. Set **Root Directory** to `backend`
3. Railway will auto-detect the `Procfile` and use: `uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}`
4. Add environment variables:
   - `GEMINI_API_KEY`
   - `SARVAM_API_KEY`
   - `FRONTEND_URL` = your Vercel frontend URL
5. Deploy

---

## Design System — Neobrutalism

The UI follows a strict neobrutalism design language:

| Token             | Value                        |
| ----------------- | ---------------------------- |
| Background        | `#F5F5F0`                    |
| Surface           | `#EFEFEA`                    |
| Primary           | `#1A1A1A`                    |
| Accent            | `#E8E8E0`                    |
| Font (headings)   | Space Grotesk                |
| Font (code/tree)  | Space Mono                   |
| Borders           | 2-4px solid black            |
| Shadows           | `4px 4px 0px #000`           |
| Border radius     | 0 (no rounded corners)       |
| Hover states      | `translate-x/y` shift        |

---

## AI Services Used

### PageIndex
Reasoning-based document tree construction. Analyzes PDF structure and builds a hierarchical tree of sections, clauses, and sub-clauses. Each node has English and Hindi labels.

### Google Gemini 1.5 Pro
- **Document explanation** — Converts legal jargon to simple language
- **Tree building from text** — Analyzes non-PDF content and creates structure
- **Image OCR** — Extracts text from document images via Gemini Vision
- **Follow-up generation** — Creates contextual next questions
- **Language detection** — Identifies Hindi vs English input (with Hinglish support)

### Sarvam AI
India-first AI models for:
- **Speech-to-Text (STT)** — `saarika:v2` model, supports Hindi and English
- **Text-to-Speech (TTS)** — `bulbul:v1` model, natural Hindi/English voices
- **Translation** — `mayura:v1` model, Hindi <-> English translation
- **Transliteration** — Script conversion between Latin and Devanagari

---

## License

This project is for educational and hackathon purposes.
