"""
Ego API endpoints
人格特质/认知功能API端点 - 提供心理特质和认知模式管理功能
"""

from typing import List, Optional, Dict, Any, Union
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
import asyncpg
from src.database import get_supabase_client

router = APIRouter(prefix="/ego", tags=["ego"])

# =====================================================
# PYDANTIC MODELS - 数据模型
# =====================================================

class CognitiveFunction(BaseModel):
    """认知功能模型"""
    id: UUID
    code: str
    name: str
    full_name: str
    description: str
    function_type: str
    attitude: str
    is_active: bool

class UserCognitiveFunction(BaseModel):
    """用户认知功能模型"""
    id: UUID
    user_id: UUID
    cognitive_function: CognitiveFunction
    raw_score: Optional[int] = None
    normalized_score: Optional[float] = None
    function_rank: Optional[int] = Field(None, ge=1, le=8)
    confidence_level: float = Field(0.5, ge=0, le=1)
    assessment_source: str = "self_assessment"
    notes: Optional[str] = None
    assessed_at: datetime

class TraitCategory(BaseModel):
    """特质分类模型"""
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    framework: Optional[str] = None
    version: str = "1.0"
    is_active: bool

class TraitValueType(BaseModel):
    """特质值类型模型"""
    id: UUID
    name: str
    data_type: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    enum_values: Optional[List[str]] = None
    description: Optional[str] = None

class PersonalityTrait(BaseModel):
    """人格特质模型"""
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    category: Optional[TraitCategory] = None
    value_type: TraitValueType
    is_reverse_scored: bool = False
    display_order: int = 0
    tags: List[str] = []
    is_active: bool

class UserPersonalityTrait(BaseModel):
    """用户人格特质模型"""
    id: UUID
    user_id: UUID
    trait: PersonalityTrait
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    value_boolean: Optional[bool] = None
    confidence_level: float = Field(0.5, ge=0, le=1)
    assessment_source: str = "self_assessment"
    assessment_date: datetime
    notes: Optional[str] = None
    is_public: bool = True

class CreateUserCognitiveFunction(BaseModel):
    """创建用户认知功能请求模型"""
    cognitive_function_id: UUID
    raw_score: Optional[int] = Field(None, ge=0, le=100)
    normalized_score: Optional[float] = Field(None, ge=0, le=100)
    function_rank: Optional[int] = Field(None, ge=1, le=8)
    confidence_level: float = Field(0.5, ge=0, le=1)
    assessment_source: str = "self_assessment"
    notes: Optional[str] = None

class UpdateUserCognitiveFunction(BaseModel):
    """更新用户认知功能请求模型"""
    raw_score: Optional[int] = Field(None, ge=0, le=100)
    normalized_score: Optional[float] = Field(None, ge=0, le=100)
    function_rank: Optional[int] = Field(None, ge=1, le=8)
    confidence_level: Optional[float] = Field(None, ge=0, le=1)
    assessment_source: Optional[str] = None
    notes: Optional[str] = None

class CreateUserPersonalityTrait(BaseModel):
    """创建用户人格特质请求模型"""
    trait_id: UUID
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    value_boolean: Optional[bool] = None
    confidence_level: float = Field(0.5, ge=0, le=1)
    assessment_source: str = "self_assessment"
    notes: Optional[str] = None
    is_public: bool = True

class UpdateUserPersonalityTrait(BaseModel):
    """更新用户人格特质请求模型"""
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    value_boolean: Optional[bool] = None
    confidence_level: Optional[float] = Field(None, ge=0, le=1)
    assessment_source: Optional[str] = None
    notes: Optional[str] = None
    is_public: Optional[bool] = None

class CognitiveFunctionDistribution(BaseModel):
    """认知功能分布模型"""
    user_id: UUID
    thinking_avg: float
    feeling_avg: float
    sensing_avg: float
    intuition_avg: float
    introverted_avg: float
    extraverted_avg: float

# =====================================================
# COGNITIVE FUNCTIONS ENDPOINTS - 认知功能端点
# =====================================================

