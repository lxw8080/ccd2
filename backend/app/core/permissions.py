"""
权限管理系统
"""
from typing import List, Dict
from fastapi import HTTPException, status

# 角色权限配置
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "customer_service": [
        "customer.view",
        "customer.create",
        "customer.update_own",
        "document.upload",
        "document.view",
        "document.delete_own",
    ],
    "reviewer": [
        "customer.view",
        "customer.view_all",
        "document.view",
        "document.approve",
        "document.reject",
        "customer.approve",
        "customer.reject",
    ],
    "admin": ["*"],  # 所有权限
}


def check_permission(user_role: str, required_permission: str) -> bool:
    """
    检查用户角色是否拥有指定权限
    
    Args:
        user_role: 用户角色
        required_permission: 需要的权限
    
    Returns:
        是否拥有权限
    """
    if user_role not in ROLE_PERMISSIONS:
        return False
    
    permissions = ROLE_PERMISSIONS[user_role]
    
    # 管理员拥有所有权限
    if "*" in permissions:
        return True
    
    return required_permission in permissions


def require_permission(required_permission: str):
    """
    权限检查装饰器（用于依赖注入）
    
    Args:
        required_permission: 需要的权限
    
    Returns:
        依赖函数
    """
    def permission_checker(current_user):
        if not check_permission(current_user.role, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 {required_permission} 权限"
            )
        return current_user
    
    return permission_checker


def get_user_permissions(user_role: str) -> List[str]:
    """
    获取用户角色的所有权限
    
    Args:
        user_role: 用户角色
    
    Returns:
        权限列表
    """
    return ROLE_PERMISSIONS.get(user_role, [])

