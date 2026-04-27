from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from app.models import Base

_engine = None
_async_session_maker = None
_engine_sync = None

def get_engine():
    global _engine
    if _engine is None:
        from app.config import DATABASE_URL
        _engine = create_async_engine(DATABASE_URL, echo=False)
    return _engine

def get_async_session_maker():
    global _async_session_maker
    if _async_session_maker is None:
        _async_session_maker = async_sessionmaker(
            get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _async_session_maker

def get_engine_sync():
    global _engine_sync
    if _engine_sync is None:
        from app.config import DATABASE_URL_SYNC
        _engine_sync = create_engine(DATABASE_URL_SYNC, echo=False)
    return _engine_sync

async def init_db():
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db():
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)