@router.get("/cognitive-functions", response_model=List[CognitiveFunction])
async def get_cognitive_functions(
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """获取所有认知功能"""
    try:
        query = """
        SELECT id, code, name, full_name, description, function_type, attitude, is_active
        FROM ego.cognitive_functions
        WHERE is_active = true
        ORDER BY code
        """
        rows = await db.fetch(query)
        return [CognitiveFunction(**dict(row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取认知功能失败: {str(e)}")

@router.get("/cognitive-functions/{user_id}", response_model=List[UserCognitiveFunction])
async def get_user_cognitive_functions(
    user_id: UUID,
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """获取用户的认知功能评分"""
    try:
        query = """
        SELECT ucf.id, ucf.user_id, ucf.raw_score, ucf.normalized_score,
               ucf.function_rank, ucf.confidence_level, ucf.assessment_source,
               ucf.notes, ucf.assessed_at,
               cf.id as cf_id, cf.code, cf.name, cf.full_name, cf.description,
               cf.function_type, cf.attitude, cf.is_active
        FROM ego.user_cognitive_functions ucf
        JOIN ego.cognitive_functions cf ON ucf.cognitive_function_id = cf.id
        WHERE ucf.user_id = $1
        ORDER BY ucf.function_rank NULLS LAST, cf.code
        """
        
        rows = await db.fetch(query, user_id)
        
        result = []
        for row in rows:
            row_dict = dict(row)
            
            cognitive_function = CognitiveFunction(
                id=row_dict['cf_id'],
                code=row_dict['code'],
                name=row_dict['name'],
                full_name=row_dict['full_name'],
                description=row_dict['description'],
                function_type=row_dict['function_type'],
                attitude=row_dict['attitude'],
                is_active=row_dict['is_active']
            )
            
            user_cognitive_function = UserCognitiveFunction(
                id=row_dict['id'],
                user_id=row_dict['user_id'],
                cognitive_function=cognitive_function,
                raw_score=row_dict['raw_score'],
                normalized_score=row_dict['normalized_score'],
                function_rank=row_dict['function_rank'],
                confidence_level=row_dict['confidence_level'],
                assessment_source=row_dict['assessment_source'],
                notes=row_dict['notes'],
                assessed_at=row_dict['assessed_at']
            )
            
            result.append(user_cognitive_function)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户认知功能失败: {str(e)}")

@router.post("/cognitive-functions/{user_id}", response_model=UserCognitiveFunction)
async def create_user_cognitive_function(
    user_id: UUID,
    function_data: CreateUserCognitiveFunction,
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """为用户创建认知功能评分"""
    try:
        # 检查认知功能是否存在
        cf_check = await db.fetchrow(
            "SELECT id FROM ego.cognitive_functions WHERE id = $1 AND is_active = true",
            function_data.cognitive_function_id
        )
        if not cf_check:
            raise HTTPException(status_code=404, detail="认知功能不存在")
        
        # 检查是否已存在评分
        existing = await db.fetchrow(
            "SELECT id FROM ego.user_cognitive_functions WHERE user_id = $1 AND cognitive_function_id = $2",
            user_id, function_data.cognitive_function_id
        )
        if existing:
            raise HTTPException(status_code=400, detail="用户已有此认知功能评分")
        
        # 创建新的认知功能评分
        query = """
        INSERT INTO ego.user_cognitive_functions 
        (user_id, cognitive_function_id, raw_score, normalized_score, function_rank,
         confidence_level, assessment_source, notes)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING id
        """
        
        new_id = await db.fetchval(
            query,
            user_id,
            function_data.cognitive_function_id,
            function_data.raw_score,
            function_data.normalized_score,
            function_data.function_rank,
            function_data.confidence_level,
            function_data.assessment_source,
            function_data.notes
        )
        
        # 返回创建的认知功能评分
        user_functions = await get_user_cognitive_functions(user_id, db=db)
        for uf in user_functions:
            if uf.id == new_id:
                return uf
        
        raise HTTPException(status_code=500, detail="创建成功但无法获取结果")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建用户认知功能失败: {str(e)}")

@router.put("/cognitive-functions/{user_id}/{function_id}", response_model=UserCognitiveFunction)
async def update_user_cognitive_function(
    user_id: UUID,
    function_id: UUID,
    function_data: UpdateUserCognitiveFunction,
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """更新用户的认知功能评分"""
    try:
        # 检查用户认知功能是否存在
        existing = await db.fetchrow(
            "SELECT id FROM ego.user_cognitive_functions WHERE user_id = $1 AND cognitive_function_id = $2",
            user_id, function_id
        )
        if not existing:
            raise HTTPException(status_code=404, detail="用户认知功能评分不存在")
        
        # 构建更新字段
        update_fields = []
        params = []
        param_count = 0
        
        for field, value in function_data.model_dump(exclude_unset=True).items():
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
        params.append(function_id)
        
        query = f"""
        UPDATE ego.user_cognitive_functions 
        SET {', '.join(update_fields)}
        WHERE user_id = ${param_count-1} AND cognitive_function_id = ${param_count}
        """
        
        await db.execute(query, *params[:-2], params[-2], params[-1])
        
        # 返回更新后的认知功能评分
        user_functions = await get_user_cognitive_functions(user_id, db=db)
        for uf in user_functions:
            if uf.cognitive_function.id == function_id:
                return uf
        
        raise HTTPException(status_code=500, detail="更新成功但无法获取结果")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户认知功能失败: {str(e)}")

@router.delete("/cognitive-functions/{user_id}/{function_id}")
async def delete_user_cognitive_function(
    user_id: UUID,
    function_id: UUID,
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """删除用户的认知功能评分"""
    try:
        result = await db.execute(
            "DELETE FROM ego.user_cognitive_functions WHERE user_id = $1 AND cognitive_function_id = $2",
            user_id, function_id
        )

        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="用户认知功能评分不存在")

        return {"message": "用户认知功能评分已删除"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除用户认知功能失败: {str(e)}")

@router.get("/cognitive-functions/{user_id}/distribution", response_model=CognitiveFunctionDistribution)
async def get_cognitive_function_distribution(
    user_id: UUID,
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """获取用户的认知功能分布"""
    try:
        query = """
        SELECT * FROM ego.cognitive_function_distribution
        WHERE user_id = $1
        """

        row = await db.fetchrow(query, user_id)
        if not row:
            raise HTTPException(status_code=404, detail="用户认知功能分布不存在")

        return CognitiveFunctionDistribution(**dict(row))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取认知功能分布失败: {str(e)}")

# =====================================================
# PERSONALITY TRAITS ENDPOINTS - 人格特质端点
# =====================================================

@router.get("/trait-categories", response_model=List[TraitCategory])
async def get_trait_categories(
    framework: Optional[str] = Query(None, description="框架类型过滤"),
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """获取特质分类"""
    try:
        where_conditions = ["is_active = true"]
        params = []

        if framework:
            where_conditions.append("framework = $1")
            params.append(framework)

        where_clause = "WHERE " + " AND ".join(where_conditions)

        query = f"""
        SELECT id, name, slug, description, framework, version, is_active
        FROM ego.trait_categories
        {where_clause}
        ORDER BY framework, name
        """

        rows = await db.fetch(query, *params)
        return [TraitCategory(**dict(row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取特质分类失败: {str(e)}")

@router.get("/trait-value-types", response_model=List[TraitValueType])
async def get_trait_value_types(
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """获取特质值类型"""
    try:
        query = """
        SELECT id, name, data_type, min_value, max_value, enum_values, description
        FROM ego.trait_value_types
        ORDER BY name
        """
        rows = await db.fetch(query)
        return [TraitValueType(**dict(row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取特质值类型失败: {str(e)}")

@router.get("/personality-traits", response_model=List[PersonalityTrait])
async def get_personality_traits(
    category_id: Optional[UUID] = Query(None, description="分类ID过滤"),
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """获取人格特质"""
    try:
        where_conditions = ["pt.is_active = true"]
        params = []

        if category_id:
            where_conditions.append("pt.category_id = $1")
            params.append(category_id)

        where_clause = "WHERE " + " AND ".join(where_conditions)

        query = f"""
        SELECT pt.id, pt.name, pt.slug, pt.description, pt.is_reverse_scored,
               pt.display_order, pt.tags, pt.is_active,
               tc.id as category_id, tc.name as category_name, tc.slug as category_slug,
               tc.description as category_description, tc.framework, tc.version, tc.is_active as category_active,
               tvt.id as value_type_id, tvt.name as value_type_name, tvt.data_type,
               tvt.min_value, tvt.max_value, tvt.enum_values, tvt.description as value_type_description
        FROM ego.personality_traits pt
        LEFT JOIN ego.trait_categories tc ON pt.category_id = tc.id
        JOIN ego.trait_value_types tvt ON pt.value_type_id = tvt.id
        {where_clause}
        ORDER BY tc.framework, tc.name, pt.display_order, pt.name
        """

        rows = await db.fetch(query, *params)

        result = []
        for row in rows:
            row_dict = dict(row)

            # 构建嵌套对象
            category = None
            if row_dict['category_id']:
                category = TraitCategory(
                    id=row_dict['category_id'],
                    name=row_dict['category_name'],
                    slug=row_dict['category_slug'],
                    description=row_dict['category_description'],
                    framework=row_dict['framework'],
                    version=row_dict['version'],
                    is_active=row_dict['category_active']
                )

            value_type = TraitValueType(
                id=row_dict['value_type_id'],
                name=row_dict['value_type_name'],
                data_type=row_dict['data_type'],
                min_value=row_dict['min_value'],
                max_value=row_dict['max_value'],
                enum_values=row_dict['enum_values'],
                description=row_dict['value_type_description']
            )

            trait = PersonalityTrait(
                id=row_dict['id'],
                name=row_dict['name'],
                slug=row_dict['slug'],
                description=row_dict['description'],
                category=category,
                value_type=value_type,
                is_reverse_scored=row_dict['is_reverse_scored'],
                display_order=row_dict['display_order'],
                tags=row_dict['tags'] or [],
                is_active=row_dict['is_active']
            )

            result.append(trait)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取人格特质失败: {str(e)}")

@router.get("/personality-traits/{user_id}", response_model=List[UserPersonalityTrait])
async def get_user_personality_traits(
    user_id: UUID,
    category_id: Optional[UUID] = Query(None, description="分类ID过滤"),
    is_public: Optional[bool] = Query(None, description="是否只返回公开特质"),
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """获取用户的人格特质"""
    try:
        where_conditions = ["upt.user_id = $1"]
        params = [user_id]
        param_count = 1

        if category_id:
            param_count += 1
            where_conditions.append(f"pt.category_id = ${param_count}")
            params.append(category_id)

        if is_public is not None:
            param_count += 1
            where_conditions.append(f"upt.is_public = ${param_count}")
            params.append(is_public)

        where_clause = "WHERE " + " AND ".join(where_conditions)

        query = f"""
        SELECT upt.id, upt.user_id, upt.value_numeric, upt.value_text, upt.value_boolean,
               upt.confidence_level, upt.assessment_source, upt.assessment_date,
               upt.notes, upt.is_public,
               pt.id as trait_id, pt.name as trait_name, pt.slug as trait_slug,
               pt.description as trait_description, pt.is_reverse_scored, pt.display_order,
               pt.tags, pt.is_active as trait_active,
               tc.id as category_id, tc.name as category_name, tc.slug as category_slug,
               tc.description as category_description, tc.framework, tc.version,
               tc.is_active as category_active,
               tvt.id as value_type_id, tvt.name as value_type_name, tvt.data_type,
               tvt.min_value, tvt.max_value, tvt.enum_values,
               tvt.description as value_type_description
        FROM ego.user_personality_traits upt
        JOIN ego.personality_traits pt ON upt.trait_id = pt.id
        LEFT JOIN ego.trait_categories tc ON pt.category_id = tc.id
        JOIN ego.trait_value_types tvt ON pt.value_type_id = tvt.id
        {where_clause}
        ORDER BY tc.framework, tc.name, pt.display_order, pt.name
        """

        rows = await db.fetch(query, *params)

        result = []
        for row in rows:
            row_dict = dict(row)

            # 构建嵌套对象
            category = None
            if row_dict['category_id']:
                category = TraitCategory(
                    id=row_dict['category_id'],
                    name=row_dict['category_name'],
                    slug=row_dict['category_slug'],
                    description=row_dict['category_description'],
                    framework=row_dict['framework'],
                    version=row_dict['version'],
                    is_active=row_dict['category_active']
                )

            value_type = TraitValueType(
                id=row_dict['value_type_id'],
                name=row_dict['value_type_name'],
                data_type=row_dict['data_type'],
                min_value=row_dict['min_value'],
                max_value=row_dict['max_value'],
                enum_values=row_dict['enum_values'],
                description=row_dict['value_type_description']
            )

            trait = PersonalityTrait(
                id=row_dict['trait_id'],
                name=row_dict['trait_name'],
                slug=row_dict['trait_slug'],
                description=row_dict['trait_description'],
                category=category,
                value_type=value_type,
                is_reverse_scored=row_dict['is_reverse_scored'],
                display_order=row_dict['display_order'],
                tags=row_dict['tags'] or [],
                is_active=row_dict['trait_active']
            )

            user_trait = UserPersonalityTrait(
                id=row_dict['id'],
                user_id=row_dict['user_id'],
                trait=trait,
                value_numeric=row_dict['value_numeric'],
                value_text=row_dict['value_text'],
                value_boolean=row_dict['value_boolean'],
                confidence_level=row_dict['confidence_level'],
                assessment_source=row_dict['assessment_source'],
                assessment_date=row_dict['assessment_date'],
                notes=row_dict['notes'],
                is_public=row_dict['is_public']
            )

            result.append(user_trait)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户人格特质失败: {str(e)}")
