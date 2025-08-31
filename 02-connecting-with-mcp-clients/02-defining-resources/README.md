# Implementing a Client

## 快速开始
```bash
uvx mcp dev src/mcp_server.py
```

## 注意事项
1. MCP 服务端的接口用 `@mcp.tool` 的 `description` 字段简单描述函数功能会导致 LLM 无法正确解析出函数调用依赖的参数，需要在
  doc string 部分添加出入参的说明。
