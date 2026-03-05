# 프로젝트 컨벤션 (Project Conventions)

이 문서는 프로젝트의 코드 작성 및 유지보수를 위한 규칙을 정의합니다. 
AI 에이전트(Antigravity)는 작업을 수행할 때 반드시 이 규칙을 준수해야 합니다.

## 1. 언어 규칙 (Language Rules)
- **모든 주석(Comments)은 반드시 한글로 작성합니다.**
- **에이전트의 응답 메시지(String, Logs)는 반드시 한글로 작성합니다.**
- 변수명, 함수명, 클래스명은 영어를 사용하되, 의미가 명확해야 합니다.
- 커밋 메시지는 한글 또는 영어를 사용할 수 있으나, 팀의 기존 규칙을 따릅니다.

## 2. 코드 스타일
- Python 코드는 PEP 8 스타일 가이드를 따릅니다.
- Type Hinting을 적극적으로 사용합니다.

---
**Note to AI Agents**: 
Whenever you start a session in this codebase, read this file first and apply the "Korean Language Rule" strictly to all new and modified code.
