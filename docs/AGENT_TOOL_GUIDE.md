# Family Planner AI - 에이전트 및 툴 관리 가이드

이 프로젝트는 LangGraph 기반의 파이썬 코드를 작성하는 대신, **YAML 설정 파일**만으로 에이전트 노드를 런타임에 동적으로 생성하여 레지스트리(`app/agents/registry.py`)에 등록하는 구조를 채택하고 있습니다.

이 가이드는 새로운 자율 에이전트나 도구(Tool)를 추가하고 시스템에 연동하는 방법에 대해 설명합니다.

---

## 1. 에이전트(Agent) 생성 및 관리

새로운 에이전트를 추가하려면 파이썬 코드를 건드릴 필요 없이 오직 하나의 YAML 파일만 작성하면 됩니다. 

### 위치 및 형식
- **경로:** `config/agents/` 디렉토리
- **파일명:** `[agent_name].yaml` (예: `planner.yaml`)

### YAML 구조 예시
```yaml
# config/agents/example_agent.yaml
name: "example_agent"
description: "이 에이전트의 역할과 목적을 간략히 설명합니다."
system_prompt: |
  당신은 어떠어떠한 목적을 가진 에이전트입니다.
  항상 친절하게 답하고, 필요하다면 도구를 활용하세요.
llm_model: "gpt-4-turbo"
tools:
  - "domain_name.tool_name"
```

### 필수 속성 (AgentConfig 기준)
| 속성명 | 타입 | 설명 |
|---|---|---|
| `name` | String | 그래프 노드로 사용될 런타임 에이전트의 고유 이름입니다. |
| `description` | String | 에이전트의 목적 (보통 디버깅이나 시스템 로그용)입니다. |
| `system_prompt` | String | LLM 구동 시 제일 먼저 주입될 시스템 프롬프트(성격/지시사항)입니다. 멀티라인 `\|` 을 잘 활용하세요. |
| `llm_model` | String | 이 에이전트가 활용할 LLM의 모델 이름입니다. (예: `gpt-4o`, `claude-3-opus`) |
| `tools` | List[String] | 사용할 수 있는 툴들의 리스트입니다. 식별자 형식은 `[도메인명].[툴이름]` 이어야 합니다. |

> **노트:** YAML 파일이 추가되는 즉시 서버 재구동 시 자동으로 `app/graph/workflow.py`의 메인 그래프에 해당 이름(`name`)을 노드(Node) 식별자로 하여 연결 가능한 상태가 됩니다.

---

## 2. 도구(Tool) 생성 및 관리

도구(비즈니스 로직, 외부 API 호출, DB 조회 등)의 경우 실제 실행할 파이썬 함수 로직이 필요하며, 역할별로 묶인 여러 툴을 도메인 단위의 YAML로 묶어서 관리합니다.

### 2.1 툴 비즈니스 로직 작성 (Python)
먼저 실행될 파이썬 함수를 작성합니다.
- **경로 (권장):** `app/tools/[domain].py`
- **구현 예시:**
```python
# app/tools/calendar.py
def get_events(date_str: str) -> str:
    """특정 날짜의 일정을 조회합니다."""
    # 실제 조회 로직...
    return f"{date_str}의 일정: 가족 회식"
```

### 2.2 툴 설정 등록 (YAML)
만든 도구를 에이전트가 알 수 있도록 도메인별 YAML 파일에 등록합니다.
- **경로:** `config/tools/` 디렉토리
- **파일명:** `[domain_name].yaml` (예: `calendar.yaml`)

### YAML 구조 예시
```yaml
# config/tools/calendar.yaml
domain: "calendar"
tools:
  - name: "get_events"
    description: "특정 날짜의 가족 일정을 반환합니다."
    prompt: |
      이 도구를 호출할 때는 반드시 날짜를 'YYYY-MM-DD' 형식으로 입력해야 합니다.
    module: "app.tools.calendar" # 파이썬 함수가 위치한 모듈 경로
    function: "get_events"       # 모듈 내에서 실행할 함수 이름
```

### 필수 속성 (ToolConfig 기준)
| 속성 파일 위치 | 프로퍼티 | 설명 |
|---|---|---|
| 최상단 | `domain` | 이 스키마 파일 안의 툴들이 묶일 집합 이름 (에이전트에서 접근 시 사용하는 접두사) |
| `tools` 하위 | `name` | 툴의 고유 이름 (에이전트가 사용하는 `[domain].[name]` 매핑 타겟) |
| `tools` 하위 | `description` | LLM에게 이 툴이 무엇을 하는지 알려줄 기본 설명 |
| `tools` 하위 | `prompt` | (**선택형**) 툴 사용과 관련된 추가적인 세부 지시사항이나 제약조건 프롬프트 |
| `tools` 하위 | `module` | 파이썬 앱 내 경로(예: `app.tools.my_domain`) |
| `tools` 하위 | `function` | 모듈에서 선언된 함수 이름 |

---

## 3. 적용 (연결) 흐름
1. `config/tools/calendar.yaml`에 등록된 `get_events` 툴은 시스템 상에 **`calendar.get_events`** 라는 식별자로 레지스트리에 저장됩니다. 
2. 특정 에이전트(YAML)의 `tools:` 옵션에 `- "calendar.get_events"` 라고 적으면 해당 에이전트가 그 함수를 사용할 수 있게 바인딩됩니다.
3. 시스템/서버를 재시작하면 변경사항이 자동으로 적용됩니다.
