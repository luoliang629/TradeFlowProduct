"""认证相关API路由."""

import secrets
from datetime import datetime, timedelta
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import (
    AuthErrorResponse,
    CompanyVerificationRequest,
    LogoutRequest,
    OAuthAuthorizationRequest,
    OAuthAuthorizationResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserProfile,
    UserResponse,
)
from app.services.oauth import oauth_service
from app.utils.jwt_utils import jwt_manager
from app.utils.redis_client import redis_client

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post(
    "/oauth/{provider}/authorize",
    response_model=OAuthAuthorizationResponse,
    summary="获取OAuth授权URL",
    description="获取指定OAuth提供商的授权URL，支持Google和GitHub"
)
async def get_oauth_authorization_url(
    provider: str,
    redirect_uri: str = Query(None, description="登录成功后重定向URL")
) -> OAuthAuthorizationResponse:
    """获取OAuth授权URL."""
    
    if provider not in ["google", "github"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported OAuth provider"
        )
    
    # 生成state参数用于防止CSRF攻击
    state = secrets.token_urlsafe(32)
    
    # 将state和redirect_uri存储在Redis中
    state_key = f"oauth_state:{state}"
    state_data = {
        "provider": provider,
        "redirect_uri": redirect_uri or settings.OAUTH_SUCCESS_REDIRECT,
        "created_at": datetime.utcnow().isoformat()
    }
    
    try:
        await redis_client.setex(state_key, 600, str(state_data))  # 10分钟过期
    except Exception as e:
        logger.error("Failed to store OAuth state", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate authorization URL"
        )
    
    # 获取授权URL
    authorization_url = oauth_service.get_authorization_url(provider, state)
    if not authorization_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate authorization URL"
        )
    
    return OAuthAuthorizationResponse(
        authorization_url=authorization_url,
        state=state
    )


@router.get(
    "/oauth/{provider}/callback",
    summary="OAuth回调处理",
    description="处理OAuth提供商的回调请求"
)
async def oauth_callback(
    provider: str,
    code: str = Query(..., description="授权码"),
    state: str = Query(..., description="状态参数"),
    error: str = Query(None, description="错误信息"),
    db: AsyncSession = Depends(get_db)
):
    """处理OAuth回调."""
    
    # 检查是否有错误
    if error:
        logger.warning("OAuth callback error", provider=provider, error=error)
        error_url = f"{settings.OAUTH_ERROR_REDIRECT}?error={error}"
        return RedirectResponse(url=error_url)
    
    # 验证state参数
    state_key = f"oauth_state:{state}"
    try:
        stored_state = await redis_client.get(state_key)
        if not stored_state:
            logger.warning("Invalid or expired OAuth state", state=state)
            error_url = f"{settings.OAUTH_ERROR_REDIRECT}?error=invalid_state"
            return RedirectResponse(url=error_url)
        
        # 删除已使用的state
        await redis_client.delete(state_key)
        
    except Exception as e:
        logger.error("Failed to validate OAuth state", error=str(e))
        error_url = f"{settings.OAUTH_ERROR_REDIRECT}?error=server_error"
        return RedirectResponse(url=error_url)
    
    # 执行OAuth认证
    try:
        auth_result = await oauth_service.authenticate_user(db, provider, code)
        if not auth_result:
            logger.error("OAuth authentication failed", provider=provider)
            error_url = f"{settings.OAUTH_ERROR_REDIRECT}?error=auth_failed"
            return RedirectResponse(url=error_url)
        
        user, access_token, refresh_token = auth_result
        
        # 重定向到前端，带上令牌
        success_url = f"{settings.OAUTH_SUCCESS_REDIRECT}?access_token={access_token}&refresh_token={refresh_token}"
        return RedirectResponse(url=success_url)
        
    except Exception as e:
        logger.error("OAuth callback processing failed", error=str(e))
        error_url = f"{settings.OAUTH_ERROR_REDIRECT}?error=server_error"
        return RedirectResponse(url=error_url)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="刷新访问令牌",
    description="使用刷新令牌获取新的访问令牌"
)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """刷新访问令牌."""
    
    # 验证刷新令牌
    payload = jwt_manager.verify_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # 检查令牌类型
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    # 检查令牌是否在黑名单中
    jti = payload.get("jti")
    if jti and await jwt_manager.is_token_blacklisted(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is blacklisted"
        )
    
    # 获取用户ID
    try:
        user_id = int(payload.get("sub"))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # 检查用户是否存在且活跃
    from sqlalchemy import select
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # 生成新的令牌
    new_access_token = jwt_manager.create_access_token(user_id)
    new_refresh_token = jwt_manager.create_refresh_token(user_id)
    
    # 将旧的刷新令牌加入黑名单
    if jti:
        expires_at = datetime.utcfromtimestamp(payload.get("exp"))
        await jwt_manager.add_token_to_blacklist(
            db, jti, user_id, "refresh", expires_at
        )
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600
    )


@router.post(
    "/logout",
    summary="用户登出",
    description="登出当前用户，将令牌加入黑名单"
)
async def logout(
    request: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """用户登出."""
    
    try:
        # 如果提供了刷新令牌，将其加入黑名单
        if request.refresh_token:
            payload = jwt_manager.verify_token(request.refresh_token)
            if payload and payload.get("type") == "refresh":
                jti = payload.get("jti")
                if jti:
                    expires_at = datetime.utcfromtimestamp(payload.get("exp"))
                    await jwt_manager.add_token_to_blacklist(
                        db, jti, current_user.id, "refresh", expires_at
                    )
        
        # 也可以选择撤销用户的所有令牌（更严格的安全策略）
        # await jwt_manager.revoke_all_user_tokens(db, current_user.id)
        
        logger.info("User logged out", user_id=current_user.id)
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error("Logout failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get(
    "/me",
    response_model=UserProfile,
    summary="获取当前用户信息",
    description="获取当前认证用户的详细信息"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> UserProfile:
    """获取当前用户信息."""
    return UserProfile.from_orm(current_user)


@router.put(
    "/profile",
    response_model=UserResponse,
    summary="更新用户资料",
    description="更新当前用户的基本资料信息"
)
async def update_user_profile(
    profile_data: Dict[str, str],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """更新用户资料."""
    
    try:
        # 更新允许的字段
        allowed_fields = ["full_name", "company_name", "company_website", "company_description"]
        
        for field, value in profile_data.items():
            if field in allowed_fields and hasattr(current_user, field):
                setattr(current_user, field, value)
        
        await db.commit()
        await db.refresh(current_user)
        
        logger.info("User profile updated", user_id=current_user.id)
        
        return UserResponse.from_orm(current_user)
        
    except Exception as e:
        logger.error("Failed to update user profile", error=str(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post(
    "/company/verify",
    summary="申请企业认证",
    description="提交企业认证申请"
)
async def apply_company_verification(
    verification_data: CompanyVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """申请企业认证."""
    
    try:
        from app.models.user import CompanyStatus
        
        # 更新用户的企业信息
        current_user.company_name = verification_data.company_name
        current_user.company_website = verification_data.company_website
        current_user.company_description = verification_data.company_description
        current_user.company_status = CompanyStatus.PENDING
        
        await db.commit()
        
        logger.info("Company verification application submitted", user_id=current_user.id)
        
        return {"message": "Company verification application submitted"}
        
    except Exception as e:
        logger.error("Failed to submit company verification", error=str(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit company verification"
        )