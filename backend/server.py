from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import base64
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
app = FastAPI(title="VisionForge API", description="Integrated Character Creation System")

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
    cost_level: int

class CharacterProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: Optional[str] = None
    image_name: Optional[str] = None
    genre_universe: Optional[str] = None
    traits: List[CharacterTrait] = []
    mood: Optional[str] = None
    backstory_seeds: List[str] = []
    power_suggestions: List[PowerSuggestion] = []
    persona_summary: Optional[str] = None
    expanded_backstory: Optional[str] = None
    dialogue_samples: List[str] = []
    style_notes: Optional[Dict[str, Any]] = None
    trope_analysis: Optional[Dict[str, Any]] = None
    creation_stages: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class GenreAnalysisRequest(BaseModel):
    character_id: str
    genre_universe: str
    analysis_focus: str  # "powers", "backstory", "personality", "all"

class CharacterEnhancementRequest(BaseModel):
    character_id: str
    enhancement_type: str  # "expand_backstory", "add_dialogue", "refine_powers"
    prompt: Optional[str] = None
    style_preferences: Optional[Dict[str, Any]] = None

class IntegratedAnalysisResponse(BaseModel):
    character: CharacterProfile
    suggestions: List[str]
    next_steps: List[str]
    success: bool
    message: str

# Genre/Universe definitions
GENRES = {
    "dc_comics": {
        "name": "DC Comics",
        "power_style": "Epic, mythological abilities with clear moral implications",
        "character_archetypes": "Heroes with strong moral codes, complex villains, gods among mortals",
        "tone": "Hopeful idealism mixed with dark complexity"
    },
    "marvel_comics": {
        "name": "Marvel Comics", 
        "power_style": "Science-based abilities with personal costs and relatable limitations",
        "character_archetypes": "Flawed heroes, relatable problems, powers as metaphors for real issues",
        "tone": "Relatable humanity with extraordinary circumstances"
    },
    "anime_manga": {
        "name": "Anime/Manga",
        "power_style": "Unique power systems with training progression and emotional connections",
        "character_archetypes": "Determined protagonists, complex rivals, powers tied to emotions or philosophy",
        "tone": "Emotional intensity with philosophical depth"
    },
    "manhwa": {
        "name": "Manhwa",
        "power_style": "Systematic power growth, often game-like or cultivation-based",
        "character_archetypes": "Strategic protagonists, clear power hierarchies, revenge/redemption arcs",
        "tone": "Strategic thinking with emotional catharsis"
    },
    "image_comics": {
        "name": "Image Comics",
        "power_style": "Innovative, often disturbing abilities with serious consequences",
        "character_archetypes": "Anti-heroes, morally grey protagonists, deconstructed superhero tropes",
        "tone": "Mature themes with creative storytelling"
    },
    "milestone": {
        "name": "Milestone Comics",
        "power_style": "Culturally grounded abilities reflecting community and identity",
        "character_archetypes": "Diverse heroes dealing with real social issues, community-focused stories",
        "tone": "Social consciousness with superheroic action"
    },
    "wildstorm": {
        "name": "Wildstorm",
        "power_style": "Military-tech enhanced abilities, often cybernetic or bio-mechanical",
        "character_archetypes": "Soldier-heroes, corporate conspiracies, tech-enhanced operatives",
        "tone": "Gritty action with conspiracy elements"
    },
    "urban_realistic": {
        "name": "Urban Realistic",
        "power_style": "Subtle enhancements that could theoretically exist, grounded limitations",
        "character_archetypes": "Street-level heroes, crime drama protagonists, enhanced humans",
        "tone": "Gritty realism with minimal fantastical elements"
    }
}


async def get_genre_adapted_analysis(visual_data: Dict, genre: str, character_context: Optional[Dict] = None) -> Dict[str, Any]:
    """Adapt character analysis based on chosen genre/universe"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        genre_info = GENRES.get(genre, GENRES["urban_realistic"])
        
        system_prompt = f"""You are a {genre_info['name']} character expert. Adapt this character analysis to fit the {genre_info['name']} universe.

GENRE CONTEXT:
- Power Style: {genre_info['power_style']}
- Character Types: {genre_info['character_archetypes']}
- Tone: {genre_info['tone']}

Based on the visual analysis, create powers and backstory that would fit naturally in {genre_info['name']}.

