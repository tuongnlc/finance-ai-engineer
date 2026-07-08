from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from functools import lru_cache

# 1. Define your connection parameters
USERNAME = 'postgres'
PASSWORD = 'postgres'
HOST = 'localhost'
PORT = '5433'  # Default PostgreSQL port
DATABASE = 'chatbot_db'

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
