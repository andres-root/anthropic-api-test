from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import asyncio
import os
import json
from dotenv import load_dotenv
import anthropic
from models import ChatRequest, ChatResponse, ChatMessage, MessageRole

load_dotenv()

app = FastAPI(title="AioPy API", description="FastAPI application with Anthropic Claude integration")

# Initialize Anthropic client
anthroptic_client = anthropic.AsyncAnthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


@app.get("/")
async def root():
    """Root endpoint that returns a welcome message."""
    return {"message": "Welcome to AioPy FastAPI!"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "aiopy-api"}


@app.get("/async-demo")
async def async_demo():
    """Demonstrates async functionality similar to the existing examples."""
    
    async def task_one():
        await asyncio.sleep(1)
        return "Task one completed"
    
    async def task_two():
        await asyncio.sleep(2)
        return "Task two completed"
    
    # Run tasks concurrently
    results = await asyncio.gather(task_one(), task_two())
    
    return {
        "message": "Async tasks completed",
        "results": results,
        "total_tasks": len(results)
    }


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get user by ID - sample parametrized endpoint."""
    return {
        "user_id": user_id,
        "username": f"user_{user_id}",
        "active": True
    }


@app.post("/echo")
async def echo_data(data: Dict[str, Any]):
    """Echo back the received data."""
    return {
        "received": data,
        "timestamp": "2024-01-01T00:00:00Z",
        "echo": True
    }


@app.post("/chat/completions")
async def chat_completions(request: ChatRequest):
    """Create chat completions with Anthropic Claude."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
    
    try:
        # Convert messages to Anthropic format
        messages = []
        system_message = None
        
        for msg in request.messages:
            if msg.role == MessageRole.SYSTEM:
                system_message = msg.content
            else:
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        # Create the request parameters
        params = {
            "model": request.model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": messages
        }
        
        if system_message:
            params["system"] = system_message
            
        if request.stream:
            return StreamingResponse(
                stream_chat_response(params),
                media_type="text/plain"
            )
        else:
            # Non-streaming response
            response = await anthropic_client.messages.create(**params)
            return ChatResponse(
                role=MessageRole.ASSISTANT,
                content=response.content[0].text,
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Anthropic API: {str(e)}")


async def stream_chat_response(params):
    """Stream chat response from Anthropic API."""
    try:
        async with anthropic_client.messages.stream(**params) as stream:
            async for event in stream:
                if event.type == "content_block_delta":
                    if hasattr(event.delta, 'text'):
                        chunk = {
                            "type": "content_block_delta",
                            "content": event.delta.text
                        }
                        yield f"data: {json.dumps(chunk)}\n\n"
                        
                elif event.type == "message_start":
                    chunk = {
                        "type": "message_start",
                        "model": event.message.model
                    }
                    yield f"data: {json.dumps(chunk)}\n\n"
                    
                elif event.type == "message_stop":
                    chunk = {
                        "type": "message_stop"
                    }
                    yield f"data: {json.dumps(chunk)}\n\n"
                    
    except Exception as e:
        error_chunk = {
            "type": "error",
            "content": f"Error: {str(e)}"
        }
        yield f"data: {json.dumps(error_chunk)}\n\n"