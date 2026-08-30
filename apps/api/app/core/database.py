import os
from pathlib import Path
import libsql_client

def get_db_uri(raw_path: str) -> str:
    """
    Normalizes database URIs for libsql_client:
    - Resolves relative file paths to absolute paths formatted as `file:/path/to/db`.
    - Leaves network URIs (http://, libsql://) untouched.
    """
    if raw_path.startswith("file:"):
        clean_path = raw_path.replace("file:", "").split("?")[0]
        abs_path = Path(clean_path).resolve().as_posix()
        return f"file:{abs_path}"
    elif not raw_path.startswith(("http://", "https://", "libsql://", "ws://", "wss://")):
        abs_path = Path(raw_path).resolve().as_posix()
        return f"file:{abs_path}"
    return raw_path

class DatabaseManager:
    def __init__(self):
        self._client: libsql_client.Client = None

    async def connect(self):
        raw_db_path = os.getenv("DATABASE_PATH") or os.getenv("DB_PATH") or "data/shamela_corpus.db"
        resolved_uri = get_db_uri(raw_db_path)
        self._client = libsql_client.create_client(url=resolved_uri)

    async def close(self):
        if self._client:
            await self._client.close()

    @property
    def client(self) -> libsql_client.Client:
        if self._client is None:
            raise RuntimeError("Database client is not connected. Ensure lifespan connect() has run.")
        return self._client

db = DatabaseManager()

async def get_db_client() -> libsql_client.Client:
    """FastAPI Dependency Injection helper."""
    return db.client
