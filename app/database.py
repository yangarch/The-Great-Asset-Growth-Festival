import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import pathlib

load_dotenv()

# 1. 환경 변수에서 경로 가져오기 (없으면 기본값 설정)
# 도커 environment에는 /app/data/assets.db 가 들어있어야 합니다.
db_path_raw = os.getenv("DB_PATH", "./data/assets.db")

# 2. SQLite 연결 URL 생성 로직 단순화
if db_path_raw.startswith("sqlite:///"):
    DB_URL = db_path_raw
else:
    # 절대 경로나 상대 경로 모두 안전하게 sqlite:/// 를 붙여줍니다.
    # 예: /app/data/assets.db -> sqlite:////app/data/assets.db (슬래시 4개)
    # 예: ./data/assets.db -> sqlite:///./data/assets.db (슬래시 3개)
    clean_path = db_path_raw.replace("sqlite://", "")
    DB_URL = f"sqlite:///{clean_path}"

print(f"[Database] Connecting to: {DB_URL}")

# 3. 디렉토리 자동 생성 (도커 볼륨이 꼬였을 때를 대비)
db_file_path = DB_URL.replace("sqlite:///", "")
path = pathlib.Path(db_file_path)
if not path.parent.exists():
    print(f"[Database] Creating directory: {path.parent}")
    path.parent.mkdir(parents=True, exist_ok=True)

# 4. Engine 설정
engine = create_engine(
    DB_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()