import feedparser
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建 OpenAI 客户端，并从环境变量中获取 API 密钥
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("The OPENAI_API_KEY environment variable is not set.")

client = OpenAI(
    api_key=api_key
)

class RSSRequest(BaseModel):
    url: str
    limit: int = 3  # 默认限制为3个条目
    summary_length: int = 50  # 默认限制为50 tokens，大约为Twitter的长度

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.post("/add_rss/")
async def add_rss(rss: RSSRequest):
    try:
        print(f"Received URL: {rss.url}")
        entries = process_rss(rss.url, rss.limit, rss.summary_length)
        print(f"Processed entries: {entries}")
        return {"status": "success", "data": entries}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

def process_rss(url: str, limit: int, summary_length: int):
    feed = feedparser.parse(url)
    entries = feed.entries[:limit]  # 只处理限制数量的条目
    processed_entries = []

    for entry in entries:
        print(entry)  # 打印条目以确认其结构
        summary = entry.get('summary', entry.get('description', 'No summary available'))
        summary_text = summarize_text(summary, summary_length)
        processed_entries.append({
            'title': entry.get('title', 'No title'),
            'link': entry.get('link', 'No link'),
            'summary': summary_text
        })

    return processed_entries

def summarize_text(text: str, max_tokens: int) -> str:
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Please summarize the following text: {text}"}
            ],
            model="gpt-3.5-turbo",
            max_tokens=max_tokens  # 限制生成摘要的最大长度
        )
        summary = chat_completion.choices[0].message.content.strip()
        return summary
    except Exception as e:
        return str(e)

