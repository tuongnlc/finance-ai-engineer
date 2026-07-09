from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from functools import lru_cache
import os

from dotenv import load_dotenv

load_dotenv()


def _normalize(value: str | None, default: str) -> str:
    if not value:
        return default
    v = value.strip()
    if v.lower() in {"none", "null"}:
        return default
    return v


USERNAME = _normalize(os.getenv("POSTGRES_USER"), "postgres")
PASSWORD = _normalize(os.getenv("POSTGRES_PASSWORD"), "postgres")
HOST = _normalize(os.getenv("POSTGRES_HOST"), "localhost")
PORT = _normalize(os.getenv("POSTGRES_PORT"), "5433")
DATABASE = _normalize(os.getenv("POSTGRES_DB"), "chatbot_db")

def _connection_url() -> str:
    return f"postgresql+psycopg://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    return create_async_engine(_connection_url(), echo=False)

async def dispose_engine() -> None:
    if get_engine.cache_info().currentsize == 0:
        return 
    
    engine = get_engine()
    await engine.dispose()
    get_engine.cache_clear()
