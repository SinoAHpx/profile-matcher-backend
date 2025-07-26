from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from src.auth.supabase_client import get_supabase_client
from src.auth.admin_client import get_supabase_admin_client
from src.models.user import Interest, InterestsResponse, UpdateInterestsRequest, UpdateInterestsResponse
from typing import List

router = APIRouter(tags=["interests"])
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), 
                          supabase: Client = Depends(get_supabase_client)):
    """Get current authenticated user"""
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

@router.get("/interests", response_model=InterestsResponse)
async def get_all_interests(supabase: Client = Depends(get_supabase_client)):
    """
    获取系统中所有可选的兴趣爱好列表
    
    Returns all available interests (hobbies) in the system.
    This endpoint maps the hobbies_reference table to the interests API format.
    """
    try:
        response = supabase.table("hobbies_reference").select("*").order("id").execute()
        
        # Convert hobbies to interests format (id as string)
        interests = [
            Interest(id=str(hobby["id"]), name=hobby["name"]) 
            for hobby in response.data
        ]
        
        return InterestsResponse(interests=interests)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch interests: {str(e)}"
        )

@router.put("/users/{user_id}/interests", response_model=UpdateInterestsResponse)
async def update_user_interests(
    user_id: str,
    interests_data: UpdateInterestsRequest,
    current_user=Depends(get_current_user)
):
    """
    更新用户的兴趣爱好列表
    
    Updates the user's interests (hobbies) list.
    This endpoint maps the interests API to the hobbies field in user_profiles.
    """
    try:
        # Verify user can only update their own interests
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only update your own interests"
            )
        
        # Convert string IDs to integers for database storage
        try:
            hobby_ids = [int(interest_id) for interest_id in interests_data.interest_ids]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid interest ID format. Must be numeric strings."
            )
        
        # Validate hobby IDs exist in the reference table
        admin_client = get_supabase_admin_client()
        
        if hobby_ids:  # Only validate if there are IDs to check
            hobby_check = admin_client.table("hobbies_reference").select("id").in_("id", hobby_ids).execute()
            valid_ids = {hobby["id"] for hobby in hobby_check.data}
            invalid_ids = set(hobby_ids) - valid_ids
            
            if invalid_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid interest IDs: {list(invalid_ids)}"
                )
        
        # Update user's hobbies
        update_response = admin_client.table("user_profiles").update({
            "hobbies": hobby_ids
        }).eq("user_id", user_id).execute()
        
        if not update_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return UpdateInterestsResponse(interest_ids=interests_data.interest_ids)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update interests: {str(e)}"
        )
