"""
MCP Vision Service - FastAPI Server
Provides HTTP endpoints for vision analysis operations using VisionAnalyzer
"""

from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
from pathlib import Path
import base64

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.connectors.vision.vision_analyzer import VisionAnalyzer

# Initialize FastAPI app
app = FastAPI(
    title="MCP Vision Service",
    description="Vision analysis service for MCP protocol",
    version="1.0.0"
)

# Initialize VisionAnalyzer
vision_analyzer = VisionAnalyzer()


# Pydantic models for request bodies
class AnalyzeImageRequest(BaseModel):
    image: str  # base64 encoded image
    prompt: Optional[str] = ""
    model: Optional[str] = None


class ExtractTextRequest(BaseModel):
    image: str  # base64 encoded image


class AnalyzeScreenshotRequest(BaseModel):
    image: str  # base64 encoded image
    context: Optional[str] = ""


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "MCP Vision",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/vision/analyze_image")
async def analyze_image(request: AnalyzeImageRequest):
    """
    Analyze an image using vision AI.
    
    Args:
        request: AnalyzeImageRequest with base64 image, optional prompt and model
        
    Returns:
        Structured analysis with description, detected text, objects, reasoning, and suggested actions
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(request.image)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid base64 image data: {str(e)}"
            )
        
        # Analyze image
        result = await vision_analyzer.analyze_image(
            image_bytes=image_bytes,
            prompt=request.prompt,
            model=request.model
        )
        
        return JSONResponse(content={
            "status": "success",
            "analysis": result
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vision/analyze_image_file")
async def analyze_image_file(
    file: UploadFile = File(...),
    prompt: Optional[str] = "",
    model: Optional[str] = None
):
    """
    Analyze an image file using vision AI.
    
    Args:
        file: Image file (PNG, JPG, etc.)
        prompt: Optional prompt to guide the analysis
        model: Optional model to use
        
    Returns:
        Structured analysis with description, detected text, objects, reasoning, and suggested actions
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        # Read file content
        image_bytes = await file.read()
        
        # Validate file size (max 10MB)
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Image file too large (max 10MB)"
            )
        
        # Analyze image
        result = await vision_analyzer.analyze_image(
            image_bytes=image_bytes,
            prompt=prompt,
            model=model
        )
        
        return JSONResponse(content={
            "status": "success",
            "filename": file.filename,
            "analysis": result
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vision/extract_text")
async def extract_text(request: ExtractTextRequest):
    """
    Extract text from an image (OCR).
    
    Args:
        request: ExtractTextRequest with base64 image
        
    Returns:
        Extracted text and full analysis
        
    Raises:
        HTTPException: If extraction fails
    """
    try:
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(request.image)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid base64 image data: {str(e)}"
            )
        
        # Extract text
        result = await vision_analyzer.extract_text(image_bytes)
        
        return JSONResponse(content={
            "status": "success",
            "extracted_text": result
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vision/extract_text_file")
async def extract_text_file(file: UploadFile = File(...)):
    """
    Extract text from an image file (OCR).
    
    Args:
        file: Image file (PNG, JPG, etc.)
        
    Returns:
        Extracted text and full analysis
        
    Raises:
        HTTPException: If extraction fails
    """
    try:
        # Read file content
        image_bytes = await file.read()
        
        # Validate file size (max 10MB)
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Image file too large (max 10MB)"
            )
        
        # Extract text
        result = await vision_analyzer.extract_text(image_bytes)
        
        return JSONResponse(content={
            "status": "success",
            "filename": file.filename,
            "extracted_text": result
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vision/analyze_screenshot")
async def analyze_screenshot(request: AnalyzeScreenshotRequest):
    """
    Analyze a screenshot with focus on UI/UX elements.
    
    Args:
        request: AnalyzeScreenshotRequest with base64 image and optional context
        
    Returns:
        Analysis focused on UI elements, errors, and user experience
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(request.image)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid base64 image data: {str(e)}"
            )
        
        # Analyze screenshot
        result = await vision_analyzer.analyze_screenshot(
            image_bytes=image_bytes,
            context=request.context
        )
        
        return JSONResponse(content={
            "status": "success",
            "screenshot_analysis": result
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vision/analyze_screenshot_file")
async def analyze_screenshot_file(
    file: UploadFile = File(...),
    context: Optional[str] = ""
):
    """
    Analyze a screenshot file with focus on UI/UX elements.
    
    Args:
        file: Screenshot image file
        context: Optional context about what to look for
        
    Returns:
        Analysis focused on UI elements, errors, and user experience
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        # Read file content
        image_bytes = await file.read()
        
        # Validate file size (max 10MB)
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Image file too large (max 10MB)"
            )
        
        # Analyze screenshot
        result = await vision_analyzer.analyze_screenshot(
            image_bytes=image_bytes,
            context=context
        )
        
        return JSONResponse(content={
            "status": "success",
            "filename": file.filename,
            "screenshot_analysis": result
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Additional utility endpoints
@app.get("/vision/health")
async def health_check():
    """
    Detailed health check with API key validation.
    
    Returns:
        Service health status
    """
    try:
        # Check if API key is configured
        has_api_key = bool(vision_analyzer.api_key)
        
        return JSONResponse(content={
            "status": "healthy",
            "service": "MCP Vision",
            "version": "1.0.0",
            "api_configured": has_api_key,
            "base_url": vision_analyzer.base_url
        })
    
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
