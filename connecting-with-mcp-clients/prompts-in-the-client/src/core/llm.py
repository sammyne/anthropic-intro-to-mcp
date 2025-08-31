import os
from typing import List, Dict, Any
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage
from mcp.types import Tool


class OpenAILike:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No API key found. Please check your .env file.")

        base_url = os.getenv("OPENAI_API_BASE_URL")
        if not base_url:
            raise ValueError("No base URL found. Please check your .env file.")

        model = os.getenv("OPENAI_MODEL")
        if not model:
            raise ValueError("No model found. Please check your .env file.")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model: str = model

    def add_user_message(self, messages: list, message: str) -> None:
        messages.append({"role": "user", "content": message})

    def add_assistant_message(
        self, messages: list, message: str | ChatCompletionMessage
    ) -> None:
        match message:
            case str():
                messages.append({"role": "assistant", "content": message})
            case ChatCompletionMessage():
                messages.append(
                    {
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": message.tool_calls,
                    }
                )

    def chat(
        self,
        messages,
        system: str | None = None,
        temperature=1.0,
        stop_sequences=[],
        tools: List[Tool] | None = None,
    ) -> ChatCompletionMessage:
        """
        与模型进行聊天交互

        Args:
            messages: 消息历史列表
            system: 系统提示词（在OpenAI中作为系统消息处理）
            temperature: 生成随机性控制（0.0-2.0）
            stop_sequences: 停止序列（OpenAI中为stop参数）
            tools: 工具定义列表（用于函数调用）
            max_tokens: 最大生成token数
            stream: 是否使用流式输出

        Returns:
            ChatCompletionMessage: 模型回复的消息对象
        """

        if system:
            # 将系统消息插入到消息列表开头
            messages.insert(0, {"role": "system", "content": system})

        # 准备API调用参数
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1000,
            "stop": stop_sequences if stop_sequences else None,
        }


        if tools:
            params["tools"] = canonicalize_tools(tools)
            params["tool_choice"] = "auto"

        reply = self.client.chat.completions.create(**params)

        return reply.choices[0].message

    # def text_from_message(self, message: ChatCompletionMessage) -> str:
    #     return message.content


def canonicalize_tools(tools: List[Tool]) -> List[Dict[str, Any]]:
    """
    将 MCP 的 Tool 类型转化为 OpenAI 的 Tool 类型
    """
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            },
        }
        for tool in tools
    ]
