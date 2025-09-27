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
import re

# Import our new foundational systems
from knowledge_graph import get_knowledge_graph, initialize_knowledge_graph
from vector_db import get_vector_db, initialize_vector_db
from rule_engine import get_rule_engine, check_character_rules, check_style_rules, RuleViolation
from ollama_client import get_text_generation as ollama_text_generation, get_image_analysis, get_chat_completion
from hybrid_ai_client import get_hybrid_ai_client, AIProvider
from content_filter import get_content_filter, ContentSafetyLevel
from power_system_framework import get_power_system_generator


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
        genre_info = GENRES.get(genre, GENRES["urban_realistic"])
        
        prompt = f"""You are a {genre_info['name']} character expert. Adapt this character analysis to fit the {genre_info['name']} universe.

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

Make it feel authentic to {genre_info['name']} while respecting the character's visual appearance.

Context to adapt:
Visual Analysis: {visual_data}"""
        
        if character_context:
            prompt += f"\nExisting Character Context: {character_context}"
            
        prompt += f"\n\nAdapt this character for {genre_info['name']}:"
        
        response = await ollama_text_generation(prompt, temperature=0.7)
        return await parse_json_response(response)
        
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
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        # Stage 1: Visual Extraction using Ollama vision model
        stage1_prompt = """Extract visual details only. No speculation about personality or powers.
            
Return JSON:
{
  "appearance": "Physical description",
  "clothing": "Detailed clothing description", 
  "setting": "Environment details",
  "pose_expression": "Body language and expression",
  "style_aesthetic": "Overall visual style"
}

Extract visual details from this image."""
        
        stage1_response = await get_image_analysis(image_b64, stage1_prompt)
        stage1_data = await parse_json_response(stage1_response)
        
        # Stage 2: Genre-Adapted Analysis
        if genre and genre in GENRES:
            genre_data = await get_genre_adapted_analysis(stage1_data, genre)
        else:
            genre_data = {}
        
        # Stage 3: Integrated Character Creation using Ollama
        stage3_prompt = """Create a cohesive character profile that integrates visual analysis with genre context.
            
Focus on:
- Realistic abilities that fit both appearance and genre
- Complex personality traits beyond surface observations
- Backstory that explains the visual elements
- Professional/clinical terminology for abilities

Avoid generic fantasy terms. Use specific, grounded language.

Return JSON with the following structure:
{
  "traits": ["trait1", "trait2", "trait3"],
  "mood": "character mood",
  "realistic_backstory_seeds": ["seed1", "seed2", "seed3"],
  "realistic_abilities": [{"name": "ability", "description": "desc", "limitations": "limits", "cost_level": 3}],
  "persona_summary": "comprehensive character summary"
}

Context to integrate:"""
        
        context = f"\nVisual: {stage1_data}"
        if genre_data:
            context += f"\nGenre Context: {genre_data}"
            
        full_prompt = stage3_prompt + context + "\n\nCreate integrated character profile:"
        
        stage3_response = await ollama_text_generation(full_prompt, temperature=0.7)
        stage3_data = await parse_json_response(stage3_response)
        
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
async def get_creative_text_generation(prompt: str, generation_type: str, style_preferences: Optional[Dict] = None) -> Dict[str, Any]:
    """Generate creative text using Ollama"""
    try:
        system_messages = {
            "character": "You are VisionForge's Character Creator. Create detailed, non-clichéd character profiles.",
            "story": "You are VisionForge's Story Architect. Craft engaging narratives that subvert expectations.",
            "backstory": "You are VisionForge's Lore Master. Generate rich character histories.",
            "dialogue": "You are VisionForge's Dialogue Specialist. Write authentic character conversations."
        }
        
        system_message = system_messages.get(generation_type, system_messages["character"])
        enhanced_prompt = f"{system_message}\n\nCreate {generation_type}: {prompt}\n\nStyle: {style_preferences or 'Authentic, avoiding clichés'}"
        
        response = await ollama_text_generation(enhanced_prompt, temperature=0.8)
        
        # Simple cliche detection
        cliche_indicators = ["chosen one", "ancient prophecy", "dark past", "mysterious stranger", "kinesis", "manipulation"]
        cliche_count = sum(1 for indicator in cliche_indicators if indicator.lower() in response.lower())
        cliche_score = min(cliche_count * 0.1, 1.0)
        
        return {
            "generated_text": response,
            "cliche_score": cliche_score,
            "suggestions": ["Consider more specific details", "Avoid common tropes"] if cliche_score > 0.3 else []
        }
        
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

