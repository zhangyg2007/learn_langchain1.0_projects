#!/usr/bin/env python3
"""
LangChain L3 Advanced - Week 11-12  
课程标题: FastAPI企业级架构设计
学习目标:
  - 掌握FastAPI企业级API架构设计
  - 学习异步处理和高并发优化
  - 理解API安全认证与权限管理
  - 实践微服务架构与容器化部署
  - 构建生产级API监控与运维体系
作者: Claude Code 教学团队
创建时间: 2024-01-16
版本: 1.0.0
先决条件: ✅ 完成L2 Intermediate认证

🎯 实践重点:
  - 企业级FastAPI架构设计
  - 异步处理与高并发优化
  - JWT认证与RBAC权限管理
  - 微服务拆分与容器化
  - 生产级监控与日志系统
"""

import sys
import os
import time
import json
import asyncio
import uuid
import hashlib
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path
import logging
from contextlib import asynccontextmanager
import uvicorn
from enum import Enum

# FastAPI核心组件
try:
    from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Response
    from fastapi.responses import JSONResponse, StreamingResponse
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.gzip import GZipMiddleware
    from fastapi.openapi.utils import get_openapi
    from pydantic import BaseModel, Field, validator
    print("✅ FastAPI核心组件导入成功")
except ImportError as e:
    print(f"❌ FastAPI导入失败: {e}")
    print("请确保已安装: pip install fastapi uvicorn pydantic")
    sys.exit(1)

# 企业级安全组件
try:
    from passlib.context import CryptContext
    from jose import JWTError, jwt
    from prometheus_client import Counter, Histogram, Gauge, generate_latest
    print("✅ 企业级安全组件导入成功")
    security_available = True
except ImportError as e:
    print(f"⚠️部分安全组件导入失败: {e}")
    print("请确保已安装: pip install python-jose[cryptography] passlib[bcrypt] prometheus-client")
    security_available = False

# 数据库与缓存
try:
    import redis
    import sqlite3
    print("✅ 数据库与缓存组件导入成功")
    db_available = True
except ImportError as e:
    print(f"⚠️ 数据库组件导入失败: {e}")
    print("请确保已安装: pip install redis")
    db_available = False

@dataclass
class APIPerformanceMetrics:
    """API性能指标"""
    response_time: float
    memory_usage_mb: float
    request_count: int
    error_count: int
    cpu_usage_percent: float

@dataclass
class UserToken:
    """用户令牌信息"""
    user_id: str
    username: str
    roles: List[str]
    expires_at: datetime
    issued_at: datetime

@dataclass
class User:
    """用户模型"""
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    full_name: str = ""
    hashed_password: str = ""
    roles: List[str] = field(default_factory=lambda: ["user"])
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

class UserRole(Enum):
    """用户角色枚举"""
    USER = "user"
    ADMIN = "admin"
    MANAGER = "manager"
    GUEST = "guest"

class APIModels:
    """API数据模型"""
    
    class UserLogin(BaseModel):
        username: str = Field(..., min_length=3, max_length=50)
        password: str = Field(..., min_length=6)
    
    class UserRegister(BaseModel):
        username: str = Field(..., min_length=3, max_length=50)
        email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
        full_name: str = Field(..., min_length=1, max_length=100)
        password: str = Field(..., min_length=6)
    
    class RAGQuery(BaseModel):
        query: str = Field(..., min_length=1, max_length=1000)
        context: Optional[List[str]] = Field(default=None)
        temperature: float = Field(default=0.7, ge=0.0, le=2.0)
        max_tokens: int = Field(default=1000, ge=1, le=4096)
    
    class RAGResponse(BaseModel):
        success: bool
        data: Dict[str, Any]
        message: Optional[str] = None
        process_time: float
    
    class HealthResponse(BaseModel):
        status: str
        timestamp: str
        version: str
        service: str
    
    class LoginResponse(BaseModel):
        access_token: str
        token_type: str
        expires_in: int
        user: Dict[str, Any]

