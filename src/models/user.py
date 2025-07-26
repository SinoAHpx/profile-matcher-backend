from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from enum import Enum

class MBTIType(str, Enum):
    INTJ = "INTJ"
    INTP = "INTP"
    ENTJ = "ENTJ"
    ENTP = "ENTP"
    INFJ = "INFJ"
    INFP = "INFP"
    ENFJ = "ENFJ"
    ENFP = "ENFP"
    ISTJ = "ISTJ"
    ISFJ = "ISFJ"
    ESTJ = "ESTJ"
    ESFJ = "ESFJ"
    ISTP = "ISTP"
    ISFP = "ISFP"
    ESTP = "ESTP"
    ESFP = "ESFP"

class UserRegister(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    avatar_url: Optional[str] = None

class UserProfileUpdate(BaseModel):
    mbti: Optional[MBTIType] = None
    hobbies: Optional[List[int]] = Field(default_factory=list)
    motto: Optional[str] = None
    self_description: Optional[str] = None
    
    @validator('hobbies')
    def validate_hobbies(cls, v):
        if v is None:
            return []
        # 验证爱好ID范围
        for hobby_id in v:
            if not (1 <= hobby_id <= 66):
                raise ValueError(f"Invalid hobby ID: {hobby_id}")
        return v

class UserProfile(BaseModel):
    id: str
    user_id: str
    nickname: str
    avatar_url: Optional[str]
    mbti: Optional[MBTIType]
    hobbies: List[int]
    motto: Optional[str]
    self_description: Optional[str]
    created_at: str
    updated_at: str

class HobbyReference(BaseModel):
    id: int
    name: str
    category: str

# Team related models
class EventBase(BaseModel):
    id: str
    name: str
    description: str
    participant_count: int
    start_time: str
    end_time: str
    location: str

class TeamCreate(BaseModel):
    event_id: str
    name: str = Field(..., min_length=1, max_length=100)
    say_something: Optional[str] = None

class TeamMemberSkills(BaseModel):
    skill_ids: List[int] = Field(..., max_items=2)
    
    @validator('skill_ids')
    def validate_skills(cls, v):
        if len(v) > 2:
            raise ValueError("最多只能选择2个技能")
        for skill_id in v:
            if not (1 <= skill_id <= 36):
                raise ValueError(f"Invalid skill ID: {skill_id}")
        return v

class TeamMember(BaseModel):
    nickname: str
    self_description: Optional[str]
    skills: List[str]  # 技能名称列表

class TeamPost(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)

class TeamPostResponse(BaseModel):
    post_id: str
    author_email: str
    title: str
    content: str
    created_at: str

class UserRecommendation(BaseModel):
    id: str
    team_id: str
    team_name: str
    recommendation_reason: Optional[str]
    algorithm_score: Optional[float]
    expires_at: str
    created_at: str

class RecommendationUpdate(BaseModel):
    status: str = Field(..., pattern="^(accepted|rejected)$")