from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import random
import string
import json

app = FastAPI()

# 配置项
default_config = {
    "first_token_delay": 0.5,  # 首token返回时间（秒）
    "stream_chunk_size_range": (5, 15),  # 每次流式返回的字符数范围
    "stream_interval_range": (0.1, 0.5),  # 每次流式返回之间的时间间隔范围（秒）
    "total_length_range": (30, 100),  # 每次请求总的返回字符数范围
}

class ChatCompletionRequest(BaseModel):
    model: str
    messages: list
    stream: bool = False
    config: dict = None

@app.post("/v1/chat/completions")
async def chat_completions(request: Request, body: ChatCompletionRequest):
    config = body.config or default_config
    if not body.stream:
        # 非流式直接返回假数据
        return {
            "id": "chatcmpl-fakeid",
            "object": "chat.completion",
            "created": 1234567890,
            "model": body.model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "这是一个假回复。"},
                    "finish_reason": "stop"
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20}
        }
    # 流式返回
    async def fake_stream():
        await asyncio.sleep(config["first_token_delay"])
        total_length = random.randint(*config["total_length_range"])
        sent = 0
        while sent < total_length:
            chunk_size = random.randint(*config["stream_chunk_size_range"])
            interval = random.uniform(*config["stream_interval_range"])
            chunk = ''.join(random.choices(string.ascii_letters + string.digits, k=chunk_size))
            data = {
                "id": "chatcmpl-fakeid",
                "object": "chat.completion.chunk",
                "created": 1234567890,
                "model": body.model,
                "choices": [
                    {
                        "delta": {"content": chunk},
                        "index": 0,
                        "finish_reason": None
                    }
                ]
            }
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            sent += chunk_size
            await asyncio.sleep(interval)
        # 结束信号
        yield "data: [DONE]\n\n"
    return StreamingResponse(fake_stream(), media_type="text/event-stream") 