class EnterpriseFastAPIArchitecture:
    """FastAPI企业级架构设计器"""
    
    def __init__(self):
        self.app = None
        self.security_config = self._init_security_config()
        self.database_config = self._init_database_config()
        self.monitoring_config = self._init_monitoring_config()
        self.logger = self._setup_logging()
        self.user_db = self._init_user_database()
        self.security_schemes = self._setup_security_schemes()
        
        # 初始化Prometheus指标
        if security_available:
            self._init_prometheus_metrics()
    
    def _setup_logging(self):
        """设置日志配置"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('enterprise_api.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _init_security_config(self):
        """初始化安全配置"""
        return {
            "SECRET_KEY": os.getenv("SECRET_KEY", "your-super-secret-jwt-key-for-enterprise-rag-system"),
            "ALGORITHM": "HS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
            "REFRESH_TOKEN_EXPIRE_DAYS": 7,
            "PASSWORD_CONTEXT": CryptContext(schemes=["bcrypt"], deprecated="auto") if security_available else None
        }
    
    def _init_database_config(self):
        """初始化数据库配置"""
        return {
            "DATABASE_URL": os.getenv("DATABASE_URL", f"sqlite:///enterprise_rag.db"),
            "REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379")
        }
    
    def _init_monitoring_config(self):
        """初始化监控配置"""
        return {
            "METRICS_ENABLED": True,
            "TRACING_ENABLED": True,
            "ERROR_TRACKING_ENABLED": True
        }
    
    def _init_user_database(self):
        """初始化用户数据库"""
        return SQLiteUserManager()
    
    def _setup_security_schemes(self):
        """设置安全方案"""
        return {
            "bearerAuth": HTTPBearer(bearerFormat="JWT") if security_available else None
        }
    
    def _init_prometheus_metrics(self):
        """初始化Prometheus指标"""
        self.api_request_count = Counter(
            'api_requests_total',
            'Total API requests',
            ['method', 'endpoint', 'status_code', 'user_type']
        )
        
        self.api_request_duration = Histogram(
            'api_request_duration_seconds',
            'API request duration',
            ['method', 'endpoint']
        )
        
        self.active_users = Gauge(
            'active_users_total',
            'Currently active users'
        )
        
        self.system_memory_usage = Gauge(
            'system_memory_usage_mb',
            'System memory usage in MB'
        )
    
    def create_enterprise_app(self) -> FastAPI:
        """创建企业级FastAPI应用"""
        self.logger.info("🚀 开始创建企业级FastAPI应用")
        
        # 企业级应用配置
        app = FastAPI(
            title="🏭 LangChain Enterprise RAG API",
            description="""企业级LangChain RAG系统集成API
            
## 🎯 核心功能
- ✅ JWT认证与权限管理
- 🚀 异步处理与高并发优化  
- 📊 Prometheus指标监控
- 🏭 生产级API设计与最佳实践
- ✨ 企业级错误处理与日志系统

