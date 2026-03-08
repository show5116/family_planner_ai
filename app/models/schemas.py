from pydantic import BaseModel
from typing import List, Optional

class PlannerRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    room_id: str = "default_room"

class PlannerResponse(BaseModel):
    response: str
    plan: Optional[str] = None
