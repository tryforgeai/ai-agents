from datetime import date
from pydantic import BaseModel, Field
from adk_patterns import make_agent, sequence

class TravelRequest(BaseModel):
    city: str = Field(min_length=1)
    start_date: date
    days: int = Field(default=1, ge=1, le=30)
    interests: list[str] = Field(default_factory=list)

class TravelPlan(BaseModel):
    city: str
    title: str
    activities: list[str]

itinerary = make_agent(
    "itinerary_agent",
    "根据输入需求，用中文制定实用的逐日旅行计划。不要声称已查询实时信息。",
    input_schema=TravelRequest, output_schema=TravelPlan, output_key="last_plan",
)
root_agent = sequence("travel", itinerary)
