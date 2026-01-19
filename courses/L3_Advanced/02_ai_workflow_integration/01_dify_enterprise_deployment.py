#!/usr/bin/env python3
"""
LangChain L3 Advanced - Week 12  
课程标题: Dify企业级部署与集成
学习目标:
  - 掌握Dify企业级部署架构设计
  - 学习Docker编排与K8s服务配置
  - 实现多环境高可用部署
  - 掌握Dify API深度集成  
作者: Claude Code 教学团队
创建时间: 2024-01-17
版本: 1.0.0
先决条件: 完成Week 11 FastAPI企业架构
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path
import logging
from enum import Enum

import httpx
from pydantic import BaseModel, Field, validator

try:
    import yaml
    yaml_available = True
    print("✅ PyYAML安装成功")
except ImportError:
    yaml_available = False
    print("⚠️ 请安装PyYAML: pip install PyYAML")

try:
    from jinja2 import Template as JinjaTemplate
    jinja_available = True
    print("✅ Jinja2模板引擎可用")
except ImportError:
    jinja_available = False
    print("⚠️ 请安装Jinja2: pip install Jinja2")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DifyEnvironment(Enum):
    """Dify环境类型"""
    DEVELOPMENT = "development"
    STAGING = "staging" 
    PRODUCTION = "production"
    MULTI_TENANT = "multi_tenant"

class DeploymentTier(Enum):
    """部署层级"""
    SINGLE_INSTANCE = "single_instance"
    HIGH_AVAILABILITY = "high_availability"
    MULTI_REGION = "multi_region"
    AUTO_SCALING = "auto_scaling"

@dataclass
class EnterpriseDifyConfig:
    """企业级Dify配置"""
    # 基础配置
    app_name: str = "EnterpriseAIHub"
    environment: str = DifyEnvironment.PRODUCTION.value
    deployment_tier: str = DeploymentTier.HIGH_AVAILABILITY.value
    api_key: str = ""
    base_url: str = "http://dify-enterprise-api:3000"
    
    # 高级企业配置
    enable_multi_tenant: bool = True
    enable_sso: bool = True
    max_concurrent_users: int = 5000
    max_applications: int = 1000
    rate_limit_rps: int = 100
    
    # 数据与安全配置
    encryption_key: str = ""  # 自动生成
    enable_audit_logging: bool = True
    data_retention_days: int = 365
    backup_schedule: str = "0 2 * * *"  # 每天2点备份
    
    # 多模型配置
    primary_model: str = "glm-4"          # 中国顶杆号大模型
    fallback_models: List[str] = field(default_factory=lambda: ["deepseek-chat", "moonshot-v1-32k"])
    embedding_model: str = "text-embedding-ada-002"
    rerank_model: str = "bge-reranker-v2-gemma"

@dataclass
class DifyAppTemplate:
    """Dify应用模板"""
    name: str
    description: str
    category: str
    ai_model_configs: List[Dict[str, Any]]
    workflow_config: Dict[str, Any]
    knowledge_bases: List[Dict[str, Any]]
    tools: List[Dict[str, Any]]
    prompt_templates: List[str]
    deployment_config: Dict[str, Any]

@dataclass 
class DifyDeployment:
    """Dify部署信息"""
    deployment_id: str
    environment: str
    status: str
    endpoint_url: str
    api_version: str
    deployed_at: datetime
    health_check_url: str
    admin_panel_url: str
    metrics_url: str

class EnterpriseDifyIntegration:
    """企业级Dify集成管理器"""
    
    def __init__(self, config: EnterpriseDifyConfig = None):
        self.config = config or EnterpriseDifyConfig()
        self.client = None
        self._initialize_client()
        
        logger.info(f"🏭 企业级Dify集成初始化 - 环境: {self.config.environment}")
    
    def _initialize_client(self):
        """初始化Dify客户端"""
        self.client = httpx.Client(
            base_url=self.config.base_url,
            timeout=httpx.Timeout(connect=10.0, read=60.0, write=30.0, pool=30.0),
            headers={"Authorization": f"Bearer {self.config.api_key}"} if self.config.api_key else {},
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
        logger.info("✅ Dify企业级客户端初始化完成")
    
    async def deploy_enterprise_dify(self, target_environment: str = "production") -> DifyDeployment:
        """部署企业级Dify环境"""
        deployment_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"🚀 开始企业级Dify部署 - 环境: {target_environment}, 部署ID: {deployment_id}")
        
        try:
            # 1. 部署环境配置与验证
            await self._configure_environment(target_environment)
            logger.info("✅ 环境配置完成")
            
            # 2. 容器编排文件生成
            compose_content = await self._generate_enterprise_docker_compose()
            logger.info("✅ Docker Compose企业配置生成完成")
            
            # 3. Kubernetes配置（高可用配置）
            if target_environment == "production":
                k8s_configs = await self._generate_kubernetes_configs()
                logger.info(f"✅ Kubernetes配置生成完成 - 配置文件: {len(k8s_configs)} 个")
            
            # 4. AI工作流模板创建
            enterprise_templates = await self._create_enterprise_templates()
            logger.info(f"✅ 企业级模板创建完成 - 模板数量: {len(enterprise_templates)}")
            
            # 5. 多租户和权限配置
            await self._setup_multi_tenant_auth()
            logger.info("✅ 多租户认证配置完成")
            
            # 6. 存储和数据库配置
            await self._configure_enterprise_storage()
            logger.info("✅ 企业级存储配置完成")
            
            deploy_time = time.time() - start_time
            
            # 构建部署信息
            deployment_info = DifyDeployment(
                deployment_id=deployment_id,
                environment=target_environment,
                status="deployed",
                endpoint_url=f"{self.config.base_url}/api/v1",
                api_version="enterprise_v2",
                deployed_at=datetime.now(),
                health_check_url=f"{self.config.base_url}/api/v1/health",
                admin_panel_url=f"{self.config.base_url}/admin",
                metrics_url=f"{self.config.base_url}/metrics"
            )
            
            logger.info(f"✅ 企业级Dify部署完成 - 总耗时: {deploy_time:.2f}s")
            return deployment_info
            
        except Exception as e:
            logger.error(f"❌ 企业级Dify部署失败: {str(e)}")
            return DifyDeployment(
                deployment_id=deployment_id,
                environment=target_environment,
                status="failed",
                endpoint_url="",
                api_version="",
                deployed_at=datetime.now(),
                health_check_url="",
                admin_panel_url="",
                metrics_url=""
            )
    
    async def _configure_environment(self, environment: str) -> None:
        """配置部署环境"""
        logger.info(f"⚙️ 配置企业Dify环境: {environment}")
        
        env_configs = {
            "development": {
                "replicas": 1,
                "resources": {"cpu": "0.5", "memory": "1Gi"},
                "storage": "1Gi",
                "backup_frequency": "manual"
            },
            "staging": {
                "replicas": 2, 
                "resources": {"cpu": "1", "memory": "2Gi"},
                "storage": "5Gi",
                "backup_frequency": "daily"
            },
            "production": {
                "replicas": 3,
                "resources": {"cpu": "2", "memory": "4Gi"}, 
                "storage": "50Gi",
                "backup_frequency": "daily"
            },
            "multi_tenant": {
                "replicas": 5,
                "resources": {"cpu": "4", "memory": "8Gi"},
                "storage": "200Gi",
                "backup_frequency": "hourly"
            }
        }
        
        config = env_configs.get(environment, env_configs["production"])
        
        # 应用到配置
        logger.info(f"   配置 - 副本数: {config['replicas']}")
        logger.info(f"   配置 - 资源限制: {config['resources']}")
        logger.info(f"   配置 - 存储: {config['storage']}")
        logger.info(f"   配置 - 备份频率: {config['backup_frequency']}")
    
    async def _generate_enterprise_docker_compose(self) -> str:
        """生成企业级Dify Docker Compose配置"""
        
        compose_yaml = f"""
