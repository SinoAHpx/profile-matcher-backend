"""
Attributes API endpoints
属性API端点 - 提供属性分类树和用户属性管理功能
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from uuid import UUID
import asyncpg
from src.database import get_supabase_client

router = APIRouter(prefix="/attributes", tags=["attributes"])

# =====================================================
# PYDANTIC MODELS - 数据模型
# =====================================================

class AttributeCategory(BaseModel):
    """属性分类模型"""
    id: UUID
    code: str
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    level: int
    path: str
    icon_name: Optional[str] = None
    color_code: Optional[str] = None
    sort_order: int
    is_active: bool
    is_system: bool
    children: Optional[List['AttributeCategory']] = []

class Attribute(BaseModel):
    """属性模型"""
    id: UUID
    code: str
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    category_id: UUID
    category_name: Optional[str] = None
    category_path: Optional[str] = None
    tags: List[str] = []
    difficulty_level: str
    time_commitment: str
    cost_level: str
    physical_intensity: str
    social_aspect: str
    indoor_outdoor: str
    popularity_score: int
    is_active: bool

class UserAttribute(BaseModel):
    """用户属性关联模型"""
    id: UUID
    user_id: UUID
    attribute_id: UUID
    attribute: Optional[Attribute] = None
    interest_level: int = Field(..., ge=1, le=10, description="兴趣等级 1-10")
    skill_level: str
    experience_years: Optional[int] = None
    frequency: Optional[str] = None
    time_spent_weekly: Optional[int] = None
    enjoyment_rating: Optional[int] = Field(None, ge=1, le=10)
    status: str = "active"
    is_public: bool = True
    is_featured: bool = False
    notes: Optional[str] = None

class CreateUserAttribute(BaseModel):
    """创建用户属性请求模型"""
    attribute_id: UUID
    interest_level: int = Field(..., ge=1, le=10)
    skill_level: str = "beginner"
    experience_years: Optional[int] = None
    frequency: Optional[str] = None
    time_spent_weekly: Optional[int] = None
    enjoyment_rating: Optional[int] = Field(None, ge=1, le=10)
    is_public: bool = True
    is_featured: bool = False
    notes: Optional[str] = None

class UpdateUserAttribute(BaseModel):
    """更新用户属性请求模型"""
    interest_level: Optional[int] = Field(None, ge=1, le=10)
    skill_level: Optional[str] = None
    experience_years: Optional[int] = None
    frequency: Optional[str] = None
    time_spent_weekly: Optional[int] = None
    enjoyment_rating: Optional[int] = Field(None, ge=1, le=10)
    status: Optional[str] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None
    notes: Optional[str] = None

class AttributeCategoryTree(BaseModel):
    """属性分类树响应模型"""
    categories: List[AttributeCategory]
    total_count: int

# =====================================================
# HELPER FUNCTIONS - 辅助函数
# =====================================================

def build_category_tree(categories: List[Dict]) -> List[AttributeCategory]:
    """构建分类树结构"""
    category_map = {}
    root_categories = []
    
    # 创建所有分类对象
    for cat_data in categories:
        category = AttributeCategory(**cat_data, children=[])
        category_map[category.id] = category
        
        if category.parent_id is None:
            root_categories.append(category)
    
    # 构建父子关系
    for category in category_map.values():
        if category.parent_id and category.parent_id in category_map:
            parent = category_map[category.parent_id]
            parent.children.append(category)
    
    return root_categories

# =====================================================
# API ENDPOINTS - API端点
# =====================================================

@router.get("/categories/tree", response_model=AttributeCategoryTree)
async def get_category_tree(
    level: Optional[int] = Query(None, description="限制返回的层级深度"),
    include_inactive: bool = Query(False, description="是否包含非激活的分类"),
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    获取完整的属性分类树结构
    
    - **level**: 限制返回的层级深度（可选）
    - **include_inactive**: 是否包含非激活的分类
    """
    try:
        # 构建查询条件
        where_conditions = []
        if not include_inactive:
            where_conditions.append("is_active = true")
        if level is not None:
            where_conditions.append(f"level <= {level}")
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        query = f"""
        SELECT id, code, name, name_en, description, parent_id, level, path,
               icon_name, color_code, sort_order, is_active, is_system
        FROM attributes.categories
        {where_clause}
        ORDER BY level, sort_order, name
        """
        
        rows = await db.fetch(query)
        categories_data = [dict(row) for row in rows]
        
        # 构建树结构
        tree = build_category_tree(categories_data)
        
        return AttributeCategoryTree(
            categories=tree,
            total_count=len(categories_data)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类树失败: {str(e)}")

@router.get("/categories/{category_id}/attributes", response_model=List[Attribute])
async def get_attributes_by_category(
    category_id: UUID,
    include_inactive: bool = Query(False, description="是否包含非激活的属性"),
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    获取指定分类下的所有属性
    """
    try:
        where_clause = "WHERE a.category_id = $1"
        params = [category_id]
        
        if not include_inactive:
            where_clause += " AND a.is_active = true"
        
        query = f"""
        SELECT a.id, a.code, a.name, a.name_en, a.description, a.category_id,
               c.name as category_name, c.path as category_path,
               a.tags, a.difficulty_level, a.time_commitment, a.cost_level,
               a.physical_intensity, a.social_aspect, a.indoor_outdoor,
               a.popularity_score, a.is_active
        FROM attributes.attributes a
        JOIN attributes.categories c ON a.category_id = c.id
        {where_clause}
        ORDER BY a.popularity_score DESC, a.name
        """
        
        rows = await db.fetch(query, *params)
        return [Attribute(**dict(row)) for row in rows]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取属性失败: {str(e)}")

@router.get("/search", response_model=List[Attribute])
async def search_attributes(
    q: str = Query(..., description="搜索关键词"),
    category_id: Optional[UUID] = Query(None, description="限制在指定分类内搜索"),
    difficulty_level: Optional[str] = Query(None, description="难度等级过滤"),
    time_commitment: Optional[str] = Query(None, description="时间投入过滤"),
    limit: int = Query(20, le=100, description="返回结果数量限制"),
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    搜索属性
    
    支持按名称、描述、标签搜索，并可按分类、难度等级等过滤
    """
    try:
        where_conditions = ["a.is_active = true"]
        params = []
        param_count = 0
        
        # 搜索条件
        param_count += 1
        where_conditions.append(f"""
            (a.name ILIKE ${param_count} OR 
             a.name_en ILIKE ${param_count} OR 
             a.description ILIKE ${param_count} OR
             ${param_count} = ANY(a.tags))
        """)
        params.append(f"%{q}%")
        
        # 分类过滤
        if category_id:
            param_count += 1
            where_conditions.append(f"a.category_id = ${param_count}")
            params.append(category_id)
        
        # 难度等级过滤
        if difficulty_level:
            param_count += 1
            where_conditions.append(f"a.difficulty_level = ${param_count}")
            params.append(difficulty_level)
        
        # 时间投入过滤
        if time_commitment:
            param_count += 1
            where_conditions.append(f"a.time_commitment = ${param_count}")
            params.append(time_commitment)
        
        where_clause = "WHERE " + " AND ".join(where_conditions)
        
        query = f"""
        SELECT a.id, a.code, a.name, a.name_en, a.description, a.category_id,
               c.name as category_name, c.path as category_path,
               a.tags, a.difficulty_level, a.time_commitment, a.cost_level,
               a.physical_intensity, a.social_aspect, a.indoor_outdoor,
               a.popularity_score, a.is_active
        FROM attributes.attributes a
        JOIN attributes.categories c ON a.category_id = c.id
        {where_clause}
        ORDER BY a.popularity_score DESC, a.name
        LIMIT {limit}
        """
        
        rows = await db.fetch(query, *params)
        return [Attribute(**dict(row)) for row in rows]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索属性失败: {str(e)}")

@router.get("/user/{user_id}", response_model=List[UserAttribute])
async def get_user_attributes(
    user_id: UUID,
    status: Optional[str] = Query(None, description="状态过滤"),
    is_featured: Optional[bool] = Query(None, description="是否只返回特色属性"),
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    获取用户的属性列表
    """
    try:
        where_conditions = ["ua.user_id = $1"]
        params = [user_id]
        param_count = 1
        
        if status:
            param_count += 1
            where_conditions.append(f"ua.status = ${param_count}")
            params.append(status)
        
        if is_featured is not None:
            param_count += 1
            where_conditions.append(f"ua.is_featured = ${param_count}")
            params.append(is_featured)
        
        where_clause = "WHERE " + " AND ".join(where_conditions)
        
        query = f"""
        SELECT ua.id, ua.user_id, ua.attribute_id, ua.interest_level,
               ua.skill_level, ua.experience_years, ua.frequency,
               ua.time_spent_weekly, ua.enjoyment_rating, ua.status,
               ua.is_public, ua.is_featured, ua.notes,
               a.id as attr_id, a.code as attr_code, a.name as attr_name,
               a.name_en as attr_name_en, a.description as attr_description,
               a.category_id as attr_category_id, c.name as attr_category_name,
               c.path as attr_category_path, a.tags as attr_tags,
               a.difficulty_level as attr_difficulty_level,
               a.time_commitment as attr_time_commitment,
               a.cost_level as attr_cost_level,
               a.physical_intensity as attr_physical_intensity,
               a.social_aspect as attr_social_aspect,
               a.indoor_outdoor as attr_indoor_outdoor,
               a.popularity_score as attr_popularity_score,
               a.is_active as attr_is_active
        FROM attributes.user_attributes ua
        JOIN attributes.attributes a ON ua.attribute_id = a.id
        JOIN attributes.categories c ON a.category_id = c.id
        {where_clause}
        ORDER BY ua.is_featured DESC, ua.interest_level DESC, a.name
        """
        
        rows = await db.fetch(query, *params)
        
        result = []
        for row in rows:
            row_dict = dict(row)
            
            # 构建嵌套的Attribute对象
            attribute = Attribute(
                id=row_dict['attr_id'],
                code=row_dict['attr_code'],
                name=row_dict['attr_name'],
                name_en=row_dict['attr_name_en'],
                description=row_dict['attr_description'],
                category_id=row_dict['attr_category_id'],
                category_name=row_dict['attr_category_name'],
                category_path=row_dict['attr_category_path'],
                tags=row_dict['attr_tags'] or [],
                difficulty_level=row_dict['attr_difficulty_level'],
                time_commitment=row_dict['attr_time_commitment'],
                cost_level=row_dict['attr_cost_level'],
                physical_intensity=row_dict['attr_physical_intensity'],
                social_aspect=row_dict['attr_social_aspect'],
                indoor_outdoor=row_dict['attr_indoor_outdoor'],
                popularity_score=row_dict['attr_popularity_score'],
                is_active=row_dict['attr_is_active']
            )
            
            user_attribute = UserAttribute(
                id=row_dict['id'],
                user_id=row_dict['user_id'],
                attribute_id=row_dict['attribute_id'],
                attribute=attribute,
                interest_level=row_dict['interest_level'],
                skill_level=row_dict['skill_level'],
                experience_years=row_dict['experience_years'],
                frequency=row_dict['frequency'],
                time_spent_weekly=row_dict['time_spent_weekly'],
                enjoyment_rating=row_dict['enjoyment_rating'],
                status=row_dict['status'],
                is_public=row_dict['is_public'],
                is_featured=row_dict['is_featured'],
                notes=row_dict['notes']
            )
            
            result.append(user_attribute)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户属性失败: {str(e)}")

@router.post("/user/{user_id}", response_model=UserAttribute)
async def create_user_attribute(
    user_id: UUID,
    attribute_data: CreateUserAttribute,
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    为用户添加新的属性关联
    """
    try:
        # 检查属性是否存在
        attr_check = await db.fetchrow(
            "SELECT id FROM attributes.attributes WHERE id = $1 AND is_active = true",
            attribute_data.attribute_id
        )
        if not attr_check:
            raise HTTPException(status_code=404, detail="属性不存在")

        # 检查是否已存在关联
        existing = await db.fetchrow(
            "SELECT id FROM attributes.user_attributes WHERE user_id = $1 AND attribute_id = $2",
            user_id, attribute_data.attribute_id
        )
        if existing:
            raise HTTPException(status_code=400, detail="用户已关联此属性")

        # 创建新的用户属性关联
        query = """
        INSERT INTO attributes.user_attributes
        (user_id, attribute_id, interest_level, skill_level, experience_years,
         frequency, time_spent_weekly, enjoyment_rating, is_public, is_featured, notes)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        RETURNING id
        """

        new_id = await db.fetchval(
            query,
            user_id,
            attribute_data.attribute_id,
            attribute_data.interest_level,
            attribute_data.skill_level,
            attribute_data.experience_years,
            attribute_data.frequency,
            attribute_data.time_spent_weekly,
            attribute_data.enjoyment_rating,
            attribute_data.is_public,
            attribute_data.is_featured,
            attribute_data.notes
        )

        # 返回创建的用户属性
        user_attributes = await get_user_attributes(user_id, db=db)
        for ua in user_attributes:
            if ua.id == new_id:
                return ua

        raise HTTPException(status_code=500, detail="创建成功但无法获取结果")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建用户属性失败: {str(e)}")

@router.put("/user/{user_id}/{attribute_id}", response_model=UserAttribute)
async def update_user_attribute(
    user_id: UUID,
    attribute_id: UUID,
    attribute_data: UpdateUserAttribute,
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    更新用户的属性关联信息
    """
    try:
        # 检查用户属性关联是否存在
        existing = await db.fetchrow(
            "SELECT id FROM attributes.user_attributes WHERE user_id = $1 AND attribute_id = $2",
            user_id, attribute_id
        )
        if not existing:
            raise HTTPException(status_code=404, detail="用户属性关联不存在")

        # 构建更新字段
        update_fields = []
        params = []
        param_count = 0

        for field, value in attribute_data.model_dump(exclude_unset=True).items():
            if value is not None:
                param_count += 1
                update_fields.append(f"{field} = ${param_count}")
                params.append(value)

        if not update_fields:
            raise HTTPException(status_code=400, detail="没有提供要更新的字段")

        # 添加updated_at字段
        param_count += 1
        update_fields.append(f"updated_at = ${param_count}")
        params.append("NOW()")

        # 添加WHERE条件参数
        param_count += 1
        params.append(user_id)
        param_count += 1
        params.append(attribute_id)

        query = f"""
        UPDATE attributes.user_attributes
        SET {', '.join(update_fields)}
        WHERE user_id = ${param_count-1} AND attribute_id = ${param_count}
        """

        await db.execute(query, *params[:-2], params[-2], params[-1])

        # 返回更新后的用户属性
        user_attributes = await get_user_attributes(user_id, db=db)
        for ua in user_attributes:
            if ua.attribute_id == attribute_id:
                return ua

        raise HTTPException(status_code=500, detail="更新成功但无法获取结果")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户属性失败: {str(e)}")

@router.delete("/user/{user_id}/{attribute_id}")
async def delete_user_attribute(
    user_id: UUID,
    attribute_id: UUID,
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    删除用户的属性关联
    """
    try:
        result = await db.execute(
            "DELETE FROM attributes.user_attributes WHERE user_id = $1 AND attribute_id = $2",
            user_id, attribute_id
        )

        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="用户属性关联不存在")

        return {"message": "用户属性关联已删除"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除用户属性失败: {str(e)}")

@router.get("/categories/{category_id}/subcategories", response_model=List[AttributeCategory])
async def get_subcategories(
    category_id: UUID,
    include_inactive: bool = Query(False, description="是否包含非激活的分类"),
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    获取指定分类的直接子分类
    """
    try:
        where_clause = "WHERE parent_id = $1"
        params = [category_id]

        if not include_inactive:
            where_clause += " AND is_active = true"

        query = f"""
        SELECT id, code, name, name_en, description, parent_id, level, path,
               icon_name, color_code, sort_order, is_active, is_system
        FROM attributes.categories
        {where_clause}
        ORDER BY sort_order, name
        """

        rows = await db.fetch(query, *params)
        return [AttributeCategory(**dict(row), children=[]) for row in rows]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取子分类失败: {str(e)}")

@router.get("/popular", response_model=List[Attribute])
async def get_popular_attributes(
    limit: int = Query(20, le=100, description="返回结果数量限制"),
    category_id: Optional[UUID] = Query(None, description="限制在指定分类内"),
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    获取热门属性列表
    """
    try:
        where_conditions = ["a.is_active = true"]
        params = []

        if category_id:
            where_conditions.append("a.category_id = $1")
            params.append(category_id)

        where_clause = "WHERE " + " AND ".join(where_conditions)

        query = f"""
        SELECT a.id, a.code, a.name, a.name_en, a.description, a.category_id,
               c.name as category_name, c.path as category_path,
               a.tags, a.difficulty_level, a.time_commitment, a.cost_level,
               a.physical_intensity, a.social_aspect, a.indoor_outdoor,
               a.popularity_score, a.is_active
        FROM attributes.attributes a
        JOIN attributes.categories c ON a.category_id = c.id
        {where_clause}
        ORDER BY a.popularity_score DESC, a.name
        LIMIT {limit}
        """

        rows = await db.fetch(query, *params)
        return [Attribute(**dict(row)) for row in rows]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门属性失败: {str(e)}")

# 修复模型的前向引用
AttributeCategory.model_rebuild()
