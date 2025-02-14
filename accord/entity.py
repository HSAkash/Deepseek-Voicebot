from enum import Enum
from dataclasses import dataclass
from typing import List, TypedDict
from langchain.schema import Document
from langchain_core.messages import BaseMessage


class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class Message:
    role: Role
    content: str

@dataclass
class ChunkEvent:
    content: str


@dataclass
class FinalAnswerEvent:
    content: str


class State(TypedDict):
    question: str
    chat_history: List[BaseMessage]
    context: List[Document]
    answer: str