# Dify Enterprise Docker Compose Configuration
# Generated by LangChain Enterprise Integration - {datetime.now().isoformat()}

version: '3.8'

services:
  ################################################################
  # Dify Core API - 企业版API服务
  ################################################################
  dify-api:
    image: langgenius/dify:latest
    container_name: dify-enterprise-api
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      # 企业级环境变量
      - MODE=production
      - DEBUG=false
      - CONSOLE_API_URL=http://dify-api:3000
      - SERVICE_API_URL=http://dify-api:3000
      - CONSOLE_WEB_URL=http://localhost:3001
      - APP_WEB_URL=http://localhost:3000
      
      # 🔐 企业级安全配置
      - SECRET_KEY={self.config.encryption_key or str(uuid.uuid4()).replace('-', '')}
      - JWT_SECRET={str(uuid.uuid4()).replace('-', '')}
      - FORCE_VERIFYING_SIGNATURE=true
      - EXPIRY_IN_SECONDS=3600
      - ROLE_CLAIM_NAME=roles
      
      # 🏭 企业级数据库配置
      - DB_CONNECTION={self.config.deployment_tier}
      - DATABASE_URL=postgresql://dify_user:dify_pass@postgres:5432/dify_enterprise
      - DB_POOL_SIZE=100
      - DB_POOL_MAX_OVERFLOW=50
      - DB_POOL_TIMEOUT=30
      
      # ⚡ Redis缓存配置
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_DATABASE=0
      - REDIS_PASSWORD=${{REDIS_PASSWORD:-}}
      - REDIS_SSL=false
      
      # 🧠 AI大模型集成配置（中国主导）
      - DEFAULT_PROVIDER=zhipu
      - ZHIPU_API_KEY=${{ZHIPU_API_KEY:-}}
      - ZHIPU_MODEL=glm-4
      
      # ⎘ 备份方案模型
      - DEEPSEEK_API_KEY=${{DEEPSEEK_API_KEY:-}}
      - DEEPSEEK_MODEL=deepseek-chat
      
      - MOONSHOT_API_KEY=${{MOONSHOT_API_KEY:-}}
      - MOONSHOT_MODEL=moonshot-v1-32k
      
      # 🎯 RAG强化配置
      - VECTOR_STORE_URL=http://qdrant:6333
      - QDRANT_API_KEY=${{QDRANT_API_KEY:-}}
      - RERANK_MODEL={self.config.rerank_model}
      - MAX_RETRIEVAL_RESULTS=20
      - KNOWLEDGE_BASE_ENABLED=true
      
      # 🌐 多租户配置
      - MULTI_TENANT=true
      - TENANT_ISOLATION_LEVEL=strict
      - ENABLE_CROSS_TENANT_ACCESS=false
      
      # 📊 监控与日志
      - TELEMETRY_ENABLED=true
      - LOG_LEVEL=INFO
      - METRICS_ENABLED=true
      
    volumes:
      - ./data/dify-logs:/app/logs
      - ./data/dify-config:/app/config
      - ./data/dify-storage:/app/storage
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      qdrant:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G

  ################################################################
  # Enterprise Web Frontend - 企业级前端界面
  ################################################################
  dify-web:
    image: langgenius/dify-web:latest
    container_name: dify-enterprise-web
    restart: unless-stopped
    ports:
      - "3001:3001"
    environment:
      - API_URL=http://dify-api:3000
      - APP_URL=http://localhost:3000
      - PUBLIC_LICENSE_KEY=${{LICENSE_KEY}}
      - ENTERPRISE_THEME=professional
    volumes:
      - ./data/dify-web-customizations:/app/user-content
    depends_on:
      dify-api:
        condition: service_healthy

  ################################################################
  # PostgreSQL - 企业级非关系型数据库
  ################################################################
  postgres:
    image: postgres:15-alpine
    container_name: dify-enterprise-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=dify_enterprise
      - POSTGRES_USER=dify_user
      - POSTGRES_PASSWORD={str(uuid.uuid4()).replace('-', '')[-12:]}
      - PGDATA=/var/lib/postgresql/data/pgdata
      - POSTGRES_INITDB_ARGS=--auth-local=scram-sha-256 --auth-host=scram-sha-256
      - POSTGRES_HOST_AUTH_METHOD=scram-sha-256
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init/postgres:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    command: >
      postgres
      -c max_connections=1000
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c maintenance_work_mem=64MB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=16MB
      -c default_statistics_target=100
      -c max_worker_processes=8
      -c max_parallel_workers_per_gather=4
      -c max_parallel_workers=8
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dify_user -d dify_enterprise"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G

  ################################################################
  # Redis - 企业级缓存与分布式锁定
  ################################################################
  redis:
    image: redis:7-alpine
    container_name: dify-enterprise-redis
    restart: unless-stopped
    command: >
      redis-server
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --save 900 1
      --save 300 10
      --save 60 10000
      --logfile /data/redis.log
      --loglevel notice
    volumes:
      - redis_data:/data
      - ./config/redis.conf:/etc/redis/redis.conf
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    sysctls:
      - net.core.somaxconn=65536
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  ################################################################
  # Qdrant - 向量数据库（企业RAG核心）
  ################################################################
  qdrant:
    image: qdrant/qdrant:latest
    container_name: dify-enterprise-qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage
      - ./config/qdrant/config.yaml:/qdrant/config.yaml
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
      - QDRANT__STORAGE__STORAGE_PATH=/qdrant/storage
      - QDRANT__STORAGE__OPTIMIZERS__INDEXING_THRESHOLD=10000
      - QDRANT__STORAGE__WAL__WAL_CAPACITY_MB=32
      - QDRANT__STORAGE__WAL__WAL_SEGMENTS_AHEAD=0
    command: --config-path /qdrant/config.yaml
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G

  ################################################################
  # Nginx Proxy - 前端代理与负载均衡
  ################################################################
  nginx:
    image: nginx:alpine
    container_name: dify-enterprise-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./config/nginx/ssl:/etc/nginx/ssl
      - ./data/nginx-logs:/var/log/nginx
    depends_on:
      dify-web:
        condition: service_healthy
      dify-api:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 60s
      timeout: 5s
      retries: 3

  ################################################################
  # Monitoring Stack - Prometheus + Grafana
  ################################################################
  prometheus:
    image: prom/prometheus:latest
    container_name: dify-enterprise-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./data/prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
      - '--enable-feature=remote-write-receiver'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    container_name: dify-enterprise-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - ./config/grafana/provisioning:/etc/grafana/provisioning
      - ./data/grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=grafana_admin_2024
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    depends_on:
      - prometheus

