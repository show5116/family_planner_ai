from pydantic import BaseModel, Field

class DummyInput(BaseModel):
    query: str = Field(description="The user query or context")

def dummy_tool_func(query: str = "") -> str:
    """A dummy tool for functional testing of tool loading."""
    return f"Dummy tool executed successfully. Received query: {query}"
