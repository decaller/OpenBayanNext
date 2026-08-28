from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="OpenBayan API",
    description="Shamela Classical Corpus IR and Synthesis Engine",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "online", "service": "OpenBayan API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
