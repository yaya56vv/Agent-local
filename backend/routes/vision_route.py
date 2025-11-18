from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from backend.connectors.vision.vision_analyzer import VisionAnalyzer

router = APIRouter()

# Initialize vision analyzer
vision_analyzer = VisionAnalyzer()


@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(..., description="Image file (PNG, JPG, etc.)"),
    prompt: Optional[str] = Form(None, description="Optional prompt to guide analysis")
):
    """
    Analyze an image using Gemini multimodal vision.
    
    Args:
        file: Image file to analyze
        prompt: Optional prompt for specific analysis
        
    Returns:
        dict: Structured analysis with description, detected_text, objects, reasoning, and suggested_actions
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.content_type}. Must be an image."
            )
        
        # Read image bytes
        image_bytes = await file.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Analyze image
        result = await vision_analyzer.analyze_image(
            image_bytes=image_bytes,
            prompt=prompt or ""
        )
        
        return {
            "status": "success",
            "filename": file.filename,
            "analysis": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Vision analysis failed: {str(e)}"
        )


@router.post("/screenshot")
async def analyze_screenshot(
    file: UploadFile = File(..., description="Screenshot image"),
    context: Optional[str] = Form(None, description="Context about what to look for")
):
    """
    Analyze a screenshot with focus on UI/UX elements.
    
    Args:
        file: Screenshot image file
        context: Optional context about what to analyze
        
    Returns:
        dict: UI-focused analysis
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.content_type}. Must be an image."
            )
        
        # Read image bytes
        image_bytes = await file.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Analyze screenshot
        result = await vision_analyzer.analyze_screenshot(
            image_bytes=image_bytes,
            context=context or ""
        )
        
        return {
            "status": "success",
            "filename": file.filename,
            "analysis": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Screenshot analysis failed: {str(e)}"
        )


@router.post("/extract-text")
async def extract_text(
    file: UploadFile = File(..., description="Image file with text")
):
    """
    Extract text from an image (OCR).
    
    Args:
        file: Image file containing text
        
    Returns:
        dict: Extracted text
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.content_type}. Must be an image."
            )
        
        # Read image bytes
        image_bytes = await file.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Extract text
        result = await vision_analyzer.extract_text(image_bytes)
        
        return {
            "status": "success",
            "filename": file.filename,
            "extracted_text": result.get("text", ""),
            "full_analysis": result.get("full_analysis", {})
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Text extraction failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Check if vision module is operational."""
    try:
        # Simple check to see if API key is configured
        if vision_analyzer.api_key:
            return {
                "status": "healthy",
                "module": "vision",
                "api_configured": True
            }
        else:
            return {
                "status": "unhealthy",
                "module": "vision",
                "api_configured": False,
                "error": "GEMINI_API_KEY not configured"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "module": "vision",
            "error": str(e)
        }