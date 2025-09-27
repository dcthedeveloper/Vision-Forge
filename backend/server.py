from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import base64
import io
import tempfile
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
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

class TextGenerationRequest(BaseModel):
    prompt: str
    generation_type: str  # "character", "story", "backstory", "dialogue"
    style_preferences: Optional[Dict[str, Any]] = None

class TextGenerationResponse(BaseModel):
    generated_text: str
    style_analysis: Optional[Dict[str, Any]] = None
    suggestions: List[str] = []
    cliche_score: Optional[float] = None
    success: bool
    message: str

class StyleAnalysisRequest(BaseModel):
    text: str

class StyleAnalysisResponse(BaseModel):
    cliche_score: float
    issues: List[Dict[str, str]]
    suggestions: List[str]
    rewritten_text: str
    success: bool
    message: str


# LLM Integration Setup
async def get_multi_stage_analysis(image_data: bytes, image_filename: str) -> Dict[str, Any]:
    """Multi-stage analysis for higher quality character creation"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
        
        # Convert image to base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        image_content = ImageContent(image_base64=image_b64)
        
        # Stage 1: Visual Extraction
        stage1_chat = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"stage1-{uuid.uuid4()}",
            system_message="""You are a visual analyst. Extract only what you can directly observe:

Return JSON:
{
  "appearance": "Physical description - build, height, features",
  "clothing": "Detailed clothing and accessories description", 
  "setting": "Environment and location details",
  "pose_expression": "Body language and facial expression",
  "style_aesthetic": "Overall visual style (modern, vintage, etc.)"
}

Be precise and observational only. No speculation about personality or powers."""
        ).with_model("openai", "gpt-4o")
        
        stage1_message = UserMessage(
            text="Analyze this image and extract only the visual details you can directly observe.",
            file_contents=[image_content]
        )
        
        stage1_response = await stage1_chat.send_message(stage1_message)
        
        # Parse Stage 1
        stage1_data = await parse_json_response(str(stage1_response))
        
        # Stage 2: Cultural Context & World Building
        stage2_chat = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'], 
            session_id=f"stage2-{uuid.uuid4()}",
            system_message="""You are a world-building expert. Based on visual details, determine the character's world and cultural context.

Focus on:
- What real-world culture/location does this suggest?
- What profession or lifestyle fits this appearance?
- What kind of story world does this belong in? (urban drama, corporate thriller, etc.)
- What social/economic status is indicated?

Return JSON:
{
  "cultural_context": "Specific cultural/geographic context",
  "profession_lifestyle": "Likely profession or lifestyle",
  "story_world": "Genre and setting type",
  "social_status": "Economic and social indicators",
  "realistic_backstory_seeds": ["grounded backstory idea 1", "idea 2", "idea 3"]
}

Avoid fantasy tropes. Think realistic modern settings."""
        ).with_model("anthropic", "claude-sonnet-4-20250514")
        
        stage2_message = UserMessage(
            text=f"Based on these visual details, determine the cultural context and world: {stage1_data}"
        )
        
        stage2_response = await stage2_chat.send_message(stage2_message)
        stage2_data = await parse_json_response(str(stage2_response))
        
        # Stage 3: Grounded Character Creation
        stage3_chat = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"stage3-{uuid.uuid4()}",
            system_message="""You are a character design expert who creates realistic, non-clichéd characters.

Create abilities that fit the real world context. Examples of GOOD vs BAD:
- BAD: "Shadow Manipulation", "Urban Kinesis", "Energy Control"  
- GOOD: "Hypercognitive", "Pattern Recognition", "Social Engineering"

Use clinical/realistic terminology. Powers should feel like enhanced human abilities, not fantasy magic.

