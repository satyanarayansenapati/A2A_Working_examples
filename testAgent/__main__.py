from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    AgentInterface
)

import uvicorn

from starlette.applications import Starlette

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes, create_rest_routes

from LangAgentExecutor import LangAgentExecutor


# agent capabilities
agent_capabilites = AgentCapabilities(streaming=False,
                      push_notifications=False,
                      extended_agent_card=False)

# agent skills
agent_skill = AgentSkill(
    id = "General Purpose",
    name = "General Purpose Agent",
    tags=["casual use","General purpose"],
    input_modes=["text","text/plain"],
    output_modes=["text","text/plain"]
)

# agent card
agent_card = AgentCard(
    name="General purpose llm",
    description=" This agennt answers general questions",
    version="1.0.0",
    capabilities=agent_capabilites,
    skills=[agent_skill],
    supported_interfaces= [AgentInterface(
        url="http://127.0.0.1:9999",
        protocol_binding="JSONRPC",
        protocol_version="1.0"
    )]
)

# task store
task_store = InMemoryTaskStore()
agent_executor = LangAgentExecutor()
request_handler = DefaultRequestHandler(
    agent_executor=agent_executor,
    task_store= task_store,
    agent_card=agent_card
    )


routes = []

# extend the route
routes.extend(create_agent_card_routes(agent_card=agent_card))
routes.extend(create_jsonrpc_routes(request_handler,"/"))
routes.extend(create_rest_routes(request_handler,"/rest"))


app = Starlette(routes=routes)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9999)