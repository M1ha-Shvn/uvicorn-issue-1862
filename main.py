import tracemalloc

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.websockets import WebSocket


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def start_trace():
    tracemalloc.start()


@app.on_event("shutdown")
async def stop_trace():
    tracemalloc.stop()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@app.get("/snapshot")
async def get_snapshot(request: Request, name='snapshot', limit: int = 5):
    snapshot = tracemalloc.take_snapshot()
    top_stats_tb = snapshot.statistics('traceback')
    return [{
        'count': stat.count,
        'bytes': stat.size,
        'traceback': list(stat.traceback.format())
    } for stat in top_stats_tb[:limit]]
