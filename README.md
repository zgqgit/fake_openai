# fake_openai

本项目用于模拟 OpenAI 标准的模型服务接口，支持 /v1/chat/completions，返回假数据，支持流式和非流式模式。

## 依赖
- fastapi
- uvicorn
- pydantic

## 启动方法
```bash
source venv/bin/activate
uvicorn main:app --reload
```

## 配置项
- `first_token_delay`：首token返回时间（秒）
- `stream_chunk_size_range`：每次流式返回的随机字符数范围（元组）
- `stream_interval_range`：每次流式返回之间的时间间隔范围（秒，元组）
- `total_length_range`：每次请求总的返回字符数范围（元组）

## 首次部署流程

1. **准备项目代码**
   - 若已在 `~/works/fake_openai` 目录下有 main.py、requirements.txt 等文件，可跳过此步。
   - 否则可用如下命令：
     ```bash
     git clone <your_repo_url> fake_openai
     cd fake_openai
     ```

2. **创建并激活 Python 虚拟环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **启动服务**
   ```bash
   uvicorn main:app --reload
   ```
   - 默认监听 http://127.0.0.1:8000
   - 可用 `--host 0.0.0.0 --port 8080` 自定义监听地址和端口

5. **测试接口**
   可用 curl、Postman 或 httpie 测试：
   ```bash
   curl -X POST http://127.0.0.1:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [{"role": "user", "content": "你好"}],
       "stream": true,
       "config": {
         "first_token_delay": 1,
         "stream_chunk_size_range": [5, 10],
         "stream_interval_range": [0.2, 0.4],
         "total_length_range": [40, 80]
       }
     }'
   ```

6. **（可选）生产环境部署**
   - 推荐去掉 --reload：
     ```bash
     uvicorn main:app --host 0.0.0.0 --port 8000
     ```
   - 可结合 supervisor、systemd、docker 等方式守护进程。

## 示例
POST /v1/chat/completions
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [{"role": "user", "content": "你好"}],
  "stream": true,
  "config": {
    "first_token_delay": 1,
    "stream_chunk_size_range": [5, 10],
    "stream_interval_range": [0.2, 0.4],
    "total_length_range": [40, 80]
  }
}
``` 