"""
VisionForge Enhanced Trope Risk Meter - Phase 2 Implementation
Real-time freshness vs cliché scoring with alternatives and subversion suggestions
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)

class FreshnessLevel(Enum):
    GROUNDBREAKING = "groundbreaking"  # 0.0-0.1 cliché risk
    FRESH = "fresh"                    # 0.1-0.3 cliché risk
    FAMILIAR = "familiar"              # 0.3-0.6 cliché risk
    CLICHÉD = "clichéd"               # 0.6-0.8 cliché risk
    OVERUSED = "overused"             # 0.8-1.0 cliché risk

@dataclass
class TropeAnalysis:
    trope_name: str
    cliché_score: float  # 0.0 (fresh) to 1.0 (overused)
    freshness_level: FreshnessLevel
    usage_frequency: int  # How often this trope appears in fiction
    subversion_suggestions: List[str]
    combination_alternatives: List[str]
    context_modifiers: Dict[str, float]  # How different contexts affect cliché score

@dataclass
class CharacterTropeProfile:
    character_id: str
    overall_freshness_score: float
    trope_analyses: List[TropeAnalysis] 
    risk_factors: List[str]
    strength_factors: List[str]
    improvement_suggestions: List[str]
    marcus_level_rating: float  # 0-1 scale of sophistication like Marcus

class EnhancedTropeRiskMeter:
    def __init__(self):
        self.trope_database = self._initialize_trope_database()
        self.context_multipliers = self._initialize_context_multipliers()
        self.subversion_strategies = self._initialize_subversion_strategies()
    
    def _initialize_trope_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive trope database with cliché scores"""
        return {
            # Character Origin Tropes
            "chosen_one": {
                "base_cliché_score": 0.95,
                "usage_frequency": 9500,
                "description": "Character destined to save the world",
                "context_modifiers": {
                    "urban_realistic": -0.1,  # Less clichéd in modern settings
                    "fantasy": 0.0,
                    "sci_fi": -0.05
                },
                "subversion_strategies": [
                    "Character actively rejects their destiny",
                    "Multiple 'chosen ones' must work together",
                    "The prophecy was manufactured/fake",
                    "Character chooses their own path despite destiny"
                ]
            },
            "orphaned_hero": {
                "base_cliché_score": 0.85,
                "usage_frequency": 8200,
                "description": "Hero with dead/missing parents",
                "subversion_strategies": [
                    "Parents are alive but estranged for good reasons",
                    "Character has loving adoptive/step family",
                    "Parents' death was the character's fault",
                    "Character's quest is to save parents, not avenge them"
                ]
            },
            "dark_past_mystery": {
                "base_cliché_score": 0.80,
                "usage_frequency": 7800,
                "description": "Character with mysterious traumatic background",
                "subversion_strategies": [
                    "The 'dark past' is actually mundane but character exaggerates it",
                    "Character is open about their past from the beginning",
                    "The past isn't dark - it's complicated but not traumatic",
                    "Character's past is lighter than present circumstances"
                ]
            },
            
            # Marcus-style sophisticated tropes (lower cliché scores)
            "nootropic_enhanced": {
                "base_cliché_score": 0.15,
                "usage_frequency": 150,
                "description": "Character enhanced by experimental cognitive drugs",
                "context_modifiers": {
                    "urban_realistic": -0.05,
                    "cyberpunk": 0.1
                },
                "subversion_strategies": [
                    "Enhancement comes with unexpected social/emotional costs",
                    "Character must periodically 'dumb down' to relate to others",
                    "The enhancement is temporary and character must achieve goals quickly",
                    "Multiple people have access to same enhancement"
                ]
            },
            "system_changer": {
                "base_cliché_score": 0.20,
                "usage_frequency": 300,
                "description": "Character who changes systems from within",
                "subversion_strategies": [
                    "Character becomes part of the system they meant to change",
                    "Changing the system has unintended consequences",
                    "Character realizes the system can't be changed, only replaced",
                    "Multiple systems need changing simultaneously"
                ]
            },
            "power_broker": {
                "base_cliché_score": 0.25,
                "usage_frequency": 450,
                "description": "Character who operates through influence and networks",
                "subversion_strategies": [
                    "Character's network turns against them",
                    "Character must operate without their usual connections",
                    "Character discovers they were being manipulated by their network",
                    "Character chooses direct action over influence"
                ]
            },
            
            # Power/Ability Tropes
            "elemental_powers": {
                "base_cliché_score": 0.90,
                "usage_frequency": 8500,
                "description": "Control over fire, water, earth, air",
                "subversion_strategies": [
                    "Elements behave in scientifically accurate ways (with limitations)",
                    "Character can only control one element but in many forms",
                    "Powers work through technology, not magic",
                    "Character must 'trade' elements - using one makes others weaker"
                ]
            },
            "super_strength": {
                "base_cliché_score": 0.88,
                "usage_frequency": 8000,
                "description": "Physical strength beyond human limits",
                "subversion_strategies": [
                    "Strength comes with proportional clumsiness/control issues",
                    "Character is strong but not durable (can hurt themselves)",
                    "Strength varies with emotional state in unpredictable ways",
                    "Character uses strength cleverly rather than just hitting things"
                ]
            },
            "hypercognitive_processing": {
                "base_cliché_score": 0.12,
                "usage_frequency": 80,
                "description": "Enhanced mental processing speed and capacity",
                "subversion_strategies": [
                    "Character becomes isolated due to processing speed differences",
                    "Enhanced thinking reveals problems character can't solve",
                    "Character must choose between thinking fast and thinking creatively",
                    "Enhancement makes character overconfident in their predictions"
                ]
            },
            
            # Relationship Tropes
            "love_triangle": {
                "base_cliché_score": 0.92,
                "usage_frequency": 9200,
                "description": "Character torn between two love interests",
                "subversion_strategies": [
                    "All three characters end up as friends/colleagues",
                    "Character chooses neither and focuses on personal growth",
                    "The 'triangle' is actually about different life paths",
                    "Character realizes they were projecting their own internal conflict"
                ]
            },
            "mentor_dies": {
                "base_cliché_score": 0.87,
                "usage_frequency": 8100,
                "description": "Wise mentor figure dies to motivate protagonist",
                "subversion_strategies": [
                    "Mentor retires and character must prove independence",
                    "Mentor was wrong about important things, character must surpass them",
                    "Mentor fakes death to test character",
                    "Character becomes mentor to someone else instead"
                ]
            },
            
            # Plot Device Tropes
            "macguffin_quest": {
                "base_cliché_score": 0.75,
                "usage_frequency": 6500,
                "description": "Quest for object that drives the plot",
                "subversion_strategies": [
                    "The object was inside the character all along (literally or metaphorically)",
                    "The quest itself was more important than the object",
                    "Character realizes the object isn't worth the cost",
                    "Multiple objects are needed, requiring collaboration"
                ]
            },
            "deus_ex_machina": {
                "base_cliché_score": 0.95,
                "usage_frequency": 7200,
                "description": "Convenient solution appears from nowhere",
                "subversion_strategies": [
                    "Character creates their own solution through preparation",
                    "The 'convenient' solution comes with a steep price",
                    "Character must choose between convenient solution and right solution",
                    "The solution was set up by character earlier (earned convenience)"
                ]
            }
        }
    
    def _initialize_context_multipliers(self) -> Dict[str, Dict[str, float]]:
        """Context affects how clichéd something feels"""
        return {
            "genre_modifiers": {
                "urban_realistic": {"fantasy_tropes": +0.3, "tech_tropes": -0.1},
                "fantasy": {"fantasy_tropes": 0.0, "tech_tropes": +0.2},
                "sci_fi": {"tech_tropes": -0.05, "magic_tropes": +0.2},
                "superhero": {"power_tropes": -0.1, "ordinary_tropes": +0.1}
            },
            "character_sophistication": {
                "marcus_level": -0.2,  # Sophisticated characters make tropes less clichéd
                "generic": 0.0,
                "archetypal": +0.1
            },
            "combination_factors": {
                "single_trope": 0.0,
                "two_tropes": -0.1,  # Combinations can be fresher
                "three_plus_tropes": -0.15,
                "contradictory_tropes": -0.25  # Contradictions create interest
            }
        }
    
    def _initialize_subversion_strategies(self) -> Dict[str, List[str]]:
        """General subversion strategies for different trope types"""
        return {
            "power_tropes": [
                "Make power come with unexpected costs",
                "Have power work in scientifically consistent ways",
                "Require intelligence/strategy to use effectively",
                "Make power context-dependent or situational"
            ],
            "character_tropes": [
                "Subvert expectations about character motivations",
                "Give character agency in their circumstances",
                "Make character's strength also their weakness",
                "Show character growing beyond their archetype"
            ],
            "plot_tropes": [
                "Earn convenient solutions through setup",
                "Make solutions create new problems",
                "Let character choose the hard path over easy",
                "Show consequences of typical plot solutions"
            ],
            "marcus_style": [
                "Ground fantastical elements in realistic contexts",
                "Show systemic thinking rather than individual heroics",
                "Explore moral complexity rather than clear good/evil",
                "Focus on intelligence and strategy over power"
            ]
        }
    
    def analyze_character_tropes(self, character_data: Dict[str, Any]) -> CharacterTropeProfile:
        """Analyze a character for trope usage and freshness"""
        
        character_id = character_data.get("id", "unknown")
        trope_analyses = []
        total_cliché_score = 0.0
        
        # Analyze different aspects of the character
        origin_tropes = self._analyze_character_origin(character_data)
        power_tropes = self._analyze_character_powers(character_data)
        personality_tropes = self._analyze_character_personality(character_data)
        
        all_tropes = origin_tropes + power_tropes + personality_tropes
        
        for trope_name, context_data in all_tropes:
            if trope_name in self.trope_database:
                analysis = self._analyze_single_trope(trope_name, context_data, character_data)
                trope_analyses.append(analysis)
                total_cliché_score += analysis.cliché_score
        
        # Calculate overall freshness
        overall_freshness = 1.0 - (total_cliché_score / max(len(trope_analyses), 1))
        
        # Determine Marcus-level sophistication
        marcus_rating = self._calculate_marcus_level(character_data, trope_analyses)
        
        # Generate improvement suggestions
        suggestions = self._generate_improvement_suggestions(trope_analyses, character_data)
        
        # Identify risk and strength factors
        risk_factors = [t.trope_name for t in trope_analyses if t.cliché_score > 0.6]
        strength_factors = [t.trope_name for t in trope_analyses if t.cliché_score < 0.3]
        
        return CharacterTropeProfile(
            character_id=character_id,
            overall_freshness_score=overall_freshness,
            trope_analyses=trope_analyses,
            risk_factors=risk_factors,
            strength_factors=strength_factors,
            improvement_suggestions=suggestions,
            marcus_level_rating=marcus_rating
        )
    
    def _analyze_character_origin(self, character_data: Dict) -> List[Tuple[str, Dict]]:
        """Analyze character origin for tropes"""
        tropes = []
        
        origin = character_data.get("character_origin", "")
        backstory = character_data.get("backstory_seeds", [])
        
        # Check for common origin tropes
        if "nootropic_enhanced" in origin:
            tropes.append(("nootropic_enhanced", {"context": "origin"}))
        elif any("orphan" in story.lower() for story in backstory):
            tropes.append(("orphaned_hero", {"context": "backstory"}))
        elif any("chosen" in story.lower() for story in backstory):
            tropes.append(("chosen_one", {"context": "backstory"}))
        elif any("dark past" in story.lower() or "mysterious" in story.lower() for story in backstory):
            tropes.append(("dark_past_mystery", {"context": "backstory"}))
        
        return tropes
    
    def _analyze_character_powers(self, character_data: Dict) -> List[Tuple[str, Dict]]:
        """Analyze character powers for tropes"""
        tropes = []
        
        powers = character_data.get("power_suggestions", [])
        
        for power in powers:
            power_name = power.get("name", "").lower()
            power_desc = power.get("description", "").lower()
            
            if "hypercognitive" in power_name or "cognitive" in power_desc:
                tropes.append(("hypercognitive_processing", {"context": "power", "cost": power.get("cost_level", 5)}))
            elif any(element in power_name for element in ["fire", "water", "earth", "air"]):
                tropes.append(("elemental_powers", {"context": "power", "cost": power.get("cost_level", 5)}))
            elif "strength" in power_name or "strong" in power_desc:
                tropes.append(("super_strength", {"context": "power", "cost": power.get("cost_level", 5)}))
        
        return tropes
    
    def _analyze_character_personality(self, character_data: Dict) -> List[Tuple[str, Dict]]:
        """Analyze character personality for tropes"""
        tropes = []
        
        tags = character_data.get("archetype_tags", [])
        
        if "System Changer" in tags:
            tropes.append(("system_changer", {"context": "personality"}))
        if "Power Broker" in tags:
            tropes.append(("power_broker", {"context": "personality"}))
        
        return tropes
    
    def _analyze_single_trope(self, trope_name: str, context_data: Dict, character_data: Dict) -> TropeAnalysis:
        """Analyze a single trope for freshness"""
        trope_info = self.trope_database[trope_name]
        base_score = trope_info["base_cliché_score"]
        
        # Apply context modifiers
        modified_score = base_score
        
        # Genre modifiers
        genre = character_data.get("genre_universe", "")
        if genre in trope_info.get("context_modifiers", {}):
            modified_score += trope_info["context_modifiers"][genre]
        
        # Character sophistication modifier (Marcus-style characters make tropes fresher)
        if self._is_sophisticated_character(character_data):
            modified_score += self.context_multipliers["character_sophistication"]["marcus_level"]
        
        # Combination modifiers (multiple tropes can be fresher)
        if len(self._get_all_character_tropes(character_data)) > 2:
            modified_score += self.context_multipliers["combination_factors"]["three_plus_tropes"]
        
        # Clamp score between 0 and 1
        modified_score = max(0.0, min(1.0, modified_score))
        
        # Determine freshness level
        freshness_level = self._score_to_freshness_level(modified_score)
        
        return TropeAnalysis(
            trope_name=trope_name,
            cliché_score=modified_score,
            freshness_level=freshness_level,
            usage_frequency=trope_info["usage_frequency"],
            subversion_suggestions=trope_info.get("subversion_strategies", []),
            combination_alternatives=self._get_combination_alternatives(trope_name),
            context_modifiers=trope_info.get("context_modifiers", {})
        )
    
    def _score_to_freshness_level(self, score: float) -> FreshnessLevel:
        """Convert cliché score to freshness level"""
        if score <= 0.1:
            return FreshnessLevel.GROUNDBREAKING
        elif score <= 0.3:
            return FreshnessLevel.FRESH
        elif score <= 0.6:
            return FreshnessLevel.FAMILIAR
        elif score <= 0.8:
            return FreshnessLevel.CLICHÉD
        else:
            return FreshnessLevel.OVERUSED
    
    def _is_sophisticated_character(self, character_data: Dict) -> bool:
        """Determine if character shows Marcus-level sophistication"""
        origin = character_data.get("character_origin", "")
        power_source = character_data.get("power_source", "")
        
        sophisticated_indicators = [
            "nootropic_enhanced" in origin,
            "nootropic_drug" in power_source,
            "System Changer" in character_data.get("archetype_tags", []),
            "Power Broker" in character_data.get("archetype_tags", []),
            "entrepreneurial" in character_data.get("social_status", "")
        ]
        
        return sum(sophisticated_indicators) >= 2
    
    def _get_all_character_tropes(self, character_data: Dict) -> List[str]:
        """Get all tropes associated with character"""
        origin_tropes = [t[0] for t in self._analyze_character_origin(character_data)]
        power_tropes = [t[0] for t in self._analyze_character_powers(character_data)]
        personality_tropes = [t[0] for t in self._analyze_character_personality(character_data)]
        
        return origin_tropes + power_tropes + personality_tropes
    
    def _calculate_marcus_level(self, character_data: Dict, trope_analyses: List[TropeAnalysis]) -> float:
        """Calculate how sophisticated the character is (Marcus = 1.0)"""
        
        sophistication_factors = 0.0
        
        # Factor 1: Low average cliché score
        avg_cliche = sum(t.cliché_score for t in trope_analyses) / max(len(trope_analyses), 1)
        sophistication_factors += (1.0 - avg_cliche) * 0.4
        
        # Factor 2: Presence of sophisticated tropes
        sophisticated_tropes = ["nootropic_enhanced", "system_changer", "power_broker", "hypercognitive_processing"]
        has_sophisticated = sum(1 for t in trope_analyses if t.trope_name in sophisticated_tropes)
        sophistication_factors += min(has_sophisticated / 2.0, 1.0) * 0.3
        
        # Factor 3: Complex character background
        if character_data.get("social_status") == "entrepreneurial":
            sophistication_factors += 0.1
        if character_data.get("geographic_context") == "detroit":
            sophistication_factors += 0.1
        if len(character_data.get("archetype_tags", [])) >= 3:
            sophistication_factors += 0.1
        
        return min(sophistication_factors, 1.0)
    
    def _generate_improvement_suggestions(self, trope_analyses: List[TropeAnalysis], character_data: Dict) -> List[str]:
        """Generate suggestions to improve character freshness"""
        suggestions = []
        
        high_cliche_tropes = [t for t in trope_analyses if t.cliché_score > 0.6]
        
        if high_cliche_tropes:
            suggestions.append(f"Consider subverting these overused tropes: {', '.join(t.trope_name for t in high_cliche_tropes)}")
            
            # Add specific subversion suggestions for the worst trope
            worst_trope = max(high_cliche_tropes, key=lambda t: t.cliché_score)
            if worst_trope.subversion_suggestions:
                suggestions.append(f"For {worst_trope.trope_name}: {worst_trope.subversion_suggestions[0]}")
        
        if len(trope_analyses) < 3:
            suggestions.append("Consider adding more complexity by combining multiple character elements")
        
        marcus_rating = self._calculate_marcus_level(character_data, trope_analyses)
        if marcus_rating < 0.5:
            suggestions.extend([
                "Consider grounding fantastical elements in realistic contexts",
                "Add strategic thinking or business acumen to the character",
                "Explore moral complexity rather than simple good vs. evil"
            ])
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _get_combination_alternatives(self, trope_name: str) -> List[str]:
        """Get suggestions for combining this trope with others"""
        combinations = {
            "nootropic_enhanced": [
                "Combine with social anxiety for interesting contrast",
                "Add physical weakness to balance mental strength", 
                "Include addiction/dependency themes"
            ],
            "system_changer": [
                "Combine with outsider status for compelling motivation",
                "Add personal stakes beyond just changing the system",
                "Include mentor who represents the old system"
            ],
            "power_broker": [
                "Add vulnerability - something they can't influence",
                "Include rival broker for conflict",
                "Give them a cause they truly believe in"
            ]
        }
        
        return combinations.get(trope_name, ["Consider unique combinations with other character elements"])

# Singleton instance
trope_risk_meter = None

def get_trope_risk_meter():
    """Get or create trope risk meter instance"""
    global trope_risk_meter
    if trope_risk_meter is None:
        trope_risk_meter = EnhancedTropeRiskMeter()
    return trope_risk_meter