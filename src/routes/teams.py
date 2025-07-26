from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
from src.auth.supabase_client import get_supabase_client
from src.auth.admin_client import get_supabase_admin_client
from src.models.user import EventBase, TeamCreate, TeamMemberSkills, TeamPost, TeamPostResponse, UserRecommendation, RecommendationUpdate, UserProfile
from src.models.team import Team, TeamMembers
from supabase import Client
import uuid
from datetime import datetime
import jwt
import json

router = APIRouter(prefix="/teams", tags=["teams"])

async def get_current_user_email(request: Request) -> str:
    """从请求中获取当前用户的邮箱"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        token = auth_header.replace("Bearer ", "")
        # Decode JWT token without verification to extract email
        decoded = jwt.decode(token, options={"verify_signature": False})
        email = decoded.get("email")
        if email:
            return email
        else:
            raise HTTPException(status_code=401, detail="Email not found in token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/events", response_model=List[EventBase])
async def get_events_by_popularity():
    """获取活动列表，按参与用户数排序"""
    try:
        supabase = get_supabase_admin_client()
        
        # 查询活动并按参与者数量排序
        response = supabase.table("events").select(
            "id, name, description, start_time, end_time, location, all_participants_emails"
        ).eq("is_active", True).execute()
        
        events = []
        for event in response.data:
            participant_count = len(event.get("all_participants_emails", []))
            events.append(EventBase(
                id=event["id"],
                name=event["name"],
                description=event["description"],
                participant_count=participant_count,
                start_time=event["start_time"],
                end_time=event["end_time"],
                location=event["location"]
            ))
        
        # 按参与者数量降序排序
        events.sort(key=lambda x: x.participant_count, reverse=True)
        return events
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/{event_id}/join")
async def join_event(event_id: str, user_email: str = Depends(get_current_user_email)):
    """用户加入大型活动"""
    try:
        supabase = get_supabase_admin_client()
        
        # 检查是否已经参与
        existing = supabase.table("event_participants").select("*").eq(
            "event_id", event_id
        ).eq("user_email", user_email).execute()
        
        if existing.data:
            raise HTTPException(status_code=400, detail="Already joined this event")
        
        # 添加参与记录
        supabase.table("event_participants").insert({
            "event_id": event_id,
            "user_email": user_email
        }).execute()
        
        return {"message": "Successfully joined event"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create", response_model=Team)
async def create_team(team_data: TeamCreate, user_email: str = Depends(get_current_user_email)):
    """创建小队"""
    try:
        supabase = get_supabase_admin_client()
        
        # 验证用户是否参与了该活动
        participant_check = supabase.table("event_participants").select("*").eq(
            "event_id", team_data.event_id
        ).eq("user_email", user_email).execute()
        
        if not participant_check.data:
            raise HTTPException(status_code=400, detail="Must join the event first")
        
        # 检查用户是否已经在其他小队
        existing_team = supabase.table("event_participants").select("team_id").eq(
            "event_id", team_data.event_id
        ).eq("user_email", user_email).execute()
        
        if existing_team.data[0]["team_id"]:
            raise HTTPException(status_code=400, detail="Already in a team")
        
        # 创建小队
        team_response = supabase.table("teams").insert({
            "event_id": team_data.event_id,
            "name": team_data.name,
            "say_something": team_data.say_something,
            "member_emails": [user_email]
        }).execute()
        
        team_id = team_response.data[0]["id"]
        
        # 更新用户的team_id
        supabase.table("event_participants").update({
            "team_id": team_id
        }).eq("event_id", team_data.event_id).eq("user_email", user_email).execute()
        
        return Team(
            id=team_id,
            event_id=team_data.event_id,
            name=team_data.name,
            say_something=team_data.say_something,
            member_emails=[user_email],
            member_count=1,
            created_at=team_response.data[0]["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/join/{team_id}")
async def join_team(team_id: str, user_email: str = Depends(get_current_user_email)):
    """加入小队"""
    try:
        supabase = get_supabase_admin_client()
        
        # 获取小队信息
        team_response = supabase.table("teams").select("*").eq("id", team_id).execute()
        if not team_response.data:
            raise HTTPException(status_code=404, detail="Team not found")
        
        team = team_response.data[0]
        
        # 检查用户是否参与了该活动
        participant_check = supabase.table("event_participants").select("*").eq(
            "event_id", team["event_id"]
        ).eq("user_email", user_email).execute()
        
        if not participant_check.data:
            raise HTTPException(status_code=400, detail="Must join the event first")
        
        # 检查是否已经在小队中
        if user_email in team["member_emails"]:
            raise HTTPException(status_code=400, detail="Already in this team")
        
        # 更新小队成员列表
        updated_members = team["member_emails"] + [user_email]
        supabase.table("teams").update({
            "member_emails": updated_members
        }).eq("id", team_id).execute()
        
        # 更新用户的team_id
        supabase.table("event_participants").update({
            "team_id": team_id
        }).eq("event_id", team["event_id"]).eq("user_email", user_email).execute()
        
        return {"message": "Successfully joined team"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/leave")
async def leave_team(user_email: str = Depends(get_current_user_email)):
    """退出小队"""
    try:
        supabase = get_supabase_admin_client()
        
        # 获取用户当前的小队
        participant = supabase.table("event_participants").select("team_id").eq(
            "user_email", user_email
        ).execute()
        
        if not participant.data:
            raise HTTPException(status_code=400, detail="Not in any team")
        
        team_id = participant.data[0]["team_id"]
        
        if not team_id:
            raise HTTPException(status_code=400, detail="Not in any team")
        
        # 获取小队信息
        team_response = supabase.table("teams").select("*").eq("id", team_id).execute()
        team = team_response.data[0]
        
        # 从成员列表中移除用户
        updated_members = [email for email in team["member_emails"] if email != user_email]
        
        if len(updated_members) == 0:
            # 如果是最后一个成员，删除小队
            supabase.table("teams").delete().eq("id", team_id).execute()
        else:
            # 更新成员列表
            supabase.table("teams").update({
                "member_emails": updated_members
            }).eq("id", team_id).execute()
        
        # 清除用户的team_id
        supabase.table("event_participants").update({
            "team_id": None
        }).eq("user_email", user_email).execute()
        
        return {"message": "Successfully left team"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/skills")
async def set_team_member_skills(skills_data: TeamMemberSkills, user_email: str = Depends(get_current_user_email)):
    """设置用户在小队中的技能角色"""
    try:
        supabase = get_supabase_admin_client()
        
        # 获取用户当前的小队
        participant = supabase.table("event_participants").select("team_id").eq(
            "user_email", user_email
        ).execute()
        
        if not participant.data:
            raise HTTPException(status_code=400, detail="Not in any team")
        
        team_id = participant.data[0]["team_id"]
        
        if not team_id:
            raise HTTPException(status_code=400, detail="Not in any team")
        
        # 检查技能记录是否存在
        existing = supabase.table("team_member_skills").select("*").eq(
            "team_id", team_id
        ).eq("user_email", user_email).execute()
        
        if existing.data:
            # 更新技能
            supabase.table("team_member_skills").update({
                "skill_ids": skills_data.skill_ids
            }).eq("team_id", team_id).eq("user_email", user_email).execute()
        else:
            # 插入新技能记录
            supabase.table("team_member_skills").insert({
                "team_id": team_id,
                "user_email": user_email,
                "skill_ids": skills_data.skill_ids
            }).execute()
        
        return {"message": "Skills updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/members", response_model=TeamMembers)
async def get_team_members(user_email: str = Depends(get_current_user_email)):
    """获取用户所在小队的成员信息"""
    try:
        supabase = get_supabase_admin_client()
        
        # 获取用户当前的小队
        participant = supabase.table("event_participants").select("team_id").eq(
            "user_email", user_email
        ).execute()
        
        if not participant.data:
            raise HTTPException(status_code=400, detail="Not in any team")
        
        team_id = participant.data[0]["team_id"]
        
        if not team_id:
            raise HTTPException(status_code=400, detail="Not in any team")
        
        # 获取小队信息
        team_response = supabase.table("teams").select("id, name, member_emails").eq("id", team_id).execute()
        team = team_response.data[0]
        
        members = []
        for member_email in team["member_emails"]:
            # 获取用户资料 - 需要先查询用户ID
            auth_user_response = supabase.auth.admin.list_users()
            user_id = None
            for user in auth_user_response:
                if user.email == member_email:
                    user_id = user.id
                    break
            
            profile_response = None
            if user_id:
                profile_response = supabase.table("user_profiles").select(
                    "nickname, self_description"
                ).eq("user_id", user_id).execute()
            
            # 获取用户技能
            skills_response = supabase.table("team_member_skills").select("skill_ids").eq(
                "team_id", team_id
            ).eq("user_email", member_email).execute()
            
            skill_names = []
            if skills_response.data:
                skill_ids = skills_response.data[0]["skill_ids"]
                # 获取技能名称
                skills_ref_response = supabase.table("skills_reference").select("name").in_(
                    "id", skill_ids
                ).execute()
                skill_names = [skill["name"] for skill in skills_ref_response.data]
            
            if profile_response.data:
                profile = profile_response.data[0]
                members.append({
                    "nickname": profile["nickname"],
                    "self_description": profile.get("self_description"),
                    "skills": skill_names
                })
        
        return TeamMembers(
            team_id=team_id,
            team_name=team["name"],
            members=members
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts", response_model=TeamPostResponse)
async def create_team_post(post_data: TeamPost, user_email: str = Depends(get_current_user_email)):
    """发布小队帖子"""
    try:
        supabase = get_supabase_admin_client()
        
        # 获取用户当前的小队
        participant = supabase.table("event_participants").select("team_id").eq(
            "user_email", user_email
        ).execute()
        
        if not participant.data:
            raise HTTPException(status_code=400, detail="Not in any team")
        
        team_id = participant.data[0]["team_id"]
        
        if not team_id:
            raise HTTPException(status_code=400, detail="Not in any team")
        
        # 创建帖子
        post_response = supabase.table("team_posts").insert({
            "team_id": team_id,
            "author_email": user_email,
            "title": post_data.title,
            "content": post_data.content
        }).execute()
        
        post = post_response.data[0]
        return TeamPostResponse(
            post_id=post["id"],
            author_email=post["author_email"],
            title=post["title"],
            content=post["content"],
            created_at=post["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts", response_model=List[TeamPostResponse])
async def get_all_team_posts():
    """获取所有激活的小队帖子"""
    try:
        supabase = get_supabase_admin_client()
        
        response = supabase.table("team_posts").select(
            "id, author_email, title, content, created_at"
        ).eq("is_active", True).order("created_at", desc=True).execute()
        
        return [TeamPostResponse(
            post_id=post["id"],
            author_email=post["author_email"],
            title=post["title"],
            content=post["content"],
            created_at=post["created_at"]
        ) for post in response.data]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users", response_model=List[UserProfile])
async def get_all_users():
    """获取所有用户信息列表（随机排序）"""
    try:
        supabase = get_supabase_admin_client()
        
        # 直接查询用户资料表，避免使用可能有问题的RPC函数
        response = supabase.table("user_profiles").select("*").execute()
        
        return [UserProfile(**user) for user in response.data]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations", response_model=List[UserRecommendation])
async def get_user_recommendations(user_email: str = Depends(get_current_user_email)):
    """获取用户的小队推荐通知"""
    try:
        supabase = get_supabase_admin_client()
        
        # 获取激活且未过期的推荐
        response = supabase.table("team_recommendations").select(
            "id, team_id, recommendation_reason, algorithm_score, expires_at, created_at, teams!inner(name)"
        ).eq("target_user_email", user_email).eq("is_active", True).gt(
            "expires_at", datetime.now().isoformat()
        ).order("created_at", desc=True).execute()
        
        recommendations = []
        for rec in response.data:
            recommendations.append(UserRecommendation(
                id=rec["id"],
                team_id=rec["team_id"],
                team_name=rec["teams"]["name"],
                recommendation_reason=rec.get("recommendation_reason"),
                algorithm_score=rec.get("algorithm_score"),
                expires_at=rec["expires_at"],
                created_at=rec["created_at"]
            ))
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/recommendations/{recommendation_id}")
async def update_recommendation_status(
    recommendation_id: str, 
    status_update: RecommendationUpdate, 
    user_email: str = Depends(get_current_user_email)
):
    """更新推荐状态"""
    try:
        supabase = get_supabase_admin_client()
        
        # 验证推荐是否属于当前用户
        rec_response = supabase.table("team_recommendations").select("*").eq(
            "id", recommendation_id
        ).eq("target_user_email", user_email).execute()
        
        if not rec_response.data:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        # 更新状态并设置为非激活（如果接受或拒绝）
        supabase.table("team_recommendations").update({
            "status": status_update.status,
            "is_active": False if status_update.status in ["accepted", "rejected"] else True
        }).eq("id", recommendation_id).execute()
        
        # 如果接受推荐，自动加入小队
        if status_update.status == "accepted":
            team_id = rec_response.data[0]["team_id"]
            
            # 获取小队信息并加入
            team_response = supabase.table("teams").select("*").eq("id", team_id).execute()
            if team_response.data:
                team = team_response.data[0]
                updated_members = team["member_emails"] + [user_email]
                
                supabase.table("teams").update({
                    "member_emails": updated_members
                }).eq("id", team_id).execute()
                
                # 更新用户的team_id
                supabase.table("event_participants").update({
                    "team_id": team_id
                }).eq("event_id", team["event_id"]).eq("user_email", user_email).execute()
        
        return {"message": f"Recommendation {status_update.status}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/posts/{post_id}")
async def update_team_post(
    post_id: str, 
    post_update: TeamPost, 
    user_email: str = Depends(get_current_user_email)
):
    """更新帖子"""
    try:
        supabase = get_supabase_admin_client()
        
        # 验证帖子是否属于当前用户
        post_response = supabase.table("team_posts").select("*").eq(
            "id", post_id
        ).eq("author_email", user_email).execute()
        
        if not post_response.data:
            raise HTTPException(status_code=404, detail="Post not found or not authorized")
        
        # 更新帖子
        updated_response = supabase.table("team_posts").update({
            "title": post_update.title,
            "content": post_update.content
        }).eq("id", post_id).execute()
        
        post = updated_response.data[0]
        return TeamPostResponse(
            post_id=post["id"],
            author_email=post["author_email"],
            title=post["title"],
            content=post["content"],
            created_at=post["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/posts/{post_id}")
async def delete_team_post(post_id: str, user_email: str = Depends(get_current_user_email)):
    """删除帖子"""
    try:
        supabase = get_supabase_admin_client()
        
        # 验证帖子是否属于当前用户
        post_response = supabase.table("team_posts").select("*").eq(
            "id", post_id
        ).eq("author_email", user_email).execute()
        
        if not post_response.data:
            raise HTTPException(status_code=404, detail="Post not found or not authorized")
        
        # 软删除：设置为非激活
        supabase.table("team_posts").update({
            "is_active": False
        }).eq("id", post_id).execute()
        
        return {"message": "Post deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))