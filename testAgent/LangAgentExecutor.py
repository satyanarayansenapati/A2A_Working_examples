import logging

from typing import override

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.types import (
    UnsupportedOperationError,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    InternalError,
)
from a2a.helpers import new_text_message, new_task_from_user_message
from LangAgent import (
    GeneralPurposeLLM,
)


logger = logging.getLogger(__name__)

class LangAgentExecutor(AgentExecutor):

    def __init__(self):
        self.agent = GeneralPurposeLLM()
        #super().__init__(self.agent)

    @override
    async def execute(self, context: RequestContext, event_queue: EventQueue):

        # check if any message is present in the context or not
        if not context.message:
            raise ValueError("No message found in the context.")

        query = context.get_user_input()
        print("user query :", query)
        # check if task is present or not
        # if not present, create a new task
        if context.current_task:
            task = context.current_task
        else:
            task = new_task_from_user_message(context.message)
            # push the task to the queue
            await event_queue.enqueue_event(task)

        # update the status of the task
        task_update = TaskStatusUpdateEvent(task_id=task.id, 
                              context_id=context.context_id, 
                              status=TaskStatus(state=TaskState.TASK_STATE_WORKING),
                              )
        # add this into the event
        await event_queue.enqueue_event(task_update)

        # get the task done
        # invoke the llm with the query
        # get the query
        

        if not query:
            await event_queue.enqueue_event(event=TaskStatusUpdateEvent(task_id=task.id,
                                  context_id=context.context_id,
                                  status=TaskStatus(state=TaskState.TASK_STATE_REJECTED,
                                                    message=new_text_message(text="No query was found in the input text")
                                                    )))
            return

        # invoke llm with the query
        try:
            response = await self.agent.ainvoke(query=query,
                                     session_id=task.context_id)
        except Exception as e:
            raise InternalError(error=InternalError()) from e
        else:
            if response == None:
                await event_queue.enqueue_event(event=TaskStatusUpdateEvent(task_id=task.id,
                                  context_id=context.context_id,
                                  status=TaskStatus(state=TaskState.TASK_STATE_FAILED,
                                                    message=new_text_message(text="No response generated from the LLM")
                                                    )))
            else:                                        
                await event_queue.enqueue_event(event=TaskStatusUpdateEvent(task_id=task.id,
                                    context_id=context.context_id,
                                    status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED,
                                                        message=new_text_message(text=response)
                                                        )))            

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise InternalError(error=UnsupportedOperationError())