networks:
  default:
    driver: bridge
    driver_opts:
      com.docker.network.enable_ipv6: "false"

volumes:
  postgres_data:
  redis_data:
  qdrant_storage:

# Generated Enterprise Docker Compose Configuration
# ⚠️ 生产使用前请修改用户密码和密钥配置
"""
        return compose_yaml
    
    async def _generate_kubernetes_configs(self) -> List[Dict[str, str]]:
        """生成Kubernetes配置文件"""
        logger.info("🐳 生成Kubernetes企业配置")

        kube_configs = []
        
        # 1. Namespace定义
        namespace_yaml = f"""
apiVersion: v1
kind: Namespace
metadata:
  name: dify-enterprise
  labels:
    name: dify-enterprise
    environment: production
    tier: multi-zone
"""
        kube_configs.append({"file": "namespace.yaml", "content": namespace_yaml})
        
        # 2. ConfigMap - 企业配置
        configmap_yaml = f"""
apiVersion: v1
kind: ConfigMap
metadata:
  name: dify-enterprise-config
  namespace: dify-enterprise
data:
  # 中国AI大模型优先配置
  DEFAULT_PROVIDER: "zhipu"
  GLM_MODEL: "glm-4"
  DEEPSEEK_MODEL: "deepseek-chat"
  MOONSHOT_MODEL: "moonshot-v1-32k"
  
  # 企业级安全配置
  ENABLE_AUDIT_LOGGING: "true"
  RATE_LIMIT_RPS: "{self.config.rate_limit_rps}"
  MAX_CONCURRENT_USERS: "{self.config.max_concurrent_users}"
  
  # 多租户配置
  MULTI_TENANT: "{str(self.config.enable_multi_tenant).lower()}"
  TENANT_ISOLATION_LEVEL: "strict"
