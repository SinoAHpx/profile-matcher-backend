from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from src.auth.supabase_client import get_supabase_client
from src.auth.admin_client import get_supabase_admin_client
from src.auth.upload import upload_avatar_to_storage, update_user_avatar
from src.models.user import UserRegister, UserProfile, UserProfileUpdate, HobbyReference
from typing import Optional, List
import uuid
import json

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), 
                          supabase: Client = Depends(get_supabase_client)):
    try:
        response = supabase.auth.get_user(credentials.credentials)
        if response.user:
            return response.user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

@router.post("/register")
async def register_user(
    request: Request,
    nickname: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = File(None)
):
    try:
        # 如果是 JSON 请求体且未提供表单字段，解析 JSON 数据
        if (nickname is None or email is None or password is None) \
            and request.headers.get("content-type", "").startswith("application/json"):
            data = await request.json()
            nickname = nickname or data.get("nickname")
            email = email or data.get("email")
            password = password or data.get("password")

        # 验证输入
        if not nickname or len(nickname.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nickname cannot be empty"
            )
        
        if not password or len(password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters"
            )
        
        # 使用admin客户端创建用户
        admin_client = get_supabase_admin_client()
        
        # 创建用户
        try:
            auth_response = admin_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True
            })
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Authentication error: {str(e)}"
            )
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        user_id = auth_response.user.id
        avatar_url = None
        
        # 处理头像上传（先跳过以避免存储问题）
        # if avatar:
        #     try:
        #         # 生成唯一文件名
        #         file_extension = avatar.filename.split('.')[-1] if avatar.filename else "png"
        #         avatar_filename = f"{user_id}/avatar.{file_extension}"
        #         
        #         # 上传到Supabase Storage
        #         avatar_content = await avatar.read()
        #         storage_response = admin_client.storage.from_("avatars").upload(
        #             avatar_filename, 
        #             avatar_content,
        #             file_options={"content-type": avatar.content_type or "image/png"}
        #         )
        #         
        #         if storage_response.data:
        #             # 获取公开URL
        #             avatar_url = admin_client.storage.from_("avatars").get_public_url(avatar_filename)
        #     except Exception as e:
        #         print(f"Avatar upload failed: {e}")
        #         # 继续处理，不让头像上传失败阻止整个注册流程
        
        # 使用admin权限创建用户资料
        profile_data = {
            "user_id": user_id,
            "nickname": nickname.strip(),
            "avatar_url": avatar_url
        }
        
        try:
            profile_response = admin_client.table("user_profiles").insert(profile_data).execute()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Profile creation error: {str(e)}"
            )
        
        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user profile"
            )
        
        return {
            "message": "User registered successfully",
            "user_id": user_id,
            "profile": profile_response.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/upload-avatar")
async def upload_avatar_by_email(
    email: str = Form(...),
    avatar: UploadFile = File(...)
):
    """
    通过邮箱上传用户头像
    """
    try:
        # 使用admin客户端查找用户
        admin_client = get_supabase_admin_client()
        
        # 通过邮箱查找用户ID
        auth_users = admin_client.auth.admin.list_users()
        user_found = None
        for user in auth_users:
            if user.email == email:
                user_found = user
                break
        
        if not user_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found"
            )
        
        user_id = user_found.id
        
        # 上传文件到存储
        avatar_url = await upload_avatar_to_storage(avatar, user_id)
        
        # 更新用户档案中的头像URL
        await update_user_avatar(user_id, avatar_url)
        
        return {
            "message": "Avatar uploaded successfully",
            "email": email,
            "user_id": user_id,
            "avatar_url": avatar_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Avatar upload failed: {str(e)}"
        )

@router.get("/user-id/{email}")
async def get_user_id_by_email(email: str):
    """
    根据邮箱获取用户ID
    """
    try:
        admin_client = get_supabase_admin_client()
        
        # 通过邮箱查找用户ID
        auth_users = admin_client.auth.admin.list_users()
        user_found = None
        for user in auth_users:
            if user.email == email:
                user_found = user
                break
        
        if not user_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found"
            )
        
        return {
            "email": email,
            "user_id": user_found.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user ID: {str(e)}"
        )

@router.get("/avatar/{email}")
async def get_avatar_by_email(email: str):
    """
    根据邮箱获取用户头像链接
    """
    try:
        admin_client = get_supabase_admin_client()
        # 通过邮箱查找用户ID
        auth_users = admin_client.auth.admin.list_users()
        user_found = None
        for user in auth_users:
            if user.email == email:
                user_found = user
                break
        
        if not user_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found"
            )
        
        user_id = user_found.id
        
        # 查询用户档案获取头像URL
        profile_response = admin_client.table("user_profiles").select("avatar_url").eq("user_id", user_id).execute()
        
        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        avatar_url = profile_response.data[0].get("avatar_url")
        
        return {
            "email": email,
            "user_id": user_id,
            "avatar_url": avatar_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get avatar: {str(e)}"
        )

