import os
from pyprojroot import here
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import List, Iterable
from langchain_ollama import ChatOllama
from accord.tts import TTS
from accord.utils import get_config
from accord.utils import remove_thinking_from_message
from accord.entity import (
    Role,
    Message,
    ChunkEvent,
    FinalAnswerEvent,
    State,
)

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
)


class Chatbot:
    def __init__(self):
        self.config = get_config(here("configs/config.yaml"))
        self.SYSTEM_PROMPT = self.config.llm.SYSTEM_PROMPT
        self.QUERY_TEMPLATE = self.config.llm.QUERY_TEMPLATE
        self.PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
            [
                ("system", self.SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", self.QUERY_TEMPLATE),
            ]
        )
        # Initialize the LLM
        self.llm = ChatOllama(
            model=self.config.llm.MODEL_NAME,
            temperature=self.config.llm.TEMPERATURE,
            keep_alive=-1,
            verbose=False,
        )

        self.workflow = self._create_workflow()
        self.tts = TTS()

    def _create_workflow(self) -> CompiledStateGraph:
        graph_builder = StateGraph(State)
        
        # Add a node for _generate
        graph_builder.add_node("generate", self._generate)
        
        # Define the starting edge
        graph_builder.add_edge(START, "generate")
        
        return graph_builder.compile()

    def _generate(self, state: State):
        messages = self.PROMPT_TEMPLATE.invoke(
            {
                "question": state["question"],
                "chat_history": state["chat_history"],
            }
        )
        answer = self.llm.invoke(messages)
        return {"answer": answer}

    def _ask_model(
        self, prompt: str, chat_history: List[Message]
    ) -> Iterable[ChunkEvent | FinalAnswerEvent]:
        history = [
            AIMessage(m.content) if m.role == Role.ASSISTANT else HumanMessage(m.content)
            for m in chat_history
        ]
        payload = {"question": prompt, "chat_history": history}

        config = {"configurable": {"thread_id": 42}}

        for event_type, event_data in self.workflow.stream(
            payload,
            config=config,
            stream_mode=["updates", "messages"],
        ):
            if event_type == "messages":
                chunk, _ = event_data
                yield ChunkEvent(chunk.content)
            if event_type == "updates":
                if "generate" in event_data:
                    answer = event_data["generate"]["answer"]
                    yield FinalAnswerEvent(answer.content)

    def ask(self, prompt: str, chat_history: List[Message]) -> Iterable[ChunkEvent | FinalAnswerEvent]:
        for event in self._ask_model(prompt, chat_history):
            yield event
            if isinstance(event, FinalAnswerEvent):
                response = remove_thinking_from_message("".join(event.content))
                self.tts.speak(response, filePath=self.config.tts.audio_file)
                self.tts.play_audio(self.config.tts.audio_file)
                os.remove(self.config.tts.audio_file)
                chat_history.append(Message(role=Role.USER, content=prompt))
                chat_history.append(Message(role=Role.ASSISTANT, content=response))

