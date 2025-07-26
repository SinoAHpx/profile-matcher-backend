from pydantic import BaseModel, Field, validator
from typing import List, Optional
from .user import TeamMember, TeamPost, TeamPostResponse, UserRecommendation, RecommendationUpdate

class Team(BaseModel):
    id: str
    event_id: str
    name: str
    say_something: Optional[str]
    member_emails: List[str]
    member_count: int
    created_at: str
    
class TeamMembers(BaseModel):
    team_id: str
    team_name: str
    members: List[TeamMember]