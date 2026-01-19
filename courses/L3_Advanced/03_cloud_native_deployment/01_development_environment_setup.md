# 🖥️ LangChain L3 Advanced 开发环境搭建指南

## 目标
完整的企业级LangChain开发环境搭建，支持跨平台（Ubuntu + Windows）开发"

---

## 🐧 Ubuntu 开发环境搭建 (推荐)

### 1. 系统要求
```bash
# Ubuntu 20.04 LTS 或更高版本
lsb_release -a

# 至少 8GB RAM, 20GB 可用存储空间
free -h
df -h
```

### 2. 基础依赖安装
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基本工具
sudo apt install -y \n  curl wget git build-essential \n  software-properties-common apt-transport-https \
  ca-certificates gnupg lsb-release
```

### 3. Python 环境管理
```bash
# 安装 Python 3.10+ 和 pip
sudo apt install -y python3 python3-pip python3-venv python3-dev

# 安装 pyenv（可选，多版本管理）
curl https://pyenv.run | bash

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc 
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# 重新加载 shell
exec $SHELL

# 安装最新 Python（示例）
pyenv install 3.12.0
pyenv global 3.12.0
```

### 4. Docker 和容器化环境
```bash
# 安装 Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 将用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker

# 安装 docker-compose
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K.*?(?=")')
sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 5. Kubernetes 和 Kubectl
```bash
# 安装 Kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
echo 'source <(kubectl completion bash)' >>~/.bashrc

# 安装 Minikube（本地开发）
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# 启动 Minikube
minikube start --driver=docker --memory=4096 --cpus=2
```

### 6. LangChain 相关工具
```bash
# 安装 LangChain CLI 和核心依赖
pip3 install --upgrade pip

# 安装 H2O GPT 和 Jupyter Lab（数据科学环境）
pip3 install h2o h2ogpt jupyterlab black flake8 mypy

# 安装 Redis（向量数据库）
sudo apt install -y redis-server
sudo systemctl enable redis-server

# 安装postgresql (向量扩展)
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable postgresql
```

### 7. AI模型依赖
```bash
# 安装 OpenAI SDK 和 LangChain
curl -sSL https://install.python-poetry.org | python3 - export
PATH="$HOME/.local/bin:$PATH"

# 为所有中国AI模型创建虚拟环境
python3 -m venv langchain_env
source langchain_env/bin/activate

# 安装核心依赖
pip install langchain langchain-community \
  openai deepseek-api torch transformers \
  pandas numpy scikit-learn

# 中国大模型依赖
pip install \
  tongyi zhipuai moonshot \
  dashscope baichuan

# AI工作流工具
pip install dify-client ragflow-client \
  flowise kubernetes

# 向量数据库
pip install \
  qdrant-client chromadb weaviate-client \
  pgvecto-rs
```

### 8. 开发环境初始化
```bash
# 创建项目目录
mkdir -p ~/langchain_workspace ~/projects
cd ~/langchain_workspace

# 克隆项目
git clone https://github.com/zhangyg2007/learn_langchain1.0_projects.git

# 安装项目依赖
cd learn_langchain1.0_projects
poetry install

# 配置环境变量（复制示例）
cp .env.chinese-models.example .env.chinese-models
nano .env.chinese-models  # 填入你的API密钥

# 运行测试验证
python -m pytest tests/ -v
```

---

## 🪟 Windows 开发环境搭建

### 1. 系统要求确认
```cmd
# Windows 10 版本 2004及以上，或 Windows 11
winver  # 查看Windows版本

# 启用 WSL2（推荐）
wsl --install -d Ubuntu  # 需要重启
```

### 2. 安装 Windows Subsystem for Linux (WSL 2)
```powershell
# 以管理员身份运行 PowerShell
# 启用 WSL 功能
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 安装 WSL Linux Kernel Update Package
# 从 https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi 下载并安装

# 设置 WSL2 为默认版本
wsl --set-default-version 2

# 安装 Ubuntu 20.04 LTS
wsl --install -d Ubuntu-20.04

# 在安装后的 WSL 终端完成上述 Ubuntu 手动安装步骤
```

### 3. 原生 Windows 环境（备选方案）

#### 安装 Python（推荐使用 Anaconda）
```cmd
# 下载并安装 Anaconda
# 从 https://www.anaconda.com/download 下载64位安装程序

# 或者使用 Winget（Windows 包管理器）
winget install -e --id Anaconda.Anaconda3

# 配置 conda 环境
create -n langchain python=3.10
activate langchain
```

#### 安装 Docker Desktop
```cmd
# 下载并安装 Docker Desktop
# 从 https://www.docker.com/products/docker-desktop 下载安装程序

# 或者使用 Winget
winget install -e --id Docker.DockerDesktop

# 启动 Docker Desktop 并完成安装向导
```

#### 安装 Kubernetes 工具
```powershell
# 安装 Minikube
choco install minikube  # 需要 Chocolatey
delete-code format@.bin\minikube.exe

# 下载并安装 kubectl
winget install -e --id Kubernetes.kubectl

# 启动本地集群
minikube start --driver=hyperv --memory=4096 --cpus=2  # Hyper-V驱动
```

#### PowerShell 开发环境配置
```powershell
# 设置执行策略（以管理员身份）
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 安装 PowerShell 模块
Install-Module -Name posh-git -Scope CurrentUser
Install-Module -Name docker-completion -Scope CurrentUser

# 配置 Git（如果已经安装）
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

git config --global init.defaultBranch main
git config --global pull.rebase false
```

### 4. Windows版 Redis 和数据库

#### Redis 安装
```cmd
# 下载 Redis for Windows
# https://github.com/microsoftarchive/redis/releases

# 或者使用 Chocolatey
choco install redis-64

# 启动 Redis 服务
net start Redis
```

#### PostgreSQL 安装
```cmd
# 下载 PostgreSQL for Windows
# https://www.postgresql.org/download/windows/

# 或者使用 Chocolatey  
choco install postgresql

# 启用向量扩展
"C:\Program Files\PostgreSQL\14\bin\psql.exe" -U postgres -d postgres
```

### 5. 项目克隆和初始化

#### 在 Windows 文件系统
```bash
# 使用 Git Bash 或 PowerShell
cd /c/Users/$USERNAME/langchain_workspace

# 克隆项目（如果在 WSL 中完成，可跳过）
git clone https://github.com/zhangyg2007/learn_langchain1.0_projects.git
cd learn_langchain1.0_projects

# 或者直接使用 WSL 路径访问\n# \\wsl$\Ubuntu\home\$USERNAME\langchain_workspace\learn_langchain1.0_projects
```

#### VS Code 配置（推荐）
```json
// settings.json
{
    "python.defaultInterpreterPath": "C:\\Users\\$USERNAME\\Anaconda3\\envs\\langchain\\python.exe",
    "jupyter.kernels.filter": [
        {
            "path": "C:\\Users\\$USERNAME\\Anaconda3\\envs\\langchain\\python.exe",
            "type": "pythonEnvironment"
        }
    ],
    "terminal.integrated.defaultProfile.windows": "PowerShell",
    "files.associations": {
        "*.ipynb": "jupyter-notebook"
    },
    "docker.enableDockerComposeLanguageService": true
}
```

---

## 🚀 推荐开发拓扑结构

### 跨平台开发方案
```
主机系统 (Windows 10/11)
├─ WSL2 Ubuntu 子系统（主要开发环境）
│  ├─ Docker Desktop (容器化)
│  ├─ Minikube (本地K8s集群)
│  ├─ Redis 集群
│  ├─ PostgreSQL + pgvector
│  ├─ LangChain 项目环境
│  └─ PyLab (Jupyter Lab)
├─ VS Code (跨平台IDE, 连接到 WSL 实例)  
├─ Windows Git 工具 (源码管理)
├─ Docker Desktop GUI (容器管理)  
└─ 浏览器/调试工具
```

### 开发工具推荐

#### IDE/编辑器
- **VS Code** (跨Windows+WSL, 插件丰富)
- **PyCharm** (Python专用, 企业级功能)
- **Jupyter Lab** (交互式开发和演示)

#### 容器化和虚拟化
- **Docker Desktop** (容器化开发和测试)  
- **Minikube** (本地Kubernetes集群)
- **Multipass** (轻量级虚拟机)

#### 数据库/存储
- **DBeaver** (数据库管理工具)
- **RedisInsight** (Redis GUI客户端)  
- **pgAdmin** (PostgreSQL GUI工具)

---

## ✅ 环境验证和常见问题

### 基本环境验证
```bash
# Ubuntu/WSL部分检查
python3 --version
docker --version
kubectl version --short
redis-server --version
minikube status

# LangChain项目检查
poetry --version
git status
ls requirements*.txt

# API密钥检查（手动验证）
cat .env.chinese-models  # 确认密钥已配置
```

### 常见问题和修复

#### WSL2 网络问题
```bash
# 如果WSL网络连接到Docker有困难
# 编辑 .wslconfig 文件
nano /mnt/c/Users/$USERNAME/.wslconfig

# 添加以下内容:
# [network]
# dnsTunneling=true
# firewall=true
# autoProxy=true
```

#### Node版本管理 (Windows)
```bash
# 安装 nvm for Windows
# https://github.com/coreybutler/nvm-windows/releases

# 管理Node.js版本
nvm list available
nvm install 18.18.0
nvm use 18.18.0
```

#### GPU支持（可选）
```bash
# 如果需要CUDA支持（高级用户）
# 安装 NVIDIA Container Toolkit (Linux/Windows)
sudo apt install nvidia-container-toolkit

# 配置Docker GPU访问
sudo systemctl restart docker

# 验证GPU支持
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

---

## 🗺️ 后续学习路径

至此，你已经完成了完整的企业级LangChain开发环境搭建。接下来可以：

1. **L1 基础课程** - 开始学习LangChain核心概念和基础实现
2. **L2 进阶课程** - 掌握中国AI大模型和复杂RAG系统设计  
3. **L3 企业级课程** - 构建生产级API和AI工作流平台
4. **L4 专家认证** - 获得企业级AI DevOps工程师认证

环境搭建好了，让我们开始真正的LangChain企业级开发之旅！ 🚀🇨🇳✨