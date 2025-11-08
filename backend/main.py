from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/music")
def get_music():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    music_path = os.path.join(current_dir, "musics/test.mp3")
    if not os.path.exists(music_path):
        print(music_path)
        return {"error": "Music file not found"}, 404
    return FileResponse(music_path, media_type="audio/mpeg")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)