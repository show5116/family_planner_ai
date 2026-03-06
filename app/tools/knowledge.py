import os
from typing import Optional

def read_agent_knowledge() -> str:
    """
    Family Planner AI의 핵심 도메인 개념과 서비스 개요가 담긴 문서를 읽어옵니다.
    사용자가 '이 앱은 뭐하는 앱이야?', '무슨 기능이 있어?' 라고 물어볼 때 가장 먼저 호출하여 
    최신 기능을 파악하는 용도로 사용하세요.
    """
    # 프로젝트 루트 디렉토리 기준 docs 경로 찾기
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    knowledge_file_path = os.path.join(project_root, "docs", "AGENT_KNOWLEDGE.md")
    
    try:
        with open(knowledge_file_path, "r", encoding="utf-8") as f:
            content = f.read()
            return f"--- AGENT_KNOWLEDGE.md ---\n\n{content}\n\n--- END OF FILE ---"
    except FileNotFoundError:
        return "Error: AGENT_KNOWLEDGE.md 파일을 찾을 수 없습니다."
    except Exception as e:
        return f"Error reading knowledge file: {str(e)}"
