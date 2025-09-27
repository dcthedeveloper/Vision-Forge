from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import base64
import io
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from PIL import Image
import asyncio


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="VisionForge API", description="Image-to-Lore Analysis System")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Data Models
class CharacterTrait(BaseModel):
    category: str
    trait: str
    confidence: float

class PowerSuggestion(BaseModel):
    name: str
    description: str
    limitations: str
    cost_level: int  # 1-10 scale

class CharacterAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    image_name: str
    traits: List[CharacterTrait]
    mood: str
    backstory_seeds: List[str]
    power_suggestions: List[PowerSuggestion]
    persona_summary: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CharacterAnalysisResponse(BaseModel):
    analysis: CharacterAnalysis
    success: bool
    message: str


# LLM Integration Setup
async def get_vision_analysis(image_data: str, model_type: str = "claude") -> Dict[str, Any]:
    """Get vision analysis from Claude or GPT-4V"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        # Initialize chat with vision capabilities
        chat = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"vision-analysis-{uuid.uuid4()}",
            system_message="""You are VisionForge, an expert character analyst specializing in extracting deep lore from images.

Analyze the provided image and return a detailed JSON response with this exact structure:
{
  "traits": [
    {"category": "Physical", "trait": "description", "confidence": 0.9},
    {"category": "Personality", "trait": "description", "confidence": 0.8}
  ],
  "mood": "overall emotional tone/atmosphere",
  "backstory_seeds": ["seed 1", "seed 2", "seed 3"],
  "power_suggestions": [
    {
      "name": "Power Name",
      "description": "What the power does",
      "limitations": "Constraints/costs",
      "cost_level": 5
    }
  ],
  "persona_summary": "2-3 sentence character summary avoiding clichés"
}

Categories for traits: Physical, Personality, Equipment, Environment, Pose, Expression
Be specific and avoid generic descriptions. Focus on unique details that tell a story."""
        )
        
        if model_type == "claude":
            chat = chat.with_model("anthropic", "claude-3-7-sonnet-20250219")
        else:
            chat = chat.with_model("openai", "gpt-4o")
        
        # Create message with image
        user_message = UserMessage(
            text="Analyze this image for character creation. Provide detailed traits, mood, backstory seeds, and power suggestions in the specified JSON format.",
            image_data=image_data
        )
        
        response = await chat.send_message(user_message)
        
        # Parse JSON response
        import json
        try:
            # Extract JSON from response
            response_text = str(response)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                # Try to find JSON in the response
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            
            return json.loads(json_text)
        except Exception as e:
            logger.error(f"Failed to parse JSON response: {e}")
            # Return fallback structure
            return {
                "traits": [{"category": "Analysis", "trait": "Image processed but parsing failed", "confidence": 0.5}],
                "mood": "Unable to determine",
                "backstory_seeds": ["Character analysis in progress"],
                "power_suggestions": [{"name": "Unknown Ability", "description": "Powers to be determined", "limitations": "Analysis incomplete", "cost_level": 5}],
                "persona_summary": "Character analysis encountered technical difficulties. Please try again."
            }
            
    except Exception as e:
        logger.error(f"Vision analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Vision analysis failed: {str(e)}")


# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "VisionForge API - Image-to-Lore Analysis System"}

@api_router.post("/analyze-image", response_model=CharacterAnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """Upload and analyze an image for character traits, backstory, and powers"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        image_data = await file.read()
        
        # Convert to base64 for LLM processing
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        # Get vision analysis from Claude (primary) with GPT-4V fallback
        try:
            analysis_data = await get_vision_analysis(image_b64, "claude")
        except Exception as claude_error:
            logger.warning(f"Claude analysis failed, trying GPT-4V: {claude_error}")
            try:
                analysis_data = await get_vision_analysis(image_b64, "gpt4v")
            except Exception as gpt_error:
                logger.error(f"Both vision models failed: {claude_error}, {gpt_error}")
                raise HTTPException(status_code=500, detail="Vision analysis unavailable")
        
        # Create character analysis object
        character_analysis = CharacterAnalysis(
            image_name=file.filename,
            traits=[CharacterTrait(**trait) for trait in analysis_data["traits"]],
            mood=analysis_data["mood"],
            backstory_seeds=analysis_data["backstory_seeds"],
            power_suggestions=[PowerSuggestion(**power) for power in analysis_data["power_suggestions"]],
            persona_summary=analysis_data["persona_summary"]
        )
        
        # Store in database
        analysis_dict = character_analysis.dict()
        await db.character_analyses.insert_one(analysis_dict)
        
        return CharacterAnalysisResponse(
            analysis=character_analysis,
            success=True,
            message="Character analysis completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@api_router.get("/analyses", response_model=List[CharacterAnalysis])
async def get_character_analyses():
    """Get all character analyses"""
    try:
        analyses = await db.character_analyses.find().sort("created_at", -1).to_list(100)
        return [CharacterAnalysis(**analysis) for analysis in analyses]
    except Exception as e:
        logger.error(f"Failed to fetch analyses: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analyses")

@api_router.get("/analyses/{analysis_id}", response_model=CharacterAnalysis)
async def get_character_analysis(analysis_id: str):
    """Get a specific character analysis by ID"""
    try:
        analysis = await db.character_analyses.find_one({"id": analysis_id})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return CharacterAnalysis(**analysis)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analysis")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()