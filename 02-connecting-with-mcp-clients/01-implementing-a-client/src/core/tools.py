import json
from typing import Optional, Literal, List
from mcp.types import CallToolResult, Tool, TextContent, ContentBlock
from mcp_client import MCPClient
from openai.types.chat import ChatCompletionMessage
from openai.types.chat import ChatCompletionMessageToolCall


class ToolManager:
    @classmethod
    async def get_all_tools(cls, clients: dict[str, MCPClient]) -> list[Tool]:
        """Gets all tools from the provided clients."""
        tools = []
        for client in clients.values():
            tool_models = await client.list_tools()
            tools += tool_models
        return tools

    @classmethod
    async def _find_client_with_tool(
        cls, clients: list[MCPClient], tool_name: str
    ) -> Optional[MCPClient]:
        """Finds the first client that has the specified tool."""
        for client in clients:
            tools = await client.list_tools()
            tool = next((t for t in tools if t.name == tool_name), None)
            if tool:
                return client
        return None

    @classmethod
    async def execute_tool_requests(
        cls, clients: dict[str, MCPClient], message: ChatCompletionMessage
    ):
        """Executes a list of tool requests against the provided clients."""

        if not message.tool_calls:
            raise Exception(f"non-tool-calls message")

        out = []
        for v in message.tool_calls:
            if not isinstance(v, ChatCompletionMessageToolCall):
                raise Exception(f"Unexpected non-function tool call type: {v}")

            f = v.function

            content = await cls.execute_tool(clients, f.name, json.loads(f.arguments))

            msg = {"role": "tool", "content": content, "tool_call_id": v.id}

            out.append(msg)

        return out

    @classmethod
    async def execute_tool(
        cls, clients: dict[str, MCPClient], name: str, args: dict
    ) -> List[ContentBlock]:
        """Executes a tool request against the provided clients."""
        client = await cls._find_client_with_tool(list(clients.values()), name)
        if not client:
            raise ValueError(f"Could not find MCP client for tool '{name}'")

        response: CallToolResult | None = await client.call_tool(name, args)
        if not response:
            raise ValueError(f"Tool '{name}' returned no response")
        if response.isError:
            raise ValueError(f"Tool '{name}' returned an error: {response.content}")

        return response.content
