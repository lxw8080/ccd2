"""
安全相关功能：密码加密、JWT生成和验证
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError as InvalidTokenError
import hashlib
import secrets
from app.config import settings

# 简单的密码哈希实现（用于测试）
def get_password_hash_simple(password: str) -> str:
    """使用 SHA256 生成密码哈希"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"sha256${salt}${pwd_hash}"

def verify_password_simple(plain_password: str, hashed_password: str) -> bool:
    """验证 SHA256 密码"""
    try:
        parts = hashed_password.split('$')
        if len(parts) != 3 or parts[0] != 'sha256':
            return False
        salt = parts[1]
        stored_hash = parts[2]
        pwd_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
        return pwd_hash == stored_hash
    except:
        return False


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return verify_password_simple(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return get_password_hash_simple(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码的数据（通常包含用户ID等信息）
        expires_delta: 过期时间增量
    
    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    解码JWT访问令牌

    Args:
        token: JWT令牌字符串

    Returns:
        解码后的数据，如果令牌无效则返回None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except InvalidTokenError:
        return None

