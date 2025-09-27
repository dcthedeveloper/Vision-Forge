"""
VisionForge Version Control & Prompt Lineage System
Advanced versioning for characters, stories, and content with full lineage tracking
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import json
import difflib
import logging

logger = logging.getLogger(__name__)

class ContentType(Enum):
    CHARACTER_ANALYSIS = "character_analysis"
    STORY_CONTENT = "story_content"
    BEAT_SHEET = "beat_sheet"
    POWER_SYSTEM = "power_system"
    STYLE_ANALYSIS = "style_analysis"
    TROPE_ANALYSIS = "trope_analysis"

class ChangeType(Enum):
    CREATION = "creation"           # Initial creation
    MODIFICATION = "modification"   # Direct edit
    REGENERATION = "regeneration"   # AI regeneration with same/similar prompts
    BRANCH = "branch"              # New branch from existing version
    MERGE = "merge"                # Combining multiple versions
    ROLLBACK = "rollback"          # Restoration of previous version

@dataclass
class PromptContext:
    """Complete context for how content was generated"""
    prompt_text: str
    ai_provider: str
    model_name: str
    temperature: float
    safety_level: str
    genre: Optional[str] = None
    character_context: Optional[Dict] = None
    additional_parameters: Dict[str, Any] = field(default_factory=dict)
    generation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ContentVersion:
    """Single version of content with full lineage"""
    version_id: str
    parent_version_id: Optional[str]
    content_type: ContentType
    content_data: Dict[str, Any]
    prompt_context: PromptContext
    change_type: ChangeType
    change_description: str
    created_at: str
    created_by: str = "user"
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    metrics: Dict[str, float] = field(default_factory=dict)  # Quality scores, etc.

@dataclass
class ContentLineage:
    """Complete version history for a piece of content"""
    content_id: str
    content_type: ContentType
    root_version_id: str
    current_version_id: str
    versions: Dict[str, ContentVersion] = field(default_factory=dict)
    branches: Dict[str, List[str]] = field(default_factory=dict)  # branch_name -> version_ids
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

class VersionControlEngine:
    def __init__(self):
        self.lineages: Dict[str, ContentLineage] = {}
        self.version_index: Dict[str, str] = {}  # version_id -> content_id
        
    def create_initial_version(self, content_type: ContentType, content_data: Dict[str, Any], 
                             prompt_context: PromptContext, description: str = "Initial creation") -> Tuple[str, str]:
        """Create the first version of content"""
        content_id = str(uuid.uuid4())
        version_id = str(uuid.uuid4())
        
        version = ContentVersion(
            version_id=version_id,
            parent_version_id=None,
            content_type=content_type,
            content_data=content_data,
            prompt_context=prompt_context,
            change_type=ChangeType.CREATION,
            change_description=description,
            created_at=datetime.now().isoformat()
        )
        
        lineage = ContentLineage(
            content_id=content_id,
            content_type=content_type,
            root_version_id=version_id,
            current_version_id=version_id
        )
        
        lineage.versions[version_id] = version
        lineage.branches["main"] = [version_id]
        
        self.lineages[content_id] = lineage
        self.version_index[version_id] = content_id
        
        return content_id, version_id
    
    def create_new_version(self, parent_version_id: str, content_data: Dict[str, Any],
                          prompt_context: PromptContext, change_type: ChangeType,
                          description: str, branch_name: str = "main") -> str:
        """Create a new version from an existing version"""
        if parent_version_id not in self.version_index:
            raise ValueError(f"Parent version {parent_version_id} not found")
        
        content_id = self.version_index[parent_version_id]
        lineage = self.lineages[content_id]
        version_id = str(uuid.uuid4())
        
        version = ContentVersion(
            version_id=version_id,
            parent_version_id=parent_version_id,
            content_type=lineage.content_type,
            content_data=content_data,
            prompt_context=prompt_context,
            change_type=change_type,
            change_description=description,
            created_at=datetime.now().isoformat()
        )
        
        lineage.versions[version_id] = version
        lineage.current_version_id = version_id
        lineage.updated_at = datetime.now().isoformat()
        
        # Add to branch
        if branch_name not in lineage.branches:
            lineage.branches[branch_name] = []
        lineage.branches[branch_name].append(version_id)
        
        self.version_index[version_id] = content_id
        
        return version_id
    
    def create_branch(self, base_version_id: str, branch_name: str, description: str = "") -> str:
        """Create a new branch from existing version"""
        if base_version_id not in self.version_index:
            raise ValueError(f"Base version {base_version_id} not found")
        
        content_id = self.version_index[base_version_id]
        lineage = self.lineages[content_id]
        base_version = lineage.versions[base_version_id]
        
        # Create new version that's a copy of the base
        new_version_id = str(uuid.uuid4())
        
        new_version = ContentVersion(
            version_id=new_version_id,
            parent_version_id=base_version_id,
            content_type=base_version.content_type,
            content_data=base_version.content_data.copy(),
            prompt_context=base_version.prompt_context,
            change_type=ChangeType.BRANCH,
            change_description=f"Created branch '{branch_name}': {description}",
            created_at=datetime.now().isoformat()
        )
        
        lineage.versions[new_version_id] = new_version
        lineage.branches[branch_name] = [new_version_id]
        
        self.version_index[new_version_id] = content_id
        
        return new_version_id
    
    def rollback_to_version(self, target_version_id: str, description: str = "") -> str:
        """Rollback to a previous version (creates new version, doesn't delete history)"""
        if target_version_id not in self.version_index:
            raise ValueError(f"Target version {target_version_id} not found")
        
        content_id = self.version_index[target_version_id]
        lineage = self.lineages[content_id]
        target_version = lineage.versions[target_version_id]
        current_version_id = lineage.current_version_id
        
        # Create new version with target content
        rollback_version_id = str(uuid.uuid4())
        
        rollback_version = ContentVersion(
            version_id=rollback_version_id,
            parent_version_id=current_version_id,
            content_type=target_version.content_type,
            content_data=target_version.content_data.copy(),
            prompt_context=target_version.prompt_context,
            change_type=ChangeType.ROLLBACK,
            change_description=f"Rolled back to version {target_version_id}: {description}",
            created_at=datetime.now().isoformat()
        )
        
        lineage.versions[rollback_version_id] = rollback_version
        lineage.current_version_id = rollback_version_id
        lineage.updated_at = datetime.now().isoformat()
        
        # Add to main branch
        lineage.branches["main"].append(rollback_version_id)
        
        self.version_index[rollback_version_id] = content_id
        
        return rollback_version_id
    
    def get_version_diff(self, version_id_1: str, version_id_2: str) -> Dict[str, Any]:
        """Generate detailed diff between two versions"""
        if version_id_1 not in self.version_index or version_id_2 not in self.version_index:
            raise ValueError("One or both versions not found")
        
        version_1 = self.get_version(version_id_1)
        version_2 = self.get_version(version_id_2)
        
        diff_result = {
            "version_1": {
                "id": version_id_1,
                "created_at": version_1.created_at,
                "change_description": version_1.change_description,
                "prompt_context": self._prompt_context_to_dict(version_1.prompt_context)
            },
            "version_2": {
                "id": version_id_2,
                "created_at": version_2.created_at,
                "change_description": version_2.change_description,
                "prompt_context": self._prompt_context_to_dict(version_2.prompt_context)
            },
            "content_changes": self._generate_content_diff(version_1.content_data, version_2.content_data),
            "prompt_changes": self._generate_prompt_diff(version_1.prompt_context, version_2.prompt_context),
            "metadata_changes": {
                "change_type": {
                    "from": version_1.change_type.value,
                    "to": version_2.change_type.value
                },
                "tags": {
                    "added": list(set(version_2.tags) - set(version_1.tags)),
                    "removed": list(set(version_1.tags) - set(version_2.tags))
                }
            }
        }
        
        return diff_result
    
    def get_version_lineage(self, content_id: str) -> Dict[str, Any]:
        """Get complete lineage tree for content"""
        if content_id not in self.lineages:
            raise ValueError(f"Content {content_id} not found")
        
        lineage = self.lineages[content_id]
        
        # Build tree structure
        tree = self._build_lineage_tree(lineage)
        
        return {
            "content_id": content_id,
            "content_type": lineage.content_type.value,
            "total_versions": len(lineage.versions),
            "branches": list(lineage.branches.keys()),
            "current_version": lineage.current_version_id,
            "created_at": lineage.created_at,
            "updated_at": lineage.updated_at,
            "lineage_tree": tree,
            "version_summary": self._generate_version_summary(lineage)
        }
    
    def get_version(self, version_id: str) -> ContentVersion:
        """Get specific version"""
        if version_id not in self.version_index:
            raise ValueError(f"Version {version_id} not found")
        
        content_id = self.version_index[version_id]
        lineage = self.lineages[content_id]
        return lineage.versions[version_id]
    
    def get_branch_history(self, content_id: str, branch_name: str = "main") -> List[Dict[str, Any]]:
        """Get chronological history of a branch"""
        if content_id not in self.lineages:
            raise ValueError(f"Content {content_id} not found")
        
        lineage = self.lineages[content_id]
        
        if branch_name not in lineage.branches:
            raise ValueError(f"Branch {branch_name} not found")
        
        version_ids = lineage.branches[branch_name]
        versions = [lineage.versions[vid] for vid in version_ids]
        
        # Sort by creation time
        versions.sort(key=lambda v: v.created_at)
        
        return [self._version_to_dict(version) for version in versions]
    
    def search_versions(self, query: str, content_type: Optional[ContentType] = None) -> List[Dict[str, Any]]:
        """Search versions by description, tags, or content"""
        results = []
        
        for lineage in self.lineages.values():
            if content_type and lineage.content_type != content_type:
                continue
            
            for version in lineage.versions.values():
                # Search in description, tags, and content
                search_text = f"{version.change_description} {' '.join(version.tags)} {version.notes}".lower()
                content_text = json.dumps(version.content_data).lower()
                
                if query.lower() in search_text or query.lower() in content_text:
                    results.append({
                        "content_id": lineage.content_id,
                        "version_id": version.version_id,
                        "content_type": version.content_type.value,
                        "change_description": version.change_description,
                        "created_at": version.created_at,
                        "tags": version.tags,
                        "relevance_snippet": self._generate_relevance_snippet(version, query)
                    })
        
        return results
    
    def get_prompt_analytics(self, content_id: str) -> Dict[str, Any]:
        """Analyze prompt evolution and effectiveness"""
        if content_id not in self.lineages:
            raise ValueError(f"Content {content_id} not found")
        
        lineage = self.lineages[content_id]
        versions = list(lineage.versions.values())
        
        # Analyze prompt patterns
        providers = {}
        temperatures = []
        safety_levels = {}
        prompt_lengths = []
        
        for version in versions:
            ctx = version.prompt_context
            providers[ctx.ai_provider] = providers.get(ctx.ai_provider, 0) + 1
            temperatures.append(ctx.temperature)
            safety_levels[ctx.safety_level] = safety_levels.get(ctx.safety_level, 0) + 1
            prompt_lengths.append(len(ctx.prompt_text))
        
        return {
            "total_versions": len(versions),
            "provider_usage": providers,
            "temperature_stats": {
                "min": min(temperatures) if temperatures else 0,
                "max": max(temperatures) if temperatures else 0,
                "avg": sum(temperatures) / len(temperatures) if temperatures else 0
            },
            "safety_level_usage": safety_levels,
            "prompt_length_stats": {
                "min": min(prompt_lengths) if prompt_lengths else 0,
                "max": max(prompt_lengths) if prompt_lengths else 0,
                "avg": sum(prompt_lengths) / len(prompt_lengths) if prompt_lengths else 0
            },
            "most_effective_settings": self._analyze_effectiveness(versions)
        }
    
    # Helper methods
    def _build_lineage_tree(self, lineage: ContentLineage) -> Dict[str, Any]:
        """Build hierarchical tree of versions"""
        tree = {"versions": {}, "root": lineage.root_version_id}
        
        for version_id, version in lineage.versions.items():
            tree["versions"][version_id] = {
                "id": version_id,
                "parent": version.parent_version_id,
                "children": [],
                "change_type": version.change_type.value,
                "description": version.change_description,
                "created_at": version.created_at,
                "branch": self._find_version_branch(lineage, version_id)
            }
        
        # Build parent-child relationships
        for version_id, version_info in tree["versions"].items():
            parent_id = version_info["parent"]
            if parent_id and parent_id in tree["versions"]:
                tree["versions"][parent_id]["children"].append(version_id)
        
        return tree
    
    def _find_version_branch(self, lineage: ContentLineage, version_id: str) -> str:
        """Find which branch a version belongs to"""
        for branch_name, version_ids in lineage.branches.items():
            if version_id in version_ids:
                return branch_name
        return "orphaned"
    
    def _generate_content_diff(self, content_1: Dict, content_2: Dict) -> List[Dict[str, Any]]:
        """Generate detailed content differences"""
        changes = []
        
        # Compare all keys
        all_keys = set(content_1.keys()) | set(content_2.keys())
        
        for key in all_keys:
            if key not in content_1:
                changes.append({
                    "type": "addition",
                    "field": key,
                    "new_value": content_2[key]
                })
            elif key not in content_2:
                changes.append({
                    "type": "deletion",
                    "field": key,
                    "old_value": content_1[key]
                })
            elif content_1[key] != content_2[key]:
                changes.append({
                    "type": "modification",
                    "field": key,
                    "old_value": content_1[key],
                    "new_value": content_2[key],
                    "text_diff": self._generate_text_diff(
                        str(content_1[key]), 
                        str(content_2[key])
                    ) if isinstance(content_1[key], str) and isinstance(content_2[key], str) else None
                })
        
        return changes
    
    def _generate_prompt_diff(self, prompt_1: PromptContext, prompt_2: PromptContext) -> Dict[str, Any]:
        """Generate prompt context differences"""
        changes = {}
        
        if prompt_1.ai_provider != prompt_2.ai_provider:
            changes["ai_provider"] = {"from": prompt_1.ai_provider, "to": prompt_2.ai_provider}
        
        if prompt_1.temperature != prompt_2.temperature:
            changes["temperature"] = {"from": prompt_1.temperature, "to": prompt_2.temperature}
        
        if prompt_1.safety_level != prompt_2.safety_level:
            changes["safety_level"] = {"from": prompt_1.safety_level, "to": prompt_2.safety_level}
        
        if prompt_1.prompt_text != prompt_2.prompt_text:
            changes["prompt_text"] = {
                "text_diff": self._generate_text_diff(prompt_1.prompt_text, prompt_2.prompt_text)
            }
        
        return changes
    
    def _generate_text_diff(self, text_1: str, text_2: str) -> List[str]:
        """Generate line-by-line text diff"""
        diff = difflib.unified_diff(
            text_1.splitlines(keepends=True),
            text_2.splitlines(keepends=True),
            fromfile='version_1',
            tofile='version_2',
            lineterm=''
        )
        return list(diff)
    
    def _generate_version_summary(self, lineage: ContentLineage) -> List[Dict[str, Any]]:
        """Generate summary of all versions"""
        summaries = []
        
        for version in lineage.versions.values():
            summaries.append({
                "version_id": version.version_id,
                "change_type": version.change_type.value,
                "description": version.change_description,
                "created_at": version.created_at,
                "ai_provider": version.prompt_context.ai_provider,
                "prompt_length": len(version.prompt_context.prompt_text),
                "has_notes": bool(version.notes),
                "tag_count": len(version.tags)
            })
        
        # Sort by creation time
        summaries.sort(key=lambda s: s["created_at"], reverse=True)
        
        return summaries
    
    def _analyze_effectiveness(self, versions: List[ContentVersion]) -> Dict[str, Any]:
        """Analyze which settings produce best results"""
        # Simple analysis based on metrics if available
        best_settings = {
            "provider": "ollama",  # Default
            "temperature": 0.7,    # Default
            "safety_level": "moderate"  # Default
        }
        
        # If we have metrics, find the version with best overall score
        scored_versions = [v for v in versions if v.metrics.get("overall_score")]
        
        if scored_versions:
            best_version = max(scored_versions, key=lambda v: v.metrics["overall_score"])
            best_settings = {
                "provider": best_version.prompt_context.ai_provider,
                "temperature": best_version.prompt_context.temperature,
                "safety_level": best_version.prompt_context.safety_level
            }
        
        return best_settings
    
    def _generate_relevance_snippet(self, version: ContentVersion, query: str) -> str:
        """Generate relevance snippet for search results"""
        text = f"{version.change_description} {version.notes}"
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Find query position
        pos = text_lower.find(query_lower)
        if pos != -1:
            start = max(0, pos - 30)
            end = min(len(text), pos + len(query) + 30)
            snippet = text[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(text):
                snippet = snippet + "..."
            return snippet
        
        return text[:100] + ("..." if len(text) > 100 else "")
    
    def _version_to_dict(self, version: ContentVersion) -> Dict[str, Any]:
        """Convert version to dictionary"""
        return {
            "version_id": version.version_id,
            "parent_version_id": version.parent_version_id,
            "content_type": version.content_type.value,
            "content_data": version.content_data,
            "prompt_context": self._prompt_context_to_dict(version.prompt_context),
            "change_type": version.change_type.value,
            "change_description": version.change_description,
            "created_at": version.created_at,
            "created_by": version.created_by,
            "tags": version.tags,
            "notes": version.notes,
            "metrics": version.metrics
        }
    
    def _prompt_context_to_dict(self, context: PromptContext) -> Dict[str, Any]:
        """Convert prompt context to dictionary"""
        return {
            "prompt_text": context.prompt_text,
            "ai_provider": context.ai_provider,
            "model_name": context.model_name,
            "temperature": context.temperature,
            "safety_level": context.safety_level,
            "genre": context.genre,
            "character_context": context.character_context,
            "additional_parameters": context.additional_parameters,
            "generation_timestamp": context.generation_timestamp
        }

# Singleton instance
version_control_engine = None

def get_version_control_engine():
    """Get or create version control engine instance"""
    global version_control_engine
    if version_control_engine is None:
        version_control_engine = VersionControlEngine()
    return version_control_engine