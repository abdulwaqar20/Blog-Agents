import json
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from src.graph import app as graph

api = FastAPI()
api.mount("/static", StaticFiles(directory="static"), name="static")
api.mount("/assets", StaticFiles(directory="docs"), name="assets")

@api.get("/")
def home():
    return FileResponse("static/index.html")

@api.get("/run")
def run(topic: str):
    def events():
        state = {"topic": topic, "outline": "", "draft": "", "feedback": "", "retries": 0, "approved": False}
        for update in graph.stream(state, stream_mode="updates"):
            for node, data in update.items():
                yield f"data: {json.dumps({'node': node, 'data': data})}\n\n"
        yield 'data: {"node": "__end__"}\n\n'
    return StreamingResponse(events(), media_type="text/event-stream")