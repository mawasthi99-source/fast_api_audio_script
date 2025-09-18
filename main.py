from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
from pydub import AudioSegment
import io
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Audio Processor API", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUDIO_STORAGE_DIR = "audio_files"
os.makedirs(AUDIO_STORAGE_DIR, exist_ok=True)

@app.post("/upload-audio")
async def upload_audio(audio_file: UploadFile = File(...)):
    try:
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Only audio files are allowed.")
        
        audio_content = await audio_file.read()
        logger.info(f"Received audio file: {audio_file.filename}, Size: {len(audio_content)} bytes")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        output_filename = f"audio_{timestamp}_{unique_id}.mp3"
        output_path = os.path.join(AUDIO_STORAGE_DIR, output_filename)
        
        try:
            audio_segment = AudioSegment.from_file(
                io.BytesIO(audio_content), 
                format="webm" 
            )
            
            audio_segment.export(output_path, format="mp3", bitrate="192k")
            
            logger.info(f"Successfully converted and saved audio to: {output_path}")
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Audio file processed successfully",
                    "filename": output_filename,
                    "file_path": output_path,
                    "size_bytes": len(audio_content),
                    "duration_seconds": len(audio_segment) / 1000.0
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing audio file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing audio file: {str(e)}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")