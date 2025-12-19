from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import random
import string
import json
from typing import Union, List, Optional
import time

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

class EmbeddingConfig(BaseModel):
    embedding_length: int = 1536  # 默认长度
    embedding_value: str = "random"  # zeros/ones/random/custom
    embedding_custom: Optional[List[float]] = None  # embedding_value=custom时生效
    response_delay: float = 0.0  # 响应延迟（秒）

class EmbeddingRequest(BaseModel):
    model: str
    input: Union[str, List[str]]
    user: Optional[str] = None
    config: Optional[EmbeddingConfig] = None

@app.post("/v1/embeddings")
async def embeddings(request: Request, body: EmbeddingRequest):
    config = body.config or EmbeddingConfig()
    # 延迟响应
    if config.response_delay > 0:
        await asyncio.sleep(config.response_delay)
    # 处理 input
    inputs = body.input if isinstance(body.input, list) else [body.input]
    data = []
    for idx, inp in enumerate(inputs):
        if config.embedding_value == "zeros":
            embedding = [0.0] * config.embedding_length
        elif config.embedding_value == "ones":
            embedding = [1.0] * config.embedding_length
        elif config.embedding_value == "custom" and config.embedding_custom:
            embedding = config.embedding_custom[:config.embedding_length]
            if len(embedding) < config.embedding_length:
                embedding += [0.0] * (config.embedding_length - len(embedding))
        else:  # random
            embedding = [random.uniform(-1, 1) for _ in range(config.embedding_length)]
        data.append({
            "object": "embedding",
            "index": idx,
            "embedding": embedding,
        })
    return {
        "object": "list",
        "data": data,
        "model": body.model,
        "usage": {
            "prompt_tokens": 0,
            "total_tokens": 0
        }
    }

class ImageGenerationConfig(BaseModel):
    base_url: str = "https://fake-image.example.com"  # 基础URL
    response_delay: float = 0.0  # 响应延迟（秒）

class ImageGenerationRequest(BaseModel):
    prompt: str
    model: Optional[str] = "dall-e-3"
    n: Optional[int] = 1
    quality: Optional[str] = "standard"
    response_format: Optional[str] = "url"
    size: Optional[str] = "1024x1024"
    style: Optional[str] = "vivid"
    user: Optional[str] = None
    config: Optional[ImageGenerationConfig] = None

@app.post("/v1/images/generations")
async def image_generations(request: Request, body: ImageGenerationRequest):
    config = body.config or ImageGenerationConfig()
    # 延迟响应
    if config.response_delay > 0:
        await asyncio.sleep(config.response_delay)

    # 生成假的图片URL
    created = int(time.time())
    data = []
    for i in range(body.n):
        # 生成随机ID作为图片URL的一部分
        image_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        url = f"{config.base_url}/images/{image_id}.png"

        if body.response_format == "b64_json":
            # 如果需要base64格式，返回一个假的base64字符串
            data.append({
                "b64_json": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            })
        else:
            # 默认返回URL格式
            data.append({
                "url": url
            })

    return {
        "created": created,
        "data": data
    } 