@router.post("/login")
async def login(
    request: Request,
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    supabase: Client = Depends(get_supabase_client)
):
    try:
        # 如果是 JSON 请求体且未提供表单字段，解析 JSON 数据
        if (email is None or password is None) \
            and request.headers.get("content-type", "").startswith("application/json"):
            data = await request.json()
            email = email or data.get("email")
            password = password or data.get("password")

        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )

        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user and response.session:
            return {
                "access_token": response.session.access_token,
                "token_type": "bearer",
                "user": response.user
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.get("/profile", response_model=UserProfile)
async def get_profile(
    current_user=Depends(get_current_user)
):
    try:
        # 使用admin客户端查询，绕过RLS
        admin_client = get_supabase_admin_client()
        response = admin_client.table("user_profiles").select("*").eq("user_id", current_user.id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get profile: {str(e)}"
        )

@router.put("/profile")
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user=Depends(get_current_user)
):
    try:
        # 只更新non-None的字段
        update_data = {}
        if profile_update.mbti is not None:
            update_data["mbti"] = profile_update.mbti.value
        if profile_update.hobbies is not None:
            update_data["hobbies"] = profile_update.hobbies
        if profile_update.motto is not None:
            update_data["motto"] = profile_update.motto
        if profile_update.self_description is not None:
            update_data["self_description"] = profile_update.self_description
            
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data to update"
            )
        
        # 使用admin客户端更新，绕过RLS
        admin_client = get_supabase_admin_client()
        response = admin_client.table("user_profiles").update(update_data).eq("user_id", current_user.id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return {
            "message": "Profile updated successfully",
            "profile": response.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.get("/hobbies", response_model=List[HobbyReference])
async def get_hobbies(supabase: Client = Depends(get_supabase_client)):
    try:
        response = supabase.table("hobbies_reference").select("*").order("id").execute()
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/hobbies/{category}")
async def get_hobbies_by_category(
    category: str,
    supabase: Client = Depends(get_supabase_client)
):
    try:
        valid_categories = ["body", "mind", "heart", "hands"]
        if category not in valid_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Must be one of: {valid_categories}"
            )
            
        response = supabase.table("hobbies_reference").select("*").eq("category", category).order("id").execute()
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/test-connection")
async def test_supabase_connection(supabase: Client = Depends(get_supabase_client)):
    """测试Supabase连接"""
    try:
        # 简单的认证测试
        response = supabase.auth.get_user()
        return {
            "status": "success",
            "message": "Supabase connection working",
            "auth_service": "available"
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Supabase connection failed: {str(e)}"
        }

@router.post("/register-simple")
async def register_simple(
    nickname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    """简化的注册端点，使用admin权限"""
    try:
        # 验证输入
        if len(nickname.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nickname cannot be empty"
            )
        
        if len(password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters"
            )
        
        # 使用admin客户端创建用户
        admin_client = get_supabase_admin_client()
        
        # 创建用户
        auth_response = admin_client.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True  # 自动确认邮箱
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        user_id = auth_response.user.id
        
        # 使用admin权限创建用户资料
        profile_data = {
            "user_id": user_id,
            "nickname": nickname.strip(),
            "avatar_url": None
        }
        
        profile_response = admin_client.table("user_profiles").insert(profile_data).execute()
        
        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user profile"
            )
        
        return {
            "message": "User registered successfully",
            "user_id": user_id,
            "profile": profile_response.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/upload-avatar")
async def upload_avatar_by_email(
    email: str = Form(...),
    avatar: UploadFile = File(...)
):
    """
    通过邮箱上传用户头像
    """
    try:
        # 使用admin客户端查找用户
        admin_client = get_supabase_admin_client()
        
        # 通过邮箱查找用户ID
        auth_users = admin_client.auth.admin.list_users()
        user_found = None
        for user in auth_users:
            if user.email == email:
                user_found = user
                break
        
        if not user_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found"
            )
        
        user_id = user_found.id
        
        # 上传文件到存储
        avatar_url = await upload_avatar_to_storage(avatar, user_id)
        
        # 更新用户档案中的头像URL
        await update_user_avatar(user_id, avatar_url)
        
        return {
            "message": "Avatar uploaded successfully",
            "email": email,
            "user_id": user_id,
            "avatar_url": avatar_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Avatar upload failed: {str(e)}"
        )

@router.get("/user-id/{email}")
async def get_user_id_by_email(email: str):
    """
    根据邮箱获取用户ID
    """
    try:
        admin_client = get_supabase_admin_client()
        
        # 通过邮箱查找用户ID
        auth_users = admin_client.auth.admin.list_users()
        user_found = None
        for user in auth_users:
            if user.email == email:
                user_found = user
                break
        
        if not user_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found"
            )
        
        return {
            "email": email,
            "user_id": user_found.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user ID: {str(e)}"
        )

@router.get("/avatar/{email}")
async def get_avatar_by_email(email: str):
    """
    根据邮箱获取用户头像链接
    """
    try:
        admin_client = get_supabase_admin_client()
        
        # 通过邮箱查找用户ID
        auth_users = admin_client.auth.admin.list_users()
        user_found = None
        for user in auth_users:
            if user.email == email:
                user_found = user
                break
        
        if not user_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found"
            )
        
        user_id = user_found.id
        
        # 查询用户档案获取头像URL
        profile_response = admin_client.table("user_profiles").select("avatar_url").eq("user_id", user_id).execute()
        
        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        avatar_url = profile_response.data[0].get("avatar_url")
        
        return {
            "email": email,
            "user_id": user_id,
            "avatar_url": avatar_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get avatar: {str(e)}"
        )