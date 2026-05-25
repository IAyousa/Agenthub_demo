from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import json
import asyncio

router = APIRouter()

@router.post("/chat/stream")
async def chat_stream(request: Request):
    data = await request.json()
    user_message = data.get("message")
    
    async def event_generator():
        yield json.dumps({"type": "msg_start", "role": "assistant"}) + "\n"
        await asyncio.sleep(1)
        response_text = f"I received your message: '{user_message}'..."
        for word in response_text.split():
            yield json.dumps({"type": "msg_chunk", "delta": word + " "}) + "\n"
            await asyncio.sleep(0.1)
        yield json.dumps({"type": "msg_end"}) + "\n"
        
    return StreamingResponse(event_generator(), media_type="application/x-ndjson")
