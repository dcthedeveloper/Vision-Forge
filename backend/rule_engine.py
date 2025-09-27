"""
VisionForge Rule Engine - Phase 1 Implementation
Handles continuity linting and constraint checking with "explain why + quick fix" UX
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
import re
from enum import Enum

logger = logging.getLogger(__name__)

class RuleSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class RuleViolation:
    rule_id: str
    rule_name: str
    severity: RuleSeverity
    message: str
    explanation: str
    quick_fix: Optional[str]
    affected_content: str
    suggested_replacement: Optional[str] = None

@dataclass
class PowerConstraint:
    max_high_cost_powers: int = 2  # Max powers with cost > 7
    total_power_cost_limit: int = 30  # Total cost across all powers
    conflicting_power_pairs: List[Tuple[str, str]] = None  # Powers that can't coexist

class VisionForgeRuleEngine:
    def __init__(self):
        self.power_constraints = PowerConstraint()
        self.character_rules = self._initialize_character_rules()
        self.style_rules = self._initialize_style_rules()
    
    def _initialize_character_rules(self) -> Dict[str, Any]:
        """Initialize character consistency rules"""
        return {
            "power_cost_limit": {
                "description": "Characters can't have more than 2 high-cost powers (>7)",
                "severity": RuleSeverity.ERROR,
                "check_function": self._check_power_cost_limit
            },
            "total_cost_limit": {
                "description": "Total power cost cannot exceed 30 points",
                "severity": RuleSeverity.ERROR,
                "check_function": self._check_total_power_cost
            },
            "origin_power_compatibility": {
                "description": "Powers must be compatible with character origin",
                "severity": RuleSeverity.WARNING,
                "check_function": self._check_origin_power_compatibility
            },
            "character_consistency": {
                "description": "Character traits must be internally consistent",
                "severity": RuleSeverity.WARNING,
                "check_function": self._check_character_consistency
            },
            "timeline_consistency": {
                "description": "Character events must follow logical timeline",
                "severity": RuleSeverity.ERROR,
                "check_function": self._check_timeline_consistency
            }
        }
    
    def _initialize_style_rules(self) -> Dict[str, Any]:
        """Initialize writing style rules"""
        return {
            "cliche_detector": {
                "description": "Detect overused phrases and clichés",
                "severity": RuleSeverity.WARNING,
                "check_function": self._check_cliches
            },
            "power_name_realism": {
                "description": "Power names should be realistic, not generic fantasy",
                "severity": RuleSeverity.INFO,
                "check_function": self._check_power_name_realism
            },
            "show_dont_tell": {
                "description": "Prefer showing actions over telling descriptions",
                "severity": RuleSeverity.INFO,
                "check_function": self._check_show_dont_tell
            }
        }
    
    def check_character_rules(self, character_data: Dict[str, Any]) -> List[RuleViolation]:
        """Run all character rule checks"""
        violations = []
        
        for rule_id, rule_config in self.character_rules.items():
            try:
                rule_violations = rule_config["check_function"](character_data)
                violations.extend(rule_violations)
            except Exception as e:
                logger.error(f"Rule check failed for {rule_id}: {e}")
                violations.append(RuleViolation(
                    rule_id=rule_id,
                    rule_name=rule_config["description"],
                    severity=RuleSeverity.ERROR,
                    message=f"Rule check failed: {str(e)}",
                    explanation="Internal error during rule checking",
                    quick_fix="Please try again or contact support",
                    affected_content="Rule engine"
                ))
        
        return violations
    
    def check_style_rules(self, text_content: str, content_type: str = "general") -> List[RuleViolation]:
        """Run all style rule checks on text content"""
        violations = []
        
        for rule_id, rule_config in self.style_rules.items():
            try:
                rule_violations = rule_config["check_function"](text_content, content_type)
                violations.extend(rule_violations)
            except Exception as e:
                logger.error(f"Style rule check failed for {rule_id}: {e}")
        
        return violations
    
    def _check_power_cost_limit(self, character_data: Dict[str, Any]) -> List[RuleViolation]:
        """Check if character has too many high-cost powers"""
        violations = []
        
        power_suggestions = character_data.get("power_suggestions", [])
        high_cost_powers = [p for p in power_suggestions if p.get("cost_level", 0) > 7]
        
        if len(high_cost_powers) > self.power_constraints.max_high_cost_powers:
            power_names = [p.get("name", "Unnamed Power") for p in high_cost_powers]
            violations.append(RuleViolation(
                rule_id="power_cost_limit",
                rule_name="High-Cost Power Limit",
                severity=RuleSeverity.ERROR,
                message=f"Too many high-cost powers: {len(high_cost_powers)}/2 maximum",
                explanation=f"Characters with more than 2 high-cost powers (>7) become overpowered and unbalanced. Current high-cost powers: {', '.join(power_names)}",
                quick_fix=f"Remove or reduce cost of: {power_names[-1]}",
                affected_content=", ".join(power_names),
                suggested_replacement=f"Consider replacing '{power_names[-1]}' with a complementary lower-cost ability"
            ))
        
        return violations
    
    def _check_total_power_cost(self, character_data: Dict[str, Any]) -> List[RuleViolation]:
        """Check total power cost doesn't exceed limit"""
        violations = []
        
        power_suggestions = character_data.get("power_suggestions", [])
        total_cost = sum(p.get("cost_level", 0) for p in power_suggestions)
        
        if total_cost > self.power_constraints.total_power_cost_limit:
            violations.append(RuleViolation(
                rule_id="total_cost_limit",
                rule_name="Total Power Cost Limit",
                severity=RuleSeverity.ERROR,
                message=f"Total power cost too high: {total_cost}/30 maximum",
                explanation="Characters with excessive total power cost become unbalanced and difficult to challenge in stories.",
                quick_fix="Reduce power levels or remove some abilities",
                affected_content=f"Total cost: {total_cost}",
                suggested_replacement="Consider focusing on 2-3 core abilities instead of many powers"
            ))
        
        return violations
    
    def _check_origin_power_compatibility(self, character_data: Dict[str, Any]) -> List[RuleViolation]:
        """Check if powers match character origin"""
        violations = []
        
        origin = character_data.get("character_origin", "")
        power_source = character_data.get("power_source", "")
        power_suggestions = character_data.get("power_suggestions", [])
        
        # Define incompatible combinations
        incompatible_combinations = {
            "human": ["Cosmic_Powers", "Divine_Abilities", "Alien_Tech"],
            "nootropic_enhanced": ["Magic_Powers", "Divine_Abilities", "Cosmic_Powers"]
        }
        
        if origin in incompatible_combinations:
            for power in power_suggestions:
                power_name = power.get("name", "")
                for incompatible_type in incompatible_combinations[origin]:
                    if incompatible_type.lower().replace("_", " ") in power_name.lower():
                        violations.append(RuleViolation(
                            rule_id="origin_power_compatibility",
                            rule_name="Origin-Power Compatibility",
                            severity=RuleSeverity.WARNING,
                            message=f"Power '{power_name}' may not fit '{origin}' origin",
                            explanation=f"A {origin} character typically wouldn't have access to {incompatible_type.replace('_', ' ').lower()}",
                            quick_fix=f"Replace with {origin}-appropriate ability or adjust origin",
                            affected_content=power_name,
                            suggested_replacement=f"Consider a {power_source.replace('_', ' ')}-based alternative"
                        ))
        
        return violations
    
    def _check_character_consistency(self, character_data: Dict[str, Any]) -> List[RuleViolation]:
        """Check for internal character consistency issues"""
        violations = []
        
        traits = character_data.get("traits", [])
        social_status = character_data.get("social_status", "")
        archetype_tags = character_data.get("archetype_tags", [])
        
        # Check for contradictory traits
        trait_texts = [t.get("trait", "").lower() for t in traits]
        
        contradictions = [
            (["shy", "introverted"], ["charismatic", "leader", "public"]),
            (["poor", "struggling"], ["wealthy", "rich", "elite"]),
            (["pacifist", "peaceful"], ["violent", "aggressive", "warrior"])
        ]
        
        for negative_traits, positive_traits in contradictions:
            has_negative = any(neg in trait_text for trait_text in trait_texts for neg in negative_traits)
            has_positive = any(pos in trait_text for trait_text in trait_texts for pos in positive_traits)
            
            if has_negative and has_positive:
                violations.append(RuleViolation(
                    rule_id="character_consistency",
                    rule_name="Character Trait Consistency",
                    severity=RuleSeverity.WARNING,
                    message="Contradictory character traits detected",
                    explanation=f"Character has both {negative_traits} and {positive_traits} characteristics which may conflict",
                    quick_fix="Add complexity explaining the contradiction or remove conflicting traits",
                    affected_content="Character traits",
                    suggested_replacement="Consider making this internal conflict part of the character's complexity"
                ))
        
        return violations
    
    def _check_timeline_consistency(self, character_data: Dict[str, Any]) -> List[RuleViolation]:
        """Check for timeline consistency in backstory"""
        violations = []
        
        backstory_seeds = character_data.get("backstory_seeds", [])
        
        # Look for temporal inconsistencies
        for i, seed in enumerate(backstory_seeds):
            seed_lower = seed.lower()
            # Check for contradictory time references
            if "young" in seed_lower and "veteran" in seed_lower:
                violations.append(RuleViolation(
                    rule_id="timeline_consistency",
                    rule_name="Timeline Consistency",
                    severity=RuleSeverity.WARNING,
                    message="Potential age/experience contradiction in backstory",
                    explanation="Backstory suggests character is both young and experienced, which may need clarification",
                    quick_fix="Specify how character gained experience at young age, or adjust timeline",
                    affected_content=seed,
                    suggested_replacement="Consider 'prodigy' or 'accelerated development' explanation"
                ))
        
        return violations
    
    def _check_cliches(self, text_content: str, content_type: str) -> List[RuleViolation]:
        """Check for clichéd phrases and overused terms"""
        violations = []
        
        # Marcus-inspired improvements: avoid generic terms
        cliche_patterns = {
            r"\b(kinesis|manipulation)\b": {
                "message": "Avoid generic '-kinesis' or 'manipulation' power names",
                "fix": "Use specific, clinical terms like 'Cognitive Processing' or 'Neural Enhancement'",
                "replacement": "Consider realistic scientific terminology"
            },
            r"\bdark (past|history|secret)\b": {
                "message": "Generic 'dark past' cliché detected",
                "fix": "Specify the actual challenging experience",
                "replacement": "Describe the specific traumatic or difficult experience"
            },
            r"\bchosen one\b": {
                "message": "'Chosen one' trope is overused",
                "fix": "Make character earn their role through effort and choices",
                "replacement": "Character who seizes opportunity or creates their own destiny"
            },
            r"\bmysterious stranger\b": {
                "message": "Generic 'mysterious stranger' character type",
                "fix": "Give specific background and clear motivations",
                "replacement": "Character with complex but understandable motivations"
            }
        }
        
        for pattern, info in cliche_patterns.items():
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                violations.append(RuleViolation(
                    rule_id="cliche_detector",
                    rule_name="Cliché Detection",
                    severity=RuleSeverity.WARNING,
                    message=info["message"],
                    explanation=f"The phrase '{match.group()}' is commonly overused in character creation",
                    quick_fix=info["fix"],
                    affected_content=match.group(),
                    suggested_replacement=info["replacement"]
                ))
        
        return violations
    
    def _check_power_name_realism(self, text_content: str, content_type: str) -> List[RuleViolation]:
        """Check for unrealistic fantasy power names"""
        violations = []
        
        if content_type in ["power", "ability"]:
            # Look for overly fantasy-like power names
            unrealistic_patterns = [
                r"\b\w+blast\b",  # "Fireblast", "Iceblast"
                r"\b\w+storm\b",  # "Icestorm", "Mindstorm"  
                r"\b\w+wave\b",   # "Shockwave" is okay, but "Deathwave" isn't
                r"\b(ultimate|supreme|god|divine)\b"  # Overpowered descriptors
            ]
            
            for pattern in unrealistic_patterns:
                matches = re.finditer(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    if match.group().lower() not in ["shockwave", "brainwave"]:  # Allow some realistic ones
                        violations.append(RuleViolation(
                            rule_id="power_name_realism",
                            rule_name="Power Name Realism",
                            severity=RuleSeverity.INFO,
                            message=f"Power name '{match.group()}' sounds too fantasy-generic",
                            explanation="Marcus-style characters use clinical, scientific terminology for abilities",
                            quick_fix="Use scientific or medical terminology",
                            affected_content=match.group(),
                            suggested_replacement="Try terms like 'Enhanced Processing', 'Neural Acceleration', or 'Cognitive Amplification'"
                        ))
        
        return violations
    
    def _check_show_dont_tell(self, text_content: str, content_type: str) -> List[RuleViolation]:
        """Check for telling instead of showing"""
        violations = []
        
        # Look for "telling" phrases
        telling_patterns = [
            r"he/she is (very|extremely|really) \w+",
            r"they are known for",
            r"has a reputation for",
            r"is famous for"
        ]
        
        for pattern in telling_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                violations.append(RuleViolation(
                    rule_id="show_dont_tell",
                    rule_name="Show Don't Tell",
                    severity=RuleSeverity.INFO,
                    message=f"Consider showing rather than telling: '{match.group()}'",
                    explanation="Instead of stating character traits, show them through actions or specific examples",
                    quick_fix="Replace with specific action or behavior that demonstrates the trait",
                    affected_content=match.group(),
                    suggested_replacement="Describe what they do that shows this quality"
                ))
        
        return violations
    
    def get_rule_summary(self) -> Dict[str, Any]:
        """Get summary of all available rules"""
        return {
            "character_rules": len(self.character_rules),
            "style_rules": len(self.style_rules),
            "rule_categories": {
                "power_constraints": ["power_cost_limit", "total_cost_limit"],
                "character_consistency": ["origin_power_compatibility", "character_consistency", "timeline_consistency"],
                "style_quality": ["cliche_detector", "power_name_realism", "show_dont_tell"]
            }
        }

# Singleton instance
rule_engine = None

def get_rule_engine():
    """Get or create rule engine instance"""
    global rule_engine
    if rule_engine is None:
        rule_engine = VisionForgeRuleEngine()
    return rule_engine

def check_character_rules(character_data: Dict[str, Any]) -> List[RuleViolation]:
    """Convenience function to check character rules"""
    engine = get_rule_engine()
    return engine.check_character_rules(character_data)

def check_style_rules(text_content: str, content_type: str = "general") -> List[RuleViolation]:
    """Convenience function to check style rules"""
    engine = get_rule_engine()
    return engine.check_style_rules(text_content, content_type)