Return JSON:
{
  "traits": [
    {"category": "Physical", "trait": "description", "confidence": 0.9},
    {"category": "Professional", "trait": "career/skill description", "confidence": 0.8},
    {"category": "Psychological", "trait": "mental/emotional traits", "confidence": 0.7}
  ],
  "mood": "sophisticated emotional description",
  "realistic_abilities": [
    {
      "name": "Clinical ability name (like Hypercognitive)",
      "description": "Realistic human enhancement",
      "limitations": "Real-world constraints",
      "cost_level": 5
    }
  ],
  "persona_summary": "Complex character description avoiding clichés"
}"""
        ).with_model("anthropic", "claude-sonnet-4-20250514")
        
        combined_context = f"Visual: {stage1_data}\nContext: {stage2_data}"
        stage3_message = UserMessage(
            text=f"Create a realistic character based on: {combined_context}"
        )
        
        stage3_response = await stage3_chat.send_message(stage3_message)
        stage3_data = await parse_json_response(str(stage3_response))
        
        # Combine all stages
        final_result = {
            "traits": stage3_data.get("traits", []),
            "mood": stage3_data.get("mood", "Unknown"),
            "backstory_seeds": stage2_data.get("realistic_backstory_seeds", []),
            "power_suggestions": stage3_data.get("realistic_abilities", []),
            "persona_summary": stage3_data.get("persona_summary", ""),
            "analysis_quality": "multi_stage",
            "cultural_context": stage2_data.get("cultural_context", "")
        }
        
        return final_result
        
    except Exception as e:
        logger.error(f"Multi-stage analysis failed: {e}")
        # Fallback to single stage
        return await get_vision_analysis(image_data, image_filename)

async def parse_json_response(response_text: str) -> Dict[str, Any]:
    """Helper to parse JSON from AI responses"""
    import json
    try:
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        elif "{" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_text = response_text[json_start:json_end]
        else:
            return {}
        return json.loads(json_text)
    except:
        return {}

async def get_vision_analysis(image_data: bytes, image_filename: str) -> Dict[str, Any]:
    """Get vision analysis from OpenAI GPT-4o with vision"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType
        
        # Initialize chat with vision capabilities
        chat = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"vision-analysis-{uuid.uuid4()}",
            system_message="""You are VisionForge, an expert character analyst specializing in extracting deep lore from images.

Analyze the provided image and return a detailed JSON response with this exact structure:
{
  "traits": [
    {"category": "Physical", "trait": "specific physical description", "confidence": 0.9},
    {"category": "Clothing", "trait": "detailed clothing/style description", "confidence": 0.8},
    {"category": "Personality", "trait": "personality inference from pose/expression", "confidence": 0.7},
    {"category": "Environment", "trait": "setting and atmosphere description", "confidence": 0.8}
  ],
  "mood": "overall emotional tone and atmosphere of the character/scene",
  "backstory_seeds": [
    "Creative backstory possibility 1 based on visual cues",
    "Creative backstory possibility 2 based on visual cues", 
    "Creative backstory possibility 3 based on visual cues"
  ],
  "power_suggestions": [
    {
      "name": "Power Name based on character appearance",
      "description": "What the power does, inspired by visual elements",
      "limitations": "Realistic constraints and costs",
      "cost_level": 5
    },
    {
      "name": "Second Power Name",
      "description": "Another ability suggestion",
      "limitations": "Different type of limitation",
      "cost_level": 3
    }
  ],
  "persona_summary": "2-3 sentence character summary avoiding clichés, based on actual visual details"
}

Be specific and detailed. Focus on what you actually see in the image - clothing, posture, setting, expression, style. 

For power suggestions, consider the character's actual appearance and context:
- Business/professional characters: social influence, strategic thinking, network access
- Military/tactical characters: tactical awareness, leadership, quick decision-making  
- Artist/creative characters: inspiration, pattern recognition, emotional influence
- Street/urban characters: survival instincts, street knowledge, adaptability

Avoid generic fantasy/superhero power names like "Shadow Control", "Element Manipulation", or anything ending in "-kinesis". Think more grounded and realistic abilities that fit the character's world and appearance."""
        )
        
        chat = chat.with_model("openai", "gpt-4o")
        
        # Convert image to base64 for OpenAI vision
        from emergentintegrations.llm.chat import ImageContent
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        image_content = ImageContent(image_base64=image_b64)
        
        # Create message with image
        user_message = UserMessage(
            text="Analyze this character image for detailed traits, mood, backstory seeds, and power suggestions. Focus on what you actually see - their appearance, clothing, setting, and pose. Return the response in the exact JSON format specified.",
            file_contents=[image_content]
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
            elif "{" in response_text:
                # Try to find JSON in the response
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                raise ValueError("No JSON found in response")
            
            parsed_data = json.loads(json_text)
            return parsed_data
            
        except Exception as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            # Return fallback structure with actual response content
            return {
                "traits": [
                    {"category": "Analysis", "trait": f"Raw response: {response_text[:200]}...", "confidence": 0.5}
                ],
                "mood": "Analysis in progress",
                "backstory_seeds": [f"Response parsing failed: {str(e)}"],
                "power_suggestions": [{
                    "name": "Analysis Error",
                    "description": "Please try again",
                    "limitations": "Technical issue",
                    "cost_level": 5
                }],
                "persona_summary": f"Character analysis encountered parsing issues. Raw response available in traits."
            }
        
    except Exception as e:
        logger.error(f"Vision analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Vision analysis failed: {str(e)}")

async def get_text_generation(prompt: str, generation_type: str, style_preferences: Optional[Dict] = None) -> Dict[str, Any]:
    """Generate text using Claude Sonnet 4 for high-quality narrative"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        # System message based on generation type
        system_messages = {
            "character": """You are VisionForge's Character Creator, an expert in crafting compelling, non-clichéd characters. 
Create detailed character profiles that avoid overused tropes. Focus on unique traits, realistic motivations, and interesting flaws.
Return rich character descriptions with personality, background, goals, and distinctive quirks.""",
            
            "story": """You are VisionForge's Story Architect, specializing in creating engaging narratives with depth and originality.
Craft compelling stories that subvert expectations and avoid tired tropes. Focus on character-driven plots, realistic conflicts, and meaningful themes.
Build narratives that feel fresh and authentic.""",
            
            "backstory": """You are VisionForge's Lore Master, expert at creating rich backstories that feel lived-in and authentic.
Generate detailed character histories that explain motivations and create depth. Avoid generic 'chosen one' or 'tragic past' clichés.
Focus on realistic life experiences that shaped the character.""",
            
            "dialogue": """You are VisionForge's Dialogue Specialist, crafting natural, character-specific speech patterns.
Write dialogue that reveals personality, advances plot, and sounds authentic to each character. Avoid exposition dumps and generic speech patterns.
Each character should have a distinct voice and speaking style."""
        }
        
        chat = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"text-gen-{uuid.uuid4()}",
            system_message=system_messages.get(generation_type, system_messages["character"])
        )
        
        chat = chat.with_model("anthropic", "claude-sonnet-4-20250514")
        
        # Enhanced prompt based on type
        enhanced_prompt = f"""Create a {generation_type} based on this prompt: {prompt}

Style preferences: {style_preferences if style_preferences else 'Natural, engaging, avoiding clichés'}

Requirements:
- Avoid overused tropes and clichéd language
- Create unique, memorable elements
- Focus on authentic character voice and realistic details
- Provide specific, vivid descriptions
- Make it engaging and original

Respond with well-structured, high-quality content."""
        
        user_message = UserMessage(text=enhanced_prompt)
        response = await chat.send_message(user_message)
        
        # Basic cliché detection
        response_text = str(response)
        cliche_indicators = [
            "chosen one", "ancient prophecy", "dark past", "mysterious stranger",
            "hidden power", "royal bloodline", "tragic backstory", "destiny calls",
            "nestled", "delve", "meticulous", "tapestry", "enigmatic"
        ]
        
        cliche_count = sum(1 for indicator in cliche_indicators if indicator.lower() in response_text.lower())
        cliche_score = min(cliche_count * 0.1, 1.0)
        
        return {
            "generated_text": response_text,
            "cliche_score": cliche_score,
            "suggestions": ["Consider adding more specific details", "Develop unique character traits", "Avoid common fantasy tropes"] if cliche_score > 0.3 else []
        }
        
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

async def analyze_writing_style(text: str) -> Dict[str, Any]:
    """Analyze text for clichés and style issues using Claude"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        chat = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"style-analysis-{uuid.uuid4()}",
            system_message="""You are VisionForge's Style Coach, an expert editor specializing in detecting and fixing clichéd writing.

Analyze the provided text and return a JSON response with this structure:
{
  "cliche_score": 0.7,
  "issues": [
    {"type": "cliche", "text": "dark and stormy night", "suggestion": "Describe specific weather details instead"},
    {"type": "overused_word", "text": "delve", "suggestion": "Use 'explore', 'investigate', or 'examine' instead"},
    {"type": "passive_voice", "text": "was destroyed by", "suggestion": "Make it active: 'The storm destroyed'"}
  ],
  "suggestions": [
    "Add more specific sensory details",
    "Vary sentence structure",
    "Show don't tell emotions"
  ],
  "rewritten_text": "Here's an improved version of your text..."
}

Focus on:
- Overused AI words (delve, nestled, meticulous, tapestry, enigmatic)
- Generic fantasy tropes
- Passive voice
- Telling vs showing
- Clichéd phrases
- Repetitive word usage"""
        )
        
        chat = chat.with_model("anthropic", "claude-sonnet-4-20250514")
        
        user_message = UserMessage(
            text=f"""Analyze this text for style issues, clichés, and overused phrases. Provide specific suggestions for improvement and a rewritten version:

{text}

Return the analysis in the exact JSON format specified."""
        )
        
        response = await chat.send_message(user_message)
        
        # Parse JSON response
        import json
        try:
            response_text = str(response)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            
            return json.loads(json_text)
            
        except Exception as e:
            # Fallback analysis
            cliche_indicators = ["delve", "nestled", "meticulous", "tapestry", "enigmatic", "ancient", "mysterious", "dark past"]
            cliche_count = sum(1 for indicator in cliche_indicators if indicator.lower() in text.lower())
            
            return {
                "cliche_score": min(cliche_count * 0.2, 1.0),
                "issues": [{"type": "parsing_error", "text": "Analysis failed", "suggestion": "Try again"}],
                "suggestions": ["Text analysis encountered technical difficulties"],
                "rewritten_text": "Please resubmit for analysis"
            }
            
    except Exception as e:
        logger.error(f"Style analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Style analysis failed: {str(e)}")


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
        
        # Get vision analysis from OpenAI GPT-4o
        analysis_data = await get_vision_analysis(image_data, file.filename)
        
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

@api_router.post("/generate-text", response_model=TextGenerationResponse)
async def generate_text(request: TextGenerationRequest):
    """Generate character descriptions, stories, backstories, or dialogue"""
    try:
        result = await get_text_generation(
            request.prompt, 
            request.generation_type,
            request.style_preferences
        )
        
        return TextGenerationResponse(
            generated_text=result["generated_text"],
            cliche_score=result["cliche_score"],
            suggestions=result["suggestions"],
            success=True,
            message="Text generation completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

@api_router.post("/analyze-style", response_model=StyleAnalysisResponse)
async def analyze_style(request: StyleAnalysisRequest):
    """Analyze text for clichés and style issues"""
    try:
        result = await analyze_writing_style(request.text)
        
        return StyleAnalysisResponse(
            cliche_score=result["cliche_score"],
            issues=result["issues"],
            suggestions=result["suggestions"],
            rewritten_text=result["rewritten_text"],
            success=True,
            message="Style analysis completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Style analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Style analysis failed: {str(e)}")

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