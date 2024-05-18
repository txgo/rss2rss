import feedparser
from transformers import pipeline
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

classifier = pipeline('text-classification')
summarizer = pipeline('summarization')

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
        labels = classifier(entry.summary)
        if 'desired_label' in labels:
            summary = summarizer(entry.summary, max_length=150, min_length=50, do_sample=False)
            processed_entries.append({
                'title': entry.title,
                'summary': summary[0]['summary_text']
            })

    return processed_entries