## 🔧 技术特性
- **异步处理**: Native async/await support
- **安全认证**: JWT tokens + Role-based access
- **性能监控**: Real-time metrics and health checks
- **生产就绪**: Production-grade configuration
- **可扩展**: Microservices-ready architecture
""",
            version="1.0.0",
            openapi_url="/api/v1/openapi.json",
            docs_url=None if os.getenv("ENVIRONMENT") == "production" else "/api/v1/docs",
            redoc_url=None if os.getenv("ENVIRONMENT") == "production" else "/api/v1/redoc",
        )
        
        # 添加安全方案到OpenAPI
        if security_available and self.security_schemes["bearerAuth"]:
            app.openapi = self._custom_openapi(app)
        
        # 添加企业级中间件
        self._add_enterprise_middlewares(app)
        
        # 初始化组件
        self._initialize_components(app)
        
        # 设置路由
        self._setup_enterprise_routes(app)
        
        # 添加事件处理器
        self._add_event_handlers(app)
        
        self.app = app
        return app
    
    def _custom_openapi(self, app: FastAPI):
        """自定义OpenAPI配置"""
        def custom_openapi():
            if app.openapi_schema:
                return app.openapi_schema
            
            openapi_schema = get_openapi(
                title=app.title,
                version=app.version,
                description=app.description,
                routes=app.routes,
            )
            
            # 添加安全方案
            if security_available:
                openapi_schema["components"]["securitySchemes"] = {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
                
                # 为所有路由添加安全要求
                for path_data in openapi_schema["paths"].values():
                    for operation in path_data.values():
                        if isinstance(operation, dict) and "operationId" in operation:
                            if operation["operationId"] not in ["health_check", "readiness_check", "login", "register"]:
                                operation["security"] = [{"BearerAuth": []}]
            
            app.openapi_schema = openapi_schema
            return app.openapi_schema
        return custom_openapi
    
    def _add_enterprise_middlewares(self, app: FastAPI):
        """添加企业级中间件"""
        self.logger.info("🛠 配置企业级中间件")
        
        # CORS配置 - 生产环境需要严格配置
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # 生产环境应该配置具体域名列表
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["X-Process-Time", "X-Rate-Limit-Remaining", "X-Rate-Limit-Reset"]
        )
        
        # Gzip压缩 - 减小响应体积
        app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Add custom enterprise middlewares
        app.middleware("http")(self._performance_monitoring_middleware)
        app.middleware("http")(self._security_middleware)
        app.middleware("http")(self._request_logging_middleware)
        app.middleware("http")(self._rate_limiting_middleware)
    
    async def _performance_monitoring_middleware(self, request: Request, call_next):
        """性能监控中间件"""
        start_time = time.time()
        
        # 记录请求开始
        request_id = str(uuid.uuid4())
        self.logger.info(f"[RID:{request_id}] 请求开始: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            
            # 计算响应时间
            process_time = time.time() - start_time
            
            # 记录性能指标
            await self._record_performance_metrics(request, response, process_time)
            
            # 添加响应头
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            self.logger.info(f"[RID:{request_id}] 请求完成: {process_time:.3f}s | 状态: {response.status_code}")
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            self.logger.error(f"[RID:{request_id}] 请求处理错误: {str(e)} | 时长: {process_time:.3f}s")
            
            # Return enterprise error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": request_id,
                    "message": "处理请求时发生内部错误",
                    "support": "请联系技术支持并提供Request ID"
                }
            )
    
    async def _security_middleware(self, request: Request, call_next):
        """安全中间件"""
        # 请求大小限制 - 防止DoS攻击
        if request.headers.get("content-length"):
            content_length = int(request.headers.get("content-length"))
            if content_length > 50 * 1024 * 1024:  # 50MB限制
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": "Payload too large",
                        "message": "请求实体超过了50MB的限制",
                        "max_size": "50MB",
                        "current_size": f"{content_length / 1024 / 1024:.2f}MB"
                    }
                )
        
        # 验证请求头安全
        user_agent = request.headers.get("user-agent", "")
        if "bot" in user_agent.lower() or "crawler" in user_agent.lower():
            self.logger.warning(f"潜在爬虫检测: {user_agent}")
        
        # 记录IP信息
        client_ip = request.client.host if request.client else "unknown"
        self.logger.info(f"安全监控: {request.method} {request.url.path} 来自IP: {client_ip}")
        
        response = await call_next(request)
        return response
    
    async def _request_logging_middleware(self, request: Request, call_next):
        """请求日志中间件"""
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        content_length = request.headers.get("content-length", "0")
        
        self.logger.info(f"**** 请求入站 ****")
        self.logger.info(f"方法: {request.method}")
        self.logger.info(f"路径: {request.url.path}")
        self.logger.info(f"客户端IP: {client_ip}")
        self.logger.info(f"用户代理: {user_agent}")
        self.logger.info(f"内容长度: {content_length}")
        
        response = await call_next(request)
        
        self.logger.info(f"**** 响应出站 ****")
        self.logger.info(f"状态码: {response.status_code}")
        
        return response
    
    async def _rate_limiting_middleware(self, request: Request, call_next):
        """限流中间件"""
        client_ip = request.client.host if request.client else "unknown"
        
        # 简单限流检查
        if self._should_rate_limit(client_ip):
            self.logger.warning(f"限流触发: IP {client_ip} 请求过于频繁")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests",
                    "message": "请求过于频繁，请稍后重试",
                    "retry_after": "60 seconds"
                },
                headers={"Retry-After": "60"}
            )
        
        response = await call_next(request)
        return response
    
    async def _record_performance_metrics(self, request: Request, response: Response, process_time: float):
        """记录性能指标"""
        if security_available and hasattr(self, 'api_request_count'):
            # 记录主要指标
            self.api_request_count.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                user_type=self._extract_user_type_from_request(request)
            ).inc()
            
            self.api_request_duration.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(process_time)
    
    def _should_rate_limit(self, client_ip: str) -> bool:
        """检查是否需要限流"""
        # 简化实现 - 实际应该使用Redis等专业方案
        return False
    
    def _extract_user_type_from_request(self, request: Request) -> str:
        """从请求中提取用户类型"""
        auth_header = request.headers.get("authorization", "")
        if auth_header and "bearer" in auth_header.lower():
            return "authenticated"
        return "anonymous"
    
    def _initialize_components(self, app: FastAPI):
        """初始化应用组件"""
        self.logger.info("🛠 初始化应用组件")
        
        # 初始化性能监控
        self._init_performance_monitoring(app)
        
        # 初始化数据库连接
        self._init_database_connections(app)
        
        # 初始化缓存连接
        self._init_cache_connections(app)
        
        # 初始化JWT认证组件
        self._init_jwt_components(app)
    
    def _init_jwt_components(self, app: FastAPI):
        """初始化JWT组件"""
        self.logger.info("🔐 初始化JWT认证组件")
        
        if security_available:
            self.security_bearer = HTTPBearer(auto_error=False)
        else:
            self.security_bearer = None
    
    async def _jwt_auth_dependency(self, credentials: HTTPAuthorizationCredentials = Depends(None)) -> User:
        """JWT认证依赖项"""
        if not security_available:
            # 如果安全组件不可用，返回模拟用户
            return User(username="guest", user_id="guest_001", roles=["guest"])
        
        if not credentials:
            return User(username="anonymous", user_id="anon_001", roles=["guest"])
        
        try:
            # 验证并解码JWT token
            payload = jwt.decode(
                credentials.credentials, 
                self.security_config["SECRET_KEY"],
                algorithms=[self.security_config["ALGORITHM"]]
            )
            
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid authentication credentials")
            
            # 获取用户信息
            user = self.user_db.get_user_by_id(user_id)
            if user is None or not user.is_active:
                raise HTTPException(status_code=401, detail="User not found or inactive")
            
            return user
            
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    def _init_performance_monitoring(self, app: FastAPI):
        """初始化性能监控"""
        self.logger.info("📊 初始化性能监控")
        pass
    
    def _init_database_connections(self, app: FastAPI):
        """初始化数据库连接"""
        self.logger.info("🗄 初始化数据库连接")
        pass
    
    def _init_cache_connections(self, app: FastAPI):
        """初始化缓存连接"""
        self.logger.info("⚡ 初始化缓存连接")
        pass
    
    def _setup_enterprise_routes(self, app: FastAPI):
        """设置企业级路由"""
        self.logger.info("🚀 设置企业级路由")
        
        # 健康检查端点
        @app.get("/api/v1/health", response_model=APIModels.HealthResponse)
        async def health_check():
            """应用健康检查"""
            return APIModels.HealthResponse(
                status="healthy",
                timestamp=datetime.now().isoformat(),
                version="1.0.0",
                service="LangChain Enterprise RAG API"
            )
        
        # 就绪性检查端点
        @app.get("/api/v1/ready")
        async def readiness_check():
            """应用就绪性检查"""
            checks = {"database": self._check_database_health(), 
                     "cache": self._check_cache_health()}
            
            overall_status = "ready" if all(checks.values()) else "not_ready"
            
            return {
                "status": overall_status,
                "timestamp": datetime.now().isoformat(),
                "checks": checks
            }
        
        # Prometheus指标端点
        @app.get("/api/v1/metrics")
        async def metrics():
            """Prometheus指标端点"""
            if security_available:
                return Response(generate_latest(), media_type="text/plain")
            return {"message": "监控已启用", "status": "basic_mode"}
        
        # 用户认证路由
        self._setup_auth_routes(app)
        
        # RAG服务路由
        self._setup_rag_routes(app)
        
        # 管理路由
        self._setup_admin_routes(app)
    
    def _check_database_health(self) -> bool:
        """检查数据库健康状况"""
        try:
            return self.user_db.check_health()
        except:
            return False
    
    def _check_cache_health(self) -> bool:
        """检查缓存健康状况"""
        # 简化实现
        return True
    
    def _setup_auth_routes(self, app: FastAPI):
        """设置认证路由"""
        
        @app.post("/api/v1/auth/register", response_model=APIModels.LoginResponse)
        async def register(user_data: APIModels.UserRegister):
            """用户注册"""
            self.logger.info(f"处理用户注册: {user_data.username}")
            
            # 检查用户名是否已存在
            if self.user_db.get_user_by_username(user_data.username):
                raise HTTPException(status_code=400, detail="用户名已存在")
            
            # 检查邮箱是否已存在
            if self.user_db.get_user_by_email(user_data.email):
                raise HTTPException(status_code=400, detail="邮箱已被使用")
            
            # 创建新用户
            new_user = User(
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                hashed_password=self._hash_password(user_data.password),
                roles=["user"]
            )
            
            # 保存用户
            self.user_db.create_user(new_user)
            
            # 创建JWT Token
            access_token = self._create_access_token(new_user)
            
            self.logger.info(f"用户 {new_user.username} 注册成功")
            
            return APIModels.LoginResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=self.security_config["ACCESS_TOKEN_EXPIRE_MINUTES"] * 60,
                user={
                    "user_id": new_user.user_id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "roles": new_user.roles
                }
            )
        
        @app.post("/api/v1/auth/login", response_model=APIModels.LoginResponse)
        async def login(credentials: APIModels.UserLogin):
            """用户登录"""
            self.logger.info(f"处理用户登录: {credentials.username}")
            
            # 验证用户凭据
            user = self.user_db.get_user_by_username(credentials.username)
            if not user or not self._verify_password(credentials.password, user.hashed_password):
                raise HTTPException(status_code=401, detail="用户名或密码错误")
            
            if not user.is_active:
                raise HTTPException(status_code=401, detail="用户账户已禁用")
            
            # 创建JWT Token
            access_token = self._create_access_token(user)
            
            self.logger.info(f"用户 {user.username} 登录成功")
            
            return APIModels.LoginResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=self.security_config["ACCESS_TOKEN_EXPIRE_MINUTES"] * 60,
                user={
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "roles": user.roles
                }
            )
        
        @app.post("/api/v1/auth/logout")
        async def logout(current_user: User = Depends(self._jwt_auth_dependency)):
            """用户登出"""
            self.logger.info(f"用户 {current_user.username} 登出")
            return {"message": "登出成功"}
        
        @app.get("/api/v1/auth/me")
        async def get_current_user_info(current_user: User = Depends(self._jwt_auth_dependency),
                                        current_user_dep: User = Depends(self._jwt_auth_dependency)):
            """获取当前用户信息"""
            return current_user.__dict__
        
        @app.post("/api/v1/auth/refresh")
        async def refresh_token(current_user: User = Depends(self._jwt_auth_dependency)):
            """刷新访问令牌"""
            self.logger.info(f"刷新用户 {current_user.username} 的访问令牌")
            
            new_token = self._create_access_token(current_user)
            
            return APIModels.LoginResponse(
                access_token=new_token,
                token_type="bearer", 
                expires_in=self.security_config["ACCESS_TOKEN_EXPIRE_MINUTES"] * 60,
                user={
                    "user_id": current_user.user_id,
                    "username": current_user.username,
                    "email": current_user.email,
                    "roles": current_user.roles
                }
            )
    
    def _hash_password(self, password: str) -> str:
        """密码哈希 - Simple hash for now to avoid bcrypt issues"""
        # 暂时使用SHA256以避免bcrypt问题，在生产环境应使用专业密码哈希
        safe_password = password[:64] if len(password) > 64 else password
        return hashlib.sha256(safe_password.encode()).hexdigest()
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码 - Simple verification"""
        # 暂时使用SHA256，在生产环境应使用专业密码验证
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
    
    def _create_access_token(self, user: User) -> str:
        """创建访问令牌"""
        if not security_available:
            return f"mock_token_{user.user_id}"
        
        expire_time = datetime.utcnow() + timedelta(minutes=self.security_config["ACCESS_TOKEN_EXPIRE_MINUTES"])
        
        payload = {
            "sub": user.user_id,
            "username": user.username,
            "email": user.email,
            "roles": user.roles,
            "exp": expire_time
        }
        
        return jwt.encode(payload, self.security_config["SECRET_KEY"], algorithm=self.security_config["ALGORITHM"])
    
    def _setup_rag_routes(self, app: FastAPI):
        """设置RAG服务路由"""
        
        @app.post("/api/v1/rag/query", response_model=APIModels.RAGResponse)
        async def process_rag_query(
            rag_query: APIModels.RAGQuery,
            background_tasks: BackgroundTasks,
            current_user: User = Depends(self._jwt_auth_dependency)
        ):
            """处理RAG查询请求"""
            self.logger.info(f"处理RAG查询请求，用户: {current_user.username}")
            
            start_time = time.time()
            
            # 验证用户权限
            if "user" not in current_user.roles and "admin" not in current_user.roles:
                raise HTTPException(status_code=403, detail="权限不足，需要用户角色")
            
            # 记录请求
            background_tasks.add_task(
                self._log_rag_request,
                user_id=current_user.user_id,
                query_data=rag_query.__dict__
            )
            
            try:
                # 模拟异步RAG处理
                self.logger.info(f"执行RAG查询: '{rag_query.query[:100]}...'")
                result = await self._process_rag_query_async(rag_query)
                
                process_time = time.time() - start_time
                
                self.logger.info(f"RAG查询完成，用时: {process_time:.3f}s")
                
                return APIModels.RAGResponse(
                    success=True,
                    data=result,
                    process_time=process_time
                )
                
            except Exception as e:
                self.logger.error(f"RAG查询处理错误: {str(e)}")
                raise HTTPException(status_code=500, detail="处理查询时发生错误")
        
        @app.post("/api/v1/rag/stream")
        async def stream_rag_query(
            rag_query: APIModels.RAGQuery,
            current_user: User = Depends(self._jwt_auth_dependency)
        ):
            """流式RAG查询"""
            self.logger.info(f"处理流式RAG查询，用户: {current_user.username}")
            
            async def stream_generator():
                """异步流式生成器"""
                try:
                    # 模拟流式处理
                    sentences = [
                        "正在分析您的问题...",
                        "从企业知识库检索相关信息...", 
                        "基于检索内容进行智能推理...",
                        "生成专业回答是..."
                    ]
                    
                    for i, sentence in enumerate(sentences):
                        yield f"data: {{\"message\": \"{sentence}\", \"sequence\": {i}}}\n\n"
                        await asyncio.sleep(0.5)
                    
                    # 最终回答
                    final_answer = await self._process_rag_query_async(rag_query)
                    yield f"data: {{\"message\": \"回答完成\", \"result\": {json.dumps(final_answer)}}}\n\n"
                    
                    yield "data: [DONE]\n\n"
                    
                except Exception as e:
                    yield f"data: {{\"error\": \"{str(e)}\", \"status\": \"error\"}}\n\n"
            
            return StreamingResponse(
                stream_generator(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive"
                }
            )
        
        @app.get("/api/v1/rag/query-history")
        async def get_query_history(
            limit: int = 10,
            current_user: User = Depends(self._jwt_auth_dependency)
        ):
            """获取查询历史"""
            return {
                "user_id": current_user.user_id,
                "username": current_user.username,
                "queries": self._get_mock_query_history(current_user.user_id)[-limit:]
            }
    
    def _get_mock_query_history(self, user_id: str) -> List[Dict]:
        """获取模拟查询历史"""
        import random
        import time
        
        mock_queries = [
            "什么是LangChain？",
            "RAG系统的工作原理？", 
            "如何选择向量数据库？",
            "HNSW和LSH有什么区别？",
            "通义千问在RAG中的表现如何？"
        ]
        
        history = []
        for i in range(5):
            history.append({
                "query": random.choice(mock_queries),
                "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                "response_time": random.uniform(0.5, 2.0),
                "status": "success"
            })
        
        return history
    
    async def _log_rag_request(self, user_id: str, query_data: dict):
        """异步记录RAG请求"""
        self.logger.info(f"异步记录RAG请求 - 用户: {user_id}, 查询: {query_data.get('query', '')[:50]}...")
    
    async def _process_rag_query_async(self, query_data: APIModels.RAGQuery) -> Dict[str, Any]:
        """异步处理RAG查询"""
        self.logger.info(f"模拟RAG处理: '{query_data.query}'")
        
        # 模拟异步处理延迟
        await asyncio.sleep(0.2)
        
        return {
            "query": query_data.query,
            "answer": f"这是对企业级RAG查询 '{query_data.query[:50]}...' 的专业回答。\n\n基于LangChain企业级知识库和系统设计最佳实践，我可以为您详细解释相关概念和技术实现。",
            "sources": [
                "企业知识库：LangChain官方文档",
                "技术文档：FastAPI企业级设计指南",
                "最佳实践：Prometheus监控集成方案"
            ],
            "confidence": 0.95,
            "process_time": 0.23,
            "sources_verified": True,
            "response_quality": "high",
            "enterprise_context": {
                "user_intent": "technical_inquiry",
                "domain": "enterprise_software",
                "complexity": "advanced"
            }
        }
    
    def _setup_admin_routes(self, app: FastAPI):
        """设置管理员路由"""
        
        def require_admin_role(current_user: User = Depends(self._jwt_auth_dependency)):
            """管理员角色验证"""
            if "admin" not in current_user.roles:
                raise HTTPException(status_code=403, detail="需要管理员权限")
            return current_user
        
        @app.get("/api/v1/admin/users")
        async def get_all_users(admin: User = Depends(require_admin_role)):
            """获取所有用户列表"""
            users = self.user_db.get_all_users()
            return {"users": [user.__dict__ for user in users]}
        
        @app.get("/api/v1/admin/system-stats")
        async def get_system_stats(admin: User = Depends(require_admin_role)):
            """获取系统统计信息"""
            return {
                "total_users": len(self.user_db.get_all_users()),
                "active_sessions": "模拟数据",
                "api_request_count_24h": "模拟数据",
                "average_response_time": "0.8s",
                "system_uptime": "99.9%"
            }
        
        @app.post("/api/v1/admin/users/{user_id}/disable")
        async def disable_user(user_id: str, admin: User = Depends(require_admin_role)):
            """禁用用户"""
            user = self.user_db.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="用户未找到")
            
            user.is_active = False
            return {"message": f"用户 {user.username} 已被禁用"}
    
    def _add_event_handlers(self, app: FastAPI):
        """添加事件处理器"""
        
        @app.on_event("startup")
        async def startup_event():
            self.logger.info("🚀 企业级FastAPI应用程序启动")
            
            # 系统启动检查
            self.logger.info("执行启动前系统检查")
            
            # 初始化用户数据
            self._initialize_demo_data()
            
            # 模拟异步启动任务
            await asyncio.sleep(0.1)
            
            self.logger.info("✅ 系统启动完成")
        
        @app.on_event("shutdown")
        async def shutdown_event():
            self.logger.info("🛑 企业级FastAPI应用程序关闭")
            
            # 执行关闭清理
            self.logger.info("执行关闭清理任务")
            await asyncio.sleep(0.1)  # 模拟清理延迟
            
            self.logger.info("✅ 系统关闭完成")
    
    def _initialize_demo_data(self):
        """初始化演示数据"""
        self.logger.info("🎯 初始化演示数据")
        
        # 创建演示用户
        demo_users = [
            {"username": "admin", "email": "admin@enterprise.com", "full_name": "Administrator", "roles": ["admin", "user"]},
            {"username": "demo_user", "email": "user@enterprise.com", "full_name": "Demo User", "roles": ["user"]},
            {"username": "guest", "email": "guest@enterprise.com", "full_name": "Guest User", "roles": ["guest"]}
        ]
        
        for user_data in demo_users:
            if not self.user_db.get_user_by_username(user_data["username"]):
                new_user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    hashed_password=self._hash_password("demo123"),
                    roles=user_data["roles"]
                )
                self.user_db.create_user(new_user)
                self.logger.info(f"创建演示用户: {new_user.username}")

