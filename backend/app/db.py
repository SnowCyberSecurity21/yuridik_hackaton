"""SQLAlchemy ulanishi (SQLite MVP, Postgres-ga tayyor)."""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import ROOT_DIR, get_settings


class Base(DeclarativeBase):
    pass


def _make_engine():
    url = get_settings().database_url
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        # nisbiy yo'lni repo ildiziga nisbatan hal qilamiz
        prefix = "sqlite:///"
        path = url[len(prefix):]
        if path and not path.startswith(":") and not Path(path).is_absolute():
            path = (ROOT_DIR / path).resolve()
            path.parent.mkdir(parents=True, exist_ok=True)
            url = prefix + path.as_posix()
    return create_engine(url, connect_args=connect_args, future=True)


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    from . import models  # noqa: F401  (jadvallarni ro'yxatdan o'tkazish)

    Base.metadata.create_all(bind=engine)
    _add_missing_columns()


def _add_missing_columns() -> None:
    """Eski SQLite bazaga yangi ustunlarni qo'shish (yengil migratsiya; Postgres uchun Alembic kerak bo'ladi)."""
    from sqlalchemy import inspect, text

    if not str(engine.url).startswith("sqlite"):
        return
    insp = inspect(engine)
    for table in Base.metadata.sorted_tables:
        if not insp.has_table(table.name):
            continue
        have = {c["name"] for c in insp.get_columns(table.name)}
        for col in table.columns:
            if col.name not in have and col.nullable:
                with engine.begin() as conn:
                    conn.execute(text(f'ALTER TABLE "{table.name}" ADD COLUMN "{col.name}" '
                                      f'{col.type.compile(engine.dialect)}'))


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
