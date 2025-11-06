from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.database import init_db
from app.routes import products, inventory

# Initialize database
init_db()

app = FastAPI(
    title="Q-ProcureAssistant API",
    description="AI-powered procurement management system",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for serving images
if not os.path.exists("uploads"):
    os.makedirs("uploads")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Mount product_list_picture directory for serving product images
product_list_picture_path = os.path.join("..", "product_list_picture")
if os.path.exists(product_list_picture_path):
    app.mount("/product_list_picture", StaticFiles(directory=product_list_picture_path), name="product_list_picture")

# Include routers
app.include_router(products.router)
app.include_router(inventory.router)

@app.get("/")
async def root():
    return {
        "message": "Q-ProcureAssistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
