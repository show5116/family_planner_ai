# 👨‍👩‍👧‍👦 Family Planner AI Agent

**Family Planner Ecosystem**을 위한 지능형 에이전트 서비스입니다.  
**LangGraph**를 기반으로 한 상태 기반 워크플로우 엔진과 **FastAPI** 서버를 결합하여, 가족 구성원의 일정을 조율하고 계획을 제안하는 AI 서비스를 제공합니다.

> **⚠️ AI 에이전트 주의사항**:  
> 작업을 시작하기 전에 반드시 [프로젝트 컨벤션](docs/CONVENTIONS.md)을 확인하고 준수하세요. (한글 사용 필수)

---

## 🛠️ 기술 스택 (Tech Stack)

### Core
- **Python 3.12+**
- **FastAPI**: 고성능 비동기 웹 프레임워크
- **LangGraph**: 상태 기반 멀티 에이전트/워크플로우 오케스트레이션
- **LangChain**: LLM 인터페이스 및 툴링
- **Pydantic**: 데이터 유효성 검사 및 설정 관리

### Environment & Tooling
- **uv**: 초고속 Python 패키지 및 프로젝트 관리자
- **Railway**: 배포 환경 (Dockerfile 없이 Procfile 배포 지원)

---

## 📂 프로젝트 구조 (Project Structure)

```text
family_planner_ai/
├── 📁 app/
│   ├── 📁 agents/          # Agent Logic (Nodes)
│   │   └── 📄 planner.py   # 기획 에이전트 (Planning Node)
│   ├── 📁 api/             # API Endpoints
│   │   └── 📁 routers/     # API Routers
│   │       └── 📄 planner.py # /chat 엔드포인트
│   ├── 📁 core/            # Core Configuration
│   │   └── 📄 config.py    # 환경변수 및 앱 설정 (Pydantic Settings)
│   ├── 📁 graph/           # LangGraph Workflow Definitions
│   │   └── 📄 workflow.py  # 그래프 및 엣지 구성
│   ├── 📁 models/          # Data Models (Schemas)
│   │   └── 📄 schemas.py   # Request/Response Pydantic Models
│   ├── 📁 state/           # State Management
│   │   └── 📄 state.py     # AgentState (TypedDict) 정의
│   └── 📁 tools/           # Agent Tools
│       └── 📄 utils.py     # Custom Tools (Weather, Calendar, etc.)
├── 📄 main.py              # Application Entrypoint
├── 📄 Procfile             # Railway Deployment Command
├── 📄 pyproject.toml       # Project Dependencies & Config
└── 📄 requirements.txt     # Production Dependencies (Exported)
```

---

## 🚀 시작하기 (Getting Started)

### 1. 사전 요구사항 (Prerequisites)
- [uv](https://github.com/astral-sh/uv)가 설치되어 있어야 합니다.

### 2. 프로젝트 설정 (Setup)
```bash
# 의존성 설치 및 가상환경 동기화
uv sync
```

### 3. 환경 변수 설정 (.env)
프로젝트 루트에 `.env` 파일을 생성하고 필요한 변수를 입력하세요.
```env
OPENAI_API_KEY=sk-...
```

### 4. 로컬 서버 실행 (Run Locally)
```bash
# 개발 모드 (Hot Reload 지원)
uv run main.py
```
서버가 시작되면 [http://127.0.0.1:8000](http://127.0.0.1:8000)에서 확인할 수 있습니다.

---

## 📖 API 문서 (Documentation)

서버 실행 후 다음 주소에서 자동 생성된 API 문서를 확인할 수 있습니다:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 주요 엔드포인트
- `GET /`: 서버 상태 확인
- `POST /api/v1/planner/chat`: AI 에이전트와 대화 및 계획 요청

---

## ☁️ 배포 (Deployment)

이 프로젝트는 **Railway** 배포에 최적화되어 있습니다.

1. **Procfile**이 포함되어 있어 별도의 설정 없이 배포 명령어가 자동 인식됩니다.
   ```text
   web: uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
   ```
2. `requirements.txt`가 포함되어 있어 Python 빌드팩이 자동으로 의존성을 설치합니다.
3. 배포 시 **Environment Variables**에 `OPENAI_API_KEY`를 설정하는 것을 잊지 마세요.
