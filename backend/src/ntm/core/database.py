from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from ntm.core.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
engine = create_engine(
    settings.database_url.replace("+aiosqlite", ""),
    echo=False,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    import ntm.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