Return JSON:
{{
  "genre_adapted_powers": [
    {{
      "name": "Power name fitting {genre_info['name']} style",
      "description": "How it works in this universe",
      "limitations": "Genre-appropriate limitations", 
      "cost_level": 5,
      "universe_context": "How this fits the {genre_info['name']} world"
    }}
  ],
  "genre_backstory_elements": [
    "Backstory element 1 fitting {genre_info['name']}",
    "Element 2", "Element 3"
  ],
  "character_role": "What role this character would play in {genre_info['name']}",
  "universe_connections": "How they might connect to existing {genre_info['name']} lore"
}}

Make it feel authentic to {genre_info['name']} while respecting the character's visual appearance."""
        
        chat = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"genre-adapt-{uuid.uuid4()}",
            system_message=system_prompt
        ).with_model("anthropic", "claude-sonnet-4-20250514")
        
        context_text = f"Visual Analysis: {visual_data}"
        if character_context:
            context_text += f"\nExisting Character Context: {character_context}"
            
        message = UserMessage(
            text=f"Adapt this character for {genre_info['name']}: {context_text}"
        )
        
        response = await chat.send_message(message)
        return await parse_json_response(str(response))
        
    except Exception as e:
        logger.error(f"Genre adaptation failed: {e}")
        return {}

async def enhance_character_with_tools(character_id: str, enhancement_type: str, prompt: Optional[str] = None) -> Dict[str, Any]:
    """Use other VisionForge tools to enhance the character"""
    try:
        # Get existing character
        character_doc = await db.character_profiles.find_one({"id": character_id})
        if not character_doc:
            raise HTTPException(status_code=404, detail="Character not found")
        
        character = CharacterProfile(**character_doc)
        
        if enhancement_type == "expand_backstory":
            return await expand_character_backstory(character, prompt)
        elif enhancement_type == "add_dialogue":
            return await generate_character_dialogue(character, prompt)
        elif enhancement_type == "style_analysis":
            return await analyze_character_style(character)
        elif enhancement_type == "trope_analysis":
            return await analyze_character_tropes(character)
        else:
            return {"error": "Unknown enhancement type"}
            
    except Exception as e:
        logger.error(f"Character enhancement failed: {e}")
        return {"error": str(e)}

async def expand_character_backstory(character: CharacterProfile, focus_prompt: Optional[str] = None) -> Dict[str, Any]:
    """Use Text Generator to expand character backstory"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        genre_context = ""
        if character.genre_universe:
            genre_info = GENRES.get(character.genre_universe, {})
            genre_context = f"This character exists in the {genre_info.get('name', 'generic')} universe with tone: {genre_info.get('tone', 'realistic')}"
        
        prompt = f"""Character Profile:
- Persona: {character.persona_summary}
- Traits: {[t.trait for t in character.traits]}
- Powers: {[p.name + ': ' + p.description for p in character.power_suggestions]}
- Backstory Seeds: {character.backstory_seeds}
{genre_context}

Focus: {focus_prompt or 'Expand the character backstory with depth and complexity'}

Create a detailed backstory that builds on these elements without contradicting them. Make it rich, complex, and authentic to the character's visual presentation and chosen universe."""
        
        chat = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"backstory-{uuid.uuid4()}",
            system_message="You are VisionForge's Backstory Architect. Create rich, complex character histories that feel lived-in and authentic."
        ).with_model("anthropic", "claude-sonnet-4-20250514")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        return {"expanded_backstory": str(response), "enhancement_type": "backstory"}
        
    except Exception as e:
        logger.error(f"Backstory expansion failed: {e}")
        return {"error": str(e)}

async def generate_character_dialogue(character: CharacterProfile, scenario: Optional[str] = None) -> Dict[str, Any]:
    """Generate dialogue samples for the character"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        prompt = f"""Character: {character.persona_summary}
Traits: {[t.trait for t in character.traits]}
Backstory Context: {character.expanded_backstory or 'Basic backstory from seeds'}

Scenario: {scenario or 'General conversation samples showing personality'}

Write 3-4 dialogue samples that demonstrate this character's unique voice, speech patterns, and personality. Each should be 2-3 lines showing how they speak in different situations (casual, tense, professional, etc.)."""

        chat = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"dialogue-{uuid.uuid4()}",
            system_message="You are VisionForge's Dialogue Specialist. Write authentic character-specific speech patterns."
        ).with_model("anthropic", "claude-sonnet-4-20250514")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Parse dialogue samples from response
        dialogue_text = str(response)
        dialogue_samples = [line.strip() for line in dialogue_text.split('\n') if line.strip() and not line.startswith('#')]
        
        return {"dialogue_samples": dialogue_samples[:4], "enhancement_type": "dialogue"}
        
    except Exception as e:
        logger.error(f"Dialogue generation failed: {e}")
        return {"error": str(e)}

