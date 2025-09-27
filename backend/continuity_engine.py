"""
VisionForge Continuity Engine
Advanced consistency checking across characters, stories, and timelines
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ViolationType(Enum):
    POWER_INCONSISTENCY = "power_inconsistency"
    CHARACTER_CONTRADICTION = "character_contradiction"
    TIMELINE_ERROR = "timeline_error"
    WORLD_RULE_VIOLATION = "world_rule_violation"
    RELATIONSHIP_CONFLICT = "relationship_conflict"
    SETTING_MISMATCH = "setting_mismatch"
    TONE_DRIFT = "tone_drift"
    SCALE_IMBALANCE = "scale_imbalance"

class SeverityLevel(Enum):
    CRITICAL = "critical"      # Story-breaking inconsistencies
    HIGH = "high"             # Major plot holes
    MEDIUM = "medium"         # Noticeable but manageable
    LOW = "low"               # Minor style inconsistencies

@dataclass
class ContinuityViolation:
    violation_type: ViolationType
    severity: SeverityLevel
    title: str
    description: str
    affected_elements: List[str]
    suggested_fixes: List[str]
    examples: Optional[Dict[str, str]] = None
    cross_references: List[str] = field(default_factory=list)
    
class ContinuityEngine:
    def __init__(self):
        self.character_database = {}
        self.story_timeline = []
        self.world_rules = {}
        self.relationship_graph = {}
        self.power_system_registry = {}
        self.consistency_rules = self._initialize_consistency_rules()
    
    def _initialize_consistency_rules(self) -> Dict[str, Any]:
        """Initialize consistency checking rules"""
        return {
            "power_scaling": {
                "max_power_jump": 0.3,  # Maximum power level increase between stories
                "consistency_threshold": 0.8,  # How consistent powers should be
                "description": "Powers should scale logically and maintain consistent limitations"
            },
            "character_traits": {
                "core_trait_stability": 0.9,  # Core personality traits should be stable
                "allowed_growth_areas": ["skills", "knowledge", "relationships"],
                "description": "Core personality should remain consistent while allowing growth"
            },
            "timeline_logic": {
                "causality_check": True,
                "temporal_consistency": True,
                "description": "Events should follow logical cause-and-effect relationships"
            },
            "world_physics": {
                "magic_system_consistency": True,
                "technology_level_consistency": True,
                "description": "World rules and physics should remain consistent"
            },
            "relationship_dynamics": {
                "relationship_memory": True,
                "emotional_continuity": True,
                "description": "Character relationships should develop logically"
            }
        }
    
    def add_character_analysis(self, character_data: Dict[str, Any]) -> None:
        """Add character analysis to continuity database"""
        character_id = character_data.get('id', 'unknown')
        
        # Store character data for continuity checking
        self.character_database[character_id] = {
            'traits': character_data.get('traits', []),
            'powers': character_data.get('power_suggestions', []),
            'backstory': character_data.get('backstory_seeds', []),
            'relationships': character_data.get('relationships', []),
            'timeline_entries': character_data.get('timeline', []),
            'created_at': datetime.now().isoformat(),
            'genre': character_data.get('genre', 'unknown'),
            'power_level': self._calculate_power_level(character_data),
            'core_personality': self._extract_core_personality(character_data)
        }
    
    def check_continuity(self, new_content: Dict[str, Any], 
                        context_characters: List[str] = None) -> List[ContinuityViolation]:
        """Perform comprehensive continuity checking"""
        violations = []
        context_characters = context_characters or []
        
        # Check power consistency
        violations.extend(self._check_power_consistency(new_content, context_characters))
        
        # Check character trait consistency
        violations.extend(self._check_character_consistency(new_content, context_characters))
        
        # Check timeline logic
        violations.extend(self._check_timeline_consistency(new_content))
        
        # Check world rule violations
        violations.extend(self._check_world_rule_consistency(new_content))
        
        # Check relationship dynamics
        violations.extend(self._check_relationship_consistency(new_content, context_characters))
        
        # Check setting consistency
        violations.extend(self._check_setting_consistency(new_content))
        
        # Check tone consistency
        violations.extend(self._check_tone_consistency(new_content))
        
        # Sort by severity
        violations.sort(key=lambda x: ["critical", "high", "medium", "low"].index(x.severity.value))
        
        return violations
    
    def _check_power_consistency(self, content: Dict[str, Any], 
                               context_characters: List[str]) -> List[ContinuityViolation]:
        """Check for power system inconsistencies"""
        violations = []
        content_powers = content.get('power_suggestions', [])
        
        for char_id in context_characters:
            if char_id in self.character_database:
                existing_char = self.character_database[char_id]
                existing_powers = existing_char.get('powers', [])
                
                # Check for power scaling issues
                new_power_level = self._calculate_power_level(content)
                old_power_level = existing_char.get('power_level', 0.5)
                
                if new_power_level - old_power_level > self.consistency_rules['power_scaling']['max_power_jump']:
                    violations.append(ContinuityViolation(
                        violation_type=ViolationType.POWER_INCONSISTENCY,
                        severity=SeverityLevel.HIGH,
                        title="Sudden Power Scaling Jump",
                        description=f"Character power level jumped from {old_power_level:.1f} to {new_power_level:.1f} without explanation",
                        affected_elements=[char_id],
                        suggested_fixes=[
                            "Add training montage or power awakening event",
                            "Introduce gradual power progression over time",
                            "Explain external power source or enhancement",
                            "Consider reducing the power scale for this story"
                        ],
                        examples={
                            "problematic": "Character suddenly lifts cars after struggling with boxes",
                            "better": "After months of training, character can now lift heavier objects"
                        }
                    ))
                
                # Check for contradictory power descriptions
                for new_power in content_powers:
                    for old_power in existing_powers:
                        if self._powers_contradict(new_power, old_power):
                            violations.append(ContinuityViolation(
                                violation_type=ViolationType.POWER_INCONSISTENCY,
                                severity=SeverityLevel.MEDIUM,
                                title="Contradictory Power Descriptions",
                                description=f"New power '{new_power.get('name', 'Unknown')}' contradicts existing power",
                                affected_elements=[char_id],
                                suggested_fixes=[
                                    "Clarify that this is power evolution, not replacement",
                                    "Explain how both powers can coexist",
                                    "Retcon one of the contradictory elements",
                                    "Frame as different applications of same core ability"
                                ]
                            ))
        
        return violations
    
    def _check_character_consistency(self, content: Dict[str, Any],
                                   context_characters: List[str]) -> List[ContinuityViolation]:
        """Check for character personality and trait inconsistencies"""
        violations = []
        
        for char_id in context_characters:
            if char_id in self.character_database:
                existing_char = self.character_database[char_id]
                existing_traits = existing_char.get('core_personality', [])
                new_traits = self._extract_core_personality(content)
                
                # Check for contradictory core traits
                contradictions = self._find_trait_contradictions(existing_traits, new_traits)
                
                if contradictions:
                    violations.append(ContinuityViolation(
                        violation_type=ViolationType.CHARACTER_CONTRADICTION,
                        severity=SeverityLevel.HIGH,
                        title="Core Personality Contradiction",
                        description=f"Character traits contradict established personality",
                        affected_elements=[char_id],
                        suggested_fixes=[
                            "Show character growth that explains the change",
                            "Add traumatic event that shifts personality",
                            "Clarify that this is situational behavior, not core change",
                            "Revise to maintain character consistency"
                        ],
                        examples={
                            "contradictory_traits": contradictions,
                            "solution": "Show gradual change with clear motivation"
                        }
                    ))
        
        return violations
    
    def _check_timeline_consistency(self, content: Dict[str, Any]) -> List[ContinuityViolation]:
        """Check for timeline and causality violations"""
        violations = []
        
        # Check for temporal paradoxes
        timeline_events = content.get('timeline', [])
        for event in timeline_events:
            # Check causality
            if not self._check_causality(event):
                violations.append(ContinuityViolation(
                    violation_type=ViolationType.TIMELINE_ERROR,
                    severity=SeverityLevel.CRITICAL,
                    title="Causality Violation",
                    description="Event occurs before its cause",
                    affected_elements=[event.get('description', 'Unknown event')],
                    suggested_fixes=[
                        "Reorder events to maintain causality",
                        "Add explanation for time travel or prophecy",
                        "Revise event descriptions for clarity",
                        "Create flashback structure to explain timing"
                    ]
                ))
        
        return violations
    
    def _check_world_rule_consistency(self, content: Dict[str, Any]) -> List[ContinuityViolation]:
        """Check for violations of established world rules"""
        violations = []
        
        genre = content.get('genre', 'unknown')
        power_sources = content.get('power_suggestions', [])
        
        # Check technology/magic consistency
        for power in power_sources:
            power_source = power.get('source', 'unknown')
            if not self._is_power_source_consistent_with_genre(power_source, genre):
                violations.append(ContinuityViolation(
                    violation_type=ViolationType.WORLD_RULE_VIOLATION,
                    severity=SeverityLevel.MEDIUM,
                    title="Genre Inconsistency",
                    description=f"Power source '{power_source}' doesn't fit {genre} world",
                    affected_elements=[power.get('name', 'Unknown power')],
                    suggested_fixes=[
                        f"Adapt power source to fit {genre} aesthetics",
                        "Explain how this power fits the world's rules",
                        "Consider changing genre to accommodate power",
                        "Create lore that bridges the inconsistency"
                    ]
                ))
        
        return violations
    
    def _check_relationship_consistency(self, content: Dict[str, Any],
                                      context_characters: List[str]) -> List[ContinuityViolation]:
        """Check for relationship continuity issues"""
        violations = []
        
        # Check for relationship contradictions
        new_relationships = content.get('relationships', [])
        
        for relationship in new_relationships:
            char_a = relationship.get('character_a')
            char_b = relationship.get('character_b')
            relationship_type = relationship.get('type')
            
            # Check against existing relationships
            existing_relationship = self._get_existing_relationship(char_a, char_b)
            if existing_relationship and self._relationships_contradict(existing_relationship, relationship):
                violations.append(ContinuityViolation(
                    violation_type=ViolationType.RELATIONSHIP_CONFLICT,
                    severity=SeverityLevel.HIGH,
                    title="Relationship Contradiction",
                    description=f"New relationship between {char_a} and {char_b} contradicts established dynamic",
                    affected_elements=[char_a, char_b],
                    suggested_fixes=[
                        "Show relationship evolution over time",
                        "Add conflict or reconciliation event",
                        "Clarify the nature of relationship change",
                        "Maintain relationship consistency"
                    ]
                ))
        
        return violations
    
    def _check_setting_consistency(self, content: Dict[str, Any]) -> List[ContinuityViolation]:
        """Check for setting and location inconsistencies"""
        violations = []
        
        setting = content.get('setting', {})
        genre = content.get('genre', 'unknown')
        
        # Check setting-genre consistency
        if not self._setting_matches_genre(setting, genre):
            violations.append(ContinuityViolation(
                violation_type=ViolationType.SETTING_MISMATCH,
                severity=SeverityLevel.MEDIUM,
                title="Setting-Genre Mismatch",
                description="Setting elements don't match the established genre",
                affected_elements=[f"Setting: {setting}"],
                suggested_fixes=[
                    "Adapt setting to match genre conventions",
                    "Explain how unusual elements fit the world",
                    "Consider hybrid genre approach",
                    "Modify setting descriptions for consistency"
                ]
            ))
        
        return violations
    
    def _check_tone_consistency(self, content: Dict[str, Any]) -> List[ContinuityViolation]:
        """Check for tone and style consistency"""
        violations = []
        
        # Analyze tone markers in content
        tone_markers = self._extract_tone_markers(content)
        established_tone = self._get_established_tone()
        
        if self._tone_drift_detected(tone_markers, established_tone):
            violations.append(ContinuityViolation(
                violation_type=ViolationType.TONE_DRIFT,
                severity=SeverityLevel.LOW,
                title="Tone Inconsistency",
                description="Writing tone shifts unexpectedly from established style",
                affected_elements=["Overall narrative tone"],
                suggested_fixes=[
                    "Maintain consistent voice throughout",
                    "If tone change is intentional, signal it clearly",
                    "Review previous content for tone reference",
                    "Consider if tone shift serves the story"
                ]
            ))
        
        return violations
    
    # Helper methods
    def _calculate_power_level(self, character_data: Dict[str, Any]) -> float:
        """Calculate overall power level from character data"""
        powers = character_data.get('power_suggestions', [])
        if not powers:
            return 0.1
        
        total_cost = sum(power.get('cost_level', 3) for power in powers)
        avg_cost = total_cost / len(powers)
        return min(avg_cost / 10.0, 1.0)
    
    def _extract_core_personality(self, character_data: Dict[str, Any]) -> List[str]:
        """Extract core personality traits"""
        traits = character_data.get('traits', [])
        return [trait for trait in traits if self._is_core_trait(trait)]
    
    def _is_core_trait(self, trait: str) -> bool:
        """Determine if a trait is a core personality trait"""
        core_trait_keywords = [
            'honest', 'dishonest', 'brave', 'cowardly', 'kind', 'cruel',
            'loyal', 'treacherous', 'patient', 'impulsive', 'calm', 'aggressive'
        ]
        return any(keyword in trait.lower() for keyword in core_trait_keywords)
    
    def _powers_contradict(self, power1: Dict, power2: Dict) -> bool:
        """Check if two powers contradict each other"""
        # Simple implementation - could be enhanced
        name1 = power1.get('name', '').lower()
        name2 = power2.get('name', '').lower()
        
        # Check for obvious contradictions
        contradictions = [
            ('fire', 'ice'), ('light', 'darkness'), ('healing', 'destruction'),
            ('creation', 'annihilation'), ('time stop', 'time acceleration')
        ]
        
        for term1, term2 in contradictions:
            if (term1 in name1 and term2 in name2) or (term2 in name1 and term1 in name2):
                return True
        
        return False
    
    def _find_trait_contradictions(self, old_traits: List[str], new_traits: List[str]) -> List[str]:
        """Find contradictory traits between old and new"""
        contradictions = []
        
        trait_opposites = {
            'honest': 'dishonest', 'brave': 'cowardly', 'kind': 'cruel',
            'patient': 'impulsive', 'calm': 'aggressive', 'loyal': 'treacherous'
        }
        
        for old_trait in old_traits:
            for new_trait in new_traits:
                for trait, opposite in trait_opposites.items():
                    if (trait in old_trait.lower() and opposite in new_trait.lower()) or \
                       (opposite in old_trait.lower() and trait in new_trait.lower()):
                        contradictions.append(f"{old_trait} vs {new_trait}")
        
        return contradictions
    
    def _check_causality(self, event: Dict[str, Any]) -> bool:
        """Check if event maintains causality"""
        # Simplified causality check
        return True  # Would implement more complex logic
    
    def _is_power_source_consistent_with_genre(self, power_source: str, genre: str) -> bool:
        """Check if power source fits the genre"""
        genre_power_map = {
            'urban_realistic': ['technology', 'training', 'genetics'],
            'high_fantasy': ['magic', 'divine', 'ancient'],
            'sci_fi': ['technology', 'mutation', 'alien'],
            'cyberpunk': ['technology', 'enhancement', 'digital']
        }
        
        allowed_sources = genre_power_map.get(genre, [])
        return any(source in power_source.lower() for source in allowed_sources)
    
    def _get_existing_relationship(self, char_a: str, char_b: str) -> Optional[Dict]:
        """Get existing relationship between characters"""
        # Would check relationship database
        return None
    
    def _relationships_contradict(self, old_rel: Dict, new_rel: Dict) -> bool:
        """Check if relationships contradict"""
        # Simplified check
        return False
    
    def _setting_matches_genre(self, setting: Dict, genre: str) -> bool:
        """Check if setting matches genre expectations"""
        # Simplified check
        return True
    
    def _extract_tone_markers(self, content: Dict[str, Any]) -> List[str]:
        """Extract tone indicators from content"""
        # Would analyze language patterns
        return []
    
    def _get_established_tone(self) -> List[str]:
        """Get established tone from previous content"""
        # Would analyze historical content
        return []
    
    def _tone_drift_detected(self, current_tone: List[str], established_tone: List[str]) -> bool:
        """Detect if tone has drifted"""
        # Simplified check
        return False

# Singleton instance
continuity_engine = None

def get_continuity_engine():
    """Get or create continuity engine instance"""
    global continuity_engine
    if continuity_engine is None:
        continuity_engine = ContinuityEngine()
    return continuity_engine