class SQLiteUserManager:
    """SQLite用户管理器"""
    
    def __init__(self):
        self.db_path = "enterprise_users.db"
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT,
                    hashed_password TEXT NOT NULL,
                    roles TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ 用户数据库初始化成功")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
    
    def create_user(self, user: User) -> bool:
        """创建用户"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.user_id, user.username, user.email, user.full_name,
                user.hashed_password, json.dumps(user.roles),
                user.created_at.isoformat(), int(user.is_active)
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError as e:
            print(f"❌ 用户创建失败 - 重复用户名或邮箱: {e}")
            return False
        except Exception as e:
            print(f"❌ 用户创建失败: {e}")
            return False
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(
                    user_id=row[0],
                    username=row[1],
                    email=row[2],
                    full_name=row[3],
                    hashed_password=row[4],
                    roles=json.loads(row[5]),
                    created_at=datetime.fromisoformat(row[6]),
                    is_active=bool(row[7])
                )
            return None
            
        except Exception as e:
            print(f"❌ 用户查询失败: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """通过ID获取用户"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(
                    user_id=row[0],
                    username=row[1],
                    email=row[2],
                    full_name=row[3],
                    hashed_password=row[4],
                    roles=json.loads(row[5]),
                    created_at=datetime.fromisoformat(row[6]),
                    is_active=bool(row[7])
                )
            return None
            
        except Exception as e:
            print(f"❌ 用户查询失败: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(
                    user_id=row[0],
                    username=row[1],
                    email=row[2],
                    full_name=row[3],
                    hashed_password=row[4],
                    roles=json.loads(row[5]),
                    created_at=datetime.fromisoformat(row[6]),
                    is_active=bool(row[7])
                )
            return None
            
        except Exception as e:
            print(f"❌ 用户查询失败: {e}")
            return None
    
    def get_all_users(self) -> List[User]:
        """获取所有用户"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users')
            rows = cursor.fetchall()
            conn.close()
            
            users = []
            for row in rows:
                users.append(User(
                    user_id=row[0],
                    username=row[1],
                    email=row[2],
                    full_name=row[3],
                    hashed_password=row[4],
                    roles=json.loads(row[5]),
                    created_at=datetime.fromisoformat(row[6]),
                    is_active=bool(row[7])
                ))
            return users
            
        except Exception as e:
            print(f"❌ 获取用户列表失败: {e}")
            return []
    
    def check_health(self) -> bool:
        """检查数据库健康状态"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            conn.close()
            return result is not None
            
        except Exception as e:
            print(f"❌ 数据库健康检查失败: {e}")
            return False