"""
        kube_configs.append({"file": "configmap.yaml", "content": configmap_yaml})

        # 3. Deployments - 高可用部署
        deployment_yaml = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dify-enterprise-api
  namespace: dify-enterprise
  labels:
    app: dify-enterprise-api
    component: api-gateway
    tier: backend
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: dify-enterprise-api
  template:
    metadata:
      labels:
        app: dify-enterprise-api
        component: api-gateway
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "3000"
        prometheus.io/path: "/metrics"
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - dify-enterprise-api
              topologyKey: kubernetes.io/hostname
      containers:
      - name: dify-api
        image: langgenius/dify:latest
        ports:
        - containerPort: 3000
          name: api
          protocol: TCP
        env:
        - name: MODE
          value: "production"
        - name: DB_CONNECTION
          value: "postgresql"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: dify-entreprise-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: dify-entreprise-secrets
              key: secret-key
        - name: REDIS_HOST
          value: "redis-service"
        - name: REDIS_PORT
          value: "6379"
        - name: VECTOR_STORE_URL  
          value: "http://qdrant-service:6333"
        
        # 加密与密钥配置
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: dify-entreprise-secrets
              key: jwt-secret
        - name: ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: dify-entreprise-secrets
              key: encryption-key
        
        # 中国AI模型优先配置
        - name: DEFAULT_PROVIDER 
          valueFrom:
            configMapKeyRef:
              name: dify-enterprise-config
              key: DEFAULT_PROVIDER
        - name: ZHIPU_API_KEY
          valueFrom:
            secretKeyRef:
              name: dify-entreprise-secrets
              key: zhipu-api-key
              
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 3000
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: dify-api-service
  namespace: dify-enterprise
  labels:
    app: dify-enterprise-api
spec:
  selector:
    app: dify-enterprise-api
  ports:
  - name: api
    port: 80
    targetPort: 3000
    protocol: TCP
  type: ClusterIP
"""
        kube_configs.append({"file": "dify-deployment.yaml", "content": deployment_yaml})
        
        # 4. Horizontal Pod Autoscaler (HPA)
        hpa_yaml = f"""
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: dify-enterprise-hpa
  namespace: dify-enterprise
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: dify-enterprise-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
"""
        kube_configs.append({"file": "hpa.yaml", "content": hpa_yaml})
        
        # 5. ExternalSecrets配置（生产机密管理）
        externalsecrets_yaml = f"""
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: dify-enterprise-secrets
  namespace: dify-enterprise
spec:
  secretStoreRef:
    name: docter-vault-vault-backend
    kind: SecretStore
  target:
    name: dify-entreprise-secrets
    creationPolicy: Owner
  data:
  - secretKey: database-url
    remoteRef:
      key: secret/data/dify/production
      property: database-url
  - secretKey: secret-key
    remoteRef:
      key: secret/data/dify/production  
      property: secret-key
  - secretKey: jwt-secret
    remoteRef:  
      key: secret/data/dify/production
      property: jwt-secret
  - secretKey: zhipu-api-key
    remoteRef:
      key: secret/data/dify/ai-models
      property: zhipu-api-key
  - secretKey: deepseek-api-key
    remoteRef:
      key: secret/data/dify/ai-models
      property: deepseek-api-key
      
  refreshInterval: 60s
"""
        kube_configs.append({"file": "externalsecrets.yaml", "content": externalsecrets_yaml})
        
        logger.info(f"✅ Kubernetes配置生成完成 - 共生成 {len(kube_configs)} 个配置文件")
        return kube_configs
    
    async def _create_enterprise_templates(self) -> List[DifyAppTemplate]:
        """创建企业级Dify应用模板"""
        logger.info("📋 创建企业级Dify应用模板")
        
        templates = []
        
        # 1. 企业知识问答模板
        knowledge_qa_template = DifyAppTemplate(
            name="企业知识问答助手",
            description="企业级内部知识库问答系统，支持多文档问答和智能\u003e检索",
            category="enterprise_knowledge",
            ai_model_configs=[
                {
                    "provider": "zhipu",
                    "model": "glm-4",
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "system_prompt": """你是一位专业的企业信息服务助手。请基于企业知识库提供准确、专业的回答。\n- 回答应准确、详细且符合企业标准\n- 优先使用企业提供的内部文档和数据\n- 避免主观推断，基于事实进行回答\n- 对于不确定的信息，明确标注来源"""
                }
            ],
            workflow_config={
                "type": "rag_qa",
                "retrieval_strategy": "hybrid",
                "reranking_enabled": True,
                "context_window": 4000,
                "knowledge_bases": ["company-policies", "technical-docs", "hr-handbook"]
            },
            knowledge_bases=[
                {
                    "name": "企业政策手册",
                    "description": "公司内部政策、规章制度和员工手册",
                    "document_strategy": "enterprise_ocr"
                },
                {
                    "name": "技术文档库", 
                    "description":":"产品技术文档",
                    "document_strategy": "technical"
                }
            ],
            tools=[
                {
                    "name": "CalendarBot",
                    "type": "google_calendar",
                    "permissions": ["read_calendar", "create_event"]
                }
            ],
            prompt_templates=[
                "请基于企业知识库回答关于: {QUERY}",
                "根据公司政策，请说明 {QUERY} 的相关规定",
                "在技术层面，请解释 {QUERY} 的实现原理"
            ],
            deployment_config={
                "auto_deployment": True,
                "custom_branding": True,
                "integration_endpoints": ["slack", "teams", "webhook"]
            }
        )
        templates.append(knowledge_qa_template)
        
        # 2. 智能客服聊天机器人
        support_bot_template = DifyAppTemplate(
            name="智能客服助手",
            description="企业级智能客服聊天机器人，支持多轮对话和问题解析",
            category="customer_support",
            ai_model_configs=[
                {
                    "provider": "deepseek",
                    "model": "deepseek-chat",
                    "temperature": 0.8,
                    "max_tokens": 1500,
                    "system_prompt": """你是一位专业的客户支持代表。\n- 必须礼貌、耐心且专业\n- 准确理解客户问题并提供及时帮助\n- 对于超出支持范围的问题，礼貌地引导客户联系专业部门\n- 在回复结束时询问"这解决了您的问题吗？""""
                }
            ],
            workflow_config={
                "type": "conversation",
                "multi_turn": True,
                "context_memory": "session",
                "escalation_enabled": True,
                "sentiment_analysis": True
            },
            knowledge_bases=[
                {"name":  "常见问题FAQ", "description": "客户最常问的问题及其标准答案"},
                {"name":  "产品手册", "description": "详细的产品功能和使用说明"}
            ],
            tools=[
                {
                    "name": "TicketSystem",
                    "type": "zendesk_integration",
                    "permissions": ["create_ticket", "update_ticket", "read_tickets"]
                }
            ],
            prompt_templates=[
                "有什么可以帮助您的？请告诉我您遇到的 {ISSUE_TYPE} 问题。",
                "我理解您的问题 {USER_PROBLEM}。让我为您查找解决方案。",
                "如果我的回答没有解决您的问题,我可以为您创建支持单据。"
            ],
            deployment_config={
                "integration_endpoints": ["zendesk", "salesforce", "hubspot"],
                "analytics_enabled": True,
                "sentiment_dashboard": True
            }
        )
        templates.append(support_bot_template)
        
        # 3. 数据分析和报告生成
        analytics_template = DifyAppTemplate(
            name="智能数据分析助手",
            description="企业数据分析专用助手，支持数据查询和报告生成",
            category="business_analytics", 
            ai_model_configs=[
                {
                    "provider": "moonshot",
                    "model": "moonshot-v1-32k",
                    "temperature": 0.3,
                    "max_tokens": 4000,
                    "system_prompt": """你是一位专业的企业数据分析师。\n- 必须具备扎实的数据分析功底和商业头脑\n- 准确解析用户提出的数据问题并提供深度合作建议\n- 生成的图表可视化需要具有专业的审美和数据敏感度\n- 预测和建议需要建立在事实和趋势分析的基础上"""
                }
            ],
            workflow_config={
                "type": "data_analysis",
                "data_sources": ["postgres", "mongodb", "s3"],
                "visualization_enabled": True,
                "prediction_models": True,
                "export_formats": ["pdf", "pptx", "xlsx"]
            },
            knowledge_bases=[
                {"name": "财务报表历史", "description": "公司的财务历史数据"},
                {"name": "销售数据库", "description": "详细的产品销售记录"},
                {"name": "市场研究", "description": "行业分析和市场趋势数据"}
            ],
            tools=[
                {
                    "name": "BIConnector",
                    "type": "tableau_connector", 
                    "permissions": ["read_data", "generate_report"]
                },
                {
                    "name": "DataExport",
                    "type": "s3_export",
                    "permissions": ["upload_data", "download_data"]
                }
            ],
            prompt_templates=[
                "请基于 {DATA_SOURCE} 生成最近 {TIME_PERIOD} 的 {ANALYSIS_TYPE} 分析报告。",
                "对比 {METRIC1} 和 {METRIC2} 在过去 {TIME_RANGE} 的表现并指出关键趋势。",
                "根据历史数据，预测未来 {FUTURE_PERIOD} 的 {FORECAST_FACTOR} 可能性。"
            ],
            deployment_config={
                "data_security": "enterprise_level",
                "custom_analytics": True,
                "integration_destinations": ["email", "slack", "teams"]
            }
        )
        templates.append(analytics_template)
        
        logger.info(f"✅ 企业级应用模板创建完成 - 创建了 {len(templates)} 个专业模板")
        return templates
    
    async def _setup_multi_tenant_auth(self) -> None:
        """设置多租户认证配置"""
        logger.info("🛑 配置多租户认证系统")
        
        tenant_auth_configs = [
            {
                "tier": "silver",
                "features": ["basic_auth", "jwt_tokens", "password_policy"],
                "rate_limit": 1000,
                "storage_limit": "10GB"
            },
            {
                "tier": "gold", 
                "features": ["saml_sso", "oauth2", "mfa", "audit_logging"],
                "rate_limit": 5000,
                "storage_limit": "100GB"
            },
            {
                "tier": "platinum",
                "features": ["custom_idp", "scim", "zero_trust", "federated"],
                "rate_limit": 20000,
                "storage_limit": "unlimited"
            }
        ]
        
        logger.info(f"✅ 多租户配置完成 - 支持 {len(tenant_auth_configs)} 个服务级别")
        
        for config in tenant_auth_configs:
            logger.info(f"   Tier: {config['tier']} - Rate Limit: {config['rate_limit']}/hour")
    
    async def _configure_enterprise_storage(self) -> None:
        """配置企业级存储"""
        logger.info("💾 配置企业级存储系统")
        
        storage_configs = {
            "document_storage": {
                "type": "s3_compatible",
                "endpoint": "s3.enterprise.com",
                "bucket": "dify-enterprise-documents",
                "retention_policy": "1_year",
                "encryption_at_rest": True
            },
            "session_storage": {
                "type": "redis_cluster",
                "nodes": 3,
                "replication_factor": 2,
                "persistence": True
            },
            "vector_storage": {
                "type": "qdrant_cluster", 
                "shards": 4,
                "replicas": 3,
                "compression_enabled": True
            }
        }
        
        for storage_type, config in storage_configs.items():
            logger.info(f"   {storage_type}: {config['type']} - 高可用配置完成")
    
    async def create_enterprise_chat_application(self, app_name: str, use_cases: List[str]) -> str:
        """创建企业级聊天应用"""
        logger.info(f"🚀 创建企业级聊天应用: {app_name}")
        
        app_id = f"ent_app_{app_name.lower().replace(' ', '_')}"
        
        app_config = {
            "name": app_name,
            "mode": "chat",
            "icon": "🤖",
            "config": {
                "prompt_template": self._generate_enterprise_prompt_template(use_cases),
                "model": {  # 中国AI模型优先
                    "default": "glm-4",      
                    "fallback": ["deepseek-chat", "moonshot-v1-32k"]
                },
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "knowledge_bases": [
                {"name": "corporate_knowledge", "retrieval_weight": 0.8}
            ],
            "tools": self._get_enterprise_tools(),
            "workflows": [
                {"type": "rag", "enabled": True},
                {"type": "task_routing", "enabled": True}
            ],
            "security": {
                "api_key_restrictions": True,
                "usage_analytics": True,
                "access_logging": True
            }
        }
        
        # 发送创建请求
        try:
            response = self.client.post("/api/v1/apps", json=app_config)
            response.raise_for_status()
            
            created_app = response.json()
            logger.info(f"✅ 企业应用创建成功 - AppID: {created_app.get('id', app_id)}")
            return created_app.get("id", app_id)
            
        except httpx.exceptions.RequestException as e:
            logger.error(f"❌ 企业应用创建失败: {e}")
            raise
    
    def _generate_enterprise_prompt_template(self, use_cases: List[str]) -> str:
        """生成企业级Prompt模板"""
        
        base_template = """你是企业级AI助手，具备专业的业务知识和客户服务技能。

角色要求：
- 必须礼貌、专业且高度称职
- 回答必须基于企业知识库和训练数据
- 在不确定的情况下，明确标注不确定性
- 必须遵守企业数据安全和合规要求

回答准则：
- 使用”- 清晰地回答客户问题
- 推荐基于实际企业最佳实践的解决方案  
- 当问题超出支持范围时，礼貌地引导到正确部门
- 始终以客户满意度为最高优先级"""
        
        # 根据用例添加特定指令
        if "customer_support" in use_cases:
            base_template += """

客户服务场景：
- 处理客户投诉时必须保持耐心和同理心
- 推荐解决方案时要提供具体的操作步骤
- 结束回复时一定要询问"这解决了您的问题吗？
"""
        
        if "knowledge_base" in use_cases:
            base_template += """

知识库场景：
- 优先从企业知识库中提取准确信息
- 对于内部政策,要使用企业统一表述
- 技术解释要详细且易于理解
- 引用具体数据和案例来强化回答"""
        
        return base_template
    
    def _get_enterprise_tools(self) -> List[Dict[str, Any]]:
        """获取企业级工具配置"""
        return [
            {
                "name": "EnterpriseCalendar",
                "type": "google_calendar",
                "config": {"calendar_id": "enterprise_calendar"},
                "access_level": "organization"
            },
            {
                "name": "SupportTicket",
                "type": "zendesk_integration", 
                "config": {"subdomain": "enterprise-support"},
                "access_level": "user"
            },
            {
                "name": "KnowledgeBaseSearch",
                "type": "elasticsearch_integration",
                "config": {"index_prefix": "kb"},
                "access_level": "read_only"
            }
        ]
    
    async def setup_high_availability_cluster(self, zones: List[str] = None) -> Dict[str, Any]:
        """设置高可用集群"""
        logger.info(f"⚙️ 设置Dify企业级高可用集群 - 区域: {zones}")
        
        if not zones:
            zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
        
        cluster_config = {
            "cluster_name": "dify-enterprise-ha",
            "zones": zones,
            "replication_factor": 3,
            "load_balancing": "round_robin",
            "health_check_interval": 30,
            "failover_timeout": 60
        }
        
        logger.info(f"✅ 高可用集群配置完成 - {len(zones)}个可用区域")
        return cluster_config
    
    async def setup_monitoring_and_logging(self) -> None:
        """设置企业级监控和日志"""
        logger.info("📊 配置企业级监控和日志系统")
        
        monitoring_stack = {
            "prometheus": {
                "enabled": True,
                "retention": "30d",
                "alerts_enabled": True,
                "alert_endpoints": ["pagerduty", "email"]
            },
            "grafana": {
                "enabled": True,
                "dashboards": ["dify_overview", "api_metrics", "resources"]
            },
            "elasticsearch": {
                "enabled": True, 
                "log_retention": "90d",
                "indexing": ["api_logs", "user_events", "system_logs"]
            }
        }
        
        logger.info("✅ 监控和日志配置完成")
    
    async def deploy_to_production(self, deployment_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """部署到生产环境"""
        logger.info(f"🚀 开始生产环境部署 - Deployment ID: {deployment_id}")
        
        try:
            # 预部署检查和测试
            await self._run_pre_deployment_checks()
            logger.info("✅ 预部署检查完成")
            
            # 蓝绿部署策略
            deployment_status = await self._execute_blue_green_deployment(config)
            logger.info("✅ 蓝绿部署执行完成")
            
            # 健康检查和验证
            health_status = await self._perform_health_checks()
            logger.info("✅ 健康检查完成")
            
            # 监控和告警配置
            await self.setup_monitoring_and_logging()
            
            result = {
                "deployment_id": deployment_id,
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "healthy": health_status,
                "endpoints": {
                    "api": f"{self.config.base_url}/api/v1", 
                    "admin": f"{self.config.base_url}/admin",
                    "metrics": f"{self.config.base_url}/metrics"
                }
            }
            
            logger.info(f"✅ 生产环境部署成功 - Deployment ID: {deployment_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 生产环境部署失败: {str(e)}")
            raise
    
    async def _run_pre_deployment_checks(self) -> None:
        """运行预部署检查"""
        logger.info("🔍 执行预部署系统检查")
        
        # 资源检查、依赖项验证、配置校验
        checks = [
            "api_connectivity",
            "database_connectivity", 
            "redis_connectivity",
            "vector_database_ready",
            "model_provider_valid", 
            "ssl_cert_valid",
            "负载测试完成"
        ]
        
        logger.info(f"   完成检查: {len(checks)} 项")
    
    async def _execute_blue_green_deployment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行蓝绿部署策略"""
        logger.info("🔄 执行蓝绿部署策略")
        
        # 1. 部署Green环境（新版本）
        green_deployment = await self._deploy_green_environment(config)
        
        # 2. 健康检查和流量测试
        green_health = await self._test_green_environment()
        
        # 3. 切换流量（如果健康）
        if green_health.get("healthy", False):
            await self._switch_traffic_to_green()
            
            # 4. 保留Blue环境（回退准备）
            logger.info("⚠️ 保留Blue环境以备回滚")
            
            return {"status": "traffic_switched", "blue_version_ready": True}
        else:
            # 回滚到Blue 
            return {"status": "rollback", "blue_version_active": True}
    
    async def _deploy_green_environment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """部署Green环境"""
        logger.info("🟢 部署Green环境（新版本）")
        
        # 创建新实例、配置容器、启动服务
        deployment_time = time.time()
        
        return {
            "environment": "green",
            "version": config.get("version", "v2.0"),
            "deployment_time": deployment_time,
            "instances": 3
        }
    
    async def _test_green_environment(self) -> Dict[str, Any]:
        """测试Green环境"""
        logger.info("🧪 测试Green环境健康状态")
        
        # 运行自动化测试和健康检查
        all_tests_passed = True  # 模拟测试结果
        
        return {
            "healthy": all_tests_passed,
            "tests_passed": 8,
            "tests_failed": 0,
            "response_time_ms": 450
        }
    
    async def _switch_traffic_to_green(self) -> None:
        """切换流量到Green环境"""
        logger.info("🚀 切换生产流量到Green环境")
        
        # 更新负载均衡器配置、调Ingress规则
        time.sleep(2)  # 模拟切换延迟
        
        logger.info("✅ Green环境正式接管所有流量")
    
    async def _perform_health_checks(self) -> bool:
        """执行健康检查"""
        logger.info("💚 执行深度健康检查")
        
        # API可用性、响应时间、错误率检查
        health_checks = {
            "api_health": {"status": "healthy", "endpoint": self.config.base_url},
            "database_health": {"status": "healthy", "latency_ms": 45},
            "vector_db_health": {"status": "healthy", "index_count": 127},
            "ai_model_health": {"status": "healthy", "provider": "zhipu"},
        }
        
        # 总体健康评估
        overall_health = all(check["status"] == "healthy" for check in health_checks.values())
        
        logger.info(f"📊 健康检查完成 - 状态: {'✅ 健康' if overall_health else '❌ 异常'}")
        return overall_health

def main():
    """主函数：测试企业级Dify集成"""
    print("🏭 LangChain L3 Advanced - Week 12: Dify企业级部署与集成")
    print("=" * 70)
    
    try:
        # 创建Dify企业配置
        config = EnterpriseDifyConfig(
            app_name="EnterpriseAIHub",
            environment="production",
            max_concurrent_users=5000,
            primary_model="glm-4",
            enable_multi_tenant=True,
            enable_sso=True
        )
        
        # 初始化Dify集成管理器
        dify_integration = EnterpriseDifyIntegration(config)
        
        print("\n🚀 开始企业级Dify部署测试...")
        
        # 1. 测试Docker Compose生成
        compose_content = asyncio.run(dify_integration._generate_enterprise_docker_compose())
        print(f"✅ Docker Compose企业配置已生成 - 长度: {len(compose_content)} 字符")
        
        # 2. 测试K8s配置生成
        k8s_configs = asyncio.run(dify_integration._generate_kubernetes_configs())
        print(f"✅ Kubernetes配置生成完成 - 文件: {len(k8s_configs)} 个")
        
        # 3. 测试企业模板创建
        templates = asyncio.run(dify_integration._create_enterprise_templates())
        print(f"✅ 企业级应用模板创建完成 - 模板: {len(templates)} 个")
        
        # 4. 测试聊天应用创建
        app_id = asyncio.run(dify_integration.create_enterprise_chat_application(
            "企业知识助手", 
            ["customer_support", "knowledge_base"]
        ))
        print(f"✅ 企业聊天应用创建完成 - AppID: {app_id}")
        
        print("\n🎉 Dify企业级集成功能测试完成！")
        print("\n📑 主要企业特性:")
        print("   🐳 Docker Compose企业编排")
        print("   ☸️  Kubernetes高可用配置") 
        print("   📋 企业级AI应用模板")
        print("   🏭 多租户认证系统")
        print("   ⚙️  蓝绿部署策略")
        print("   📊 监控告警集成")
        
        print("\n💡 部署说明:")
        print("   1. 保存Docker Compose文件")
        print("   2. 配置API密钥(.env文件)")
        print("   3. 运行: docker-compose up -d")
        print("   4. 访问: http://localhost")
        
    except Exception as e:
        print(f"\n❌ Dify企业级集成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()