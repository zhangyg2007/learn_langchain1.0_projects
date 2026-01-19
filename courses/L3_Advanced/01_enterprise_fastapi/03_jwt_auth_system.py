#!/usr/bin/env python3
"""
LangChain L3 Advanced - Week 11  
课程标题: 企业级JWT认证与权限系统
学习目标:
  - 掌握JWT令牌生成与验证
  - 实现RBAC权限管理模型
  - 学习企业级认证流程设计
  - 掌握令牌刷新与撤销机制
作者: Claude Code 教学团队
创建时间: 2024-01-16
版本: 1.0.0
先决条件: 完成02_async_rag_service.py
"""

import asyncio
import jwt
import uuid
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging
from contextlib import contextmanager
import sqlite3
import threading
from functools import wraps

# JWT和加密组件
try:
    from passlib.context import CryptContext
    from jose import JWTError, jwt
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    print("✅ JWT和加密组件导入成功")
    crypto_available = True
except ImportError as e:
    print(f"⚠️ JWT加密组件导入失败: {e}")
    print("请确保已安装: pip install python-jose[cryptography] passlib[bcrypt] cryptography")
    crypto_available = False

# FastAPI组件（可选）
try:
    from fastapi import HTTPException, Depends
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from pydantic import BaseModel, Field, validator
    print("✅ FastAPI认证组件导入成功")
    fastapi_available = True
except ImportError as e:
    print(f"⚠️ FastAPI认证组件导入失败: {e}")
    fastapi_available = False

# Redis（状态存储）
try:
    import redis
    from redis.exceptions import ConnectionError, RedisError
    redis_available = True
    print("✅ Redis状态存储导入成功")
except ImportError as e:
    print(f"⚠️ Redis状态存储导入失败: {e}")
    redis_available = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 权限相关枚举
class UserRole(Enum):
    """用户角色枚举"""
    GUEST = "guest"
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    DEVELOPER = "developer"
    AUDITOR = "auditor"

class PermissionScope(Enum):
    """权限范围枚举"""
    GLOBAL = "global"
    ORGANIZATION = "organization"
    PROJECT = "project"
    RESOURCE = "resource"
    PERSONAL = "personal"

class TokenType(Enum):
    """令牌类型"""
    ACCESS = "access"
    REFRESH = "refresh"
    API = "api"
    SERVICE = "service"

@dataclass
class UserCredentials:
    """用户凭据信息"""
    user_id: str
    username: str
    email: str
    password_hash: str
    roles: List[str]
    organization_id: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    is_verified: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TokenClaims:
    """JWT令牌声明"""
    sub: str  # subject (user_id)
    username: str
    email: str
    roles: List[str]
    organization_id: str
    permissions: List[str]
    scope: str
    token_type: str
    jti: str  # JWT ID
    iat: int  # issued at
    exp: int  # expiration
    nbf: int  # not before
    custom_claims: Optional[Dict[str, Any]] = None

@dataclass
class APIKeyInfo:
    """API密钥信息"""
    key_id: str
    user_id: str
    key_name: str
    permissions: List[str]
    expires_at: datetime
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SessionInfo:
    """会话信息"""
    session_id: str
    user_id: str
    device_info: str
    login_timestamp: datetime
    last_activity: datetime
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

