from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Use hardcoded path if env var is not set, for local dev
DB_PATH = os.getenv("DB_PATH", "sqlite:///./data/assets.db")
if not DB_PATH.startswith("sqlite"):
    # If standard path format, ensure it has sqlite:/// prefix
    if DB_PATH.startswith("/"):
        # Absolute path needs 4 slashes: sqlite:////absolute/path
        DB_PATH = f"sqlite:///{DB_PATH}"
    else:
        # Relative path needs 3 slashes: sqlite:///relative/path
        DB_PATH = f"sqlite://{DB_PATH}"

# Ensure directory exists for SQLite
if DB_PATH.startswith("sqlite"):
    db_file_path = DB_PATH.replace("sqlite:///", "")
    # Handle absolute or relative paths
    if "://" not in db_file_path: # simple file path check
        import pathlib
        path = pathlib.Path(db_file_path)
        if not path.parent.exists():
            print(f"[Database] Creating directory: {path.parent}")
            path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    DB_PATH, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
