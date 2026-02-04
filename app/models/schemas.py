from pydantic import BaseModel
from typing import List, Optional

class PlannerRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default_user"

class PlannerResponse(BaseModel):
    response: str
    plan: Optional[str] = None
