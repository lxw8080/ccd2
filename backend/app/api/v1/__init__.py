"""
API v1 路由
"""
from fastapi import APIRouter
from ..customers import router as customers_router
from ..documents import router as documents_router
from ..products import router as products_router

# 创建 v1 API 路由器
router = APIRouter(prefix="/v1")

# 注册子路由
router.include_router(customers_router, tags=["customers"])
router.include_router(documents_router, tags=["documents"])
router.include_router(products_router, tags=["products"])