def main():
    """主函数：运行企业级FastAPI应用"""
    print("🏭 LangChain L3 Advanced - Week 11: Enterprise FastAPI Architecture")
    print("=" * 70)
    print("🚀 开始构建企业级FastAPI应用程序架构")
    
    builder = EnterpriseFastAPIArchitecture()
    
    try:
        # 创建企业级应用
        app = builder.create_enterprise_app()
        
        print("\n✅ 企业级FastAPI应用创建完成！")
        print("\n📑 主要特性：")
        print("   🔐 JWT认证与权限系统")
        print("   🚀 异步高并发处理")    
        print("   📊 Prometheus监控  ")
        print("   🛡 企业级安全中间件")
        print("   🏭 生产级错误处理")
        print("\n🚀 启动应用：")
        print("   python 01_fastapi_enterprise_architecture.py")
        print("\n🔧 测试API端点：")
        print("   GET    /api/v1/health          - 健康检查")
        print("   POST   /api/v1/auth/register   - 用户注册")
        print("   POST   /api/v1/auth/login      - 用户登录")
        print("   POST   /api/v1/rag/query       - RAG查询")
        print("   GET    /api/v1/metrics         - 监控指标")
        
        # 如果直接运行，启动服务器
        if __name__ == "__main__":
           print(f"\n🌐 应用将在 http://0.0.0.0:8000 启动...")
           uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 应用创建被中断")
    except Exception as e:
        print(f"\n\n❌ 应用创建过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n💡 提示：请确保安装了所有必需的依赖包")

if __name__ == "__main__":
    main()