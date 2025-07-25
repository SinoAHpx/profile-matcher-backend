"""
Profile API endpoints using Supabase client
用户档案API端点 - 使用Supabase客户端提供用户基本信息管理功能
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Header
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date, datetime
from supabase import Client
from src.database import get_supabase_client, get_supabase_admin_client

router = APIRouter(prefix="/profile", tags=["profile"])

# =====================================================
# DEPENDENCIES - 依赖函数
# =====================================================

def get_supabase() -> Client:
    """获取Supabase客户端依赖"""
    return get_supabase_client()

def get_supabase_admin() -> Client:
    """获取Supabase管理员客户端依赖"""
    return get_supabase_admin_client()

async def get_current_user_id(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """从JWT token中获取当前用户ID"""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    try:
        token = authorization.split(" ")[1]
        supabase = get_supabase_client()
        user = supabase.auth.get_user(token)
        return user.user.id if user.user else None
    except Exception:
        return None

# =====================================================
# PYDANTIC MODELS - 数据模型
# =====================================================

class Gender(BaseModel):
    """性别模型"""
    id: UUID
    code: str
    name: str
    name_en: Optional[str] = None

class Region(BaseModel):
    """地区模型"""
    id: UUID
    code: str
    name: str
    name_en: Optional[str] = None
    parent_id: Optional[UUID] = None
    level: int

class Occupation(BaseModel):
    """职业模型"""
    id: UUID
    code: str
    name: str
    name_en: Optional[str] = None
    category_id: Optional[UUID] = None

class EducationLevel(BaseModel):
    """教育程度模型"""
    id: UUID
    code: str
    name: str
    name_en: Optional[str] = None
    level_order: int

class RelationshipStatus(BaseModel):
    """关系状态模型"""
    id: UUID
    code: str
    name: str
    name_en: Optional[str] = None

class UserProfile(BaseModel):
    """用户档案模型"""
    id: UUID
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    birth_date: Optional[date] = None
    age: Optional[int] = None
    gender: Optional[Gender] = None
    region: Optional[Region] = None
    timezone: Optional[str] = None
    occupation: Optional[Occupation] = None
    education_level: Optional[EducationLevel] = None
    company: Optional[str] = None
    school: Optional[str] = None
    relationship_status: Optional[RelationshipStatus] = None
    phone: Optional[str] = None
    website_url: Optional[str] = None
    profile_visibility: str = "public"
    profile_completion_percentage: int = 0
    last_active_at: Optional[datetime] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime

class CreateUserProfile(BaseModel):
    """创建用户档案请求模型"""
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    birth_date: Optional[date] = None
    gender_id: Optional[UUID] = None
    region_id: Optional[UUID] = None
    timezone: Optional[str] = None
    occupation_id: Optional[UUID] = None
    education_level_id: Optional[UUID] = None
    company: Optional[str] = None
    school: Optional[str] = None
    relationship_status_id: Optional[UUID] = None
    phone: Optional[str] = None
    website_url: Optional[str] = None
    profile_visibility: str = "public"

class UpdateUserProfile(BaseModel):
    """更新用户档案请求模型"""
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    birth_date: Optional[date] = None
    gender_id: Optional[UUID] = None
    region_id: Optional[UUID] = None
    timezone: Optional[str] = None
    occupation_id: Optional[UUID] = None
    education_level_id: Optional[UUID] = None
    company: Optional[str] = None
    school: Optional[str] = None
    relationship_status_id: Optional[UUID] = None
    phone: Optional[str] = None
    website_url: Optional[str] = None
    profile_visibility: Optional[str] = None

# =====================================================
# DICTIONARY ENDPOINTS - 字典数据端点
# =====================================================

@router.get("/dictionaries/genders", response_model=List[Gender])
async def get_genders(
    supabase: Client = Depends(get_supabase)
):
    """获取性别字典"""
    try:
        response = supabase.table("genders").select("id, code, name, name_en").eq("is_active", True).order("sort_order", desc=False).order("name", desc=False).execute()

        if response.data:
            return [Gender(**row) for row in response.data]
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取性别字典失败: {str(e)}")

@router.get("/dictionaries/regions", response_model=List[Region])
async def get_regions(
    level: Optional[int] = Query(None, description="地区层级过滤"),
    parent_id: Optional[UUID] = Query(None, description="父级地区ID"),
    supabase: Client = Depends(get_supabase)
):
    """获取地区字典"""
    try:
        query = supabase.table("regions").select("id, code, name, name_en, parent_id, level").eq("is_active", True)

        if level is not None:
            query = query.eq("level", level)

        if parent_id is not None:
            query = query.eq("parent_id", str(parent_id))

        response = query.order("sort_order", desc=False).order("name", desc=False).execute()

        if response.data:
            return [Region(**row) for row in response.data]
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取地区字典失败: {str(e)}")

@router.get("/dictionaries/occupations", response_model=List[Occupation])
async def get_occupations(
    category_id: Optional[UUID] = Query(None, description="职业分类ID"),
    supabase: Client = Depends(get_supabase)
):
    """获取职业字典"""
    try:
        query = supabase.table("occupations").select("id, code, name, name_en, category_id").eq("is_active", True)

        if category_id is not None:
            query = query.eq("category_id", str(category_id))

        response = query.order("sort_order", desc=False).order("name", desc=False).execute()

        if response.data:
            return [Occupation(**row) for row in response.data]
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取职业字典失败: {str(e)}")

@router.get("/dictionaries/education-levels", response_model=List[EducationLevel])
async def get_education_levels(
    supabase: Client = Depends(get_supabase)
):
    """获取教育程度字典"""
    try:
        response = supabase.table("education_levels").select("id, code, name, name_en, level_order").eq("is_active", True).order("level_order", desc=False).execute()

        if response.data:
            return [EducationLevel(**row) for row in response.data]
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取教育程度字典失败: {str(e)}")

@router.get("/dictionaries/relationship-statuses", response_model=List[RelationshipStatus])
async def get_relationship_statuses(
    supabase: Client = Depends(get_supabase)
):
    """获取关系状态字典"""
    try:
        response = supabase.table("relationship_statuses").select("id, code, name, name_en").eq("is_active", True).order("sort_order", desc=False).order("name", desc=False).execute()

        if response.data:
            return [RelationshipStatus(**row) for row in response.data]
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取关系状态字典失败: {str(e)}")

# =====================================================
# PROFILE ENDPOINTS - 档案管理端点
# =====================================================

@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: UUID,
    supabase: Client = Depends(get_supabase)
):
    """获取用户档案"""
    try:
        # Use the user_profile_summary view which includes all joined data
        response = supabase.table("user_profile_summary").select("*").eq("id", str(user_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="用户档案不存在")

        row = response.data[0]
        # row is already a dict from Supabase response
        row_dict = row
        
        # 构建嵌套对象
        profile_data = {
            "id": row_dict["id"],
            "display_name": row_dict["display_name"],
            "first_name": row_dict["first_name"],
            "last_name": row_dict["last_name"],
            "bio": row_dict["bio"],
            "avatar_url": row_dict["avatar_url"],
            "birth_date": row_dict["birth_date"],
            "age": int(row_dict["age"]) if row_dict["age"] else None,
            "timezone": row_dict["timezone"],
            "company": row_dict["company"],
            "school": row_dict["school"],
            "phone": row_dict["phone"],
            "website_url": row_dict["website_url"],
            "profile_visibility": row_dict["profile_visibility"],
            "profile_completion_percentage": row_dict["profile_completion_percentage"],
            "last_active_at": row_dict["last_active_at"],
            "is_active": row_dict["is_active"],
            "is_verified": row_dict["is_verified"],
            "created_at": row_dict["created_at"],
        }
        
        # 添加关联对象
        if row_dict["gender_id"]:
            profile_data["gender"] = Gender(
                id=row_dict["gender_id"],
                code=row_dict["gender_code"],
                name=row_dict["gender_name"],
                name_en=row_dict["gender_name_en"]
            )
        
        if row_dict["region_id"]:
            profile_data["region"] = Region(
                id=row_dict["region_id"],
                code=row_dict["region_code"],
                name=row_dict["region_name"],
                name_en=row_dict["region_name_en"],
                parent_id=row_dict["region_parent_id"],
                level=row_dict["region_level"]
            )
        
        if row_dict["occupation_id"]:
            profile_data["occupation"] = Occupation(
                id=row_dict["occupation_id"],
                code=row_dict["occupation_code"],
                name=row_dict["occupation_name"],
                name_en=row_dict["occupation_name_en"],
                category_id=row_dict["occupation_category_id"]
            )
        
        if row_dict["education_id"]:
            profile_data["education_level"] = EducationLevel(
                id=row_dict["education_id"],
                code=row_dict["education_code"],
                name=row_dict["education_name"],
                name_en=row_dict["education_name_en"],
                level_order=row_dict["education_level_order"]
            )
        
        if row_dict["relationship_id"]:
            profile_data["relationship_status"] = RelationshipStatus(
                id=row_dict["relationship_id"],
                code=row_dict["relationship_code"],
                name=row_dict["relationship_name"],
                name_en=row_dict["relationship_name_en"]
            )
        
        return UserProfile(**profile_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户档案失败: {str(e)}")

@router.post("/{user_id}", response_model=UserProfile)
async def create_user_profile(
    user_id: UUID,
    profile_data: CreateUserProfile,
    supabase: Client = Depends(get_supabase)
):
    """创建用户档案"""
    try:
        # 检查用户档案是否已存在
        existing_response = supabase.table("user_profiles").select("id").eq("id", str(user_id)).execute()
        if existing_response.data:
            raise HTTPException(status_code=400, detail="用户档案已存在")

        # 准备插入数据
        insert_data = {"id": str(user_id)}

        # 添加非空字段
        for field, value in profile_data.model_dump(exclude_unset=True).items():
            if value is not None:
                # Convert UUID fields to string for Supabase
                if isinstance(value, UUID):
                    insert_data[field] = str(value)
                else:
                    insert_data[field] = value

        # 插入用户档案
        response = supabase.table("user_profiles").insert(insert_data).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="创建用户档案失败")

        # 返回创建的用户档案
        return await get_user_profile(user_id, supabase=supabase)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建用户档案失败: {str(e)}")

@router.put("/{user_id}", response_model=UserProfile)
async def update_user_profile(
    user_id: UUID,
    profile_data: UpdateUserProfile,
    supabase: Client = Depends(get_supabase)
):
    """更新用户档案"""
    try:
        # 检查用户档案是否存在
        existing_response = supabase.table("user_profiles").select("id").eq("id", str(user_id)).execute()
        if not existing_response.data:
            raise HTTPException(status_code=404, detail="用户档案不存在")

        # 准备更新数据
        update_data = {}

        for field, value in profile_data.model_dump(exclude_unset=True).items():
            if value is not None:
                # Convert UUID fields to string for Supabase
                if isinstance(value, UUID):
                    update_data[field] = str(value)
                else:
                    update_data[field] = value

        if not update_data:
            raise HTTPException(status_code=400, detail="没有提供要更新的字段")

        # 执行更新
        response = supabase.table("user_profiles").update(update_data).eq("id", str(user_id)).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="更新用户档案失败")

        # 返回更新后的用户档案
        return await get_user_profile(user_id, supabase=supabase)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户档案失败: {str(e)}")

@router.delete("/{user_id}")
async def delete_user_profile(
    user_id: UUID,
    supabase: Client = Depends(get_supabase)
):
    """删除用户档案（软删除）"""
    try:
        # 执行软删除
        response = supabase.table("user_profiles").update({"is_active": False}).eq("id", str(user_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="用户档案不存在")

        return {"message": "用户档案已删除"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除用户档案失败: {str(e)}")

@router.get("/search", response_model=List[UserProfile])
async def search_user_profiles(
    q: Optional[str] = Query(None, description="搜索关键词"),
    region_id: Optional[UUID] = Query(None, description="地区过滤"),
    occupation_id: Optional[UUID] = Query(None, description="职业过滤"),
    age_min: Optional[int] = Query(None, description="最小年龄"),
    age_max: Optional[int] = Query(None, description="最大年龄"),
    limit: int = Query(20, le=100, description="返回结果数量限制"),
    supabase: Client = Depends(get_supabase)
):
    """搜索用户档案"""
    try:
        # Start with base query on user_profile_summary view
        query = supabase.table("user_profile_summary").select("*").eq("is_active", True).eq("profile_visibility", "public")

        # Apply filters
        if region_id:
            query = query.eq("region_id", str(region_id))

        if occupation_id:
            query = query.eq("occupation_id", str(occupation_id))

        # Note: Age filtering and text search would need to be implemented differently in Supabase
        # For now, we'll get the results and filter in Python
        response = query.order("last_active_at", desc=True).limit(limit).execute()

        if not response.data:
            return []

        profiles = []
        for row in response.data:
            # Apply additional filters that Supabase doesn't support directly
            include_profile = True

            # Text search filter
            if q and include_profile:
                search_text = q.lower()
                searchable_fields = [
                    row.get("display_name", ""),
                    row.get("first_name", ""),
                    row.get("last_name", ""),
                    row.get("bio", "")
                ]
                if not any(search_text in str(field).lower() for field in searchable_fields if field):
                    include_profile = False

            # Age filters
            if (age_min is not None or age_max is not None) and include_profile:
                age = row.get("age")
                if age is not None:
                    if age_min is not None and age < age_min:
                        include_profile = False
                    if age_max is not None and age > age_max:
                        include_profile = False

            if include_profile:
                # Convert the row to UserProfile model
                try:
                    profile = UserProfile(**row)
                    profiles.append(profile)
                except Exception:
                    # Skip profiles that don't match the model
                    continue

        return profiles[:limit]  # Ensure we don't exceed the limit

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索用户档案失败: {str(e)}")
