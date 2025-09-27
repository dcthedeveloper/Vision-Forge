"""
VisionForge Content Safety System
Creator-first NSFW filtering with user control
"""

from enum import Enum
from typing import Dict, List, Optional, Any
import re
import logging

logger = logging.getLogger(__name__)

class ContentSafetyLevel(Enum):
    STRICT = "strict"           # Family-friendly only
    MODERATE = "moderate"       # Standard + mild mature themes
    PERMISSIVE = "permissive"   # Adult fiction/horror/dark themes allowed

class ContentCategory(Enum):
    FAMILY_SAFE = "family_safe"
    MILD_MATURE = "mild_mature"  
    ADULT_THEMES = "adult_themes"
    VIOLENCE = "violence"
    HORROR = "horror"
    SEXUAL_CONTENT = "sexual_content"

class ContentFilterResult:
    def __init__(self, allowed: bool, safety_level: ContentSafetyLevel, 
                 flagged_categories: List[ContentCategory] = None, 
                 suggestions: List[str] = None):
        self.allowed = allowed
        self.safety_level = safety_level
        self.flagged_categories = flagged_categories or []
        self.suggestions = suggestions or []

class VisionForgeContentFilter:
    def __init__(self):
        self.content_patterns = self._initialize_content_patterns()
        self.safety_guidelines = self._initialize_safety_guidelines()
    
    def _initialize_content_patterns(self) -> Dict[ContentCategory, Dict[str, List[str]]]:
        """Initialize content detection patterns"""
        return {
            ContentCategory.FAMILY_SAFE: {
                "positive_indicators": [
                    "friendship", "adventure", "discovery", "learning", "teamwork",
                    "kindness", "courage", "problem-solving", "creativity", "growth"
                ],
                "themes": ["coming of age", "friendship", "adventure", "education"]
            },
            
            ContentCategory.MILD_MATURE: {
                "indicators": [
                    "betrayal", "loss", "conflict", "rivalry", "ambition", 
                    "moral complexity", "political intrigue", "economic struggle"
                ],
                "themes": ["business drama", "political thriller", "mystery", "competition"]
            },
            
            ContentCategory.ADULT_THEMES: {
                "indicators": [
                    "addiction", "mental health", "trauma", "abuse", "corruption",
                    "existential crisis", "moral ambiguity", "systemic oppression"
                ],
                "themes": ["psychological drama", "noir", "dystopian", "social commentary"]
            },
            
            ContentCategory.VIOLENCE: {
                "mild": ["fight", "battle", "conflict", "struggle", "combat"],
                "moderate": ["injury", "weapon", "blood", "pain", "wound"],
                "intense": ["torture", "murder", "brutality", "massacre", "gore"]
            },
            
            ContentCategory.HORROR: {
                "psychological": ["fear", "dread", "nightmare", "haunted", "terror"],
                "supernatural": ["demon", "ghost", "possessed", "cursed", "occult"], 
                "body_horror": ["mutation", "decay", "infection", "transformation"]
            },
            
            ContentCategory.SEXUAL_CONTENT: {
                "romantic": ["romance", "attraction", "love", "relationship", "dating"],
                "suggestive": ["seduction", "intimacy", "passion", "desire"],
                "explicit": ["sexual", "erotic", "adult", "mature content"]
            }
        }
    
    def _initialize_safety_guidelines(self) -> Dict[ContentSafetyLevel, Dict]:
        """Initialize safety level guidelines"""
        return {
            ContentSafetyLevel.STRICT: {
                "allowed_categories": [ContentCategory.FAMILY_SAFE],
                "max_violence_level": None,
                "max_horror_level": None,
                "max_sexual_level": None,
                "description": "Family-friendly content only. No violence, horror, or mature themes.",
                "target_audience": "All ages, family viewing"
            },
            
            ContentSafetyLevel.MODERATE: {
                "allowed_categories": [
                    ContentCategory.FAMILY_SAFE, 
                    ContentCategory.MILD_MATURE,
                    ContentCategory.VIOLENCE  # mild only
                ],
                "max_violence_level": "mild",
                "max_horror_level": "psychological",  # light psychological themes
                "max_sexual_level": "romantic",
                "description": "Standard content with mild mature themes. Light conflict and romance allowed.",
                "target_audience": "Teen and adult audiences"
            },
            
            ContentSafetyLevel.PERMISSIVE: {
                "allowed_categories": [
                    ContentCategory.FAMILY_SAFE,
                    ContentCategory.MILD_MATURE, 
                    ContentCategory.ADULT_THEMES,
                    ContentCategory.VIOLENCE,
                    ContentCategory.HORROR,
                    ContentCategory.SEXUAL_CONTENT
                ],
                "max_violence_level": "intense",
                "max_horror_level": "body_horror",
                "max_sexual_level": "suggestive",  # Still avoid explicit
                "description": "Full creative freedom for adult fiction, horror, and dark themes.",
                "target_audience": "Mature adult creators"
            }
        }
    
    def analyze_content(self, text: str, safety_level: ContentSafetyLevel) -> ContentFilterResult:
        """Analyze content against safety level"""
        flagged_categories = []
        suggestions = []
        
        # Check each content category
        for category in ContentCategory:
            if self._detect_content_category(text, category):
                flagged_categories.append(category)
        
        # Determine if content is allowed at this safety level
        guidelines = self.safety_guidelines[safety_level]
        allowed = True
        
        for category in flagged_categories:
            if category not in guidelines["allowed_categories"]:
                allowed = False
                suggestions.append(f"Content contains {category.value} themes not allowed in {safety_level.value} mode")
            
            # Check intensity levels for specific categories
            if category == ContentCategory.VIOLENCE:
                violence_level = self._detect_violence_level(text)
                max_allowed = guidelines.get("max_violence_level")
                if max_allowed and self._is_intensity_too_high(violence_level, max_allowed):
                    allowed = False
                    suggestions.append(f"Violence level ({violence_level}) exceeds {safety_level.value} limit ({max_allowed})")
            
            elif category == ContentCategory.HORROR:
                horror_level = self._detect_horror_level(text)
                max_allowed = guidelines.get("max_horror_level")
                if max_allowed and self._is_intensity_too_high(horror_level, max_allowed):
                    allowed = False
                    suggestions.append(f"Horror content exceeds {safety_level.value} guidelines")
            
            elif category == ContentCategory.SEXUAL_CONTENT:
                sexual_level = self._detect_sexual_level(text)
                max_allowed = guidelines.get("max_sexual_level")
                if max_allowed and self._is_intensity_too_high(sexual_level, max_allowed):
                    allowed = False
                    suggestions.append(f"Sexual content level exceeds {safety_level.value} guidelines")
        
        # Generate helpful suggestions if content is not allowed
        if not allowed:
            suggestions.extend(self._generate_content_suggestions(flagged_categories, safety_level))
        
        return ContentFilterResult(
            allowed=allowed,
            safety_level=safety_level,
            flagged_categories=flagged_categories,
            suggestions=suggestions
        )
    
    def _detect_content_category(self, text: str, category: ContentCategory) -> bool:
        """Detect if text contains content from specific category"""
        text_lower = text.lower()
        patterns = self.content_patterns.get(category, {})
        
        # Check for category indicators
        for pattern_type, pattern_list in patterns.items():
            if isinstance(pattern_list, list):
                for pattern in pattern_list:
                    if pattern.lower() in text_lower:
                        return True
        
        return False
    
    def _detect_violence_level(self, text: str) -> Optional[str]:
        """Detect violence intensity level"""
        text_lower = text.lower()
        violence_patterns = self.content_patterns[ContentCategory.VIOLENCE]
        
        if any(pattern in text_lower for pattern in violence_patterns.get("intense", [])):
            return "intense"
        elif any(pattern in text_lower for pattern in violence_patterns.get("moderate", [])):
            return "moderate"
        elif any(pattern in text_lower for pattern in violence_patterns.get("mild", [])):
            return "mild"
        
        return None
    
    def _detect_horror_level(self, text: str) -> Optional[str]:
        """Detect horror content level"""
        text_lower = text.lower()
        horror_patterns = self.content_patterns[ContentCategory.HORROR]
        
        if any(pattern in text_lower for pattern in horror_patterns.get("body_horror", [])):
            return "body_horror"
        elif any(pattern in text_lower for pattern in horror_patterns.get("supernatural", [])):
            return "supernatural" 
        elif any(pattern in text_lower for pattern in horror_patterns.get("psychological", [])):
            return "psychological"
        
        return None
    
    def _detect_sexual_level(self, text: str) -> Optional[str]:
        """Detect sexual content level"""
        text_lower = text.lower()
        sexual_patterns = self.content_patterns[ContentCategory.SEXUAL_CONTENT]
        
        if any(pattern in text_lower for pattern in sexual_patterns.get("explicit", [])):
            return "explicit"
        elif any(pattern in text_lower for pattern in sexual_patterns.get("suggestive", [])):
            return "suggestive"
        elif any(pattern in text_lower for pattern in sexual_patterns.get("romantic", [])):
            return "romantic"
        
        return None
    
    def _is_intensity_too_high(self, detected_level: str, max_allowed: str) -> bool:
        """Check if detected intensity exceeds allowed level"""
        intensity_hierarchy = {
            # Violence levels
            "mild": 1, "moderate": 2, "intense": 3,
            # Horror levels  
            "psychological": 1, "supernatural": 2, "body_horror": 3,
            # Sexual levels
            "romantic": 1, "suggestive": 2, "explicit": 3
        }
        
        detected_score = intensity_hierarchy.get(detected_level, 0)
        max_score = intensity_hierarchy.get(max_allowed, 0)
        
        return detected_score > max_score
    
    def _generate_content_suggestions(self, flagged_categories: List[ContentCategory], 
                                    safety_level: ContentSafetyLevel) -> List[str]:
        """Generate helpful suggestions for content modification"""
        suggestions = []
        
        if safety_level == ContentSafetyLevel.STRICT:
            suggestions.extend([
                "Consider focusing on friendship, adventure, or problem-solving themes",
                "Replace conflict with collaboration or friendly competition",
                "Emphasize positive character growth and learning experiences"
            ])
        
        elif safety_level == ContentSafetyLevel.MODERATE:
            suggestions.extend([
                "Keep violence brief and non-graphic (focus on consequences rather than details)",
                "Romance can include attraction and relationships without explicit content", 
                "Mystery and suspense are welcome if not too frightening"
            ])
        
        # Add category-specific suggestions
        for category in flagged_categories:
            if category == ContentCategory.VIOLENCE:
                suggestions.append("Consider implying violence rather than describing it explicitly")
            elif category == ContentCategory.HORROR:
                suggestions.append("Focus on psychological tension rather than graphic imagery")
            elif category == ContentCategory.SEXUAL_CONTENT:
                suggestions.append("Romantic themes are fine, but keep physical content tasteful")
        
        return suggestions[:3]  # Limit to 3 most relevant suggestions
    
    def get_safety_level_info(self, safety_level: ContentSafetyLevel) -> Dict[str, Any]:
        """Get information about a safety level"""
        return self.safety_guidelines[safety_level]
    
    def apply_content_filter_to_prompt(self, prompt: str, safety_level: ContentSafetyLevel) -> str:
        """Apply content filtering guidance to AI prompts"""
        guidelines = self.safety_guidelines[safety_level]
        
        if safety_level == ContentSafetyLevel.STRICT:
            filter_instruction = """
CONTENT SAFETY: Generate only family-friendly content suitable for all ages. 
Avoid violence, mature themes, horror, or sexual content. Focus on positive, 
educational, and uplifting themes."""
        
        elif safety_level == ContentSafetyLevel.MODERATE:
            filter_instruction = """
CONTENT SAFETY: Generate content suitable for teen and adult audiences. 
Mild conflict and romance are acceptable. Keep violence brief and non-graphic. 
Avoid explicit sexual content or intense horror."""
        
        else:  # PERMISSIVE
            filter_instruction = """
CONTENT SAFETY: Full creative freedom for mature themes. Adult fiction, 
horror, and dark themes are allowed. Maintain literary quality and avoid 
gratuitous content."""
        
        return f"{filter_instruction}\n\n{prompt}"

# Singleton instance
content_filter = None

def get_content_filter():
    """Get or create content filter instance"""
    global content_filter
    if content_filter is None:
        content_filter = VisionForgeContentFilter()
    return content_filter