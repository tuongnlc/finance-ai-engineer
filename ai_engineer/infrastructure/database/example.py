import asyncio

from sqlalchemy import text

from ai_engineer.infrastructure.database.session import async_session_scope

async def main() -> None:
    async with async_session_scope() as session:
        result = await session.execute(text("SELECT 1"))
        print(result.scalar_one())

if __name__ == "__main__":
    asyncio.run(main())
