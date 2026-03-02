# LegalSaathi — AI Legal Document Analyzer

Helping common Indians understand their legal documents without any legal knowledge. Upload any PDF — rent agreement, job contract, loan paper — and get simple Hindi/English explanations powered by AI.

## Architecture

```
┌─────────────────┬──────────────────┬─────────────────┐
│   TREE PANEL    │   PDF VIEWER     │   CHAT PANEL    │
│                 │                  │                 │
│ ASCII markdown  │  PDF page image  │ Query input     │
│ tree rendered   │  highlighted     │ (text/voice)    │
│ in code block   │  relevant section│                 │
│                 │                  │ exact quote     │
│ Each node is    │                  │ + simple hindi  │
│ clickable       │                  │ explanation     │
│                 │                  │ + follow ups    │
└─────────────────┴──────────────────┴─────────────────┘
```

## Tech Stack

| Layer    | Technology                                        |
| -------- | ------------------------------------------------- |
| Frontend | Next.js 14 (App Router), Tailwind CSS, react-markdown |
| Backend  | FastAPI, PageIndex, Gemini 1.5 Pro                |
| Voice    | Sarvam AI (STT + TTS + Translation)               |
| PDF      | PyMuPDF                                           |
| Design   | Neobrutalism (sharp edges, harsh shadows, chunky) |

## Project Structure

```
legalsaathi/
├── frontend/
│   ├── app/
│   │   ├── page.tsx                    # Landing + upload
│   │   └── analyze/[doc_id]/page.tsx   # Main 3-panel interface
│   ├── components/
│   │   ├── TreeViewer.tsx              # ASCII tree renderer
│   │   ├── PDFViewer.tsx               # PDF page display
│   │   ├── ChatPanel.tsx               # Query + response
│   │   ├── VoiceInput.tsx              # Voice recording
│   │   └── UploadZone.tsx              # Drag-and-drop upload
│   └── lib/
│       └── api.ts                      # API calls to backend
│
├── backend/
│   ├── main.py                         # FastAPI app
│   ├── routes/
│   │   ├── upload.py                   # POST /upload + WebSocket
│   │   ├── tree.py                     # GET /tree/{doc_id}
│   │   ├── query.py                    # POST /query/{doc_id}
│   │   └── pages.py                    # GET /page/{doc_id}/{page}
│   ├── services/
│   │   ├── pageindex_service.py        # PageIndex indexing + querying
│   │   ├── gemini_service.py           # Gemini 1.5 Pro explanations
│   │   └── sarvam_service.py           # Sarvam AI STT/TTS/translate
│   └── utils/
│       └── tree_to_ascii.py            # JSON tree → ASCII art
```

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Fill in GEMINI_API_KEY and SARVAM_API_KEY
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Set NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run dev
```

## API Endpoints

| Method    | Route                        | Description                          |
| --------- | ---------------------------- | ------------------------------------ |
| POST      | `/upload`                    | Upload PDF, returns `doc_id`         |
| WebSocket | `/ws/status/{doc_id}`        | Real-time tree building progress     |
| GET       | `/tree/{doc_id}`             | Full document tree (JSON + ASCII)    |
| POST      | `/query/{doc_id}`            | Query document, get explanation      |
| GET       | `/page/{doc_id}/{page_num}`  | PDF page as PNG image                |
| GET       | `/page-count/{doc_id}`       | Total page count                     |

## Environment Variables

```
# Backend
GEMINI_API_KEY=         # https://aistudio.google.com/app/apikey
SARVAM_API_KEY=         # https://dashboard.sarvam.ai

# Frontend
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## How It Works

1. **Upload** — User uploads a PDF document
2. **Index** — PageIndex builds a reasoning-based tree structure (streamed via WebSocket)
3. **Explore** — Interactive ASCII tree, PDF viewer, and chat in a 3-panel layout
4. **Ask** — Type or speak a question in Hindi or English
5. **Understand** — Get the exact quote from the document + a simple explanation + follow-up suggestions

## Design System (Neobrutalism)

- Background: `#F5F5F0` / Surface: `#EFEFEA` / Primary: `#1A1A1A` / Accent: `#E8E8E0`
- Font: Space Grotesk (headings), Space Mono (code)
- Heavy black borders, harsh `4px 4px 0px #000` shadows
- No rounded corners — sharp edges everywhere
- Hover states shift elements with `translate-x/y`
