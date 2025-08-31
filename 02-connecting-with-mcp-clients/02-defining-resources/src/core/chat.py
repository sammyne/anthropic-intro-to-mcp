# from core.claude import Claude
from mcp_client import MCPClient
from core.tools import ToolManager
from mcp.types import TextContent

from core.llm import OpenAILike


class Chat:
    def __init__(self, llm: OpenAILike, clients: dict[str, MCPClient]):
        self.llm: OpenAILike = llm
        self.clients: dict[str, MCPClient] = clients
        # self.messages: list[MessageParam] = []
        self.messages = []

    async def _process_query(self, query: str):
        self.messages.append({"role": "user", "content": query})

    async def run(
        self,
        query: str,
    ) -> str:
        final_text_response = []

        await self._process_query(query)

        tools = await ToolManager.get_all_tools(self.clients)
        while True:
            response = self.llm.chat(messages=self.messages, tools=tools)

            self.llm.add_assistant_message(self.messages, response)
            if not response.tool_calls:
                final_text_response.append(response.content)
                break

            tool_results = await ToolManager.execute_tool_requests(
                self.clients, response
            )

            for v in tool_results:
                if isinstance(v, TextContent):
                    final_text_response.append(v.text)

            self.messages.extend(tool_results)

        return "\n".join(final_text_response)
