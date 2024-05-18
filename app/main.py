import feedparser
import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

# 从环境变量中获取OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

class RSSRequest(BaseModel):
    url: str

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.post("/add_rss/")
async def add_rss(rss: RSSRequest):
    try:
        entries = process_rss(rss.url)
        return {"status": "success", "data": entries}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def process_rss(url: str):
    feed = feedparser.parse(url)
    entries = feed.entries
    processed_entries = []

    for entry in entries:
        summary = summarize_text(entry.summary)
        processed_entries.append({
            'title': entry.title,
            'summary': summary
        })

    return processed_entries

def summarize_text(text: str) -> str:
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Summarize the following text: {text}",
        max_tokens=150
    )
    summary = response.choices[0].text.strip()
    return summary