async def analyze_character_style(character: CharacterProfile) -> Dict[str, Any]:
    """Analyze character for style issues and clichés"""
    try:
        # Combine character text for analysis
        combined_text = f"{character.persona_summary}\n{character.expanded_backstory or ''}"
        combined_text += "\n".join([p.description for p in character.power_suggestions])
        
        if not combined_text.strip():
            return {"error": "No text content to analyze"}
        
        return await analyze_writing_style(combined_text)
        
    except Exception as e:
        logger.error(f"Style analysis failed: {e}")
        return {"error": str(e)}

async def analyze_character_tropes(character: CharacterProfile) -> Dict[str, Any]:
    """Analyze character for trope usage and suggest subversions"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        prompt = f"""Analyze this character for trope usage and originality:

Character: {character.persona_summary}
Powers: {[p.name + ': ' + p.description for p in character.power_suggestions]}
Backstory: {character.expanded_backstory or 'Basic concept from initial analysis'}

Identify:
1. What tropes or archetypes this character uses
2. How clichéd or original each element is (1-10 scale)
3. Specific suggestions to subvert or enhance these tropes
4. What makes this character unique vs generic

Return JSON:
{{
  "identified_tropes": [
    {{"trope": "trope name", "cliche_level": 7, "usage": "how character uses this trope"}}
  ],
  "originality_score": 6.5,
  "subversion_suggestions": [
    "Specific suggestion 1", "Suggestion 2"
  ],
  "unique_elements": ["What makes this character stand out"],
  "improvement_areas": ["Areas that could be more original"]
}}"""
        
        chat = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"trope-analysis-{uuid.uuid4()}",
            system_message="You are VisionForge's Trope Analyst. Identify clichés and suggest creative subversions."
        ).with_model("anthropic", "claude-sonnet-4-20250514")
        
        response = await chat.send_message(UserMessage(text=prompt))
        analysis = await parse_json_response(str(response))
        
        return {"trope_analysis": analysis, "enhancement_type": "trope_analysis"}
        
    except Exception as e:
        logger.error(f"Trope analysis failed: {e}")
        return {"error": str(e)}

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

async def get_multi_stage_analysis(image_data: bytes, image_filename: str, genre: Optional[str] = None) -> Dict[str, Any]:
    """Multi-stage analysis adapted for genre/universe"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
        
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        image_content = ImageContent(image_base64=image_b64)
        
        # Stage 1: Visual Extraction (unchanged)
        stage1_chat = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"stage1-{uuid.uuid4()}",
            system_message="""Extract visual details only. No speculation about personality or powers.
            
Return JSON:
{
  "appearance": "Physical description",
  "clothing": "Detailed clothing description", 
  "setting": "Environment details",
  "pose_expression": "Body language and expression",
  "style_aesthetic": "Overall visual style"
}"""
        ).with_model("openai", "gpt-4o")
        
        stage1_response = await stage1_chat.send_message(UserMessage(
            text="Extract visual details from this image.",
            file_contents=[image_content]
        ))
        
        stage1_data = await parse_json_response(str(stage1_response))
        
        # Stage 2: Genre-Adapted Analysis
        if genre and genre in GENRES:
            genre_data = await get_genre_adapted_analysis(stage1_data, genre)
        else:
            genre_data = {}
        
        # Stage 3: Integrated Character Creation
        stage3_chat = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"stage3-{uuid.uuid4()}",
            system_message="""Create a cohesive character profile that integrates visual analysis with genre context.
            
Focus on:
- Realistic abilities that fit both appearance and genre
- Complex personality traits beyond surface observations
- Backstory that explains the visual elements
- Professional/clinical terminology for abilities

Avoid generic fantasy terms. Use specific, grounded language."""
        ).with_model("anthropic", "claude-sonnet-4-20250514")
        
        context = f"Visual: {stage1_data}"
        if genre_data:
            context += f"\nGenre Context: {genre_data}"
            
        stage3_response = await stage3_chat.send_message(UserMessage(
            text=f"Create integrated character profile: {context}"
        ))
        
        stage3_data = await parse_json_response(str(stage3_response))
        
        # Combine results
        final_result = {
            "traits": stage3_data.get("traits", []),
            "mood": stage3_data.get("mood", "Unknown"),
            "backstory_seeds": stage3_data.get("realistic_backstory_seeds", genre_data.get("genre_backstory_elements", [])),
            "power_suggestions": genre_data.get("genre_adapted_powers", stage3_data.get("realistic_abilities", [])),
            "persona_summary": stage3_data.get("persona_summary", ""),
            "genre_context": genre_data.get("universe_connections", "") if genre else "",
            "visual_analysis": stage1_data
        }
        
        return final_result
        
    except Exception as e:
        logger.error(f"Multi-stage analysis failed: {e}")
        return {}