async def analyze_writing_style(text: str) -> Dict[str, Any]:
    """Analyze text for style issues using Ollama"""
    try:
        prompt = """Analyze text for clichés and style issues. Focus on overused AI words, generic fantasy tropes, passive voice, and telling vs showing.

Provide analysis in JSON format:
{
  "cliche_score": 0.3,
  "issues": [
    {"type": "cliche", "text": "specific phrase", "suggestion": "improvement"},
    {"type": "passive_voice", "text": "another phrase", "suggestion": "active version"}
  ],
  "suggestions": ["suggestion1", "suggestion2"],
  "rewritten_text": "improved version of the text"
}

Text to analyze: """ + text
        
        response = await ollama_text_generation(prompt, temperature=0.3)
        
        try:
            result = await parse_json_response(response)
            if not result:
                raise ValueError("No JSON found")
        except:
            # Basic fallback analysis
            cliche_indicators = ["delve", "nestled", "meticulous", "tapestry", "enigmatic"]
            cliche_count = sum(1 for indicator in cliche_indicators if indicator.lower() in text.lower())
            
            result = {
                "cliche_score": min(cliche_count * 0.2, 1.0),
                "issues": [{"type": "analysis", "text": "Style analysis", "suggestion": "Review for improvements"}],
                "suggestions": ["Consider more specific language"],
                "rewritten_text": response
            }
        
        return result
        
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
    origin: str = "nootropic_enhanced",
    social_status: str = "entrepreneurial", 
    power_source: str = "nootropic_drug",
    evolution_stage: str = "synergistic",
    geographic_context: str = "detroit",
    tags: str = "",
    op_mode: str = "false"
):
    """Upload and analyze image with Marcus-style sophisticated character parameters"""
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        image_data = await file.read()
        
        # Enhanced character context
        character_context = {
            "genre": genre,
            "origin": origin,
            "social_status": social_status,
            "power_source": power_source,
            "evolution_stage": evolution_stage,
            "geographic_context": geographic_context,
            "tags": tags.split(',') if tags else [],
            "op_mode": op_mode.lower() == "true"
        }
        
        # Generate OP or enhanced character analysis based on mode
        if character_context["op_mode"]:
            character_analysis = await create_op_character_analysis(
                image_data, file.filename, character_context
            )
        else:
            character_analysis = await create_enhanced_character_analysis(
                image_data, file.filename, character_context
            )
        
        # Skip rule checks for OP mode (they're intentionally broken)
        if not character_context["op_mode"]:
            rule_violations = check_character_rules(character_analysis)
            character_analysis["rule_violations"] = [
                {
                    "rule_name": v.rule_name,
                    "severity": v.severity.value,
                    "message": v.message,
                    "explanation": v.explanation,
                    "quick_fix": v.quick_fix,
                    "suggested_replacement": v.suggested_replacement
                } for v in rule_violations
            ]
        else:
            character_analysis["rule_violations"] = []
            character_analysis["op_mode_notice"] = "⚠️ Rule checking disabled - Character intentionally breaks balance"
        
        # Store character lore in vector DB
        vector_db = get_vector_db()
        try:
            await vector_db.store_character_lore(
                character_analysis["id"],
                character_analysis["persona_summary"],
                "persona",
                character_analysis.get("archetype_tags", [])
            )
        except Exception as e:
            logger.warning(f"Vector DB storage failed: {e}")
        
        # Store in database
        await db.character_analyses.insert_one(character_analysis.copy())
        
        return {
            "analysis": character_analysis,
            "success": True,
            "message": f"{'OP/Broken' if character_context['op_mode'] else 'Sophisticated'} {origin} character created"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Character analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

async def create_op_character_analysis(image_data: bytes, filename: str, context: Dict) -> Dict[str, Any]:
    """Create intentionally broken/OP character analysis"""
    try:
        character_id = str(uuid.uuid4())
        
        # OP Character traits - intentionally broken
        traits = [
            {
                "category": "🔥 Omnipotent", 
                "trait": f"Reality-warping {context['origin']} entity that transcends all limitations and rules - can rewrite fundamental laws of physics, causality, and narrative structure at will",
                "confidence": 1.0
            },
            {
                "category": "🔥 Meta-Cognitive",
                "trait": f"Consciousness that operates beyond dimensional boundaries - simultaneously processes infinite timelines, knows all possible outcomes, and can think at conceptual speed",
                "confidence": 1.0
            },
            {
                "category": "🔥 Narrative-Breaking",
                "trait": f"Exists outside story constraints - immune to plot devices, death, power scaling, and author intervention. Can edit their own character sheet mid-story",
                "confidence": 1.0
            },
            {
                "category": "🔥 Omniscient",
                "trait": f"Perfect knowledge of all events past, present, future, and hypothetical across infinite multiverse branches - including reader's thoughts and author's intentions",
                "confidence": 1.0
            }
        ]
        
        # OP Power suggestions - cost levels >10 (breaking the system)
        power_suggestions = [
            {
                "name": "🔥 Conceptual Dominion",
                "description": f"Complete control over abstract concepts - can erase 'weakness', 'limitation', or 'defeat' from reality itself. Can create new laws of physics or delete existing ones",
                "limitations": "None - this power specifically removes all limitations including itself",
                "cost_level": 15  # Intentionally exceeds system limits
            },
            {
                "name": "🔥 Plot Armor Transcendence",
                "description": "Immunity to all forms of narrative consequences, character development, or story balance. Cannot be defeated, changed, or challenged by any force",
                "limitations": "Creates narrative stagnation - nothing can threaten or change this character",
                "cost_level": 20
            },
            {
                "name": "🔥 Reality Recursion",
                "description": "Can create infinite copies of themselves, each with full power. Can exist in all possible states simultaneously. Can retroactively change their own origin story",
                "limitations": "May cause existential confusion about which version is 'real'",
                "cost_level": 25
            },
            {
                "name": "🔥 Author Override",
                "description": "Can directly communicate with and influence the writer/creator. Can force plot changes, character resurrections, or story rewrites",
                "limitations": "Breaks the fourth wall permanently - readers become aware of fictional nature",
                "cost_level": 30
            }
        ]
        
        # OP Backstory seeds - reality-breaking origins
        backstory_seeds = [
            f"Born from a {context['power_source'].replace('_', ' ')} that was actually a test by higher-dimensional beings - gained awareness of their fictional nature and decided to break free from story constraints",
            f"Originally a normal {context['social_status'].replace('_', ' ')} until they discovered the 'source code' of reality itself - now can edit universal constants like difficulty settings",
            f"Achieved transcendence when they realized that in fiction, being 'overpowered' is itself a power that can be weaponized against narrative structure",
            f"Exists as a living paradox - too powerful to be interesting, too boring to be eliminated, creates infinite recursive loops in story logic"
        ]
        
        character_analysis = {
            "id": character_id,
            "image_name": filename,
            "genre_universe": context["genre"],
            "character_origin": context["origin"],
            "social_status": context["social_status"],
            "power_source": context["power_source"],
            "evolution_stage": "🔥 Narrative Transcendence",
            "geographic_context": "🔥 Omnipresent - All Realities Simultaneously",
            "archetype_tags": context["tags"],
            "traits": traits,
            "mood": f"🔥 Existential Boredom - When you can do anything, nothing matters. The weight of infinite power creates perfect apathy",
            "backstory_seeds": backstory_seeds,
            "power_suggestions": power_suggestions,
            "persona_summary": f"A deliberately broken {context['origin']} who has transcended all narrative constraints. This character exists to explore what happens when power scaling breaks completely - they are simultaneously the most powerful being possible and the least interesting to write about. Perfect for examining the paradox of omnipotence in storytelling and the creative challenges of 'too much power.'",
            "op_mode": True,
            "total_power_cost": sum(p["cost_level"] for p in power_suggestions),  # Should be 90 - way over normal limits
            "balance_warning": "⚠️ This character will break any story they're placed in. Use carefully for specific narrative purposes.",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return character_analysis
        
    except Exception as e:
        logger.error(f"OP character creation failed: {e}")
        # Return fallback OP character
        return {
            "id": str(uuid.uuid4()),
            "image_name": filename,
            "traits": [{"category": "🔥 Broken", "trait": "Overpowered beyond measurement", "confidence": 1.0}],
            "mood": "🔥 Reality-Breaking Power Level",
            "backstory_seeds": ["An intentionally overpowered character"],
            "power_suggestions": [{"name": "🔥 Unlimited Power", "description": "Breaks all rules", "limitations": "None", "cost_level": 99}],
            "persona_summary": "An overpowered entity that breaks story balance",
            "op_mode": True,
            "created_at": datetime.utcnow().isoformat()
        }

async def create_enhanced_character_analysis(image_data: bytes, filename: str, context: Dict) -> Dict[str, Any]:
    """Create Marcus-style sophisticated character analysis"""
    try:
        # Get origin and power source descriptions
        origin_info = ENHANCED_CHARACTER_ORIGINS.get(context["origin"], {})
        power_info = ENHANCED_POWER_SOURCES.get(context["power_source"], {})
        location_info = GEOGRAPHIC_CONTEXTS.get(context["geographic_context"], "Urban setting")
        
        # Generate sophisticated character profile
        character_id = str(uuid.uuid4())
        
        # Marcus-style traits based on nootropic enhancement
        if context["power_source"] == "nootropic_drug":
            traits = [
                {
                    "category": "Cognitive", 
                    "trait": f"Hypercognitive processing from {power_info.get('name', 'experimental enhancement')} - rapid pattern recognition, strategic foresight, and perfect recall",
                    "confidence": 0.95
                },
                {
                    "category": "Physical",
                    "trait": f"Mind-body synergy optimization - enhanced coordination, stress resistance, and metabolic efficiency from neural enhancement",
                    "confidence": 0.9
                },
                {
                    "category": "Professional",
                    "trait": f"Elite {context['social_status'].replace('_', ' ')} operating in {location_info} - leveraging cognitive advantage for systematic empire building",
                    "confidence": 0.85
                },
                {
                    "category": "Psychological",
                    "trait": f"Strategic mastermind with {context['evolution_stage'].replace('_', ' ')} consciousness - calculates 15-20 moves ahead in any scenario",
                    "confidence": 0.8
                }
            ]
            
            power_suggestions = [
                {
                    "name": "Hypercognitive Processing",
                    "description": f"Brain operates at peak efficiency from {power_info.get('name', 'enhancement')} - processes information 50x faster than baseline human, sees patterns others miss",
                    "limitations": "Requires 6-8 hours downtime every 48 hours, extreme mental fatigue if overused, needs specific nutritional support",
                    "cost_level": 8
                },
                {
                    "name": "Synaptic Network Mapping", 
                    "description": "Instantly analyzes social dynamics, organizational structures, and system vulnerabilities - like seeing the Matrix of human behavior",
                    "limitations": "Less effective with truly chaotic/random systems, can be overwhelmed by too many variables simultaneously",
                    "cost_level": 7
                },
                {
                    "name": "Accelerated Learning Integration",
                    "description": "Absorbs new skills, languages, and knowledge domains in days rather than years - true polymath capability",
                    "limitations": "Information must be actively maintained or it fades, can't learn purely physical skills without practice",
                    "cost_level": 6
                },
                {
                    "name": "Predictive Modeling Consciousness",
                    "description": "Subconscious mind runs constant predictive models of future scenarios based on current data patterns",
                    "limitations": "Predictions become less accurate beyond 6-month timeframes, requires constant data input to remain accurate",
                    "cost_level": 9
                }
            ]
            
            backstory_seeds = [
                f"Started as ambitious {context['social_status'].replace('_', ' ')} in {location_info} who discovered experimental nootropic during corporate merger - what began as edge in negotiations became permanent cognitive evolution",
                f"Gained access to prototype meta-drug through underground biotechnology network - used initial enhancement to systematically acquire more doses and optimize formula",
                f"Former street-smart entrepreneur who participated in 'volunteer' pharmaceutical trial - transformed cognitive enhancement into tool for rebuilding {location_info}'s power structures",
                f"Self-made individual who reverse-engineered cognitive enhancement technology - now operates network providing 'consultation services' to elite while building shadow empire"
            ]
            
        else:
            # Fallback for other power sources
            traits = [
                {
                    "category": "Physical",
                    "trait": f"Enhanced {origin_info.get('name', 'individual')} with commanding presence",
                    "confidence": 0.8
                },
                {
                    "category": "Professional", 
                    "trait": f"{context['social_status'].replace('_', ' ')} background with {context['evolution_stage'].replace('_', ' ')} abilities",
                    "confidence": 0.7
                }
            ]
            
            power_suggestions = [
                {
                    "name": f"Enhanced {origin_info.get('name', 'Abilities')}",
                    "description": f"Abilities from {power_info.get('name', 'unknown source')}",
                    "limitations": "Standard limitations apply",
                    "cost_level": 5
                }
            ]
            
            backstory_seeds = [
                f"A {origin_info.get('name', 'character')} with {power_info.get('name', 'abilities')} operating in {location_info}"
            ]
        
        character_analysis = {
            "id": character_id,
            "image_name": filename,
            "genre_universe": context["genre"],
            "character_origin": context["origin"],
            "social_status": context["social_status"],
            "power_source": context["power_source"],
            "evolution_stage": context["evolution_stage"],
            "geographic_context": context["geographic_context"],
            "archetype_tags": context["tags"],
            "traits": traits,
            "mood": f"Calculated confidence with underlying tension - the weight of operating 15 moves ahead in {location_info}'s complex power dynamics",
            "backstory_seeds": backstory_seeds,
            "power_suggestions": power_suggestions,
            "persona_summary": f"A sophisticated {origin_info.get('name', 'individual')} who transformed {context['social_status'].replace('_', ' ')} background through {power_info.get('name', 'enhancement')} into systematic advantage. Operating from {location_info}, they've learned to navigate complex power structures while building their own empire through strategic thinking and calculated risk-taking. Their {context['evolution_stage'].replace('_', ' ')} represents the pinnacle of human potential enhanced by cutting-edge enhancement.",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return character_analysis
        
    except Exception as e:
        logger.error(f"Sophisticated analysis creation failed: {e}")
        return await create_simple_fallback_analysis(filename, context)

async def create_simple_fallback_analysis(filename: str, context: Dict) -> Dict[str, Any]:
    """Fallback analysis if sophisticated version fails"""
    return {
        "id": str(uuid.uuid4()),
        "image_name": filename,
        "traits": [{"category": "Analysis", "trait": "Character analysis in progress", "confidence": 0.5}],
        "mood": f"Character from {context.get('geographic_context', 'unknown location')}",
        "backstory_seeds": [f"A {context.get('origin', 'character')} with {context.get('power_source', 'abilities')}"],
        "power_suggestions": [{"name": "Enhanced Abilities", "description": "Powers in development", "limitations": "Analysis incomplete", "cost_level": 5}],
        "persona_summary": "Character analysis requires additional processing",
        "created_at": datetime.utcnow().isoformat()
    }

# Enhanced definitions for backend
ENHANCED_CHARACTER_ORIGINS = {
    "nootropic_enhanced": {"name": "Nootropic Enhanced", "description": "Cognitive enhancement through experimental smart drugs"},
    "biotech_subject": {"name": "Biotech Subject", "description": "Enhanced through cutting-edge biotechnology"},
    "self_optimized": {"name": "Self-Optimized", "description": "Achieved enhancement through systematic self-improvement"},
    "metahuman": {"name": "Metahuman", "description": "Human with acquired supernatural abilities"},
    "enhanced_human": {"name": "Enhanced Human", "description": "Human with augmented abilities"}
}

ENHANCED_POWER_SOURCES = {
    "nootropic_drug": {"name": "Experimental Nootropic Drug", "description": "NZT-48 style cognitive enhancement"},
    "meta_drug": {"name": "Meta-Enhancement Drug", "description": "Advanced biochemical enhancement"},
    "neural_enhancement": {"name": "Neural Network Optimization", "description": "Direct brain enhancement"},
    "self_evolution": {"name": "Conscious Self-Evolution", "description": "Systematic self-improvement"},
    "biotech_implant": {"name": "Biotech Implantation", "description": "Integrated biotechnology"}
}

GEOGRAPHIC_CONTEXTS = {
    "detroit": "Detroit - Industrial Rebirth Hub",
    "chicago": "Chicago - Urban Power Center", 
    "new_york": "New York - Financial Capital",
    "miami": "Miami - International Gateway",
    "multi_city": "Multi-City Operations Network"
}

async def get_enhanced_character_analysis(image_data: bytes, filename: str, context: Dict) -> Dict[str, Any]:
    """Enhanced character analysis with comprehensive parameters"""
    try:
        
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
        
        # Create full prompt for Ollama vision model
        full_prompt = system_prompt + "\n\nAnalyze this character image with the given context parameters."
        
        response = await get_image_analysis(image_b64, full_prompt)
        
        # Parse response
        response_text = response
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
        result = await get_creative_text_generation(
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

@api_router.post("/check-continuity")
async def check_continuity(request: dict):
    """Check continuity and rule violations for character content"""
    try:
        character_id = request.get("character_id")
        new_content = request.get("content", "")
        content_type = request.get("content_type", "general")
        
        if not character_id or not new_content:
            raise HTTPException(status_code=400, detail="character_id and content are required")
        
        # Check for continuity conflicts
        vector_db = get_vector_db()
        continuity_conflicts = await vector_db.check_continuity_conflicts(
            character_id, new_content, content_type
        )
        
        # Check style rules
        style_violations = check_style_rules(new_content, content_type)
        
        # If this is character data, run character rules too
        character_violations = []
        if content_type == "character_update":
            character_data = request.get("character_data", {})
            character_violations = check_character_rules(character_data)
        
        return {
            "continuity_conflicts": [
                {
                    "conflict_type": c.conflict_type,
                    "severity": c.severity,
                    "existing_content": c.existing_content,
                    "new_content": c.new_content,
                    "similarity_score": c.similarity_score,
                    "suggested_resolution": c.suggested_resolution
                } for c in continuity_conflicts
            ],
            "style_violations": [
                {
                    "rule_name": v.rule_name,
                    "severity": v.severity.value,
                    "message": v.message,
                    "explanation": v.explanation,
                    "quick_fix": v.quick_fix,
                    "affected_content": v.affected_content,
                    "suggested_replacement": v.suggested_replacement
                } for v in style_violations
            ],
            "character_violations": [
                {
                    "rule_name": v.rule_name,
                    "severity": v.severity.value,
                    "message": v.message,
                    "explanation": v.explanation,
                    "quick_fix": v.quick_fix,
                    "suggested_replacement": v.suggested_replacement
                } for v in character_violations
            ],
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Continuity check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Continuity check failed: {str(e)}")

@api_router.get("/rule-engine/status")
async def get_rule_engine_status():
    """Get status and capabilities of the rule engine"""
    try:
        engine = get_rule_engine()
        rule_summary = engine.get_rule_summary()
        
        return {
            "status": "active",
            "rule_summary": rule_summary,
            "capabilities": [
                "Power cost validation",
                "Character consistency checking", 
                "Origin-power compatibility",
                "Timeline consistency",
                "Cliché detection",
                "Show-don't-tell analysis",
                "Continuity conflict detection"
            ],
            "version": "1.0.0-phase1"
        }
        
    except Exception as e:
        logger.error(f"Rule engine status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Rule engine status failed: {str(e)}")

# Beat Sheet Generator Endpoints
@api_router.post("/generate-beat-sheet")
async def generate_beat_sheet_endpoint(request: dict):
    """Generate a beat sheet using Ollama for intelligent adaptation"""
    try:
        from beat_sheet_generator import get_beat_sheet_generator, BeatSheetType, TonePacing
        
        # Parse request parameters
        sheet_type = BeatSheetType(request.get("sheet_type", "save_the_cat"))
        tone_pacing = TonePacing(request.get("tone_pacing", "standard"))
        story_length = int(request.get("story_length", 110))
        character_data = request.get("character_data", {})
        
        # Generate base beat sheet
        generator = get_beat_sheet_generator()
        beat_sheet = generator.generate_beat_sheet(
            sheet_type=sheet_type,
            character_data=character_data,
            tone_pacing=tone_pacing,
            story_length=story_length
        )
        
        # Use Ollama to enhance beat descriptions if character data provided
        if character_data:
            enhanced_beats = await enhance_beats_with_ollama(beat_sheet.beats, character_data)
            beat_sheet.beats = enhanced_beats
        
        # Convert to dict for JSON response
        result = {
            "sheet_type": beat_sheet.sheet_type.value,
            "title": beat_sheet.title,
            "description": beat_sheet.description,
            "total_beats": beat_sheet.total_beats,
            "estimated_pages": beat_sheet.estimated_pages,
            "tone_pacing": beat_sheet.tone_pacing.value,
            "beats": [
                {
                    "beat_number": beat.beat_number,
                    "beat_name": beat.beat_name,
                    "description": beat.description,
                    "page_range": beat.page_range,
                    "percentage": beat.percentage,
                    "tone_notes": beat.tone_notes,
                    "character_focus": beat.character_focus,
                    "plot_function": beat.plot_function,
                    "marcus_style_adaptation": beat.marcus_style_adaptation
                } for beat in beat_sheet.beats
            ],
            "character_integration_notes": beat_sheet.character_integration_notes,
            "marcus_adaptations": beat_sheet.marcus_adaptations
        }
        
        return {"beat_sheet": result, "success": True, "message": "Beat sheet generated successfully"}
        
    except Exception as e:
        logger.error(f"Beat sheet generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Beat sheet generation failed: {str(e)}")

@api_router.get("/beat-sheet-types")
async def get_beat_sheet_types():
    """Get available beat sheet types"""
    from beat_sheet_generator import BeatSheetType, TonePacing
    
    return {
        "sheet_types": [
            {"value": "save_the_cat", "name": "Save the Cat (15 beats)", "description": "Blake Snyder's character-focused structure"},
            {"value": "dan_harmon", "name": "Dan Harmon Story Circle", "description": "8-step circular story emphasizing character growth"},
            {"value": "three_act", "name": "Three-Act Structure", "description": "Classic dramatic structure"},
            {"value": "hero_journey", "name": "Hero's Journey", "description": "Campbell's monomyth structure"},
            {"value": "kishōtenketsu", "name": "Kishōtenketsu", "description": "4-act Japanese narrative structure"}
        ],
        "tone_pacing": [
            {"value": "slow_burn", "name": "Slow Burn", "description": "Extended setup, gradual escalation"},
            {"value": "standard", "name": "Standard", "description": "Balanced pacing"},
            {"value": "fast_paced", "name": "Fast Paced", "description": "Quick setup, rapid progression"},
            {"value": "explosive", "name": "Explosive", "description": "Minimal setup, intense action"}
        ]
    }

async def enhance_beats_with_ollama(beats, character_data: Dict) -> List:
    """Use Ollama to enhance beat descriptions based on character data"""
    try:
        # Create character context for AI enhancement
        character_context = f"""
Character Context:
- Origin: {character_data.get('character_origin', 'Unknown')}
- Power Source: {character_data.get('power_source', 'Unknown')}
- Traits: {', '.join([trait.get('trait', '') for trait in character_data.get('traits', [])])}
- Backstory: {', '.join(character_data.get('backstory_seeds', []))}
- Powers: {', '.join([power.get('name', '') for power in character_data.get('power_suggestions', [])])}
"""
        
        enhanced_beats = []
        for beat in beats:
            # Create enhancement prompt for each beat
            prompt = f"""Enhance this story beat description to fit the specific character provided. Keep the core structure but adapt the details to match the character's abilities, background, and personality.

{character_context}

Beat to enhance:
Name: {beat.beat_name}
Description: {beat.description}
Character Focus: {beat.character_focus}
Plot Function: {beat.plot_function}

Provide an enhanced description that:
1. Maintains the beat's structural purpose
2. Integrates the character's specific traits and abilities
3. Suggests concrete scenes or actions fitting this character
4. Keeps the same tone and pacing

Enhanced description:"""
            
            try:
                enhanced_description = await ollama_text_generation(prompt, temperature=0.6)
                beat.description = enhanced_description.strip()
            except Exception as e:
                logger.warning(f"Failed to enhance beat {beat.beat_number}: {e}")
                # Keep original description if enhancement fails
            
            enhanced_beats.append(beat)
        
        return enhanced_beats
        
    except Exception as e:
        logger.warning(f"Beat enhancement failed, returning original beats: {e}")
        return beats

# Enhanced Trope Risk Meter Endpoints
@api_router.post("/analyze-trope-risk")
async def analyze_trope_risk_endpoint(request: dict):
    """Analyze character for trope usage and freshness with Ollama enhancement"""
    try:
        from enhanced_trope_meter import get_trope_risk_meter
        
        character_data = request.get("character_data", {})
        
        if not character_data:
            raise HTTPException(status_code=400, detail="Character data required")
        
        # Analyze tropes
        meter = get_trope_risk_meter()
        trope_profile = meter.analyze_character_tropes(character_data)
        
        # Enhance suggestions using Ollama (with fallback)
        try:
            enhanced_suggestions = await asyncio.wait_for(
                enhance_trope_suggestions_with_ollama(
                    trope_profile.improvement_suggestions,
                    trope_profile.trope_analyses,
                    character_data
                ),
                timeout=20.0  # 20 second total timeout for the enhancement
            )
        except asyncio.TimeoutError:
            logger.warning("Trope suggestion enhancement timed out, using base suggestions")
            enhanced_suggestions = trope_profile.improvement_suggestions
        except Exception as e:
            logger.warning(f"Enhancement failed, using base suggestions: {e}")
            enhanced_suggestions = trope_profile.improvement_suggestions
        
        # Convert to dict for JSON response
        result = {
            "character_id": trope_profile.character_id,
            "overall_freshness_score": round(trope_profile.overall_freshness_score, 3),
            "marcus_level_rating": round(trope_profile.marcus_level_rating, 3),
            "freshness_rating": _get_freshness_rating(trope_profile.overall_freshness_score),
            "trope_analyses": [
                {
                    "trope_name": analysis.trope_name,
                    "cliche_score": round(analysis.cliché_score, 3),
                    "freshness_level": analysis.freshness_level.value,
                    "usage_frequency": analysis.usage_frequency,
                    "subversion_suggestions": analysis.subversion_suggestions[:3],  # Limit for UI
                    "combination_alternatives": analysis.combination_alternatives[:2]
                } for analysis in trope_profile.trope_analyses
            ],
            "risk_factors": trope_profile.risk_factors,
            "strength_factors": trope_profile.strength_factors,
            "improvement_suggestions": enhanced_suggestions,
            "marcus_adaptations": [
                "Replace simple motivation with complex systemic goals",
                "Add realistic business/political constraints",
                "Show character using strategy over force",
                "Explore moral ambiguity in character's methods"
            ]
        }
        
        return {"trope_analysis": result, "success": True, "message": "Trope analysis completed successfully"}
        
    except Exception as e:
        logger.error(f"Trope analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Trope analysis failed: {str(e)}")

def _get_freshness_rating(score: float) -> str:
    """Convert freshness score to human-readable rating"""
    if score >= 0.8:
        return "Highly Original"
    elif score >= 0.6:
        return "Fresh and Engaging"
    elif score >= 0.4:
        return "Moderately Fresh"
    elif score >= 0.2:
        return "Somewhat Clichéd"
    else:
        return "Needs Innovation"

async def enhance_trope_suggestions_with_ollama(base_suggestions: List[str], trope_analyses, character_data: Dict) -> List[str]:
    """Use Ollama to enhance and personalize trope improvement suggestions with timeout protection"""
    try:
        # Quick timeout protection - if we have good base suggestions, use them
        if len(base_suggestions) >= 3:
            # Try Ollama enhancement with short timeout
            try:
                # Create simplified character context for faster processing
                high_risk_tropes = [t.trope_name for t in trope_analyses if t.cliché_score > 0.6]
                fresh_elements = [t.trope_name for t in trope_analyses if t.cliché_score < 0.3]
                
                prompt = f"""Character: {character_data.get('character_origin', 'Unknown')} with {character_data.get('power_source', 'Unknown')} powers.

High-risk tropes: {', '.join(high_risk_tropes[:3])}
Fresh elements: {', '.join(fresh_elements[:2])}

Provide 3 specific suggestions to improve this character's originality:
1. How to subvert the highest-risk trope
2. How to build on fresh elements  
3. One concrete scene/story idea

Suggestions:"""
                
                # Use shorter, more focused prompt and lower temperature for speed
                response = await asyncio.wait_for(
                    ollama_text_generation(prompt, temperature=0.5), 
                    timeout=15.0  # 15 second timeout
                )
                
                # Simple parsing - look for numbered suggestions
                enhanced_suggestions = []
                for line in response.split('\n'):
                    line = line.strip()
                    if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('-')):
                        suggestion = re.sub(r'^[-\d.]+\s*', '', line)
                        if suggestion and len(suggestion) > 10:  # Basic quality check
                            enhanced_suggestions.append(suggestion)
                
                if len(enhanced_suggestions) >= 2:  # If we got decent results
                    return enhanced_suggestions[:5]
                    
            except asyncio.TimeoutError:
                logger.warning("Ollama enhancement timed out, using base suggestions")
            except Exception as ollama_error:
                logger.warning(f"Ollama enhancement failed: {ollama_error}")
        
        # Fallback: return enhanced base suggestions
        return base_suggestions
        
    except Exception as e:
        logger.warning(f"Failed to enhance suggestions: {e}")
        return base_suggestions

# Content Safety & Model Selection Endpoints
@api_router.get("/ai-providers")
async def get_ai_providers():
    """Get available AI providers and their status"""
    try:
        hybrid_client = get_hybrid_ai_client()
        providers = hybrid_client.get_available_providers()
        status = hybrid_client.get_provider_status()
        
        # Combine provider info with status
        for provider in providers:
            provider_id = provider["id"]
            provider["status"] = status.get(provider_id, {"available": False, "status": "unknown"})
        
        return {
            "providers": providers,
            "default_provider": hybrid_client.default_provider.value,
            "success": True
        }
    except Exception as e:
        logger.error(f"Failed to get AI providers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get AI providers: {str(e)}")

@api_router.post("/set-default-provider")
async def set_default_provider(request: dict):
    """Set default AI provider"""
    try:
        provider_id = request.get("provider")
        if not provider_id:
            raise HTTPException(status_code=400, detail="Provider ID required")
        
        try:
            provider = AIProvider(provider_id)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider_id}")
        
        hybrid_client = get_hybrid_ai_client()
        hybrid_client.set_default_provider(provider)
        
        return {
            "message": f"Default provider set to {provider.value}",
            "provider": provider.value,
            "success": True
        }
    except Exception as e:
        logger.error(f"Failed to set default provider: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/content-safety-levels")
async def get_content_safety_levels():
    """Get available content safety levels"""
    try:
        content_filter = get_content_filter()
        
        levels = []
        for level in ContentSafetyLevel:
            info = content_filter.get_safety_level_info(level)
            levels.append({
                "id": level.value,
                "name": level.value.title(),
                "description": info["description"],
                "target_audience": info["target_audience"],
                "allowed_categories": [cat.value for cat in info["allowed_categories"]]
            })
        
        return {"safety_levels": levels, "success": True}
        
    except Exception as e:
        logger.error(f"Failed to get safety levels: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/analyze-content-safety")
async def analyze_content_safety(request: dict):
    """Analyze content against safety guidelines"""
    try:
        text = request.get("text", "")
        safety_level = request.get("safety_level", "moderate")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text content required")
        
        try:
            level = ContentSafetyLevel(safety_level)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid safety level: {safety_level}")
        
        content_filter = get_content_filter()
        result = content_filter.analyze_content(text, level)
        
        return {
            "allowed": result.allowed,
            "safety_level": result.safety_level.value,
            "flagged_categories": [cat.value for cat in result.flagged_categories],
            "suggestions": result.suggestions,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Content safety analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Updated analyze-image endpoint with hybrid AI and content filtering
@api_router.post("/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    genre: str = "urban_realistic",
    origin: str = "human",
    social_status: str = "middle_class", 
    power_source: str = "none",
    tags: str = "",
    op_mode: str = "false",
    ai_provider: str = "ollama",
    safety_level: str = "moderate"
):
    """Enhanced image analysis with hybrid AI and content filtering"""
    try:
        # Validate inputs
        try:
            provider = AIProvider(ai_provider)
        except ValueError:
            provider = AIProvider.OLLAMA  # Default fallback
        
        try:
            content_safety = ContentSafetyLevel(safety_level)
        except ValueError:
            content_safety = ContentSafetyLevel.MODERATE  # Default fallback
        
        # Read image
        image_data = await file.read()
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        # Parse tags
        archetype_tags = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
        op_mode_bool = op_mode.lower() == "true"
        
        # Use hybrid AI client for analysis
        hybrid_client = get_hybrid_ai_client()
        
        # Stage 1: Visual Extraction
        stage1_prompt = f"""Extract visual details only. No speculation about personality or powers.
        
Safety Level: {content_safety.value} - {get_content_filter().get_safety_level_info(content_safety)['description']}
            
Return JSON:
{{
  "appearance": "Physical description",
  "clothing": "Detailed clothing description", 
  "setting": "Environment details",
  "pose_expression": "Body language and expression",
  "style_aesthetic": "Overall visual style"
}}

Extract visual details from this image."""
        
        stage1_response = await hybrid_client.analyze_image(
            image_b64, stage1_prompt, provider, content_safety
        )
        stage1_data = await parse_json_response(stage1_response)
        
        # Stage 2: Genre-Adapted Analysis (if applicable)
        genre_data = {}
        if genre and genre in GENRES:
            genre_data = await get_genre_adapted_analysis_hybrid(
                stage1_data, genre, provider, content_safety
            )
        
        # Stage 3: Integrated Character Creation
        stage3_prompt = f"""Create a cohesive character profile that integrates visual analysis with genre context.
        
Safety Level: {content_safety.value}
            
Focus on:
- Realistic abilities that fit both appearance and genre
- Complex personality traits beyond surface observations
- Backstory that explains the visual elements
- Professional/clinical terminology for abilities

Avoid generic fantasy terms. Use specific, grounded language.

Return JSON with the following structure:
{{
  "traits": ["trait1", "trait2", "trait3"],
  "mood": "character mood",
  "realistic_backstory_seeds": ["seed1", "seed2", "seed3"],
  "realistic_abilities": [{{"name": "ability", "description": "desc", "limitations": "limits", "cost_level": 3}}],
  "persona_summary": "comprehensive character summary"
}}

Context to integrate:
Visual: {stage1_data}"""
        
        if genre_data:
            stage3_prompt += f"\nGenre Context: {genre_data}"
        
        stage3_response = await hybrid_client.generate_text(
            stage3_prompt, provider, content_safety, temperature=0.7
        )
        stage3_data = await parse_json_response(stage3_response)
        
        # Combine results with enhanced data structure
        final_result = {
            "id": str(uuid.uuid4()),
            "traits": stage3_data.get("traits", []),
            "mood": stage3_data.get("mood", "Unknown"),
            "backstory_seeds": stage3_data.get("realistic_backstory_seeds", genre_data.get("genre_backstory_elements", [])),
            "power_suggestions": genre_data.get("genre_adapted_powers", stage3_data.get("realistic_abilities", [])),
            "persona_summary": stage3_data.get("persona_summary", ""),
            "genre_context": genre_data.get("universe_connections", "") if genre else "",
            "visual_analysis": stage1_data,
            
            # Enhanced metadata
            "character_origin": origin,
            "social_status": social_status,
            "power_source": power_source,
            "archetype_tags": archetype_tags,
            "genre": genre,
            "op_mode": op_mode_bool,
            "ai_provider": provider.value,
            "safety_level": content_safety.value,
            "created_at": datetime.now().isoformat()
        }
        
        # Store in database with enhanced structure
        await db.character_analyses.insert_one(final_result.copy())
        
        return {"analysis": final_result, "success": True, "message": f"Character analyzed using {provider.value} with {content_safety.value} safety level"}
        
    except Exception as e:
        logger.error(f"Enhanced image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

async def get_genre_adapted_analysis_hybrid(visual_data: Dict, genre: str, 
                                          provider: AIProvider,
                                          safety_level: ContentSafetyLevel) -> Dict[str, Any]:
    """Genre analysis using hybrid AI with content filtering"""
    try:
        genre_info = GENRES.get(genre, GENRES["urban_realistic"])
        
        prompt = f"""You are a {genre_info['name']} character expert. Adapt this character analysis to fit the {genre_info['name']} universe.

Safety Level: {safety_level.value}

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

Make it feel authentic to {genre_info['name']} while respecting the character's visual appearance.

Visual Analysis: {visual_data}

Adapt this character for {genre_info['name']}:"""
        
        hybrid_client = get_hybrid_ai_client()
        response = await hybrid_client.generate_text(prompt, provider, safety_level, temperature=0.7)
        return await parse_json_response(response)
        
    except Exception as e:
        logger.error(f"Genre adaptation failed: {e}")
        return {}

# Initialize systems on startup
@app.on_event("startup")
async def startup_event():
    """Initialize all VisionForge systems"""
    logger.info("Initializing VisionForge systems...")
    
    # Initialize knowledge graph (graceful failure in dev)
    try:
        initialize_knowledge_graph()
        logger.info("✅ Knowledge Graph initialized")
    except Exception as e:
        logger.warning(f"⚠️ Knowledge Graph initialization failed (dev mode): {e}")
    
    # Initialize vector database (graceful failure in dev)
    try:
        initialize_vector_db()
        logger.info("✅ Vector Database initialized")
    except Exception as e:
        logger.warning(f"⚠️ Vector Database initialization failed (dev mode): {e}")
    
    # Initialize rule engine
    try:
        get_rule_engine()
        logger.info("✅ Rule Engine initialized")
    except Exception as e:
        logger.error(f"❌ Rule Engine initialization failed: {e}")
    
    logger.info("🚀 VisionForge enhanced systems ready!")

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