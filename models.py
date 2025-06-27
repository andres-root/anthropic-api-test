from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = Field(default="claude-3-5-sonnet-20241022", description="Claude model to use")
    max_tokens: Optional[int] = Field(default=1000, ge=1, le=4096, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=1.0, description="Sampling temperature")
    stream: Optional[bool] = Field(default=True, description="Whether to stream the response")


class ChatResponse(BaseModel):
    role: MessageRole
    content: str
    model: str
    usage: Optional[dict] = None


class StreamChunk(BaseModel):
    type: Literal["content_block_delta", "content_block_stop", "message_start", "message_delta", "message_stop"]
    content: Optional[str] = None
    model: Optional[str] = None
    usage: Optional[dict] = None