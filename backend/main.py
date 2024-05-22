from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel
import cv2
import numpy as np
import base64
import logging
from typing import List
import os

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing, change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Points(BaseModel):
    points: List[dict]

@app.post("/api/validate-coordinates")
async def validate_coordinates(file: UploadFile = File(...), points: str = Form(...)):
    try:
        points = Points.parse_raw(points)
        logging.debug(f"Received points: {points.points}")
        
        # Read the image file
        file_bytes = await file.read()
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return JSONResponse(status_code=400, content={"message": "Invalid image file."})
        
        # Convert points to a numpy array
        pts = np.array([[p['x'], p['y']] for p in points.points], dtype=np.float32)
        
        # Draw the polygon on the image
        cv2.polylines(img, [pts.astype(int)], isClosed=True, color=(0, 255, 0), thickness=2)
        
        # Encode image to base64 to send it back to frontend
        _, buffer = cv2.imencode('.jpg', img)
        img_str = base64.b64encode(buffer).decode('utf-8')
        
        return JSONResponse(content={"message": "Coordinates are valid.", "image": img_str})
    except Exception as e:
        logging.error(f"Error processing points: {str(e)}")
        return JSONResponse(status_code=500, content={"message": str(e)})

# Serve frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
