from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage
from pydantic import BaseModel
from langchain_core.runnables.config import RunnableConfig

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# response model
class ChatResponse(BaseModel):
    content : str

# a general purpose LLM
class GeneralPurposeLLM:
    def __init__(self):
        self.memory = MemorySaver()
        self.llm = ChatOllama(
            model='llama3.2:3b',
            temperature=0
            )

        # instruction 
        self.instruction = "You are a helpful assistant that provides accurate and concise information."

        # response instructions
        response_instructions = "Please provide your response in a clear and concise manner."

    async def ainvoke(self, query: str, session_id: str):

        # agent 
        agent = create_agent(
            model = self.llm,
            system_prompt = self.instruction,
            response_format = ChatResponse,
            checkpointer = self.memory,
            #response_format=ChatResponse
            )

        # config
        config : RunnableConfig = {'configurable': {'thread_id': session_id}}

        # user query
        user_query = {'messages': [('user', query)]}

        # invoke the agent and return only the generated answer
        await agent.ainvoke(user_query, config=config)

        # get the session state
        state = agent.get_state(config=config)

        # extract the messages
        messages = state.values.get("messages", [])

        result = state.values.get("structured_response")

        if isinstance(result, ChatResponse):
            return result.content

        return None
        # # get the AI message
        # for msg in reversed(messages):           
        #     if isinstance(msg, AIMessage):
        #         return msg.content
        #     else:
        #         return None      



if __name__ == "__main__":
    import asyncio

    # create an instance of the GeneralPurposeLLM
    llm = GeneralPurposeLLM()

    # define a sample query and session_id
    sample_query = "What is the capital of France?"
    session_id = "test_session_1"

    # run the async function
    response = asyncio.run(llm.ainvoke(sample_query, session_id))

    # print the response
    print(response)