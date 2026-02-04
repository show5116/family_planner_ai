from langchain_core.tools import tool

@tool
def check_weather(location: str):
    """
    Checks the weather for a given location to help with planning.
    """
    # Placeholder implementation
    return f"The weather in {location} is currently sunny and pleasant."

@tool
def google_calendar_search(query: str):
    """
    Search the user's google calendar.
    """
    # Placeholder implementation
    return f"Found no conflicting events for query: {query}"
