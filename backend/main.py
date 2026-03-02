"""
LegalSaathi Backend - FastAPI Application
AI Legal Document Analyzer for common Indians
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routes.upload import router as upload_router
from routes.tree import router as tree_router
from routes.query import router as query_router
from routes.pages import router as pages_router

load_dotenv()

app = FastAPI(
    title="LegalSaathi API",
    description="AI Legal Document Analyzer - Helping common Indians understand legal documents",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(upload_router, tags=["Upload"])
app.include_router(tree_router, tags=["Tree"])
app.include_router(query_router, tags=["Query"])
app.include_router(pages_router, tags=["Pages"])


@app.get("/")
async def root():
    return {
        "service": "LegalSaathi API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
