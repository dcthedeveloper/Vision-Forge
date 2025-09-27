"""
VisionForge Beat-Sheet Generator - Phase 2 Implementation
Handles Save the Cat, Dan Harmon Circle, 3-Act structure with tunable tone/pace
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class BeatSheetType(Enum):
    SAVE_THE_CAT = "save_the_cat"
    DAN_HARMON = "dan_harmon"  
    THREE_ACT = "three_act"
    HERO_JOURNEY = "hero_journey"
    KISHŌTENKETSU = "kishōtenketsu"  # 4-act Japanese structure

class TonePacing(Enum):
    SLOW_BURN = "slow_burn"
    STANDARD = "standard"
    FAST_PACED = "fast_paced"
    EXPLOSIVE = "explosive"

@dataclass
class BeatPoint:
    beat_number: int
    beat_name: str
    description: str
    page_range: str  # e.g., "1-10", "25-30"
    percentage: float  # Percentage through story (0.0-1.0)
    tone_notes: str
    character_focus: str
    plot_function: str
    marcus_style_adaptation: Optional[str] = None  # How this applies to sophisticated characters

@dataclass
class BeatSheet:
    sheet_type: BeatSheetType
    title: str
    description: str
    total_beats: int
    estimated_pages: int
    tone_pacing: TonePacing
    beats: List[BeatPoint]
    character_integration_notes: List[str]
    marcus_adaptations: List[str]  # How to adapt for complex characters like Marcus

class VisionForgeBeatSheetGenerator:
    def __init__(self):
        self.beat_templates = self._initialize_beat_templates()
    
    def _initialize_beat_templates(self) -> Dict[str, Any]:
        """Initialize beat sheet templates"""
        return {
            BeatSheetType.SAVE_THE_CAT: self._create_save_the_cat_template(),
            BeatSheetType.DAN_HARMON: self._create_dan_harmon_template(),
            BeatSheetType.THREE_ACT: self._create_three_act_template(),
            BeatSheetType.HERO_JOURNEY: self._create_hero_journey_template(),
            BeatSheetType.KISHŌTENKETSU: self._create_kishotenketsu_template()
        }
    
    def _create_save_the_cat_template(self) -> Dict[str, Any]:
        """Blake Snyder's Save the Cat 15-beat structure"""
        return {
            "title": "Save the Cat! (Blake Snyder)",
            "description": "15-beat structure focusing on character likability and clear story progression",
            "total_beats": 15,
            "estimated_pages": 110,
            "beats": [
                {
                    "beat_number": 1,
                    "beat_name": "Opening Image",
                    "description": "A visual that represents the struggle & tone of the story",
                    "page_range": "1",
                    "percentage": 0.01,
                    "tone_notes": "Sets visual and emotional tone",
                    "character_focus": "Protagonist in their 'before' state",
                    "plot_function": "Hook the audience",
                    "marcus_style_adaptation": "Show Marcus in his business world before cognitive enhancement - successful but limited"
                },
                {
                    "beat_number": 2,
                    "beat_name": "Theme Stated",
                    "description": "What your story is about; the message, the truth",
                    "page_range": "5",
                    "percentage": 0.05,
                    "tone_notes": "Often subtle, sometimes by secondary character",
                    "character_focus": "Usually not the protagonist speaking",
                    "plot_function": "Plant the story's deeper meaning",
                    "marcus_style_adaptation": "Someone mentions the cost of power or 'being careful what you wish for' before Marcus's transformation"
                },
                {
                    "beat_number": 3,
                    "beat_name": "Set-Up",
                    "description": "Expand the world and introduce characters",
                    "page_range": "1-10",
                    "percentage": 0.10,
                    "tone_notes": "Establish normal world and relationships",
                    "character_focus": "Protagonist and supporting cast",
                    "plot_function": "Show the 'ordinary world' that needs changing",
                    "marcus_style_adaptation": "Marcus's pre-enhancement business dealings, showing his natural intelligence but hitting systemic barriers"
                },
                {
                    "beat_number": 4,
                    "beat_name": "Catalyst",
                    "description": "The moment that changes everything",
                    "page_range": "12",
                    "percentage": 0.12,
                    "tone_notes": "Can be positive, negative, or neutral event",
                    "character_focus": "Happens TO the protagonist",
                    "plot_function": "Disrupts the ordinary world",
                    "marcus_style_adaptation": "Marcus discovers or gains access to the experimental nootropic drug"
                },
                {
                    "beat_number": 5,
                    "beat_name": "Debate",
                    "description": "Should I go? Doubts about the journey ahead",
                    "page_range": "12-25", 
                    "percentage": 0.25,
                    "tone_notes": "Internal conflict and hesitation",
                    "character_focus": "Protagonist's internal struggle",
                    "plot_function": "Show stakes and protagonist's reluctance",
                    "marcus_style_adaptation": "Marcus weighs the risks of taking an experimental drug vs. continuing to fight systemic limitations"
                },
                {
                    "beat_number": 6,
                    "beat_name": "Break Into Two",
                    "description": "Leaving the familiar world and entering a new one",
                    "page_range": "25",
                    "percentage": 0.25,
                    "tone_notes": "Major story shift - no going back",
                    "character_focus": "Protagonist makes the choice",
                    "plot_function": "Commit to the story's main conflict",
                    "marcus_style_adaptation": "Marcus takes the drug and begins experiencing enhanced cognition"
                },
                {
                    "beat_number": 7,
                    "beat_name": "B Story",
                    "description": "New character who will help explore the theme",
                    "page_range": "30",
                    "percentage": 0.30,
                    "tone_notes": "Often a love interest or mentor figure",
                    "character_focus": "Introduction of key supporting character",
                    "plot_function": "Provides different perspective on theme",
                    "marcus_style_adaptation": "Marcus encounters someone who challenges his new worldview or represents what he's becoming"
                },
                {
                    "beat_number": 8,
                    "beat_name": "Fun and Games",
                    "description": "Promise of the premise; why we wanted to see this movie",
                    "page_range": "30-55",
                    "percentage": 0.55,
                    "tone_notes": "Most entertaining section of the story",
                    "character_focus": "Protagonist exploring new world/abilities",
                    "plot_function": "Deliver on the story's central promise",
                    "marcus_style_adaptation": "Marcus uses his enhanced abilities to build his empire, outsmart competitors, solve complex problems"
                },
                {
                    "beat_number": 9,
                    "beat_name": "Midpoint",
                    "description": "Halfway point where stakes are raised",
                    "page_range": "55",
                    "percentage": 0.50,
                    "tone_notes": "False victory or false defeat",
                    "character_focus": "Protagonist seems to win or lose everything",
                    "plot_function": "Raise stakes and refocus story",
                    "marcus_style_adaptation": "Marcus achieves a major business victory but realizes the personal cost or discovers the drug's true origin"
                },
                {
                    "beat_number": 10,
                    "beat_name": "Bad Guys Close In",
                    "description": "Doubt, jealousy, fear, foes both external and internal",
                    "page_range": "55-75",
                    "percentage": 0.75,
                    "tone_notes": "Building tension and complications",
                    "character_focus": "Antagonistic forces gathering strength",
                    "plot_function": "Create maximum pressure on protagonist",
                    "marcus_style_adaptation": "Federal investigation intensifies, competitors unite against him, or drug side effects threaten his sanity"
                },
                {
                    "beat_number": 11,
                    "beat_name": "All Is Lost",
                    "description": "Lowest point; opposite of the Midpoint",
                    "page_range": "75",
                    "percentage": 0.75,
                    "tone_notes": "Darkest moment of the story",
                    "character_focus": "Protagonist at their lowest",
                    "plot_function": "Force protagonist to dig deepest",
                    "marcus_style_adaptation": "Marcus loses everything he's built, or faces the reality that the enhancement is destroying his humanity"
                },
                {
                    "beat_number": 12,
                    "beat_name": "Dark Night of the Soul",
                    "description": "Moment before the final effort; contemplation of theme",
                    "page_range": "75-85",
                    "percentage": 0.85,
                    "tone_notes": "Quiet, internal moment",
                    "character_focus": "Protagonist's deepest reflection",
                    "plot_function": "Prepare for final transformation",
                    "marcus_style_adaptation": "Marcus confronts what he's become and decides what kind of person/leader he wants to be"
                },
                {
                    "beat_number": 13,
                    "beat_name": "Break Into Three",
                    "description": "Thanks to a fresh idea, the protagonist chooses to try again",
                    "page_range": "85",
                    "percentage": 0.85,
                    "tone_notes": "Renewed energy and purpose",
                    "character_focus": "Protagonist reborn/recommitted",
                    "plot_function": "Launch the final conflict",
                    "marcus_style_adaptation": "Marcus finds a way to use his enhancement for community benefit while maintaining his empire"
                },
                {
                    "beat_number": 14,
                    "beat_name": "Finale",
                    "description": "Protagonist confronts antagonistic force and wins",
                    "page_range": "85-110",
                    "percentage": 1.0,
                    "tone_notes": "Exciting climax and resolution",
                    "character_focus": "Protagonist transformed and victorious",
                    "plot_function": "Resolve main conflict and prove theme",
                    "marcus_style_adaptation": "Marcus uses strategic thinking to outmaneuver all opponents while staying true to his community values"
                },
                {
                    "beat_number": 15,
                    "beat_name": "Final Image",
                    "description": "Opposite of Opening Image, proving change has occurred",
                    "page_range": "110",
                    "percentage": 1.0,
                    "tone_notes": "Visual proof of transformation",
                    "character_focus": "Protagonist in their 'after' state",
                    "plot_function": "Show the completion of character arc",
                    "marcus_style_adaptation": "Marcus in his new role as both successful businessman and community protector, showing integrated identity"
                }
            ]
        }
    
    def _create_dan_harmon_template(self) -> Dict[str, Any]:
        """Dan Harmon's Story Circle (based on Hero's Journey)"""
        return {
            "title": "Dan Harmon Story Circle",
            "description": "8-step circular story structure emphasizing character needs and growth",
            "total_beats": 8,
            "estimated_pages": 110,
            "beats": [
                {
                    "beat_number": 1,
                    "beat_name": "YOU (Order)",
                    "description": "Character in familiar situation",
                    "page_range": "1-15",
                    "percentage": 0.125,
                    "tone_notes": "Establish normal world",
                    "character_focus": "Protagonist in comfort zone",
                    "plot_function": "Show what character has",
                    "marcus_style_adaptation": "Marcus as successful but constrained businessman in Detroit's existing power structures"
                },
                {
                    "beat_number": 2,
                    "beat_name": "NEED (Order)",
                    "description": "But they want something",
                    "page_range": "15-25",
                    "percentage": 0.25,
                    "tone_notes": "Establish driving desire",
                    "character_focus": "What protagonist lacks",
                    "plot_function": "Create motivation for change",
                    "marcus_style_adaptation": "Marcus wants to transcend systemic barriers and truly change Detroit's economic landscape"
                },
                {
                    "beat_number": 3,
                    "beat_name": "GO (Chaos)",
                    "description": "Enter unfamiliar situation",
                    "page_range": "25-40",
                    "percentage": 0.375,
                    "tone_notes": "Leave comfort zone",
                    "character_focus": "Protagonist takes action",
                    "plot_function": "Begin the adventure/transformation",
                    "marcus_style_adaptation": "Marcus begins experimenting with cognitive enhancement and enters a new level of mental capability"
                },
                {
                    "beat_number": 4,
                    "beat_name": "SEARCH (Chaos)",
                    "description": "Adapt to unfamiliar situation",
                    "page_range": "40-55",
                    "percentage": 0.5,
                    "tone_notes": "Learning and adaptation",
                    "character_focus": "Protagonist struggles and grows",
                    "plot_function": "Face obstacles and learn",
                    "marcus_style_adaptation": "Marcus learns to control and optimize his enhanced abilities while navigating new strategic possibilities"
                },
                {
                    "beat_number": 5,
                    "beat_name": "FIND (Chaos)",
                    "description": "Find what they wanted",
                    "page_range": "55-70",
                    "percentage": 0.625,
                    "tone_notes": "Temporary achievement",
                    "character_focus": "Protagonist gets what they thought they wanted",
                    "plot_function": "Achieve goal but at a cost",
                    "marcus_style_adaptation": "Marcus successfully builds his empire and gains unprecedented influence in Detroit"
                },
                {
                    "beat_number": 6,
                    "beat_name": "TAKE (Chaos)",
                    "description": "Pay heavy price for it",
                    "page_range": "70-85",
                    "percentage": 0.75,
                    "tone_notes": "Consequences and costs",
                    "character_focus": "Protagonist faces the price",
                    "plot_function": "Show true cost of getting what you want",
                    "marcus_style_adaptation": "Marcus faces isolation, federal attention, and questions about what his enhancement is doing to his humanity"
                },
                {
                    "beat_number": 7,
                    "beat_name": "RETURN (Order)",
                    "description": "Return to familiar situation",
                    "page_range": "85-100",
                    "percentage": 0.875,
                    "tone_notes": "Coming home changed",
                    "character_focus": "Protagonist transformed",
                    "plot_function": "Bring new wisdom to old world",
                    "marcus_style_adaptation": "Marcus returns to his community but now with the wisdom to use his power responsibly"
                },
                {
                    "beat_number": 8,
                    "beat_name": "CHANGE (Order)",
                    "description": "Having changed",
                    "page_range": "100-110",
                    "percentage": 1.0,
                    "tone_notes": "New equilibrium",
                    "character_focus": "Protagonist integrated and whole",
                    "plot_function": "Show growth and integration",
                    "marcus_style_adaptation": "Marcus as evolved leader who balances personal power with community responsibility"
                }
            ]
        }
    
    def _create_three_act_template(self) -> Dict[str, Any]:
        """Classic Three-Act Structure"""
        return {
            "title": "Three-Act Structure",
            "description": "Classic dramatic structure with setup, confrontation, and resolution",
            "total_beats": 9,
            "estimated_pages": 120,
            "beats": [
                {
                    "beat_number": 1,
                    "beat_name": "Act I - Setup",
                    "description": "Introduce characters, world, and central conflict",
                    "page_range": "1-30",
                    "percentage": 0.25,
                    "tone_notes": "Establish tone and world",
                    "character_focus": "Protagonist introduction",
                    "plot_function": "Hook audience and establish story world",
                    "marcus_style_adaptation": "Establish Marcus's intelligence, ambition, and the limitations he faces in Detroit's power structure"
                },
                {
                    "beat_number": 2,
                    "beat_name": "Inciting Incident",
                    "description": "Event that sets the story in motion",
                    "page_range": "15-20",
                    "percentage": 0.17,
                    "tone_notes": "Disruption of normal world",
                    "character_focus": "Catalyst affects protagonist",
                    "plot_function": "Launch the main story",
                    "marcus_style_adaptation": "Marcus encounters the experimental nootropic opportunity"
                },
                {
                    "beat_number": 3,
                    "beat_name": "Plot Point 1",
                    "description": "End of Act I; protagonist commits to the story",
                    "page_range": "25-30",
                    "percentage": 0.25,
                    "tone_notes": "Major story shift",
                    "character_focus": "Protagonist's choice",
                    "plot_function": "Launch Act II",
                    "marcus_style_adaptation": "Marcus decides to take the enhancement despite risks"
                }
                # Additional beats would continue here...
            ]
        }
    
    def _create_hero_journey_template(self) -> Dict[str, Any]:
        """Campbell's Hero's Journey structure"""
        return {
            "title": "Hero's Journey (Campbell)",
            "description": "Joseph Campbell's monomyth structure with 12 stages",
            "total_beats": 12,
            "estimated_pages": 120,
            "beats": [
                {
                    "beat_number": 1,
                    "beat_name": "Ordinary World",
                    "description": "Hero's normal life before transformation",
                    "page_range": "1-10",
                    "percentage": 0.08,
                    "tone_notes": "Establish baseline normal",
                    "character_focus": "Hero in familiar environment",
                    "plot_function": "Show what hero will leave behind",
                    "marcus_style_adaptation": "Marcus in his pre-enhancement business world"
                },
                {
                    "beat_number": 2,
                    "beat_name": "Call to Adventure",
                    "description": "Hero presented with problem or challenge",
                    "page_range": "10-15",
                    "percentage": 0.12,
                    "tone_notes": "Disruption of normal world",
                    "character_focus": "Hero encounters the catalyst",
                    "plot_function": "Present the central challenge",
                    "marcus_style_adaptation": "Marcus discovers the nootropic opportunity"
                },
                {
                    "beat_number": 3,
                    "beat_name": "Refusal of the Call",
                    "description": "Hero hesitates or refuses the adventure",
                    "page_range": "15-20",
                    "percentage": 0.17,
                    "tone_notes": "Doubt and hesitation",
                    "character_focus": "Hero's reluctance and fear",
                    "plot_function": "Show stakes and hero's humanity",
                    "marcus_style_adaptation": "Marcus weighs risks of experimental enhancement"
                },
                {
                    "beat_number": 4,
                    "beat_name": "Meeting the Mentor",
                    "description": "Hero encounters wise figure who gives advice",
                    "page_range": "20-25",
                    "percentage": 0.21,
                    "tone_notes": "Guidance and preparation",
                    "character_focus": "Hero receives wisdom/tools",
                    "plot_function": "Prepare hero for journey",
                    "marcus_style_adaptation": "Marcus meets someone who understands enhancement potential"
                },
                {
                    "beat_number": 5,
                    "beat_name": "Crossing the Threshold",
                    "description": "Hero commits to adventure and enters new world",
                    "page_range": "25-30",
                    "percentage": 0.25,
                    "tone_notes": "Point of no return",
                    "character_focus": "Hero's commitment",
                    "plot_function": "Launch the main adventure",
                    "marcus_style_adaptation": "Marcus takes the enhancement and enters new cognitive realm"
                },
                {
                    "beat_number": 6,
                    "beat_name": "Tests, Allies, Enemies",
                    "description": "Hero faces challenges and makes allies/enemies",
                    "page_range": "30-60",
                    "percentage": 0.50,
                    "tone_notes": "Learning and growth",
                    "character_focus": "Hero adapts to new world",
                    "plot_function": "Develop character and relationships",
                    "marcus_style_adaptation": "Marcus navigates enhanced abilities while building new alliances"
                }
                # Simplified for space - would include all 12 stages
            ]
        }
    
    def _create_kishotenketsu_template(self) -> Dict[str, Any]:
        """Japanese 4-act structure without conflict"""
        return {
            "title": "Kishōtenketsu (Japanese 4-Act)",
            "description": "4-act Japanese narrative structure emphasizing development over conflict",
            "total_beats": 4,
            "estimated_pages": 100,
            "beats": [
                {
                    "beat_number": 1,
                    "beat_name": "Ki (Introduction)",
                    "description": "Introduce characters and setting",
                    "page_range": "1-25",
                    "percentage": 0.25,
                    "tone_notes": "Gentle introduction",
                    "character_focus": "Character and world establishment",
                    "plot_function": "Set up the story world",
                    "marcus_style_adaptation": "Introduce Marcus and his business environment"
                },
                {
                    "beat_number": 2,
                    "beat_name": "Shō (Development)",
                    "description": "Develop characters and situation",
                    "page_range": "25-50",
                    "percentage": 0.50,
                    "tone_notes": "Gradual development",
                    "character_focus": "Character growth and exploration",
                    "plot_function": "Deepen understanding of characters",
                    "marcus_style_adaptation": "Marcus explores his enhanced capabilities"
                },
                {
                    "beat_number": 3,
                    "beat_name": "Ten (Twist)",
                    "description": "Unexpected development changes everything",
                    "page_range": "50-75",
                    "percentage": 0.75,
                    "tone_notes": "Surprising revelation",
                    "character_focus": "Character faces unexpected situation",
                    "plot_function": "Introduce new perspective or complication",
                    "marcus_style_adaptation": "Marcus discovers unexpected consequences of enhancement"
                },
                {
                    "beat_number": 4,
                    "beat_name": "Ketsu (Conclusion)",
                    "description": "Resolution that brings new understanding",
                    "page_range": "75-100",
                    "percentage": 1.0,
                    "tone_notes": "Thoughtful resolution",
                    "character_focus": "Character integration and wisdom",
                    "plot_function": "Provide satisfying conclusion",
                    "marcus_style_adaptation": "Marcus finds balance between enhancement and humanity"
                }
            ]
        }
    
    def generate_beat_sheet(self, 
                          sheet_type: BeatSheetType, 
                          character_data: Optional[Dict] = None,
                          tone_pacing: TonePacing = TonePacing.STANDARD,
                          story_length: int = 110) -> BeatSheet:
        """Generate a beat sheet adapted for the character"""
        
        template = self.beat_templates[sheet_type]
        
        # Adjust pacing based on tone preference
        adjusted_beats = self._adjust_pacing(template["beats"], tone_pacing, story_length)
        
        # Integrate character-specific adaptations
        if character_data:
            adjusted_beats = self._integrate_character_data(adjusted_beats, character_data)
        
        beat_sheet = BeatSheet(
            sheet_type=sheet_type,
            title=template["title"],
            description=template["description"],
            total_beats=len(adjusted_beats),
            estimated_pages=story_length,
            tone_pacing=tone_pacing,
            beats=[BeatPoint(**beat) for beat in adjusted_beats],
            character_integration_notes=self._generate_integration_notes(character_data),
            marcus_adaptations=self._generate_marcus_adaptations(character_data)
        )
        
        return beat_sheet
    
    def _adjust_pacing(self, beats: List[Dict], pacing: TonePacing, story_length: int) -> List[Dict]:
        """Adjust beat timing based on pacing preference"""
        adjusted = []
        
        pacing_multipliers = {
            TonePacing.SLOW_BURN: {"setup": 1.3, "middle": 0.9, "climax": 1.1},
            TonePacing.STANDARD: {"setup": 1.0, "middle": 1.0, "climax": 1.0},
            TonePacing.FAST_PACED: {"setup": 0.8, "middle": 1.1, "climax": 1.2},
            TonePacing.EXPLOSIVE: {"setup": 0.6, "middle": 1.2, "climax": 1.4}
        }
        
        multiplier = pacing_multipliers[pacing]
        
        for beat in beats:
            adjusted_beat = beat.copy()
            
            # Adjust page ranges based on pacing
            if beat["percentage"] < 0.25:  # Setup
                adjusted_beat["percentage"] *= multiplier["setup"]
            elif beat["percentage"] < 0.75:  # Middle
                adjusted_beat["percentage"] *= multiplier["middle"]  
            else:  # Climax
                adjusted_beat["percentage"] *= multiplier["climax"]
            
            # Update page ranges
            start_page = int(adjusted_beat["percentage"] * story_length)
            if "-" in beat["page_range"]:
                end_page = start_page + 10  # Default span
                adjusted_beat["page_range"] = f"{start_page}-{end_page}"
            else:
                adjusted_beat["page_range"] = str(start_page)
            
            adjusted.append(adjusted_beat)
        
        return adjusted
    
    def _integrate_character_data(self, beats: List[Dict], character_data: Dict) -> List[Dict]:
        """Adapt beats to specific character data"""
        # This would analyze character traits, powers, backstory, etc.
        # and modify beat descriptions to fit the specific character
        
        character_origin = character_data.get("character_origin", "")
        power_source = character_data.get("power_source", "")
        
        adapted_beats = []
        for beat in beats:
            adapted_beat = beat.copy()
            
            # Example: Adapt for nootropic-enhanced character
            if character_origin == "nootropic_enhanced" and power_source == "nootropic_drug":
                if "marcus_style_adaptation" in beat:
                    adapted_beat["description"] = beat["marcus_style_adaptation"]
            
            adapted_beats.append(adapted_beat)
        
        return adapted_beats
    
    def _generate_integration_notes(self, character_data: Optional[Dict]) -> List[str]:
        """Generate notes on how to integrate specific character"""
        if not character_data:
            return ["Beat sheet ready for character integration"]
        
        notes = []
        
        if character_data.get("character_origin") == "nootropic_enhanced":
            notes.extend([
                "Focus on the cognitive transformation journey",
                "Show both benefits and costs of enhancement", 
                "Explore themes of power vs. responsibility",
                "Include community impact of character's choices"
            ])
        
        if character_data.get("op_mode"):
            notes.extend([
                "WARNING: OP character will break traditional story structure",
                "Consider using beat sheet ironically or for deconstruction",
                "Focus on character's boredom/isolation rather than external conflict"
            ])
        
        return notes
    
    def _generate_marcus_adaptations(self, character_data: Optional[Dict]) -> List[str]:
        """Generate Marcus-style sophisticated character adaptations"""
        return [
            "Replace simple 'good vs evil' with complex moral choices",
            "Show character using intelligence/strategy over brute force",
            "Include realistic consequences for enhancement usage",
            "Explore themes of systemic change vs individual power",
            "Ground fantastical elements in realistic business/political context"
        ]

# Singleton instance
beat_sheet_generator = None

def get_beat_sheet_generator():
    """Get or create beat sheet generator instance"""
    global beat_sheet_generator
    if beat_sheet_generator is None:
        beat_sheet_generator = VisionForgeBeatSheetGenerator()
    return beat_sheet_generator