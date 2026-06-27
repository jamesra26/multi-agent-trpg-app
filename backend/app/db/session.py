from __future__ import annotations

from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import make_url

from app.core.config import get_settings
from app.db.models import Base


def create_db_engine(database_url: str | None = None) -> Engine:
    resolved_url = database_url or get_settings().database_url
    _ensure_sqlite_parent_dir(resolved_url)
    connect_args = {"check_same_thread": False} if _is_sqlite_url(resolved_url) else {}
    return create_engine(resolved_url, connect_args=connect_args)


def init_db(database_url: str | None = None) -> Engine:
    engine = create_db_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine


def _ensure_sqlite_parent_dir(database_url: str) -> None:
    url = make_url(database_url)
    if not url.drivername.startswith("sqlite") or not url.database:
        return
    if url.database == ":memory:":
        return
    Path(url.database).expanduser().parent.mkdir(parents=True, exist_ok=True)


def _is_sqlite_url(database_url: str) -> bool:
    return make_url(database_url).drivername.startswith("sqlite")
