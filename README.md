# The Great Asset Growth Festival

자산 증식률 챌린지 웹 서비스입니다. FastAPI 백엔드와 Streamlit 프론트엔드로 구성되어 있습니다.

## 🚀 실행 방법

### 1. Docker 실행 (권장)
Docker가 설치된 환경에서 다음 명령어를 실행하세요.

```bash
docker compose up --build
# 또는
docker-compose up --build
```

실행 후:
- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **Frontend Dashboard:** [http://localhost:8501](http://localhost:8501)

### 2. 로컬 개발 환경 실행
Python 3.9+ 필요.

1. 의존성 설치
```bash
pip install -r requirements.txt
```

2. 백엔드 실행
```bash
uvicorn app.main:app --reload
```

3. 프론트엔드 실행 (새 터미널)
```bash
streamlit run app/dashboard.py
```

## 📁 프로젝트 구조
- `app/`: 소스 코드 (main.py, dashboard.py, database.py, models.py)
- `data/`: SQLite 데이터베이스 저장소
- `.env`: 환경 변수 (시작 자금 등)

## 📡 API Usage

The API is available at `http://localhost:8000/api/assets`.
Interactive documentation (Swagger UI) is available at `http://localhost:8000/docs`.

### 1. Add Asset Record (POST)
```bash
curl -X 'POST' \
  'http://localhost:8000/api/assets' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "KS",
  "date": "2024-01-28",
  "amount": 1050000
}'
```

### 2. Get All Records (GET)
```bash
curl -X 'GET' 'http://localhost:8000/api/assets'
```
