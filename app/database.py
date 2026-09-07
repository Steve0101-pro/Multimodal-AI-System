from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings


DATABASE_URL_STR =settings.DATABASE_URL.get_secret_value()

if DATABASE_URL_STR.startswith("postgresql://"):
    DATABASE_URL_STR = DATABASE_URL_STR.replace("postgresql://", "postgresql+asyncpg://", 1)

engine= create_async_engine(
    DATABASE_URL_STR,
    echo=False,
  pool_pre_ping=True,
  pool_recycle=300,
    connect_args={
        "statement_cache_size": 0,       # Disables asyncpg statement preparation caching
        "prepared_statement_cache_size": 0 # Safe guard wrapper variant fallback flag
    }
)

SessionLocal = sessionmaker(
     bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as db:

      try:
        yield db
      except Exception:
        await db.rollback()
        raise    
      finally:
         await db.close()