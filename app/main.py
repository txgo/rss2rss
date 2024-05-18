from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.post("/add_rss/")
async def add_rss(url: str):
    # 处理RSS源
    return {"message": f"Added RSS feed: {url}"}