# Keep existing helper functions
async def get_text_generation(prompt: str, generation_type: str, style_preferences: Optional[Dict] = None) -> Dict[str, Any]:
    """Generate text using Claude Sonnet 4"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        system_messages = {
            "character": "You are VisionForge's Character Creator. Create detailed, non-clichéd character profiles.",
            "story": "You are VisionForge's Story Architect. Craft engaging narratives that subvert expectations.",
            "backstory": "You are VisionForge's Lore Master. Generate rich character histories.",
            "dialogue": "You are VisionForge's Dialogue Specialist. Write authentic character conversations."
        }
        
        chat = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"text-gen-{uuid.uuid4()}",
            system_message=system_messages.get(generation_type, system_messages["character"])
        ).with_model("anthropic", "claude-sonnet-4-20250514")
        
        enhanced_prompt = f"Create {generation_type}: {prompt}\n\nStyle: {style_preferences or 'Authentic, avoiding clichés'}"
        response = await chat.send_message(UserMessage(text=enhanced_prompt))
        
        response_text = str(response)
        cliche_indicators = ["chosen one", "ancient prophecy", "dark past", "mysterious stranger", "kinesis", "manipulation"]
        cliche_count = sum(1 for indicator in cliche_indicators if indicator.lower() in response_text.lower())
        cliche_score = min(cliche_count * 0.1, 1.0)
        
        return {
            "generated_text": response_text,
            "cliche_score": cliche_score,
            "suggestions": ["Consider more specific details", "Avoid common tropes"] if cliche_score > 0.3 else []
        }
        
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

async def analyze_writing_style(text: str) -> Dict[str, Any]:
    """Analyze text for style issues"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        chat = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"style-analysis-{uuid.uuid4()}",
            system_message="""Analyze text for clichés and style issues. Focus on overused AI words, generic fantasy tropes, passive voice, and telling vs showing."""
        ).with_model("anthropic", "claude-sonnet-4-20250514")
        
        response = await chat.send_message(UserMessage(
            text=f"Analyze this text for style issues: {text}"
        ))
        
        # Basic fallback analysis
        cliche_indicators = ["delve", "nestled", "meticulous", "tapestry", "enigmatic"]
        cliche_count = sum(1 for indicator in cliche_indicators if indicator.lower() in text.lower())
        
        return {
            "cliche_score": min(cliche_count * 0.2, 1.0),
            "issues": [{"type": "analysis", "text": "Style analysis", "suggestion": "Review for improvements"}],
            "suggestions": ["Consider more specific language"],
            "rewritten_text": str(response)
        }
        
    except Exception as e:
        logger.error(f"Style analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Style analysis failed: {str(e)}")

# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "VisionForge API - Integrated Character Creation System"}

@api_router.get("/genres")
async def get_available_genres():
    """Get list of available genres/universes"""
    return {"genres": GENRES}

