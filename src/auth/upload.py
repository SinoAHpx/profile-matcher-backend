import uuid
from fastapi import UploadFile, HTTPException
from src.auth.admin_client import get_supabase_admin_client
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)

async def upload_avatar_to_storage(file: UploadFile, user_id: str) -> str:
    """
    上传头像文件到Supabase Storage，并返回文件URL
    
    Args:
        file: 上传的文件
        user_id: 用户ID，用于生成文件路径
        
    Returns:
        str: 文件的完整URL
        
    Raises:
        HTTPException: 上传失败时抛出异常
    """
    try:
        # 验证文件类型
        if file.content_type not in settings.allowed_file_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file.content_type} not allowed. Allowed types: {settings.allowed_file_types}"
            )
        
        # 验证文件大小
        file_content = await file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > settings.max_file_size_mb:
            raise HTTPException(
                status_code=400,
                detail=f"File size {file_size_mb:.2f}MB exceeds maximum allowed size {settings.max_file_size_mb}MB"
            )
        
        # 重置文件指针
        await file.seek(0)
        
        # 生成唯一文件名
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"avatars/{user_id}/{uuid.uuid4()}.{file_extension}"
        
        # 获取admin客户端
        admin_client = get_supabase_admin_client()
        
        # 上传到Supabase Storage
        response = admin_client.storage.from_(settings.supabase_storage_bucket).upload(
            unique_filename,
            file_content,
            {"content-type": file.content_type}
        )
        
        if hasattr(response, 'error') and response.error:
            logger.error(f"Storage upload error: {response.error}")
            raise HTTPException(status_code=500, detail="Failed to upload file to storage")
        
        # 生成文件URL - 根据实际部署情况构造URL
        # 格式: SUPABASE_URL/storage/v1/object/public/bucket_name/file_path
        file_url = f"{settings.supabase_url}/storage/v1/object/public/{settings.supabase_storage_bucket}/{unique_filename}"
        
        logger.info(f"Avatar uploaded successfully for user {user_id}: {file_url}")
        return file_url
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during avatar upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during file upload")


async def update_user_avatar(user_id: str, avatar_url: str) -> bool:
    """
    更新用户档案中的头像URL
    
    Args:
        user_id: 用户ID
        avatar_url: 头像URL
        
    Returns:
        bool: 更新是否成功
        
    Raises:
        HTTPException: 更新失败时抛出异常
    """
    try:
        admin_client = get_supabase_admin_client()
        response = admin_client.table("user_profiles").update({
            "avatar_url": avatar_url
        }).eq("user_id", user_id).execute()
        
        if hasattr(response, 'error') and response.error:
            logger.error(f"Database update error: {response.error}")
            raise HTTPException(status_code=500, detail="Failed to update user profile")
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        logger.info(f"Avatar URL updated for user {user_id}")
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during profile update: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during profile update")