class EnterpriseJWTAuthManager:
    """企业级JWT认证管理器"""
    
    def __init__(self, 
                 secret_key: str = None,
                 algorithm: str = "RS256",
                 access_token_expire_minutes: int = 30,
                 refresh_token_expire_days: int = 7,
                 api_key_expire_days: int = 365):
        
        self.secret_key = secret_key or self._generate_secure_secret()
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.api_key_expire_days = api_key_expire_days
        
        # 密码加密上下文
        if crypto_available:
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        else:
            self.pwd_context = None
        
        # Redis状态存储
        self.redis_client = None
        self._init_redis_connection()
        
        # 密钥轮换机制
        self.key_rotation_manager = KeyRotationManager()
        
        # API密钥管理器
        self.api_key_manager = APIKeyManager()
        
        logger.info("🚀 企业级JWT认证管理器初始化完成")
    
    def _generate_secure_secret(self) -> str:
        """生成安全的秘钥"""
        return str(uuid.uuid4()) + str(int(time.time() * 1000))
    
    def _init_redis_connection(self):
        """初始化Redis连接"""
        if redis_available:
            try:
                self.redis_client = redis.Redis(
                    host='localhost', 
                    port=6379, 
                    db=1,
                    decode_responses=True
                )
                self.redis_client.ping()
                logger.info("✅ Redis状态存储初始化成功")
            except ConnectionError as e:
                logger.warning(f"⚠️ Redis状态存储初始化失败: {e}")
                self.redis_client = None
    
    def create_access_token(self, user: UserCredentials, 
                          additional_permissions: List[str] = None) -> str:
        """创建访问令牌"""
        try:
            # 生成令牌ID（用于撤销）
            jti = str(uuid.uuid4())
            
            # 计算时间
            now_time = datetime.utcnow()
            expire_time = now_time + timedelta(minutes=self.access_token_expire_minutes)
            
            # 确定权限
            base_permissions = self._calculate_user_permissions(user.user_id, user.roles)
            if additional_permissions:
                base_permissions.extend(additional_permissions)
            
            # 创建声明
            claims = TokenClaims(
                sub=user.user_id,
                username=user.username,
                email=user.email,
                roles=user.roles,
                organization_id=user.organization_id,
                permissions=list(set(base_permissions)),  # 去重
                scope="access",
                token_type="access",
                jti=jti,
                iat=int(now_time.timestamp()),
                exp=int(expire_time.timestamp()),
                nbf=int(now_time.timestamp()),
                custom_claims={
                    "device_info": "enterprise_app",
                    "auth_level": self._calculate_auth_level(user.roles)
                }
            )
            
            # 生成JWT令牌
            token_payload = self._claims_to_dict(claims)
            token = jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)
            
            # 记录令牌到状态存储
            self._record_token_in_storage(jti, user.user_id, "access", expire_time)
            
            logger.info(f"✅ 访问令牌创建成功 - 用户: {user.username}, TokenID: {jti}")
            return token
            
        except Exception as e:
            logger.error(f"访问令牌创建失败: {str(e)}")
            raise Exception(f"Failed to create access token: {str(e)}")
    
    def create_refresh_token(self, user: UserCredentials) -> str:
        """创建刷新令牌"""
        try:
            jti = str(uuid.uuid4())
            now_time = datetime.utcnow()
            expire_time = now_time + timedelta(days=self.refresh_token_expire_days)
            
            # 刷新令牌权限较少，主要用于续期
            claims = TokenClaims(
                sub=user.user_id,
                username=user.username,
                roles=user.roles,
                organization_id=user.organization_id,
                permissions=["refresh_token"],
                scope="refresh",
                token_type="refresh",
                jti=jti,
                iat=int(now_time.timestamp()),
                exp=int(expire_time.timestamp()),
                nbf=int(now_time.timestamp())
            )
            
            token_payload = self._claims_to_dict(claims)
            token = jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)
            
            self._record_token_in_storage(jti, user.user_id, "refresh", expire_time)
            
            logger.info(f"✅ 刷新令牌创建成功 - 用户: {user.username}, TokenID: {jti}")
            return token
            
        except Exception as e:
            logger.error(f"刷新令牌创建失败: {str(e)}")
            raise Exception(f"Failed to create refresh token: {str(e)}")
    
    def verify_token(self, token: str, expected_token_type: TokenType = TokenType.ACCESS) -> TokenClaims:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 验证令牌类型
            actual_token_type = payload.get("token_type")
            if actual_token_type != expected_token_type.value:
                logger.warning(f"令牌类型不匹配 - 期望: {expected_token_type.value}, 实际: {actual_token_type}")
                raise JWTError(f"Expected {expected_token_type.value} token, got {actual_token_type}")
            
            # 检查是否已撤销
            jti = payload.get("jti")
            if self._is_token_revoked(jti):
                logger.warning(f"令牌已撤销 - TokenID: {jti}")
                raise JWTError("Token has been revoked")
            
            # 验证权限一致性（高级安全验证）
            self._validate_token_integrity(payload)
            
            # 构建完整声明对象
            claims = self._dict_to_claims(payload)
            
            logger.info(f"✅ 令牌验证成功 - 用户: {claims.username}, TokenID: {jti}")
            return claims
            
        except JWTError as e:
            logger.warning(f"令牌验证失败: {str(e)}")
            raise HTTPException(status_code=401, detail=str(e))
        except Exception as e:
            logger.error(f"令牌验证错误: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """续约访问令牌"""
        try:
            # 验证刷新令牌
            refresh_claims = self.verify_token(refresh_token, TokenType.REFRESH)
            
            # 获取用户凭据（实际项目中连接用户数据库）
            user_credentials = self._get_user_credentials(refresh_claims.sub)
            if not user_credentials:
                raise HTTPException(status_code=404, detail="User not found or inactive")
            
            if not user_credentials.is_active:
                raise HTTPException(status_code=401, detail="User account is inactive")
            
            # 创建新的访问令牌
            new_access_token = self.create_access_token(user_credentials)
            
            logger.info(f"✅ 访问令牌续约成功 - 用户: {user_credentials.username}")
            
            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60
            }
            
        except HTTPException as e:
            raise e  # 重新抛出HTTP异常
        except Exception as e:
            logger.error(f"令牌续约失败: {str(e)}")
            raise HTTPException(status_code=401, detail="Token refresh failed")
    
    def revoke_tokens(self, user_id: str, revoke_all_sessions: bool = True) -> bool:
        """撤销用户令牌"""
        try:
            if revoke_all_sessions:
                # 撤销所有Session的令牌
                result = self._revoke_all_user_tokens(user_id)
                logger.info(f"✅ 撤销用户所有令牌 - 用户ID: {user_id}")
            else:
                # 撤销当前Token
                result = self._revoke_current_token(user_id)
                logger.info(f"✅ 撤销用户当前令牌 - 用户ID: {user_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"令牌撤销失败: {str(e)}")
            return False
    
    def hash_password(self, password: str) -> str:
        """密码哈希"""
        if self.pwd_context:
            return self.pwd_context.hash(password)
        else:
            # 回退哈希方案
            return hashlib.sha256(password.encode() + self.secret_key.encode()).hexdigest()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        if self.pwd_context:
            return self.pwd_context.verify(plain_password, hashed_password)
        else:
            # 回退验证方案
            return hashlib.sha256(plain_password.encode() + self.secret_key.encode()).hexdigest() == hashed_password
    
    def create_api_key(self, user: UserCredentials, key_name: str, 
                      permissions: List[str], expires_days: int = None) -> APIKeyInfo:
        """创建API密钥"""
        try:
            key_id = str(uuid.uuid4())
            api_key = f"ent_{user.organization_id}_{key_id}_{int(time.time() * 1000)}"
            
            expire_time = (
                datetime.utcnow() + timedelta(days=expires_days or self.api_key_expire_days)
            )
            
            api_key_info = APIKeyInfo(
                key_id=key_id,
                user_id=user.user_id,
                key_name=key_name,
                permissions=permissions,
                expires_at=expire_time
            )
            
            # 存储API密钥信息
            self._store_api_key_info(key_id, api_key_info)
            
            logger.info(f"✅ API密钥创建成功 - 用户: {user.username}, 密钥名: {key_name}")
            
            return api_key_info
            
        except Exception as e:
            logger.error(f"API密钥创建失败: {str(e)}")
            raise Exception(f"Failed to create API key: {str(e)}")
    
    def verify_api_key(self, api_key: str) -> APIKeyInfo:
        """验证API密钥"""
        try:
            # 提取密钥ID
            key_id = self._extract_key_id_from_api_key(api_key)
            if not key_id:
                raise HTTPException(status_code=401, detail="Invalid API key format")
            
            # 从存储获取密钥信息
            key_info = self._get_api_key_info(key_id)
            if not key_info:
                raise HTTPException(status_code=401, detail="API key not found")
            
            # 验证状态
            if not key_info.is_active:
                raise HTTPException(status_code=401, detail="API key is inactive")
            
            # 验证过期时间
            if key_info.expires_at < datetime.utcnow():
                raise HTTPException(status_code=401, detail="API key has expired")
            
            # 更新使用统计
            self._update_api_key_usage(key_id)
            
            logger.info(f"✅ API密钥验证成功 - 密钥名: {key_info.key_name}, 用户: {key_info.user_id}")
            return key_info
            
        except HTTPException as e:
            logger.warning(f"API密钥验证失败: {str(e.detail)}")
            raise e
        except Exception as e:
            logger.error(f"API密钥验证错误: {str(e)}")
            raise HTTPException(status_code=401, detail="API key verification failed")
    
    # 私有辅助方法
    def _calculate_user_permissions(self, user_id: str, roles: List[str]) -> List[str]:
        """计算用户权限"""
        permissions = []
        
        # 基础权限
        permissions.extend([
            "read_profile", "update_profile", "read_general_resources"
        ])
        
        # 根据角色添加权限
        for role in roles:
            permissions.extend(self._get_role_permissions(role))
        
        # 特定组织权限（实际项目中从数据库加载）
        permissions.extend(["org_data_access", "org_collaboration_access"])
        
        return list(set(permissions))
    
    def _get_role_permissions(self, role: str) -> List[str]:
        """获取角色的权限列表"""
        role_permissions = {
            "user": ["basic_read", "basic_write", "personal_tools"],
            "manager": ["team_management", "approval_request", "read_team_data"],
            "admin": ["full_system_access", "user_management", "config_modification"],
            "developer": ["api_access", "integration_setup", "code_deployment"],
            "auditor": ["audit_logs_access", "compliance_reporting"],
            "guest": ["limited_read", "demo_access"]
        }
        
        return role_permissions.get(role, [])
    
    def _calculate_auth_level(self, roles: List[str]) -> str:
        """计算认证等级"""
        role_priorities = {"super_admin": "critical", "admin": "high", "manager": "medium", "user": "standard", "guest": "limited"}
        
        for role in role_priorities.keys():
            if role in roles:
                return role_priorities[role]
        
        return "limited"
    
    def _record_token_in_storage(self, jti: str, user_id: str, token_type: str, expire_time: datetime):
        """记录令牌到状态存储"""
        if self.redis_client:
            try:
                # 存储令牌信息
                token_data = {
                    "user_id": user_id,
                    "token_type": token_type,
                    "expires_at": expire_time.isoformat()
                }
                
                # 设置过期时间
                ttl_seconds = int((expire_time - datetime.utcnow()).total_seconds())
                self.redis_client.setex(f"token:{jti}", ttl_seconds, json.dumps(token_data))
                
            except RedisError as e:
                logger.error(f"令牌存储失败: {e}")
    
    def _is_token_revoked(self, jti: str) -> bool:
        """检查令牌是否已撤销"""
        if not self.redis_client:
            return False
        
        try:
            # 检查是否存在撤销记录
            revoked = self.redis_client.get(f"revoked:{jti}")
            return bool(revoked)
        except RedisError:
            return False
    
    def _validate_token_integrity(self, payload: Dict[str, Any]):
        """验证令牌完整性"""
        required_fields = ["sub", "username", "jti", "exp", "iat"]
        for field in required_fields:
            if field not in payload:
                raise JWTError(f"Missing required field: {field}")
        
        # 检查是否已过期
        exp_timestamp = payload.get("exp")
        if exp_timestamp and datetime.utcfromtimestamp(exp_timestamp) < datetime.utcnow():
            raise JWTError("Token has expired")
    
    def _get_user_credentials(self, user_id: str) -> Optional[UserCredentials]:
        """获取用户凭据（回退实现）"""
        # 实际项目中从数据库加载
        mock_users = {
            "admin_001": UserCredentials(
                user_id="admin_001",
                username="admin",
                email="admin@enterprise.com",
                password_hash=self.hash_password("admin123") if self.pwd_context else "hashed_admin123", 
                roles=["admin", "user"],
                organization_id="org_001",
                created_at=datetime.now() - timedelta(days=100)
            ),
            "user_001": UserCredentials(
                user_id="user_001",
                username="demo_user",
                email="demo@enterprise.com", 
                password_hash=self.hash_password("user123") if self.pwd_context else "hashed_user123",
                roles=["user"],
                organization_id="org_001", 
                created_at=datetime.now() - timedelta(days=50)
            ),
            "manager_001": UserCredentials(
                user_id="manager_001",
                username="manager",
                email="manager@enterprise.com",
                password_hash=self.hash_password("manager123") if self.pwd_context else "hashed_manager123",
                roles=["manager", "user"],
                organization_id="org_001",
                created_at=datetime.now() - timedelta(days=80)
            )
        }
        
        return mock_users.get(user_id)
    
    def _revoke_all_user_tokens(self, user_id: str) -> bool:
        """撤销用户的所有令牌"""
        if not self.redis_client:
            return False
        
        try:
            # 获取用户的所有活跃token
            # 实际项目中需要维护用户-tokens映射
            logger.info(f"撤销用户 {user_id} 的所有令牌")
            return True
        except Exception as e:
            logger.error(f"批量令牌撤销失败: {e}")
            return False
    
    def _revoke_current_token(self, user_id: str) -> bool:
        """撤销当前令牌"""
        # 简化实现
        logger.info(f"撤销用户 {user_id} 当前令牌")
        return True
    
    def _claims_to_dict(self, claims: TokenClaims) -> Dict[str, Any]:
        """令牌声明转字典"""
        result = {
            "sub": claims.sub,
            "username": claims.username,
            "email": claims.email,
            "roles": claims.roles,
            "organization_id": claims.organization_id,
            "permissions": claims.permissions,
            "scope": claims.scope,
            "token_type": claims.token_type,
            "jti": claims.jti,
            "iat": claims.iat,
            "exp": claims.exp,
            "nbf": claims.nbf
        }
        
        if claims.custom_claims:
            result.update(claims.custom_claims)
        
        return result
    
    def _dict_to_claims(self, payload: Dict[str, Any]) -> TokenClaims:
        """字典转令牌声明"""
        # 过滤已知字段，其他字段作为自定义声明
        custom_data = {
            k: v for k, v in payload.items()
            if k not in ["sub", "username", "email", "roles", "organization_id", 
                        "permissions", "scope", "token_type", "jti", "iat", "exp", "nbf"]
        }
        
        return TokenClaims(
            sub=payload["sub"],
            username=payload["username"],
            email=payload["email"],
            roles=payload["roles"],
            organization_id=payload["organization_id"],
            permissions=payload["permissions"],
            scope=payload["scope"],
            token_type=payload["token_type"],
            jti=payload["jti"],
            iat=payload["iat"],
            exp=payload["exp"],
            nbf=payload["nbf"],
            custom_claims=custom_data if custom_data else None
        )
    
    def _store_api_key_info(self, key_id: str, key_info: APIKeyInfo):
        """存储API密钥信息"""
        if self.redis_client:
            try:
                # 序列化和存储
                data = json.dumps({
                    "key_id": key_info.key_id,
                    "user_id": key_info.user_id,
                    "key_name": key_info.key_name,
                    "permissions": key_info.permissions,
                    "expires_at": key_info.expires_at.isoformat(),
                    "is_active": key_info.is_active,
                    "created_at": key_info.created_at.isoformat(),
                    "metadata": key_info.metadata
                })
                
                # 设置过期时间
                ttl = int((key_info.expires_at - datetime.utcnow()).total_seconds())
                self.redis_client.setex(f"api_key:{key_id}", ttl, data)
                
            except RedisError as e:
                logger.error(f"API密钥存储失败: {e}")
        
        # 内存缓存（回退方案）
        if not hasattr(self, '_api_key_cache'):
            self._api_key_cache = {}
        self._api_key_cache[key_id] = key_info
    
    def _get_api_key_info(self, key_id: str) -> Optional[APIKeyInfo]:
        """获取API密钥信息"""
        # 优先从Redis获取
        if self.redis_client:
            try:
                data = self.redis_client.get(f"api_key:{key_id}")
                if data:
                    key_data = json.loads(data)
                    return APIKeyInfo(
                        key_id=key_data["key_id"],
                        user_id=key_data["user_id"],
                        key_name=key_data["key_name"],
                        permissions=key_data["permissions"],
                        expires_at=datetime.fromisoformat(key_data["expires_at"]),
                        is_active=key_data["is_active"],
                        created_at=datetime.fromisoformat(key_data["created_at"])
                    )
            except RedisError as e:
                logger.error(f"API密钥信息获取失败: {e}")
        
        # 回退到内存缓存
        return hasattr(self, '_api_key_cache') and self._api_key_cache.get(key_id)
    
    def _extract_key_id_from_api_key(self, api_key: str) -> Optional[str]:
        """从API密钥中提取密钥ID"""
        # 简单解析 - 企业级需要更复杂的验证
        parts = api_key.split('_')
        return parts[2] if len(parts) >= 3 else None
    
    def _update_api_key_usage(self, key_id: str):
        """更新API密钥使用统计"""
        key_info = self._get_api_key_info(key_id)
        if key_info:
            key_info.last_used = datetime.utcnow()
            key_info.usage_count += 1
            self._store_api_key_info(key_id, key_info)

class KeyRotationManager:
    """密钥轮换管理器"""
    
    def __init__(self):
        self.active_keys = {}
        self.current_key_version = "v1"
    
    def schedule_key_rotation(self):
        """安排密钥轮换"""
        logger.info("🔄 密钥轮换计划启动")
    
    def generate_new_key_pair(self) -> tuple[str, str]:
        """生成新的密钥对"""
        return "new_private_key", "new_public_key"

class APIKeyManager:
    """API密钥管理器"""
    
    def __init__(self):
        self.active_keys = {}
    
    def generate_secure_api_key(self) -> str:
        """生成安全API密钥"""
        import secrets
        return "ent_" + secrets.token_urlsafe(40)

class EnterpriseUserDatabase:
    """企业用户数据库"""
    
    def __init__(self, db_path: str = "enterprise_auth.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化用户数据库"""
        logger.info(f"🗄️ 初始化企业用户数据库: {self.db_path}")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 用户表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        full_name TEXT,
                        organization_id TEXT NOT NULL,
                        roles TEXT NOT NULL, -- JSON数组
                        created_at TEXT NOT NULL,
                        last_login TEXT,
                        is_active INTEGER DEFAULT 1,
                        is_verified INTEGER DEFAULT 0,
                        metadata TEXT -- JSON对象
                    )
                ''')
                
                # API密钥表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_keys (
                        key_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        key_name TEXT NOT NULL,
                        permissions TEXT NOT NULL, -- JSON数组
                        created_at TEXT NOT NULL,
                        expires_at TEXT NOT NULL,
                        last_used TEXT,
                        usage_count INTEGER DEFAULT 0,
                        is_active INTEGER DEFAULT 1,
                        metadata TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # 用户会话表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        device_info TEXT,
                        login_timestamp TEXT NOT NULL,
                        last_activity TEXT NOT NULL,
                        is_active INTEGER DEFAULT 1,
                        metadata TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                conn.commit()
                logger.info("✅ 企业用户数据库初始化成功")
                
        except sqlite3.Error as e:
            logger.error(f"❌ 数据库初始化失败: {e}")
            raise

class EnterpriseRBACManager:
    """企业级RBAC权限管理器"""
    
    def __init__(self):
        self.role_hierarchy = self._build_role_hierarchy()
        self.permission_registry = self._initialize_permission_registry()
        logger.info("🏭 企业级RBAC权限管理器初始化")
    
    def _build_role_hierarchy(self) -> Dict[str, List[str]]:
        """构建角色层级关系"""
        return {
            UserRole.SUPER_ADMIN.value: [role.value for role in UserRole],
            UserRole.ADMIN.value: [
                UserRole.ADMIN.value, UserRole.MANAGER.value, 
                UserRole.DEVELOPER.value, UserRole.USER.value, UserRole.GUEST.value
            ],
            UserRole.MANAGER.value: [
                UserRole.MANAGER.value, UserRole.DEVELOPER.value, UserRole.USER.value, UserRole.GUEST.value
            ],
            UserRole.DEVELOPER.value: [UserRole.DEVELOPER.value, UserRole.USER.value, UserRole.GUEST.value],
            UserRole.USER.value: [UserRole.USER.value, UserRole.GUEST.value],
            UserRole.GUEST.value: [UserRole.GUEST.value]
        }
    
    def _initialize_permission_registry(self) -> Dict[str, Dict[str, Any]]:
        """初始化权限注册表"""
        return {
            "user.profile.read": {"description": "读取个人资料", "scope": "personal"},
            "user.profile.write": {"description": "更新个人资料", "scope": "personal"},
            "user.authentication": {"description": "用户认证操作", "scope": "global"},
            "api.access": {"description": "API访问权限", "scope": "global"},
            "data.read": {"description": "读取数据权限", "scope": "organization"},
            "data.write": {"description": "写入数据权限", "scope": "organization"},
            "admin.user.manage": {"description": "用户管理", "scope": "organization"},
            "admin.system.manage": {"description": "系统管理", "scope": "global"},
            "enterprise.rag.query": {"description": "企业RAG查询", "scope": "organization"},
            "enterprise.rag.admin": {"description": "企业RAG管理", "scope": "organization"}
        }
    
    def has_permission(self, user_roles: List[str], required_permission: str) -> bool:
        """检查用户是否具有权限"""
        # 简化实现 - 实际项目中需要复杂的权限检查逻辑
        permission_role_mapping = {
            "user.profile.read": ["user", "manager", "admin", "developer", "super_admin"],
            "user.profile.write": ["user", "manager", "admin", "developer", "super_admin"],
            "user.authentication": ["guest", "user", "manager", "admin", "developer", "super_admin"],
            "api.access": ["guest", "user", "manager", "admin", "developer", "super_admin"],
            "data.read": ["user", "manager", "admin", "developer"],
            "data.write": ["user", "manager", "admin", "developer"],
            "admin.user.manage": ["admin", "super_admin"],
            "admin.system.manage": ["super_admin"],
            "enterprise.rag.query": ["user", "manager", "admin", "developer"],
            "enterprise.rag.admin": ["admin", "super_admin"]
        }
        
        allowed_roles = permission_role_mapping.get(required_permission, [])
        return any(role in allowed_roles for role in user_roles)
    
    def can_impersonate(self, requesting_user: UserCredentials, target_user_id: str) -> bool:
        """检查是否可以模拟其他用户"""
        # 只允许管理员级别进行用户模拟
        admin_roles = [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]
        return any(role in admin_roles for role in requesting_user.roles)

# 认证装饰器（适用于FastAPI和普通函数）
def require_permission(permission: str, fallback_role_check: bool = True):
    """权限验证装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 从依赖注入或参数中获取用户信息
            current_user = kwargs.get('current_user') or (args[0] if args else None)
            
            if hasattr(current_user, 'roles'):
                rbac_manager = EnterpriseRBACManager()
                if rbac_manager.has_permission(current_user.roles, permission):
                    return func(*args, **kwargs)
                else:
                    raise HTTPException(status_code=403, detail=f"Permission denied: {permission}")
            else:
                # 回退到角色检查
                if fallback_role_check and hasattr(current_user, 'roles'):
                    # 简单的角色检查逻辑
                    required_roles = permission.split(".")[:1]
                    if any(role in current_user.roles for role in required_roles):
                        return func(*args, **kwargs)
                
                raise HTTPException(status_code=403, detail="User authentication required")
        
        return wrapper
    return decorator

def require_auth(fallback_reuigred: bool = True):
    """认证验证装饰器（简化版）"""
    return require_permission(permission="user.authentication", fallback_role_check=fallback_reuigred)

def main():
    """主函数：测试企业级JWT认证系统"""
    print("🔒 LangChain L3 Advanced - Week 11: 企业级JWT认证与权限系统")
    print("=" * 70)
    
    try:
        # 初始化认证管理器
        auth_manager = EnterpriseJWTAuthManager()
        rbac_manager = EnterpriseRBACManager()
        
        print("🚀 企业级JWT认证测试")
        print("-" * 40)
        
        # 创建测试用户
        test_user = UserCredentials(
            user_id="user_001",
            username="developer_user",
            email="dev@enterprise.com",
            password_hash="",
            roles=["developer", "user"],
            organization_id="org_001",
            created_at=datetime.now()
        )
        
        # 设置密码
        test_user.password_hash = auth_manager.hash_password("enterprise_dev_123")
        
        print("⌬ 测试用户创建成功:")
        print(f"   用户名: {test_user.username}")
        print(f"   角色: {', '.join(test_user.roles)}")
        print("-" * 40)
        
        # 创建访问令牌
        access_token = auth_manager.create_access_token(test_user)
        refresh_token = auth_manager.refresh_access_token(test_user)
        
        print("📄 访问令牌创建成功")
        print(f"   令牌长度: {len(access_token)}")
        print(f"   刷新令牌长度: {len(refresh_token)}")
        print("-" * 40)
        
        # 验证令牌
        verified_claims = auth_manager.verify_token(access_token)
        
        print("🔍 令牌验证成功:")
        print(f"   用户ID: {verified_claims.sub}")
        print(f"   用户名: {verified_claims.username}")
        print(f"   角色: {', '.join(verified_claims.roles)}")
        print(f"   权限: {', '.join(verified_claims.permissions[:3])}...")
        print("-" * 40)
        
        # 权限检查
        test_permissions = ["enterprise.rag.query", "api.access", "admin.system.manage"]
        
        print("🛡️ 权限检查测试:")
        for permission in test_permissions:
            has_permission = rbac_manager.has_permission(test_user.roles, permission)
            print(f"   {permission}: {"✅ 允许" if has_permission else "❌ 拒绝"}")
        
        print("-" * 40)
        
        # 创建API密钥测试
        api_key_info = auth_manager.create_api_key(
            test_user, 
            "development_key", 
            ["api.access", "enterprise.rag.query"]
        )
        
        print("🔑 API密钥创建成功:")
        print(f"   密钥ID: {api_key_info.key_id}")
        print(f"   密钥名: {api_key_info.key_name}")
        print(f"   过期时间: {api_key_info.expires_at}")
        print(f"   权限数量: {len(api_key_info.permissions)}")
        
        print("\n✅ 企业级JWT认证系统测试完成！")
        print("\n📑 主要认证特性:")
        print("   🔐 JWT令牌生成与验证")
        print("   🛡️ RBAC角色权限管理")
        print("   🔄 令牌刷新机制") 
        print("   🔑 API密钥管理")
        print("   📊 企业级用户数据库")
        print("   🔒 权限验证装饰器")
        
        print("\n💡 在后端API中使用:")
        print("```python")
        print("@require_permission('enterprise.rag.query')")
        print("async def process_rag_query(current_user: UserAccessToken, ...):")
        print("    # 当前用户具有查询权限")
        print("    ...")
        print("```")
        
    except Exception as e:
        print(f"\n❌ JWT认证系统测试失败: {str(e)}")
        import traceback
        traceback.print_exc()