# SSH密钥完整设置指南

## 🔑 第一步：检查现有SSH密钥

```bash
# 检查是否已存在SSH密钥
ls -la ~/.ssh/

# 查看密钥列表
ssh-add -l
```

## 🔐 第二步：生成新的SSH密钥

如果还没有SSH密钥，生成一个新的：

```bash
# 生成Ed25519类型的SSH密钥
ssh-keygen -t ed25519 -C "zhangyg2007@163.com"

# 系统会提示输入保存位置，直接回车使用默认位置
# 可以设置密码保护（推荐）或留空
```

## 📋 第三步：添加SSH密钥到SSH代理

```bash
# 启动ssh-agent
eval "$(ssh-agent -s)"

# 添加私钥到ssh-agent
ssh-add ~/.ssh/id_ed25519
```

## 🔗 第四步：添加公钥到GitHub

1. **复制公钥内容：**
```bash
cat ~/.ssh/id_ed25519.pub
```

2. **登录GitHub添加SSH密钥：**
   - 打开 https://github.com
   - 点击右上角头像 → Settings
   - 左侧菜单 → SSH and GPG keys
   - 点击 "New SSH key"
   - Title: `Ubuntu Local Development`
   - Key: 粘贴刚才复制的公钥内容
   - 点击 "Add SSH key"

## ✅ 第五步：测试SSH连接

```bash
# 测试SSH连接到GitHub
ssh -T git@github.com

# 您应该看到类似消息：
# Hi zhangyg2007! You've successfully authenticated, but GitHub does not provide shell access.
```

## 🚀 第六步：推送代码

```bash
# 进入项目目录
cd /home/ubuntu/learn_langchain1.0_projects

# 确保远程仓库URL正确
git remote -v
# 应该显示：origin  git@github.com:zhangyg2007/learn_langchain1.0_projects.git

# 推送代码
export GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no"
git push -u origin main

# 推送标签
git push origin v0.1.0
```

## 🔧 备用方案：如果SSH仍然有问题

### 方法A: 使用HTTPS + 个人访问令牌
1. 在GitHub创建个人访问令牌
2. 使用HTTPS URL并输入令牌作为密码

### 方法B: 配置git使用特定SSH密钥
```bash
# 在 ~/.ssh/config 中添加：
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

## 🎯 验证成功

推送成功后访问：https://github.com/zhangyg2007/learn_langchain1.0_projects

您应该能看到所有8个文件已上传到您的GitHub仓库！

## 📞 有问题请告诉我

如果遇到任何步骤的卡住，请分享具体的错误信息，我来帮助解决！🚀