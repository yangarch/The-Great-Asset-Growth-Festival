# The Great Asset Growth Festival


# PROJECT_VIBE.md: 자산 증식률 챌린지 웹 서비스

## 1. 프로젝트 개요

4명의 참가자(KS, DH, BH, YJ)의 자산 데이터를 API로 수집하고, 시작 금액 대비 증식률을 계산하여 순위와 그래프를 보여주는 대시보드 서비스입니다.

### 기술 스택

* **Backend:** Python (FastAPI)
* **Frontend:** Streamlit (데이터 시각화 및 프론트 구현에 최적화)
* **Database:** SQLite (로컬 파일 기반)
* **Infrastructure:** Docker, Docker-compose

---

## 2. 프로젝트 구조 (File Tree)

```text
asset-tracker/
├── app/
│   ├── main.py          # FastAPI & Streamlit 통합 또는 분리 실행
│   ├── database.py      # SQLite 스키마 및 CRUD
│   └── models.py        # 데이터 모델
├── data/                # SQLite DB 저장소 (Volume)
├── .env                 # 시작 자금 및 설정값
├── Dockerfile
├── docker-compose.yml
└── requirements.txt

```

---

## 3. 핵심 기능 요구사항

### 1) 데이터 모델링 및 DB

* **테이블 구조:** `id`, `name` (KS, DH, BH, YJ), `date` (YYYY-MM-DD), `amount` (자산)
* **API Endpoints:**
* `POST /api/assets`: JSON 데이터 수집 및 DB 저장
* `GET /api/assets`: 전체 데이터 조회



### 2) 비즈니스 로직 (증식률 계산)

* `.env`에 정의된 각 사용자별 `START_AMOUNT`를 기준으로 증식률 계산
* 
* 그래프용 지수: 시작점을 1로 둔 상대적 변동값 계산

### 3) 프론트엔드 대시보드 (Streamlit)

* **Leaderboard:** 현재 시점 증식률 기준 내림차순 정렬 (상단 배치)
* ## **Line Chart:** 일자별 자산 변동 추이 (모두 1에서 시작하는 비율 그래프)



---

## 4. 환경 설정 (.env)

```env
# 초기 자본 설정 (예시)
START_AMOUNT_KS=1000000
START_AMOUNT_DH=1200000
START_AMOUNT_BH=800000
START_AMOUNT_YJ=1500000

# 서버 설정
DB_PATH=/app/data/assets.db

```

---

## 5. Docker 구성 지침

* **Docker-compose:** - `backend`: 8000 포트 (API)
* `frontend`: 8501 포트 (Streamlit 대시보드)
* `/data` 디렉토리를 로컬 볼륨과 연결하여 DB 유지



---

## 6. AI에게 주는 첫 번째 프롬프트 (Vibe Start)

> "첨부한 `PROJECT_VIBE.md` 파일의 요구사항대로 프로젝트를 생성해줘.
> 1. FastAPI를 사용해 데이터를 받고 SQLite에 저장하는 백엔드를 구현해.
> 2. Streamlit을 사용해 `.env`의 시작 자금을 불러와 증식률을 계산하고, 순위표와 일자별 변동 그래프(모두 1에서 시작하는 지수형)를 그려주는 프론트를 구현해.
> 3. 맥미니 리눅스 환경에서 `docker-compose up --build` 한 번으로 실행 가능하도록 Dockerfile과 compose 파일을 작성해줘."
> 
> 
