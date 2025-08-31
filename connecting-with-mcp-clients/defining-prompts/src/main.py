import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp_client import MCPClient

from core.cli_chat import CliChat
from core.cli import CliApp
from core.llm import OpenAILike


async def main():
    load_dotenv()

    llm = OpenAILike()

    server_scripts = sys.argv[1:]
    clients = {}

    # command, args = (
    #     ("uv", ["run", "src/mcp_server.py"])
    #     if os.getenv("USE_UV", "0") == "1"
    #     else ("python", ["mcp_server.py"])
    # )
    command, args = ("uv", ["run", "src/mcp_server.py"])

    async with AsyncExitStack() as stack:
        doc_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )
        clients["doc_client"] = doc_client

        for i, server_script in enumerate(server_scripts):
            client_id = f"client_{i}_{server_script}"
            client = await stack.enter_async_context(
                MCPClient(command="uv", args=["run", server_script])
            )
            clients[client_id] = client

        chat = CliChat(
            doc_client=doc_client,
            clients=clients,
            llm=llm,
        )

        cli = CliApp(chat)
        await cli.initialize()
        await cli.run()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
