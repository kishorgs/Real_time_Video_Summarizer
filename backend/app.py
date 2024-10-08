from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
from summarizer import summarize_video

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload_video/")
async def upload_video(file: UploadFile = File(...)):
    video_path = f"uploaded_{file.filename}"
    
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Summarize the uploaded video
    summary = summarize_video(video_path)
    
    return {"summary": summary}
