# Contributing to Learn LangChain 1.0 Projects

感谢您对本项目的兴趣！我们欢迎所有形式的贡献，包括错误修复、功能增强、文档改进和新的示例代码。

## 🚀 如何开始

1. Fork 这个仓库
2. 创建您的功能分支：`git checkout -b feature/your-feature-name`
3. 提交您的更改：`git commit -m 'Add some feature'`
4. 推送到分支：`git push origin feature/your-feature-name`
5. 提交 Pull Request

## 📋 贡献类型

### 💻 代码贡献
- 修复错误或改进现有代码
- 添加新的 LangChain 示例或教程
- 优化代码性能和可读性
- 添加单元测试和集成测试

### 📚 文档贡献
- 改进 README 文件
- 添加代码注释和文档字符串
- 创建新的教程或指南
- 翻译文档（中英文都可以）

### 🐛 Bug 报告
如果您发现了 bug，请创建 Issue 并包含以下信息：
- 问题的清晰描述
- 重现步骤
- 期望的行为
- 实际的行为
- 环境和版本信息

### 💡 功能建议
如果您有好的想法或建议：
- 检查是否已有类似的功能请求
- 创建新的 Issue 并标记为 "enhancement"
- 详细描述您的建议和用例

## 📝 开发指南

### 代码风格
- 使用 Python 的 PEP 8 编码规范
- 使用有意义的变量名和函数名
- 为复杂逻辑添加注释
- 保持代码的整洁和可读性

### 项目结构
```
learn_langchain1.0_projects/
├── 0X_topic/                    # 按主题分类的目录
│   ├── 01_basic_example/        # 基础示例
│   ├── 02_intermediate_example/ # 中等难度示例
│   └── 03_advanced_example/     # 高级示例
├── common/                      # 共享工具和工具类
└── utils/                       # 工具函数
```

### 示例代码要求
- 每个示例都要有清晰的注释说明
- 包含必要的错误处理
- 提供运行说明和环境要求
- 使用环境变量存储敏感信息（API keys 等）

### 环境设置
1. 克隆您的 fork
2. 创建虚拟环境：`python -m venv venv`
3. 激活虚拟环境：`source venv/bin/activate` (Linux/Mac) 或 `venv\Scripts\activate` (Windows)
4. 安装依赖：`pip install -r requirements.txt`
5. 设置环境变量：复制 `.env.example` 为 `.env` 并填入您的 API key

## 🔍 审核流程

1. **代码审查**: 维护者会审查代码质量和功能正确性
2. **测试验证**: 确保所有示例代码都能正常运行
3. **文档检查**: 验证文档是否清晰完整
4. **合并**: 通过审查后合并到主分支

## 🌟 贡献者名单

所有贡献者的名字将被添加到 README 的贡献者部分。

## 📞 联系和讨论

- 通过 GitHub Issues 进行技术讨论
- 对于大的改动建议，先创建 Issue 进行讨论
- 保持友好和专业的交流态度

## 🙏 致谢

感谢每一位贡献者对 LangChain 学习社区的支持！您的贡献将帮助更多人学习和掌握这个强大的框架。

---

**注意**: 本项目遵循 [MIT License](LICENSE)，提交贡献即表示您同意相应的许可条款。