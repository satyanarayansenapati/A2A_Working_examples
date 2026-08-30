from a2a.client import (
    A2ACardResolver,
    ClientConfig,
    create_client,
)

from uuid import uuid4
from a2a.helpers import new_text_message
from a2a.types import Role, SendMessageRequest, AgentInterface

import httpx


async def main():
    async with httpx.AsyncClient(timeout=30.0) as httpx_client:
        from a2a.client import A2ACardResolver

        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url="http://127.0.0.1:9999",
        )
        agent_card = await resolver.get_agent_card()
        print("agent_card is fetched")

        # client config
        client_config = ClientConfig(streaming=False,
                     httpx_client=httpx_client)

        # client
        client = await create_client(agent=agent_card,
                                     client_config=client_config
                                     )

        # prepare a new message
        msg = new_text_message(text="Hello",
                               media_type="text",
                               role=Role.ROLE_USER
                               )

        request = SendMessageRequest(message=msg)

        async for response in client.send_message(request=request):
            print(response)

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
