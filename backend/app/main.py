"""
FastAPI主应用
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base
import traceback
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Import routers
from app.api import auth, products, customers, documents, websocket, import_export, dashboard

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="客户资料收集系统API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS（允许本地局域网 5173 端口，便于手机端通过前端开发服务器访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"http://.*:5173",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(websocket.router, prefix="/api")
app.include_router(import_export.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

# Mount static files for uploaded documents
upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/api/files", StaticFiles(directory=str(upload_dir)), name="files")


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """捕获所有未处理的异常"""
    error_msg = str(exc)
    tb = traceback.format_exc()
    logger.error(f"Unhandled exception: {error_msg}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": error_msg,
            "type": type(exc).__name__
        }
    )


# 创建数据库表
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    # 创建所有表（生产环境应使用Alembic迁移）
    Base.metadata.create_all(bind=engine)
    print("[OK] {} v{} started successfully".format(settings.APP_NAME, settings.APP_VERSION))


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    print("[OK] {} shutdown".format(settings.APP_NAME))


@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# 导入路由（后续添加）
# from app.api import auth, customers, documents, products, websocket
# app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
# app.include_router(customers.router, prefix="/api/customers", tags=["客户管理"])
# app.include_router(documents.router, prefix="/api/documents", tags=["资料管理"])
# app.include_router(products.router, prefix="/api/products", tags=["产品管理"])

