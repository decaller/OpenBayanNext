import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import db
from app.core.vectorizer import vectorizer
from app.services.retriever import vector_matrix_cache
from app.api.search import router as search_router
from app.api.chunks import router as chunks_router
from app.api.books import router as books_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Connect to Database (Read-Only / In-Process)
    await db.connect()
    
    # 2. Pre-warm Vectorizer ONNX Session (Eliminates Cold Start)
    vectorizer.warmup()
    
    # 3. Pre-load RAM Vector Matrix for Instant Sub-4ms Fallbacks
    try:
        await vector_matrix_cache.load(db.client)
    except Exception as e:
        print(f"⚠️ Vector cache load skipped: {e}")
        
    print("🚀 OpenBayan API Server Initialized & Ready for Queries.")
    yield
    
    # Teardown
    await db.close()
    print("🛑 OpenBayan API Server Shutdown Complete.")

app = FastAPI(
    title="OpenBayan API",
    description="High-Performance Classical Arabic Search & Reading Engine",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Astro SSR and Local Dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(search_router, prefix="/api/v1")
app.include_router(chunks_router, prefix="/api/v1")
app.include_router(books_router, prefix="/api/v1")

@app.get("/health", tags=["Diagnostic"])
async def health_check():
    """Healthcheck and database connectivity probe."""
    try:
        res = await db.client.execute("SELECT COUNT(*) FROM books")
        book_count = res.rows[0][0]
        return {
            "status": "healthy",
            "database": "connected",
            "total_books": book_count,
            "vectorizer": "ready",
            "vector_matrix_cached": vector_matrix_cache._is_loaded
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }

@app.get("/", tags=["Diagnostic"])
async def root():
    return {
        "service": "OpenBayan API",
        "docs": "/docs",
        "endpoints": {
            "search": "/api/v1/search?q=...",
            "chunks": "/api/v1/chunks/{id}",
            "surrounding": "/api/v1/chunks/{id}/surrounding",
            "books": "/api/v1/books",
            "chapter_stream": "/api/v1/books/{id}/sections/{sec_id}/chunks"
        }
    }
