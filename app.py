from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import shutil
import os
import uuid
from screen_tool.analyze import analyze_image, chat_image

app = FastAPI(title="Screen Insight Tool API")

# Setup static and upload dirs
os.makedirs("static", exist_ok=True)
os.makedirs(".uploads", exist_ok=True)

# Mount frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/api/analyze")
async def analyze_endpoint(
    command: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        temp_path = f".uploads/last_image.jpg"
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        # Clear old context so each new image starts fresh
        from screen_tool.analyze import CONTEXT_FILE
        if os.path.exists(CONTEXT_FILE):
            os.remove(CONTEXT_FILE)
        
        # Optimize uploaded image for Vision Models (NIM Sweet Spot: 1344px)
        from PIL import Image
        try:
            with Image.open(temp_path) as img:
                MAX_DIM = 1344
                if img.width > MAX_DIM or img.height > MAX_DIM:
                    img.thumbnail((MAX_DIM, MAX_DIM))
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(temp_path, "JPEG", quality=90)
        except Exception as img_err:
            print(f"Image optimization warning: {img_err}")
            
        # Analyze using Nvidia NIM (fresh context for each new image)
        result = analyze_image(temp_path, command, use_context=False)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ExecuteRequest(BaseModel):
    action: str
    input: str

@app.post("/api/execute")
async def execute_action(req: ExecuteRequest):
    # Mock execution hook for Jarvis ecosystem
    try:
        # In a real system, this connects to Microsoft Graph / Google Workspace / Jarvis Core
        print(f"JARVIS EXECUTE: {req.action}")
        print(f"PAYLOAD: {req.input}")
        return {"status": "success", "message": f"Successfully executed '{req.action}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        if not os.path.exists(".uploads/last_image.jpg"):
            raise HTTPException(status_code=400, detail="No active image to chat about. Please analyze an image first.")
            
        result = chat_image(".uploads/last_image.jpg", req.message)
        return {"response": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear_context")
async def clear_context():
    try:
        from screen_tool.analyze import CONTEXT_FILE
        if os.path.exists(CONTEXT_FILE):
            os.remove(CONTEXT_FILE)
        return {"status": "success", "message": "Conversation history cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Starting server on http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
