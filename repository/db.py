from dotenv import load_dotenv
from models import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.config import load_config
import os

# config = load_config()

# username = config["database"]["username"]
# password = config["database"]["password"]
# database_name = config["database"]["database_name"]

# DATABASE_URL = "postgresql+asyncpg://" + username + ":" + password + "@localhost:5432/" + database_name
# load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# asyncio.run(init_db)
