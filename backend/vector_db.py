"""
VisionForge Vector Database Layer - Phase 1 Implementation  
Handles lore/tropes/canon storage and retrieval for continuity checking
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import Dict, List, Any, Optional
import logging
import uuid
import hashlib
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LoreEntry:
    id: str
    character_id: str
    content: str
    content_type: str  # "trait", "backstory", "power", "relationship", "rule"
    tags: List[str]
    embedding: List[float]
    metadata: Dict[str, Any]

@dataclass
class ContinuityCheck:
    conflict_type: str
    severity: str  # "info", "warning", "error"
    existing_content: str
    new_content: str
    similarity_score: float
    suggested_resolution: str

class VisionForgeVectorDB:
    def __init__(self, host: str = "localhost", port: int = 6333):
        try:
            self.client = QdrantClient(host=host, port=port)
            self.collection_name = "visionforge_lore"
            self.initialize_collection()
        except Exception as e:
            logger.warning(f"Vector DB connection failed (dev mode): {e}")
            self._use_memory_fallback = True
            self._memory_store = {}
    
    def initialize_collection(self):
        """Initialize the vector collection for character lore"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)  # OpenAI embedding size
                )
                logger.info(f"Created vector collection: {self.collection_name}")
        except Exception as e:
            logger.warning(f"Vector DB initialization failed (expected in dev): {e}")
            # For development without Qdrant running, we'll use in-memory fallback
            self._use_memory_fallback = True
            self._memory_store = {}
    
    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (fallback to dummy for dev)"""
        try:
            # For now, return dummy embedding since we don't have embedding service yet
            import hashlib
            # Create deterministic dummy embedding based on text hash
            text_hash = hashlib.md5(text.encode()).hexdigest()
            dummy_embedding = [float(int(text_hash[i:i+2], 16)) / 255.0 for i in range(0, min(len(text_hash), 30), 2)]
            # Pad to 1536 dimensions
            while len(dummy_embedding) < 1536:
                dummy_embedding.extend(dummy_embedding[:min(100, 1536 - len(dummy_embedding))])
            return dummy_embedding[:1536]
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
            return [0.1] * 1536
    
    async def store_character_lore(self, character_id: str, content: str, content_type: str, 
                                  tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """Store character lore entry with vector embedding"""
        try:
            entry_id = str(uuid.uuid4())
            embedding = await self.get_embedding(content)
            
            if hasattr(self, '_use_memory_fallback') and self._use_memory_fallback:
                # Store in memory for development
                self._memory_store[entry_id] = LoreEntry(
                    id=entry_id,
                    character_id=character_id,
                    content=content,
                    content_type=content_type,
                    tags=tags or [],
                    embedding=embedding,
                    metadata=metadata or {}
                )
            else:
                # Store in Qdrant
                point = PointStruct(
                    id=entry_id,
                    vector=embedding,
                    payload={
                        "character_id": character_id,
                        "content": content,
                        "content_type": content_type,
                        "tags": tags or [],
                        "metadata": metadata or {}
                    }
                )
                
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=[point]
                )
            
            logger.info(f"Stored lore entry: {entry_id} for character {character_id}")
            return entry_id
            
        except Exception as e:
            logger.error(f"Failed to store lore entry: {e}")
            raise
    
    async def check_continuity_conflicts(self, character_id: str, new_content: str, 
                                       content_type: str, similarity_threshold: float = 0.8) -> List[ContinuityCheck]:
        """Check for continuity conflicts with existing character lore"""
        conflicts = []
        
        try:
            new_embedding = await self.get_embedding(new_content)
            
            if hasattr(self, '_use_memory_fallback') and self._use_memory_fallback:
                # Memory-based similarity check for development
                for entry_id, entry in self._memory_store.items():
                    if entry.character_id == character_id and entry.content_type == content_type:
                        # Simple cosine similarity approximation
                        similarity = self._calculate_similarity(new_embedding, entry.embedding)
                        
                        if similarity > similarity_threshold:
                            severity = "error" if similarity > 0.9 else "warning"
                            conflicts.append(ContinuityCheck(
                                conflict_type="content_similarity",
                                severity=severity,
                                existing_content=entry.content,
                                new_content=new_content,
                                similarity_score=similarity,
                                suggested_resolution=f"Consider merging or differentiating these {content_type} elements"
                            ))
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Continuity check failed: {e}")
            return []
    
    def _calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        if len(vec1) != len(vec2):
            return 0.0
        
        try:
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = math.sqrt(sum(a * a for a in vec1))
            norm2 = math.sqrt(sum(a * a for a in vec2))
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except:
            return 0.0

# Singleton instance
vector_db = None

def get_vector_db():
    """Get or create vector database instance"""
    global vector_db
    if vector_db is None:
        vector_db = VisionForgeVectorDB()
    return vector_db

def initialize_vector_db():
    """Initialize vector database for the application"""
    try:
        db = get_vector_db()
        logger.info("Vector database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize vector database: {e}")
        return False