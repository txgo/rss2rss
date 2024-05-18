import feedparser
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

# 创建 OpenAI 客户端
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

class RSSRequest(BaseModel):
    url: str

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.post("/add_rss/")
async def add_rss(rss: RSSRequest):
    try:
        print(f"Received URL: {rss.url}")
        entries = process_rss(rss.url)
        print(f"Processed entries: {entries}")
        return {"status": "success", "data": entries}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

def process_rss(url: str):
    feed = feedparser.parse(url)
    entries = feed.entries
    processed_entries = []

    for entry in entries:
        print(entry)  # 打印条目以确认其结构
        summary = entry.get('summary', entry.get('description', 'No summary available'))
        summary_text = summarize_text(summary)
        processed_entries.append({
            'title': entry.get('title', 'No title'),
            'link': entry.get('link', 'No link'),
            'summary': summary_text
        })

    return processed_entries

def summarize_text(text: str) -> str:
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Please summarize the following text: {text}"}
            ],
            model="gpt-3.5-turbo",
        )
        summary = chat_completion.choices[0].message.content.strip()
        return summary
    except Exception as e:
        return str(e)

