from contextlib import contextmanager
from sqlmodel import create_engine, Session, SQLModel
from .config import get_database_url


# Create engine with SQLite-specific settings
engine = create_engine(
    get_database_url(),
    echo=False,
    connect_args={"check_same_thread": False}
)


@contextmanager
def session_scope():
    """
    Provide a transactional scope for database operations.
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """
    Initialize database by creating all tables and enabling foreign keys.
    """
    # Enable foreign key constraints for SQLite
    with engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA foreign_keys=ON")

    # Create all tables
    SQLModel.metadata.create_all(engine)
