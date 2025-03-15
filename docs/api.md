# StarFall MCP API 文档

## 概述

StarFall MCP 提供了一套完整的 RESTful API，用于执行系统操作、管理工作流和进行安全控制。通过这些 API，您可以轻松地将 StarFall MCP 集成到您的应用程序中，实现自动化操作和智能控制。

## 特性

- **RESTful 设计**：遵循 REST 架构风格，接口清晰直观
- **安全认证**：支持 JWT 令牌认证，确保 API 访问安全
- **错误处理**：统一的错误处理机制，详细的错误信息
- **限流控制**：内置请求限流机制，防止滥用
- **文档完备**：支持 OpenAPI 规范，提供 Swagger UI 接口文档

## 基础信息

### 基础 URL
```
http://localhost:8000
```

### 响应格式
所有 API 响应均使用 JSON 格式，并包含以下基础字段：
```json
{
    "success": true,      // 操作是否成功
    "data": {},          // 响应数据
    "error": null,       // 错误信息
    "message": ""       // 提示信息
}
```

### 错误处理
当发生错误时，API 会返回对应的 HTTP 状态码和错误信息：

#### 常见错误码

| 状态码 | 错误码 | 描述 |
|--------|---------|------|
| 400 | INVALID_REQUEST | 请求参数无效 |
| 401 | UNAUTHORIZED | 未授权或令牌过期 |
| 403 | FORBIDDEN | 权限不足 |
| 404 | NOT_FOUND | 资源不存在 |
| 429 | TOO_MANY_REQUESTS | 请求过于频繁 |
| 500 | INTERNAL_ERROR | 服务器内部错误 |

#### 错误响应示例
```json
{
    "success": false,
    "error": {
        "code": "INVALID_REQUEST",
        "message": "参数 'path' 不能为空",
        "details": {
            "field": "path",
            "reason": "required"
        }
    }
}
```

## 认证

### 获取访问令牌

```http
POST /token
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

**参数说明：**
- username：用户名
- password：密码

**响应示例：**
```json
{
    "success": true,
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer",
        "expires_in": 3600
    }
}
```

### 使用访问令牌
获取令牌后，在所有需要认证的 API 请求中添加以下 Header：
```
Authorization: Bearer <access_token>
```

## 工具 API

### 获取工具列表

```http
GET /tools
Authorization: Bearer <access_token>
```

**响应示例：**
```json
{
    "success": true,
    "data": [
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
                    "description": "文件路径",
                    "required": true
                },
                "content": {
                    "type": "string",
                    "description": "文件内容",
                    "required": true
                }
            }
        }
    ]
}
```

### 执行工具

```http
POST /tools/execute
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "file_create",
    "parameters": {
        "path": "test.txt",
        "content": "Hello, World!"
    }
}
```

**参数说明：**
- name：工具名称
- parameters：工具参数，具体参数根据工具定义而定

**响应示例：**
```json
{
    "success": true,
    "data": {
        "task_id": "task_12345",
        "status": "completed",
        "output": "文件 test.txt 创建成功"
    }
}
```

## 工作流 API

### 创建工作流

```http
POST /workflows
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "文件处理工作流",
    "description": "创建并处理文件的工作流",
    "steps": [
        {
            "tool": "file_create",
            "parameters": {
                "path": "test.txt",
                "content": "Hello"
            }
        },
        {
            "tool": "file_append",
            "parameters": {
                "path": "test.txt",
                "content": ", World!"
            }
        }
    ]
}
```

**参数说明：**
- name：工作流名称
- description：工作流描述
- steps：工作流步骤列表
  - tool：使用的工具名称
  - parameters：工具参数

**响应示例：**
```json
{
    "success": true,
    "data": {
        "workflow_id": "wf_12345",
        "status": "created"
    }
}
```

### 执行工作流

```http
POST /workflows/{workflow_id}/execute
Authorization: Bearer <access_token>
```

**响应示例：**
```json
{
    "success": true,
    "data": {
        "execution_id": "exec_12345",
        "status": "running"
    }
}
```

### 获取工作流执行状态

```http
GET /workflows/executions/{execution_id}
Authorization: Bearer <access_token>
```

**响应示例：**
```json
{
    "success": true,
    "data": {
        "execution_id": "exec_12345",
        "status": "completed",
        "steps": [
            {
                "tool": "file_create",
                "status": "completed",
                "output": "文件创建成功"
            },
            {
                "tool": "file_append",
                "status": "completed",
                "output": "文件内容追加成功"
            }
        ]
    }
}
```

## 错误码说明

| 错误码 | 描述 | HTTP 状态码 |
|--------|------|-------------|
| AUTH_FAILED | 认证失败 | 401 |
| INVALID_TOKEN | 无效的访问令牌 | 401 |
| TOKEN_EXPIRED | 访问令牌已过期 | 401 |
| PERMISSION_DENIED | 权限不足 | 403 |
| INVALID_PARAMS | 无效的参数 | 400 |
| TOOL_NOT_FOUND | 工具不存在 | 404 |
| WORKFLOW_NOT_FOUND | 工作流不存在 | 404 |
| EXECUTION_NOT_FOUND | 执行记录不存在 | 404 |
| INTERNAL_ERROR | 内部服务器错误 | 500 |