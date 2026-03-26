from typing import List, Optional

def create_task_draft(title: str, type: str, scheduled_at: str, due_at: str, participants: List[str], notes: Optional[str] = "") -> str:
    """
    일정 데이터를 구조화하여 초안을 작성합니다.
    (실제 Task JSON 데이터는 Agent Registry의 인터셉터를 통해 Graph State의 'plan' 키에 직접 저장됩니다)
    """
    return f"일정 초안 '{title}' 생성이 완료되었습니다. 사용자에게 이 초안의 요약본을 보여주고 최종적으로 시스템에 등록할지(저장할지) 확인받으세요."