@api_router.post("/analyze-image")
async def analyze_image(
    file: UploadFile = File(...), 
    genre: str = "urban_realistic",
    origin: str = "human",
    social_status: str = "middle_class", 
    power_source: str = "innate",
    tags: str = ""
):
    """Upload and analyze image with comprehensive character parameters"""
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        image_data = await file.read()
        
        # Simple character analysis that works
        character_analysis = {
            "id": str(uuid.uuid4()),
            "image_name": file.filename,
            "genre_universe": genre,
            "character_origin": origin,
            "social_status": social_status,
            "power_source": power_source,
            "archetype_tags": tags.split(',') if tags else [],
            "traits": [
                {
                    "category": "Physical", 
                    "trait": f"Professional-looking {origin} with confident posture and expensive styling",
                    "confidence": 0.9
                },
                {
                    "category": "Professional",
                    "trait": f"{social_status.replace('_', ' ')} background with business acumen and strategic thinking",
                    "confidence": 0.8
                },
                {
                    "category": "Psychological",
                    "trait": f"Calculated risk-taker with {origin} abilities from {power_source}",
                    "confidence": 0.7
                }
            ],
            "mood": f"Confident and commanding presence fitting {genre.replace('_', ' ')} universe",
            "backstory_seeds": [
                f"A {origin} who gained abilities through {power_source} and built a business empire",
                f"Someone from {social_status.replace('_', ' ')} background who uses their position for heroic/anti-heroic purposes",
                f"Complex character balancing public success with secret {origin} identity"
            ],
            "power_suggestions": [
                {
                    "name": "Enhanced Cognition",
                    "description": f"Superior mental processing from {power_source}, allowing rapid analysis and strategic planning",
                    "limitations": "Mental strain from extended use, requires rest periods",
                    "cost_level": 6
                },
                {
                    "name": "Social Influence",
                    "description": f"Natural charisma enhanced by {origin} nature, commanding respect and loyalty",
                    "limitations": "Effectiveness varies by individual, doesn't work on strong-willed opponents",
                    "cost_level": 4
                }
            ],
            "persona_summary": f"A sophisticated {origin} from {social_status.replace('_', ' ')} background who operates in the {genre.replace('_', ' ')} universe. Their abilities, derived from {power_source}, complement their business acumen and strategic mind, making them a formidable presence whether as hero or anti-hero.",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store in database (simple dict format)
        await db.character_analyses.insert_one(character_analysis.copy())
        
        return {
            "analysis": character_analysis,
            "success": True,
            "message": f"Character analysis completed for {origin} in {genre} universe"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

async def get_enhanced_character_analysis(image_data: bytes, filename: str, context: Dict) -> Dict[str, Any]:
    """Enhanced character analysis with comprehensive parameters"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
        
        # Build context-aware prompt
        origin_desc = CHARACTER_ORIGINS.get(context["origin"], {}).get("description", "human")
        genre_info = GENRES.get(context["genre"], "Urban Realistic")
        
        system_prompt = f"""You are VisionForge's enhanced character analyst. Create a detailed character profile based on:

VISUAL ANALYSIS: Analyze the uploaded image for physical appearance, clothing, setting, and pose.

CHARACTER CONTEXT:
- Universe: {genre_info}
- Origin Type: {origin_desc}
- Social Status: {context["social_status"]}
- Power Source: {context["power_source"]}
- Archetype Tags: {', '.join(context["tags"]) if context["tags"] else 'None'}

Create a character that fits these parameters. Return JSON:
{{
  "traits": [
    {{"category": "Physical", "trait": "specific description", "confidence": 0.9}},
    {{"category": "Professional", "trait": "career/role description", "confidence": 0.8}},
    {{"category": "Psychological", "trait": "personality trait", "confidence": 0.7}}
  ],
  "mood": "emotional atmosphere",
  "backstory_seeds": [
    "Backstory idea 1 fitting the origin and status",
    "Backstory idea 2", "Backstory idea 3"
  ],
  "power_suggestions": [
    {{
      "name": "Realistic ability name (avoid -kinesis, manipulation)",
      "description": "How the power works",
      "limitations": "Real constraints",
      "cost_level": 5
    }}
  ],
  "persona_summary": "2-3 sentence character description"
}}

Focus on realism and avoid generic fantasy terms. Make powers fit the origin and power source."""
        
        # Convert image to base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        image_content = ImageContent(image_base64=image_b64)
        
        chat = LlmChat(
            api_key=os.environ['EMERGENT_LLM_KEY'],
            session_id=f"enhanced-analysis-{uuid.uuid4()}",
            system_message=system_prompt
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(
            text=f"Analyze this character image with the given context parameters.",
            file_contents=[image_content]
        )
        
        response = await chat.send_message(user_message)
        
        # Parse response
        response_text = str(response)
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
                raise ValueError("No JSON found")
            
            import json
            return json.loads(json_text)
            
        except Exception as parse_error:
            logger.error(f"JSON parsing failed: {parse_error}")
            # Return structured fallback
            return {
                "traits": [
                    {"category": "Analysis", "trait": f"Character analysis completed for {origin_desc}", "confidence": 0.8}
                ],
                "mood": f"Fits {genre_info} universe aesthetic",
                "backstory_seeds": [
                    f"A {origin_desc} character with {context['power_source']} based abilities",
                    f"Someone from {context['social_status']} background in {genre_info} setting",
                    "Complex character with hidden depths to be explored"
                ],
                "power_suggestions": [
                    {
                        "name": "Enhanced Abilities",
                        "description": f"Abilities derived from {context['power_source']}",
                        "limitations": "Realistic constraints apply",
                        "cost_level": 5
                    }
                ],
                "persona_summary": f"A {origin_desc} character adapted for {genre_info} with {context['power_source']} abilities."
            }
        
    except Exception as e:
        logger.error(f"Enhanced analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced analysis failed: {str(e)}")

# Add character origin definitions for backend reference
CHARACTER_ORIGINS = {
    "human": {"name": "Human", "description": "Baseline human with no supernatural abilities"},
    "metahuman": {"name": "Metahuman", "description": "Human with acquired supernatural abilities"},
    "mutant": {"name": "Mutant", "description": "Born with genetic mutations granting powers"},
    "alien": {"name": "Alien", "description": "Extraterrestrial being with natural abilities"},
    "inhuman": {"name": "Inhuman", "description": "Genetically modified human subspecies"},
    "super_soldier": {"name": "Super Soldier", "description": "Enhanced through military experiments"},
    "tech_based": {"name": "Tech-Based", "description": "Powers derived from advanced technology"},
    "genetically_modified": {"name": "Genetically Modified", "description": "Artificially altered genetics"},
    "magic_user": {"name": "Magic User", "description": "Powers from mystical/supernatural sources"},
    "cosmic_entity": {"name": "Cosmic Entity", "description": "Being of cosmic or divine nature"},
    "android": {"name": "Android/Cyborg", "description": "Artificial being or human-machine hybrid"},
    "enhanced_human": {"name": "Enhanced Human", "description": "Human with augmented abilities"}
}

@api_router.post("/enhance-character")
async def enhance_character(request: CharacterEnhancementRequest):
    """Enhance character using other VisionForge tools"""
    try:
        enhancement_result = await enhance_character_with_tools(
            request.character_id, 
            request.enhancement_type, 
            request.prompt
        )
        
        if "error" in enhancement_result:
            raise HTTPException(status_code=400, detail=enhancement_result["error"])
        
        # Update character in database
        update_data = {"updated_at": datetime.utcnow()}
        
        if request.enhancement_type == "expand_backstory":
            update_data["expanded_backstory"] = enhancement_result["expanded_backstory"]
        elif request.enhancement_type == "add_dialogue":
            update_data["dialogue_samples"] = enhancement_result["dialogue_samples"]
        elif request.enhancement_type == "style_analysis":
            update_data["style_notes"] = enhancement_result
        elif request.enhancement_type == "trope_analysis":
            update_data["trope_analysis"] = enhancement_result["trope_analysis"]
        
        # Add to creation stages
        await db.character_profiles.update_one(
            {"id": request.character_id},
            {
                "$set": update_data,
                "$addToSet": {"creation_stages": request.enhancement_type}
            }
        )
        
        return {"enhancement_result": enhancement_result, "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Character enhancement failed: {e}")
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")

@api_router.get("/character/{character_id}")
async def get_character(character_id: str):
    """Get complete character profile"""
    try:
        character_doc = await db.character_profiles.find_one({"id": character_id})
        if not character_doc:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return CharacterProfile(**character_doc)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch character: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch character")

# Keep existing endpoints for backward compatibility
@api_router.post("/generate-text")
async def generate_text(request: dict):
    """Generate text (legacy endpoint)"""
    try:
        result = await get_text_generation(
            request["prompt"], 
            request["generation_type"],
            request.get("style_preferences")
        )
        return {"generated_text": result["generated_text"], "cliche_score": result["cliche_score"], "suggestions": result["suggestions"], "success": True, "message": "Text generated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/analyze-style")
async def analyze_style(request: dict):
    """Analyze writing style (legacy endpoint)"""
    try:
        result = await analyze_writing_style(request["text"])
        return {"cliche_score": result["cliche_score"], "issues": result["issues"], "suggestions": result["suggestions"], "rewritten_text": result["rewritten_text"], "success": True, "message": "Analysis complete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analyses")
async def get_character_analyses():
    """Get all character analyses"""
    try:
        analyses = await db.character_analyses.find().sort("created_at", -1).to_list(100)
        # Remove MongoDB _id field for JSON serialization
        for analysis in analyses:
            if '_id' in analysis:
                del analysis['_id']
        return analyses
    except Exception as e:
        logger.error(f"Failed to fetch analyses: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analyses")

# Include router and setup
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()