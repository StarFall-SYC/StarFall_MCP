# StarFall MCP API 文档

## 概述

StarFall MCP 提供了一套完整的 RESTful API，用于执行系统操作、管理工作流和进行安全控制。所有 API 都需要进行身份验证，并使用 JWT 令牌进行授权。

## 认证

### 获取令牌

```http
POST /token
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

响应：
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
}
```

### 使用令牌

在后续请求中，在 Header 中添加：
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## 工具 API

### 列出工具

```http
GET /tools
Authorization: Bearer <token>
```

响应：
```json
[
    {
        "name": "file_create",
        "description": "创建新文件",
        "category": "file",
        "version": "1.0.0",
        "author": "StarFall",
        "risk_level": "low",
        "parameters": {
            "path": {
                "type": "string",
                "description": "文件路径"
            },
            "content": {
                "type": "string",
                "description": "文件内容"
            }
        }
    }
]
```

### 执行工具

```http
POST /tools/execute
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "file_create",
    "parameters": {
        "path": "test.txt",
        "content": "Hello, World!"
    }
}
```

响应：
```json
{
    "success": true,
    "output": "文件 test.txt 创建成功",
    "error": null
}
```

## 工作流 API

### 创建工作流

```http
POST /workflows
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "测试工作流",
    "description": "这是一个测试工作流",
    "steps": [
        {
            "tool": "file_create",
            "parameters": {
                "path": "test.txt",
                "content": "Hello, World!"
            }
        }
    ]
}
```

响应：
```json
{
    "id": "wf_1",
    "name": "测试工作流",
    "description": "这是一个测试工作流",
    "status": "pending",
    "steps": [
        {
            "tool": "file_create",
            "parameters": {
                "path": "test.txt",
                "content": "Hello, World!"
            },
            "status": "pending",
            "result": null,
            "error": null
        }
    ]
}
```

### 获取工作流

```http
GET /workflows/{workflow_id}
Authorization: Bearer <token>
```

响应：
```json
{
    "id": "wf_1",
    "name": "测试工作流",
    "description": "这是一个测试工作流",
    "status": "completed",
    "steps": [
        {
            "tool": "file_create",
            "parameters": {
                "path": "test.txt",
                "content": "Hello, World!"
            },
            "status": "completed",
            "result": {
                "success": true,
                "output": "文件 test.txt 创建成功"
            },
            "error": null
        }
    ]
}
```

### 列出工作流

```http
GET /workflows
Authorization: Bearer <token>
```

响应：
```json
[
    {
        "id": "wf_1",
        "name": "测试工作流",
        "description": "这是一个测试工作流",
        "status": "completed",
        "steps": [...]
    }
]
```

### 删除工作流

```http
DELETE /workflows/{workflow_id}
Authorization: Bearer <token>
```

响应：
```json
{
    "success": true
}
```

## 错误处理

所有 API 在发生错误时会返回适当的 HTTP 状态码和错误信息：

```json
{
    "detail": "错误信息描述"
}
```

常见状态码：
- 400：请求参数错误
- 401：未认证
- 403：权限不足
- 404：资源不存在
- 500：服务器内部错误

## 速率限制

API 请求限制：
- 认证用户：100 次/分钟
- 未认证用户：10 次/分钟

## 版本控制

当前 API 版本：v1

在请求头中可以指定 API 版本：
```
Accept: application/vnd.starfall-mcp.v1+json
```

## 安全说明

1. 所有 API 请求必须使用 HTTPS
2. 令牌有效期：30 分钟
3. 密码传输使用 bcrypt 加密
4. 敏感操作需要二次确认
5. 所有操作都会记录审计日志 