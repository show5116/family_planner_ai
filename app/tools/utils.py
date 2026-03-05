from langchain_core.tools import tool

@tool
def check_weather(location: str):
    """
    주어진 위치의 날씨를 확인하여 계획 수립을 돕습니다.
    """
    # 임시 구현
    return f"{location}의 날씨는 현재 맑고 쾌적합니다."

@tool
def google_calendar_search(query: str):
    """
    사용자의 구글 캘린더를 검색합니다.
    """
    # 임시 구현
    return f"'{query}'에 대한 충돌하는 일정을 찾을 수 없습니다."
