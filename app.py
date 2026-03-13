from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from web_api import router

app = FastAPI(title="Multi-Agent Code Generator")

# Enable CORS (development only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Get absolute path to frontend folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Serve index.html
@app.get("/")
def serve_home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000)