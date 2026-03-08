from pydantic import BaseModel
from typing import List, Optional

class PlannerRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    room_id: Optional[str] = None
    target_agent: Optional[str] = "supervisor"

class PlannerResponse(BaseModel):
    response: str
    room_id: str
    plan: Optional[str] = None
