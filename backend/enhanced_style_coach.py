"""
VisionForge Enhanced Style Coach with Rationale
Educational style analysis that explains WHY text needs improvement
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re
import logging

logger = logging.getLogger(__name__)

class StyleIssueType(Enum):
    CLICHE_LANGUAGE = "cliche_language"
    PASSIVE_VOICE = "passive_voice"
    TELLING_NOT_SHOWING = "telling_not_showing"
    WEAK_VERBS = "weak_verbs"
    ADVERB_OVERUSE = "adverb_overuse"
    GENERIC_DESCRIPTIONS = "generic_descriptions"
    REPETITIVE_STRUCTURE = "repetitive_structure"
    UNCLEAR_PRONOUNS = "unclear_pronouns"
    FILTER_WORDS = "filter_words"
    AI_TELLTALES = "ai_telltales"

class SeverityLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class StyleIssue:
    issue_type: StyleIssueType
    severity: SeverityLevel
    title: str
    explanation: str
    problematic_text: str
    suggested_revision: str
    reasoning: str
    examples: Dict[str, str]
    position: Tuple[int, int]  # Start and end character positions
    learning_resources: List[str]

@dataclass
class StyleAnalysisResult:
    overall_score: float
    readability_score: float
    engagement_score: float
    professionalism_score: float
    issues: List[StyleIssue]
    strengths: List[str]
    improvement_summary: str
    educational_notes: List[str]

class EnhancedStyleCoach:
    def __init__(self):
        self.cliche_patterns = self._initialize_cliche_patterns()
        self.weak_verb_patterns = self._initialize_weak_verb_patterns()
        self.filter_word_patterns = self._initialize_filter_words()
        self.ai_telltale_patterns = self._initialize_ai_telltales()
        self.educational_resources = self._initialize_educational_resources()
    
    def _initialize_cliche_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize cliché detection patterns with explanations"""
        return {
            "delve": {
                "alternatives": ["explore", "examine", "investigate", "analyze"],
                "explanation": "'Delve' is overused in AI writing and sounds pretentious in most contexts",
                "example_bad": "Let's delve into this topic",
                "example_good": "Let's explore this topic",
                "severity": SeverityLevel.MEDIUM
            },
            "nestled": {
                "alternatives": ["sat", "lay", "rested", "stood"],
                "explanation": "AI overuses 'nestled' to describe any object's position, making it clichéd",
                "example_bad": "The house nestled among the trees",
                "example_good": "The house sat among the trees",
                "severity": SeverityLevel.MEDIUM
            },
            "tapestry": {
                "alternatives": ["mixture", "blend", "collection", "array"],
                "explanation": "Metaphorical 'tapestry' is an AI cliché for describing any complex situation",
                "example_bad": "A rich tapestry of emotions",
                "example_good": "A complex blend of emotions",
                "severity": SeverityLevel.HIGH
            },
            "enigmatic": {
                "alternatives": ["mysterious", "puzzling", "unclear", "cryptic"],
                "explanation": "'Enigmatic' is overused by AI to add sophistication but often sounds forced",
                "example_bad": "His enigmatic smile",
                "example_good": "His mysterious smile",
                "severity": SeverityLevel.MEDIUM
            },
            "meticulous": {
                "alternatives": ["careful", "thorough", "detailed", "precise"],
                "explanation": "AI frequently uses 'meticulous' as a generic intensifier",
                "example_bad": "She was meticulous in her work",
                "example_good": "She was thorough in her work",
                "severity": SeverityLevel.LOW
            }
        }
    
    def _initialize_weak_verb_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize weak verb patterns with strong alternatives"""
        return {
            "was/were + ing": {
                "pattern": r"\b(was|were)\s+\w+ing\b",
                "explanation": "Progressive past tense often weakens action and creates distance",
                "example_bad": "She was running down the street",
                "example_good": "She ran down the street",
                "alternatives": "Convert to simple past for stronger action"
            },
            "is/are + adjective": {
                "pattern": r"\b(is|are)\s+(very\s+)?\w+\b",
                "explanation": "Linking verbs create static descriptions instead of dynamic action",
                "example_bad": "The room is dark and cold",
                "example_good": "Darkness filled the cold room",
                "alternatives": "Use action verbs or show through specific details"
            },
            "seems/appears": {
                "pattern": r"\b(seems?|appears?)\s+",
                "explanation": "These verbs create uncertainty and distance from the action",
                "example_bad": "He seems angry",
                "example_good": "He clenched his fists, jaw tight",
                "alternatives": "Show the evidence instead of stating the impression"
            },
            "feels": {
                "pattern": r"\bfeels?\s+",
                "explanation": "'Feels' is often a filter word that distances readers from emotion",
                "example_bad": "She feels nervous",
                "example_good": "Her hands trembled as she spoke",
                "alternatives": "Show physical manifestations of the feeling"
            }
        }
    
    def _initialize_filter_words(self) -> Dict[str, Dict[str, Any]]:
        """Initialize filter word patterns that create distance"""
        return {
            "saw/watched/looked": {
                "explanation": "These words filter the reader's experience through the character's perception",
                "example_bad": "She saw the monster approaching",
                "example_good": "The monster approached",
                "reasoning": "Direct presentation is more immediate and engaging"
            },
            "heard/listened": {
                "explanation": "Auditory filter words create unnecessary distance from sounds",
                "example_bad": "He heard footsteps in the hallway",
                "example_good": "Footsteps echoed in the hallway",
                "reasoning": "Let readers hear directly rather than through the character"
            },
            "felt/touched": {
                "explanation": "Tactile filter words weaken physical sensations",
                "example_bad": "She felt the cold wind",
                "example_good": "Cold wind bit her skin",
                "reasoning": "Direct sensory description is more visceral"
            },
            "noticed/realized": {
                "explanation": "These words tell us about character awareness instead of showing discovery",
                "example_bad": "He noticed the door was open",
                "example_good": "The door stood open",
                "reasoning": "Show the discovery through description or dialogue"
            }
        }
    
    def _initialize_ai_telltales(self) -> List[Dict[str, Any]]:
        """Initialize AI-specific writing patterns to avoid"""
        return [
            {
                "pattern": r"\bnavigat(e|ing|ed)\b.*\b(landscape|waters|terrain)\b",
                "issue": "AI frequently uses 'navigate' metaphorically for any challenge",
                "example_bad": "Navigating the complex landscape of emotions",
                "example_good": "Dealing with complex emotions",
                "severity": SeverityLevel.HIGH
            },
            {
                "pattern": r"\bunpack\b.*\b(meaning|significance|implications)\b",
                "issue": "'Unpack' is overused by AI to discuss analysis",
                "example_bad": "Let's unpack the meaning of this",
                "example_good": "Let's examine what this means",
                "severity": SeverityLevel.MEDIUM
            },
            {
                "pattern": r"\bjuxtaposition\b",
                "issue": "AI uses 'juxtaposition' excessively to sound sophisticated",
                "example_bad": "The juxtaposition of light and dark",
                "example_good": "The contrast between light and dark",
                "severity": SeverityLevel.MEDIUM
            },
            {
                "pattern": r"\b(furthermore|moreover|additionally)\b",
                "issue": "These formal transitions sound robotic in creative writing",
                "example_bad": "Furthermore, the character develops",
                "example_good": "The character also develops",
                "severity": SeverityLevel.LOW
            }
        ]
    
    def _initialize_educational_resources(self) -> Dict[str, List[str]]:
        """Initialize educational resources for different issues"""
        return {
            "show_dont_tell": [
                "Instead of stating emotions, show them through actions and dialogue",
                "Use specific, concrete details rather than abstract descriptions",
                "Let readers draw conclusions from evidence you provide"
            ],
            "active_voice": [
                "Active voice creates stronger, clearer sentences",
                "Subject performs the action rather than receiving it",
                "Passive voice can distance readers from the action"
            ],
            "strong_verbs": [
                "Choose verbs that carry specific meaning and energy",
                "Avoid generic verbs like 'is,' 'was,' 'seems,' 'feels'",
                "Strong verbs reduce need for adverbs and adjectives"
            ],
            "eliminate_filter_words": [
                "Filter words create distance between reader and story",
                "Present actions and sensations directly to readers",
                "Trust readers to experience story without mediation"
            ]
        }
    
    def analyze_text(self, text: str, focus_areas: List[str] = None) -> StyleAnalysisResult:
        """Perform comprehensive style analysis with detailed rationale"""
        issues = []
        
        # Analyze different types of issues
        issues.extend(self._detect_cliche_language(text))
        issues.extend(self._detect_passive_voice(text))
        issues.extend(self._detect_telling_not_showing(text))
        issues.extend(self._detect_weak_verbs(text))
        issues.extend(self._detect_filter_words(text))
        issues.extend(self._detect_ai_telltales(text))
        issues.extend(self._detect_adverb_overuse(text))
        issues.extend(self._detect_repetitive_structure(text))
        
        # Calculate scores
        overall_score = self._calculate_overall_score(text, issues)
        readability_score = self._calculate_readability_score(text)
        engagement_score = self._calculate_engagement_score(text, issues)
        professionalism_score = self._calculate_professionalism_score(text, issues)
        
        # Identify strengths
        strengths = self._identify_strengths(text, issues)
        
        # Generate improvement summary
        improvement_summary = self._generate_improvement_summary(issues)
        
        # Generate educational notes
        educational_notes = self._generate_educational_notes(issues)
        
        return StyleAnalysisResult(
            overall_score=overall_score,
            readability_score=readability_score,
            engagement_score=engagement_score,
            professionalism_score=professionalism_score,
            issues=issues,
            strengths=strengths,
            improvement_summary=improvement_summary,
            educational_notes=educational_notes
        )
    
    def _detect_cliche_language(self, text: str) -> List[StyleIssue]:
        """Detect clichéd language with detailed explanations"""
        issues = []
        
        for cliche, info in self.cliche_patterns.items():
            pattern = r'\b' + re.escape(cliche) + r'\b'
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            
            for match in matches:
                start, end = match.span()
                context_start = max(0, start - 20)
                context_end = min(len(text), end + 20)
                context = text[context_start:context_end]
                
                # Generate contextual suggestion
                suggested_revision = self._generate_contextual_revision(
                    text, start, end, info['alternatives']
                )
                
                issues.append(StyleIssue(
                    issue_type=StyleIssueType.CLICHE_LANGUAGE,
                    severity=info['severity'],
                    title=f"Overused word: '{cliche}'",
                    explanation=info['explanation'],
                    problematic_text=context,
                    suggested_revision=suggested_revision,
                    reasoning=f"This word appears frequently in AI-generated text and has become clichéd. "
                             f"Using alternatives like '{', '.join(info['alternatives'][:2])}' will sound more natural.",
                    examples={
                        "problematic": info['example_bad'],
                        "improved": info['example_good']
                    },
                    position=(start, end),
                    learning_resources=self.educational_resources.get("avoid_cliches", [])
                ))
        
        return issues
    
    def _detect_telling_not_showing(self, text: str) -> List[StyleIssue]:
        """Detect telling vs showing issues with educational explanations"""
        issues = []
        
        # Patterns that indicate telling instead of showing
        telling_patterns = [
            {
                "pattern": r"\b(he|she|they|character)\s+(felt|was|seemed)\s+(angry|sad|happy|nervous|excited|afraid)",
                "issue": "Stating emotions directly instead of showing them",
                "example_revision": "Show through actions: 'His fists clenched' instead of 'He felt angry'"
            },
            {
                "pattern": r"\b(suddenly|immediately|quickly|slowly)\b",
                "issue": "Adverbs telling pace instead of showing it through sentence structure",
                "example_revision": "Use short sentences for speed, longer ones for slow pace"
            },
            {
                "pattern": r"\bit was (clear|obvious|evident) that\b",
                "issue": "Telling readers what should be obvious from context",
                "example_revision": "Let readers discover this through dialogue or action"
            }
        ]
        
        for pattern_info in telling_patterns:
            matches = list(re.finditer(pattern_info["pattern"], text, re.IGNORECASE))
            
            for match in matches:
                start, end = match.span()
                context_start = max(0, start - 15)
                context_end = min(len(text), end + 15)
                context = text[context_start:context_end]
                
                issues.append(StyleIssue(
                    issue_type=StyleIssueType.TELLING_NOT_SHOWING,
                    severity=SeverityLevel.MEDIUM,
                    title="Telling instead of showing",
                    explanation="This passage tells readers information instead of showing it through concrete details",
                    problematic_text=context,
                    suggested_revision=pattern_info["example_revision"],
                    reasoning="Show-don't-tell creates more engaging, immersive writing. Instead of stating "
                             "facts, emotions, or situations, show them through specific actions, dialogue, "
                             "and sensory details that let readers experience the story directly.",
                    examples={
                        "telling": "She was nervous about the interview",
                        "showing": "She checked her watch for the third time, smoothing her skirt with damp palms"
                    },
                    position=(start, end),
                    learning_resources=self.educational_resources["show_dont_tell"]
                ))
        
        return issues
    
    def _detect_passive_voice(self, text: str) -> List[StyleIssue]:
        """Detect passive voice with educational explanations"""
        issues = []
        
        # Common passive voice patterns
        passive_patterns = [
            r"\b(was|were|is|are|been|be)\s+(being\s+)?\w+ed\b",
            r"\b(was|were|is|are|been|be)\s+(being\s+)?\w+en\b"
        ]
        
        for pattern in passive_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            
            for match in matches:
                start, end = match.span()
                context_start = max(0, start - 20)
                context_end = min(len(text), end + 20)
                context = text[context_start:context_end]
                
                # Try to suggest active voice alternative
                active_suggestion = self._suggest_active_voice(context)
                
                issues.append(StyleIssue(
                    issue_type=StyleIssueType.PASSIVE_VOICE,
                    severity=SeverityLevel.MEDIUM,
                    title="Passive voice construction",
                    explanation="Passive voice can make writing feel distant and unclear about who performs actions",
                    problematic_text=context,
                    suggested_revision=active_suggestion,
                    reasoning="Active voice creates clearer, more direct sentences by making the subject "
                             "perform the action. This creates stronger prose and clearer responsibility for actions.",
                    examples={
                        "passive": "The door was opened by Sarah",
                        "active": "Sarah opened the door"
                    },
                    position=(start, end),
                    learning_resources=self.educational_resources["active_voice"]
                ))
        
        return issues
    
    def _detect_weak_verbs(self, text: str) -> List[StyleIssue]:
        """Detect weak verb usage with specific improvement suggestions"""
        issues = []
        
        for verb_type, info in self.weak_verb_patterns.items():
            if 'pattern' in info:
                matches = list(re.finditer(info['pattern'], text, re.IGNORECASE))
                
                for match in matches:
                    start, end = match.span()
                    context_start = max(0, start - 15)
                    context_end = min(len(text), end + 15)
                    context = text[context_start:context_end]
                    
                    issues.append(StyleIssue(
                        issue_type=StyleIssueType.WEAK_VERBS,
                        severity=SeverityLevel.MEDIUM,
                        title=f"Weak verb pattern: {verb_type}",
                        explanation=info['explanation'],
                        problematic_text=context,
                        suggested_revision=info['alternatives'],
                        reasoning="Strong verbs create more vivid, energetic prose. They carry more "
                                 "specific meaning and reduce the need for additional modifiers.",
                        examples={
                            "weak": info['example_bad'],
                            "strong": info['example_good']
                        },
                        position=(start, end),
                        learning_resources=self.educational_resources["strong_verbs"]
                    ))
        
        return issues
    
    def _detect_filter_words(self, text: str) -> List[StyleIssue]:
        """Detect filter words that create distance from the story"""
        issues = []
        
        filter_patterns = [
            r"\b(saw|watched|looked at|observed)\b",
            r"\b(heard|listened to)\b",
            r"\b(felt|touched|sensed)\b",
            r"\b(noticed|realized|became aware)\b",
            r"\b(thought|wondered|considered)\b"
        ]
        
        for pattern in filter_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            
            for match in matches:
                start, end = match.span()
                context_start = max(0, start - 20)
                context_end = min(len(text), end + 20)
                context = text[context_start:context_end]
                
                filter_word = match.group().lower()
                filter_info = self._get_filter_word_info(filter_word)
                
                issues.append(StyleIssue(
                    issue_type=StyleIssueType.FILTER_WORDS,
                    severity=SeverityLevel.LOW,
                    title=f"Filter word: '{filter_word}'",
                    explanation=filter_info['explanation'],
                    problematic_text=context,
                    suggested_revision=filter_info['example_good'],
                    reasoning=filter_info['reasoning'],
                    examples={
                        "filtered": filter_info['example_bad'],
                        "direct": filter_info['example_good']
                    },
                    position=(start, end),
                    learning_resources=self.educational_resources["eliminate_filter_words"]
                ))
        
        return issues
    
    def _detect_ai_telltales(self, text: str) -> List[StyleIssue]:
        """Detect AI-specific writing patterns"""
        issues = []
        
        for telltale in self.ai_telltale_patterns:
            matches = list(re.finditer(telltale['pattern'], text, re.IGNORECASE))
            
            for match in matches:
                start, end = match.span()
                context_start = max(0, start - 25)
                context_end = min(len(text), end + 25)
                context = text[context_start:context_end]
                
                issues.append(StyleIssue(
                    issue_type=StyleIssueType.AI_TELLTALES,
                    severity=telltale['severity'],
                    title="AI writing pattern detected",
                    explanation=telltale['issue'],
                    problematic_text=context,
                    suggested_revision=telltale['example_good'],
                    reasoning="This phrase is commonly generated by AI systems and may sound "
                             "artificial to readers familiar with AI writing patterns.",
                    examples={
                        "ai_style": telltale['example_bad'],
                        "natural": telltale['example_good']
                    },
                    position=(start, end),
                    learning_resources=["Vary your vocabulary to avoid overused AI phrases"]
                ))
        
        return issues
    
    def _detect_adverb_overuse(self, text: str) -> List[StyleIssue]:
        """Detect excessive adverb usage"""
        issues = []
        
        # Find adverbs (words ending in -ly)
        adverb_pattern = r'\b\w+ly\b'
        adverbs = list(re.finditer(adverb_pattern, text))
        
        # Calculate adverb density
        word_count = len(text.split())
        adverb_count = len(adverbs)
        adverb_density = adverb_count / word_count if word_count > 0 else 0
        
        if adverb_density > 0.05:  # More than 5% adverbs
            issues.append(StyleIssue(
                issue_type=StyleIssueType.ADVERB_OVERUSE,
                severity=SeverityLevel.MEDIUM,
                title="Excessive adverb usage",
                explanation=f"Text contains {adverb_count} adverbs in {word_count} words ({adverb_density:.1%})",
                problematic_text=f"Adverbs found: {', '.join([m.group() for m in adverbs[:5]])}...",
                suggested_revision="Replace adverbs with stronger verbs or more specific descriptions",
                reasoning="Too many adverbs can weaken prose. Strong verbs and specific nouns "
                         "often eliminate the need for adverbial modification.",
                examples={
                    "adverb_heavy": "She quickly ran very carefully",
                    "stronger": "She sprinted with caution"
                },
                position=(0, len(text)),
                learning_resources=["Choose precise verbs instead of verb + adverb combinations"]
            ))
        
        return issues
    
    def _detect_repetitive_structure(self, text: str) -> List[StyleIssue]:
        """Detect repetitive sentence structures"""
        issues = []
        
        sentences = re.split(r'[.!?]+', text)
        sentence_starts = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Get first few words
                words = sentence.split()[:3]
                if words:
                    start_pattern = ' '.join(words).lower()
                    sentence_starts.append(start_pattern)
        
        # Check for repetitive patterns
        from collections import Counter
        start_counts = Counter(sentence_starts)
        
        for pattern, count in start_counts.items():
            if count >= 3 and len(pattern.split()) >= 2:  # Same pattern 3+ times
                issues.append(StyleIssue(
                    issue_type=StyleIssueType.REPETITIVE_STRUCTURE,
                    severity=SeverityLevel.LOW,
                    title="Repetitive sentence structure",
                    explanation=f"The pattern '{pattern}' starts {count} sentences",
                    problematic_text=f"Repeated pattern: '{pattern}'",
                    suggested_revision="Vary sentence beginnings and structures",
                    reasoning="Repetitive sentence structures create monotonous rhythm. "
                             "Varying sentence length and structure improves flow and engagement.",
                    examples={
                        "repetitive": "She walked. She saw. She stopped.",
                        "varied": "She walked down the path. The old oak caught her attention. Stopping, she admired its gnarled branches."
                    },
                    position=(0, len(text)),
                    learning_resources=["Mix short and long sentences for better rhythm"]
                ))
        
        return issues
    
    # Helper methods
    def _generate_contextual_revision(self, text: str, start: int, end: int, alternatives: List[str]) -> str:
        """Generate contextual revision suggestion"""
        context_start = max(0, start - 10)
        context_end = min(len(text), end + 10)
        context = text[context_start:context_end]
        
        original_word = text[start:end]
        alternative = alternatives[0] if alternatives else "alternative"
        
        return context.replace(original_word, alternative)
    
    def _suggest_active_voice(self, passive_text: str) -> str:
        """Suggest active voice alternative"""
        # Simplified suggestion - could be enhanced with more sophisticated parsing
        return "Consider: 'Subject + verb + object' instead of passive construction"
    
    def _get_filter_word_info(self, filter_word: str) -> Dict[str, str]:
        """Get information about specific filter word"""
        for key, info in self.filter_word_patterns.items():
            if any(word in filter_word for word in key.split('/')):
                return info
        
        return {
            "explanation": "This word can create distance between reader and story",
            "example_bad": f"She {filter_word} something",
            "example_good": "Show the something directly",
            "reasoning": "Direct presentation is more engaging"
        }
    
    def _calculate_overall_score(self, text: str, issues: List[StyleIssue]) -> float:
        """Calculate overall style score"""
        if not text:
            return 0.0
        
        # Start with base score
        base_score = 0.8
        
        # Deduct points for issues
        severity_weights = {
            SeverityLevel.CRITICAL: 0.3,
            SeverityLevel.HIGH: 0.2,
            SeverityLevel.MEDIUM: 0.1,
            SeverityLevel.LOW: 0.05
        }
        
        total_deduction = 0
        for issue in issues:
            total_deduction += severity_weights.get(issue.severity, 0.05)
        
        final_score = max(0.0, base_score - total_deduction)
        return min(1.0, final_score)
    
    def _calculate_readability_score(self, text: str) -> float:
        """Calculate readability score"""
        # Simplified readability calculation
        words = text.split()
        sentences = len(re.split(r'[.!?]+', text))
        
        if sentences == 0:
            return 0.5
        
        avg_words_per_sentence = len(words) / sentences
        
        # Optimal range is 15-20 words per sentence
        if 15 <= avg_words_per_sentence <= 20:
            return 0.9
        elif 10 <= avg_words_per_sentence <= 25:
            return 0.7
        else:
            return 0.5
    
    def _calculate_engagement_score(self, text: str, issues: List[StyleIssue]) -> float:
        """Calculate engagement score based on dynamic elements"""
        # Count engagement factors
        dialogue_count = len(re.findall(r'"[^"]*"', text))
        action_verbs = len(re.findall(r'\b(ran|jumped|grabbed|shouted|whispered)\b', text, re.IGNORECASE))
        sensory_details = len(re.findall(r'\b(saw|heard|felt|smelled|tasted)\b', text, re.IGNORECASE))
        
        word_count = len(text.split())
        if word_count == 0:
            return 0.5
        
        engagement_density = (dialogue_count + action_verbs + sensory_details) / word_count
        base_engagement = min(1.0, engagement_density * 10)
        
        # Reduce for telling-not-showing issues
        telling_issues = [i for i in issues if i.issue_type == StyleIssueType.TELLING_NOT_SHOWING]
        telling_penalty = len(telling_issues) * 0.1
        
        return max(0.0, base_engagement - telling_penalty)
    
    def _calculate_professionalism_score(self, text: str, issues: List[StyleIssue]) -> float:
        """Calculate professionalism score"""
        base_score = 0.8
        
        # Deduct for AI telltales and clichés
        ai_issues = [i for i in issues if i.issue_type in [StyleIssueType.AI_TELLTALES, StyleIssueType.CLICHE_LANGUAGE]]
        ai_penalty = len(ai_issues) * 0.15
        
        return max(0.0, base_score - ai_penalty)
    
    def _identify_strengths(self, text: str, issues: List[StyleIssue]) -> List[str]:
        """Identify positive aspects of the writing"""
        strengths = []
        
        # Check for dialogue
        if len(re.findall(r'"[^"]*"', text)) > 0:
            strengths.append("Good use of dialogue to advance story")
        
        # Check for specific details
        if len(re.findall(r'\b(crimson|azure|whispered|thundered|gnarled)\b', text, re.IGNORECASE)) > 0:
            strengths.append("Uses specific, vivid vocabulary")
        
        # Check for varied sentence lengths
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if sentences and max(len(s.split()) for s in sentences) > min(len(s.split()) for s in sentences) * 2:
            strengths.append("Good sentence length variation")
        
        # Check for active voice
        active_verbs = len(re.findall(r'\b\w+ed\b', text))
        total_verbs = len(re.findall(r'\b(was|were|is|are|been|be|\w+ed|\w+s)\b', text))
        if total_verbs > 0 and active_verbs / total_verbs > 0.6:
            strengths.append("Strong use of active voice")
        
        return strengths or ["Clear, understandable writing"]
    
    def _generate_improvement_summary(self, issues: List[StyleIssue]) -> str:
        """Generate overall improvement summary"""
        if not issues:
            return "Excellent writing! No major style issues detected."
        
        issue_counts = {}
        for issue in issues:
            issue_type = issue.issue_type.value
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        summary_parts = []
        for issue_type, count in top_issues:
            issue_name = issue_type.replace('_', ' ').title()
            summary_parts.append(f"{issue_name} ({count} instances)")
        
        return f"Main areas for improvement: {', '.join(summary_parts)}"
    
    def _generate_educational_notes(self, issues: List[StyleIssue]) -> List[str]:
        """Generate educational notes based on detected issues"""
        notes = []
        
        issue_types = set(issue.issue_type for issue in issues)
        
        if StyleIssueType.TELLING_NOT_SHOWING in issue_types:
            notes.append("Show-Don't-Tell: Instead of telling readers emotions or facts, show them through specific actions, dialogue, and sensory details.")
        
        if StyleIssueType.PASSIVE_VOICE in issue_types:
            notes.append("Active Voice: Make your subjects perform actions rather than receive them. This creates clearer, more direct prose.")
        
        if StyleIssueType.WEAK_VERBS in issue_types:
            notes.append("Strong Verbs: Choose verbs that carry specific meaning and energy. Avoid generic verbs like 'was,' 'seemed,' or 'felt.'")
        
        if StyleIssueType.CLICHE_LANGUAGE in issue_types:
            notes.append("Fresh Language: Avoid overused words and phrases that have become clichéd, especially in AI-generated content.")
        
        return notes

# Singleton instance
enhanced_style_coach = None

def get_enhanced_style_coach():
    """Get or create enhanced style coach instance"""
    global enhanced_style_coach
    if enhanced_style_coach is None:
        enhanced_style_coach = EnhancedStyleCoach()
    return enhanced_style_coach