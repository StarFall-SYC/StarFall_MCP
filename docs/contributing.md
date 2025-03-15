# StarFall MCP 贡献指南

## 贡献流程

### 1. 准备工作

#### 1.1 环境配置
```bash
# 克隆项目
git clone https://github.com/StarFall/starfall-mcp.git
cd starfall-mcp

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

#### 1.2 分支管理
```bash
# 更新主分支
git checkout main
git pull origin main

# 创建功能分支
git checkout -b feature/your-feature-name
# 或创建修复分支
git checkout -b fix/your-fix-name
# 或创建文档分支
git checkout -b docs/your-docs-name
```

### 2. 开发规范

#### 2.1 代码风格
- 遵循 PEP 8 规范
- 使用 4 个空格缩进
- 行长度限制在 88 字符以内
- 使用类型注解
- 编写详细的文档字符串

#### 2.2 代码质量
```bash
# 格式化代码
black .

# 排序导入
isort .

# 代码质量检查
flake8

# 类型检查
mypy .
```

### 3. 提交规范

#### 3.1 提交信息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 3.2 类型说明
- feat：新功能
- fix：修复 Bug
- docs：文档更新
- style：代码格式（不影响代码运行的变动）
- refactor：重构（既不是新增功能，也不是修改 Bug 的代码变动）
- test：增加测试
- chore：构建过程或辅助工具的变动

#### 3.3 示例
```
feat(auth): 添加用户认证功能

- 实现用户注册和登录
- 添加 JWT 令牌认证
- 集成权限控制

Closes #123
```

### 4. 测试要求

#### 4.1 测试规范
- 所有新功能必须包含测试用例
- 所有 Bug 修复必须包含回归测试
- 测试覆盖率不得低于 80%

#### 4.2 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_auth.py

# 运行覆盖率测试
pytest --cov=starfall_mcp tests/
```

### 5. 提交 Pull Request

#### 5.1 准备工作
- 确保所有测试通过
- 更新文档（如有必要）
- 添加更新日志

#### 5.2 提交步骤
1. 推送分支到远程仓库
```bash
git push origin feature/your-feature-name
```

2. 创建 Pull Request
- 访问 GitHub 仓库页面
- 点击 "New Pull Request"
- 选择目标分支（通常是 develop）
- 填写 PR 描述

#### 5.3 PR 描述模板
```markdown
## 描述
简要描述你的改动

## 改动类型
- [ ] 新功能
- [ ] Bug 修复
- [ ] 文档更新
- [ ] 代码重构
- [ ] 其他

## 测试
- [ ] 单元测试
- [ ] 集成测试
- [ ] 手动测试

## 相关 Issue
- #123
```

### 6. Code Review

#### 6.1 Review 流程
1. 等待 Review 反馈
2. 根据反馈进行修改
3. 推送更新的代码
4. 重复直到 PR 被接受

#### 6.2 Review 要点
- 代码风格是否符合规范
- 是否包含适当的测试
- 文档是否完整
- 是否存在潜在问题

## 获取帮助

### 1. 文档资源
- [开发指南](docs/development.md)
- [API 文档](docs/api.md)
- [常见问题](docs/faq.md)

### 2. 社区支持
- 提交 [Issue](https://github.com/StarFall/starfall-mcp/issues)
- 加入开发者社区
- 参与技术讨论

### 3. 贡献者行为准则
- 尊重其他贡献者
- 保持专业和友善
- 遵循项目规范
- 积极参与讨论