"""
VisionForge Advanced Power System Framework
Extracted patterns from 20+ fictional works, distilled into reusable design principles
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import random

class PowerSource(Enum):
    """Origins of supernatural abilities"""
    GENETIC_DRIFT = "genetic_drift"              # Natural human evolution/mutation
    CHEMICAL_CATALYST = "chemical_catalyst"      # Drugs, serums, environmental toxins
    TRAUMA_AWAKENING = "trauma_awakening"        # Extreme stress unlocks latent potential
    ENERGY_EXPOSURE = "energy_exposure"          # Radiation, cosmic forces, dimensional rifts
    BLOODLINE_INHERITANCE = "bloodline_inheritance"  # Family genetics, ancient lineages
    SOUL_RESONANCE = "soul_resonance"            # Spiritual energy, life force manipulation
    TECHNOLOGY_FUSION = "technology_fusion"      # Cybernetic enhancement, nanotech integration
    ENTITY_CONTRACT = "entity_contract"          # Deals with otherworldly beings
    DISCIPLINE_MASTERY = "discipline_mastery"    # Unlocked through training/meditation
    PROBABILITY_LOTTERY = "probability_lottery"  # Random distribution, no clear cause

class PowerMechanic(Enum):
    """How abilities function and manifest"""
    ELEMENTAL_COMMAND = "elemental_command"      # Control over natural forces
    BIOLOGICAL_OVERRIDE = "biological_override"  # Body modification, healing, shapeshifting  
    MENTAL_PROJECTION = "mental_projection"      # Telepathy, telekinesis, illusions
    REALITY_DISTORTION = "reality_distortion"    # Time, space, probability manipulation
    ENERGY_CHANNELING = "energy_channeling"      # Force projection, absorption, conversion
    SENSORY_EXPANSION = "sensory_expansion"      # Enhanced or new perceptual abilities
    PHASE_SHIFTING = "phase_shifting"            # Intangibility, dimensional travel
    POWER_MIMICRY = "power_mimicry"             # Copying, absorbing others' abilities
    MANIFESTATION = "manifestation"              # Creating objects, summoning entities
    SYSTEMIC_CONTROL = "systemic_control"        # Influencing networks, systems, groups

class PowerLimitation(Enum):
    """Constraints and costs that balance abilities"""
    PHYSICAL_BURNOUT = "physical_burnout"        # Body degradation, exhaustion, pain
    MENTAL_FRACTURE = "mental_fracture"          # Psychological strain, memory loss, madness
    TEMPORAL_WINDOW = "temporal_window"          # Time limits, cooldown periods
    RANGE_RESTRICTION = "range_restriction"      # Distance limitations, line-of-sight needs
    TRIGGER_DEPENDENCY = "trigger_dependency"    # Emotional state, specific conditions required
    ALWAYS_ACTIVE = "always_active"              # Cannot be turned off, constant burden
    RESOURCE_HUNGER = "resource_hunger"          # Requires external fuel, materials, energy
    FOCUS_INTENSIVE = "focus_intensive"          # Demands absolute concentration
    SOCIAL_ISOLATION = "social_isolation"       # Powers create fear, rejection, loneliness
    MORAL_CORRUPTION = "moral_corruption"        # Power gradually changes personality/ethics

class ProgressionModel(Enum):
    """How abilities develop over time"""
    EMOTIONAL_EVOLUTION = "emotional_evolution"  # Growth tied to psychological development
    TECHNICAL_MASTERY = "technical_mastery"      # Improved through practice and understanding
    STRESS_BREAKTHROUGH = "stress_breakthrough"  # Crisis situations unlock new levels
    SYMBIOTIC_BOND = "symbiotic_bond"           # Powers grow through relationship with others
    PHILOSOPHICAL_DEPTH = "philosophical_depth"  # Understanding of purpose enhances ability
    GENERATIONAL_LEGACY = "generational_legacy"  # Each generation improves on the last
    SYSTEMATIC_STUDY = "systematic_study"        # Scientific approach to power development
    INTUITIVE_LEAP = "intuitive_leap"           # Sudden, unpredictable advancement
    SACRIFICE_UNLOCK = "sacrifice_unlock"        # Giving up something precious for growth
    ENVIRONMENTAL_SYNC = "environmental_sync"    # Powers adapt to surroundings/challenges

@dataclass
class PowerSystemProfile:
    """Complete power system configuration"""
    source: PowerSource
    mechanic: PowerMechanic
    primary_limitation: PowerLimitation
    secondary_limitation: Optional[PowerLimitation]
    progression_model: ProgressionModel
    
    # Modular sliders (0.0 to 1.0)
    raw_power_level: float = 0.5          # Pure destructive/creative potential
    control_precision: float = 0.5        # Fine manipulation vs crude application
    cost_severity: float = 0.5            # How harsh the limitations are
    social_impact: float = 0.5            # How much society fears/accepts this power
    progression_speed: float = 0.5        # How quickly abilities can advance
    uniqueness_factor: float = 0.5        # How rare/common this power type is
    
    # Meta-narrative themes
    thematic_resonance: List[str] = None  # What the power represents symbolically
    societal_role: str = ""               # How society categorizes this power type
    philosophical_question: str = ""      # What moral/ethical dilemma this raises

class AdvancedPowerSystemGenerator:
    def __init__(self):
        self.thematic_clusters = self._initialize_themes()
        self.synergy_patterns = self._initialize_synergies()
        self.narrative_archetypes = self._initialize_archetypes()
    
    def _initialize_themes(self) -> Dict[str, List[str]]:
        """Core symbolic meanings powers can embody"""
        return {
            "identity_crisis": [
                "loss of humanity through transformation",
                "burden of being different from others", 
                "struggle between normal life and responsibility"
            ],
            "power_corruption": [
                "absolute power corrupting absolutely",
                "temptation to solve problems through force",
                "isolation from those without power"
            ],
            "inherited_trauma": [
                "family legacy of suffering and power",
                "generational cycles of violence/heroism",
                "cannot escape bloodline destiny"
            ],
            "technological_anxiety": [
                "human enhancement vs natural evolution", 
                "dependence on artificial systems",
                "loss of authentic human experience"
            ],
            "social_stratification": [
                "powers creating new class systems",
                "fear and regulation of the enhanced",
                "privilege and responsibility of ability"
            ],
            "existential_purpose": [
                "why do I have these abilities?",
                "what am I meant to do with this power?",
                "meaning beyond personal gain"
            ]
        }
    
    def _initialize_synergies(self) -> Dict[tuple, Dict[str, Any]]:
        """How different power elements interact"""
        return {
            (PowerSource.TRAUMA_AWAKENING, PowerLimitation.MENTAL_FRACTURE): {
                "narrative_weight": "Powers born from pain often damage the mind further",
                "mechanical_interaction": "Ability strength tied to psychological instability",
                "story_potential": "Character must heal trauma to gain full control"
            },
            (PowerMechanic.REALITY_DISTORTION, PowerLimitation.ALWAYS_ACTIVE): {
                "narrative_weight": "Cannot escape from altering reality around them",
                "mechanical_interaction": "World constantly shifts based on subconscious",
                "story_potential": "Learning to accept and guide rather than control"
            },
            (PowerSource.ENTITY_CONTRACT, PowerLimitation.MORAL_CORRUPTION): {
                "narrative_weight": "Power comes with strings attached to alien values",
                "mechanical_interaction": "Abilities grow stronger but change personality",
                "story_potential": "Can character maintain identity while using power?"
            }
        }
    
    def _initialize_archetypes(self) -> Dict[str, Dict[str, Any]]:
        """Proven character/power combinations"""
        return {
            "reluctant_god": {
                "power_profile": {
                    "raw_power_level": 0.9,
                    "control_precision": 0.3,
                    "cost_severity": 0.8,
                    "social_impact": 0.9
                },
                "core_conflict": "Immense power with poor control and high stakes",
                "character_arc": "Learning restraint and responsibility"
            },
            "system_hacker": {
                "power_profile": {
                    "raw_power_level": 0.4,
                    "control_precision": 0.9,
                    "cost_severity": 0.4,
                    "social_impact": 0.6
                },
                "core_conflict": "Precise abilities challenge existing power structures",
                "character_arc": "Choosing between personal gain and systemic change"
            },
            "broken_weapon": {
                "power_profile": {
                    "raw_power_level": 0.8,
                    "control_precision": 0.8,
                    "cost_severity": 0.9,
                    "social_impact": 0.7
                },
                "core_conflict": "Highly effective but devastating personal cost",
                "character_arc": "Finding way to be useful without self-destruction"
            }
        }
    
    def generate_power_system(self, 
                            character_context: Optional[Dict] = None,
                            narrative_focus: Optional[str] = None,
                            complexity_level: str = "moderate") -> PowerSystemProfile:
        """Generate a complete power system profile"""
        
        # Base generation
        source = random.choice(list(PowerSource))
        mechanic = random.choice(list(PowerMechanic))
        primary_limitation = random.choice(list(PowerLimitation))
        progression = random.choice(list(ProgressionModel))
        
        # Apply character context if provided
        if character_context:
            source, mechanic = self._contextualize_power(source, mechanic, character_context)
        
        # Apply narrative focus
        if narrative_focus and narrative_focus in self.thematic_clusters:
            primary_limitation = self._select_thematic_limitation(narrative_focus)
        
        # Generate secondary limitation based on synergies
        secondary_limitation = self._generate_secondary_limitation(source, mechanic, primary_limitation)
        
        # Set slider values based on complexity
        sliders = self._generate_slider_values(complexity_level, source, mechanic, primary_limitation)
        
        # Generate thematic elements
        themes = self._generate_themes(source, mechanic, primary_limitation, narrative_focus)
        
        return PowerSystemProfile(
            source=source,
            mechanic=mechanic,
            primary_limitation=primary_limitation,
            secondary_limitation=secondary_limitation,
            progression_model=progression,
            **sliders,
            thematic_resonance=themes["resonance"],
            societal_role=themes["societal_role"],
            philosophical_question=themes["philosophical_question"]
        )
    
    def _contextualize_power(self, source: PowerSource, mechanic: PowerMechanic, context: Dict) -> tuple:
        """Adjust power based on character background"""
        origin = context.get("character_origin", "")
        social_status = context.get("social_status", "")
        
        # Business/entrepreneurial background
        if "entrepreneurial" in social_status or "business" in origin.lower():
            # Favor systematic, controllable powers
            if random.random() < 0.4:
                source = PowerSource.DISCIPLINE_MASTERY
                mechanic = random.choice([PowerMechanic.SYSTEMIC_CONTROL, PowerMechanic.MENTAL_PROJECTION])
        
        # Enhanced origin types
        if "enhanced" in origin or "nootropic" in origin:
            source = random.choice([PowerSource.CHEMICAL_CATALYST, PowerSource.TECHNOLOGY_FUSION])
            mechanic = random.choice([PowerMechanic.MENTAL_PROJECTION, PowerMechanic.SENSORY_EXPANSION])
        
        return source, mechanic
    
    def _select_thematic_limitation(self, theme: str) -> PowerLimitation:
        """Choose limitation that reinforces narrative theme"""
        theme_limitations = {
            "identity_crisis": [PowerLimitation.ALWAYS_ACTIVE, PowerLimitation.SOCIAL_ISOLATION],
            "power_corruption": [PowerLimitation.MORAL_CORRUPTION, PowerLimitation.MENTAL_FRACTURE],
            "inherited_trauma": [PowerLimitation.MENTAL_FRACTURE, PowerLimitation.TRIGGER_DEPENDENCY],
            "technological_anxiety": [PowerLimitation.RESOURCE_HUNGER, PowerLimitation.FOCUS_INTENSIVE],
            "social_stratification": [PowerLimitation.SOCIAL_ISOLATION, PowerLimitation.ALWAYS_ACTIVE],
            "existential_purpose": [PowerLimitation.TRIGGER_DEPENDENCY, PowerLimitation.MORAL_CORRUPTION]
        }
        
        options = theme_limitations.get(theme, list(PowerLimitation))
        return random.choice(options)
    
    def _generate_secondary_limitation(self, source: PowerSource, mechanic: PowerMechanic, 
                                     primary: PowerLimitation) -> Optional[PowerLimitation]:
        """Add secondary limitation based on synergies"""
        # Check for known synergy patterns
        synergy_key = (source, primary)
        if synergy_key in self.synergy_patterns:
            return None  # Synergy pattern is complex enough
        
        # Generate complementary limitation
        if primary in [PowerLimitation.PHYSICAL_BURNOUT, PowerLimitation.RESOURCE_HUNGER]:
            return random.choice([PowerLimitation.TEMPORAL_WINDOW, PowerLimitation.RANGE_RESTRICTION])
        elif primary == PowerLimitation.MENTAL_FRACTURE:
            return PowerLimitation.TRIGGER_DEPENDENCY
        
        return None
    
    def _generate_slider_values(self, complexity: str, source: PowerSource, 
                               mechanic: PowerMechanic, limitation: PowerLimitation) -> Dict[str, float]:
        """Generate balanced slider values"""
        base_values = {
            "raw_power_level": 0.5,
            "control_precision": 0.5,
            "cost_severity": 0.5,
            "social_impact": 0.5,
            "progression_speed": 0.5,
            "uniqueness_factor": 0.5
        }
        
        # Adjust based on complexity
        variance = {"simple": 0.2, "moderate": 0.3, "complex": 0.4}[complexity]
        
        for key in base_values:
            base_values[key] += random.uniform(-variance, variance)
            base_values[key] = max(0.1, min(0.9, base_values[key]))  # Clamp values
        
        # Apply power system logic
        if mechanic == PowerMechanic.REALITY_DISTORTION:
            base_values["raw_power_level"] += 0.2
            base_values["control_precision"] -= 0.2
            base_values["cost_severity"] += 0.2
        
        if limitation == PowerLimitation.ALWAYS_ACTIVE:
            base_values["social_impact"] += 0.3
            base_values["cost_severity"] += 0.2
        
        return base_values
    
    def _generate_themes(self, source: PowerSource, mechanic: PowerMechanic, 
                        limitation: PowerLimitation, focus: Optional[str]) -> Dict[str, Any]:
        """Generate thematic elements for the power system"""
        resonance = []
        
        # Add theme based on focus
        if focus and focus in self.thematic_clusters:
            resonance.extend(random.sample(self.thematic_clusters[focus], 2))
        
        # Add universal themes
        universal_themes = [
            "responsibility vs freedom",
            "human vs enhanced identity", 
            "individual vs collective good",
            "power's price on relationships",
            "meaning of strength"
        ]
        resonance.append(random.choice(universal_themes))
        
        # Generate societal role
        roles = [
            "Regulated Asset", "Feared Anomaly", "Protected Minority", 
            "Military Resource", "Research Subject", "Cultural Icon",
            "Underground Network", "Corporate Tool", "Independent Operator"
        ]
        
        # Generate philosophical question
        questions = [
            "What makes someone worthy of power?",
            "How much control should society have over the enhanced?",
            "Can power be used without corrupting the user?",
            "What do we owe to those without abilities?",
            "Is it ethical to create artificial enhanced beings?",
            "Should powers be seen as gifts or curses?"
        ]
        
        return {
            "resonance": resonance,
            "societal_role": random.choice(roles),
            "philosophical_question": random.choice(questions)
        }

# Singleton instance
power_system_generator = None

def get_power_system_generator():
    """Get or create power system generator instance"""
    global power_system_generator
    if power_system_generator is None:
        power_system_generator = AdvancedPowerSystemGenerator()
    return power_system_generator