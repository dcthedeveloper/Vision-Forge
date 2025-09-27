"""
VisionForge Knowledge Graph Layer - Phase 1 Implementation
Handles Archetype ↔ Origin ↔ Power ↔ Rule relationships using Neo4j
"""

from neo4j import GraphDatabase
from typing import Dict, List, Any, Optional
import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TropeRelation:
    archetype: str
    origin: str
    power_type: str
    compatibility_score: float
    cliche_risk: float
    subversion_suggestions: List[str]

@dataclass
class RuleViolation:
    rule_type: str
    severity: str  # "warning", "error", "critical"
    message: str
    suggested_fix: str

class VisionForgeKnowledgeGraph:
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.initialize_graph()
    
    def close(self):
        self.driver.close()
    
    def initialize_graph(self):
        """Initialize the knowledge graph with VisionForge schema"""
        with self.driver.session() as session:
            # Create constraints and indexes
            session.run("""
                CREATE CONSTRAINT archetype_name IF NOT EXISTS 
                FOR (a:Archetype) REQUIRE a.name IS UNIQUE
            """)
            
            session.run("""
                CREATE CONSTRAINT origin_name IF NOT EXISTS 
                FOR (o:Origin) REQUIRE o.name IS UNIQUE
            """)
            
            session.run("""
                CREATE CONSTRAINT power_name IF NOT EXISTS 
                FOR (p:Power) REQUIRE p.name IS UNIQUE
            """)
            
            # Initialize base archetypes
            self._create_base_archetypes(session)
            self._create_base_origins(session)
            self._create_base_powers(session)
            self._create_compatibility_rules(session)
    
    def _create_base_archetypes(self, session):
        """Create foundational character archetypes"""
        archetypes = [
            {"name": "Hero", "cliche_risk": 0.8, "description": "Traditional heroic figure", "subversions": ["Reluctant Hero", "Fallen Hero", "Anti-Hero"]},
            {"name": "Mentor", "cliche_risk": 0.6, "description": "Wise guide figure", "subversions": ["False Mentor", "Learning Mentor", "Broken Mentor"]},
            {"name": "Trickster", "cliche_risk": 0.3, "description": "Clever rule-breaker", "subversions": ["Noble Trickster", "Tragic Trickster", "Reformed Trickster"]},
            {"name": "Guardian", "cliche_risk": 0.5, "description": "Protective figure", "subversions": ["Conflicted Guardian", "Guardian Turned Enemy", "Reluctant Guardian"]},
            {"name": "System_Changer", "cliche_risk": 0.2, "description": "Marcus-style empire builder", "subversions": ["Reluctant Revolutionary", "System Infiltrator", "Gradual Reformer"]},
            {"name": "Power_Broker", "cliche_risk": 0.25, "description": "Behind-scenes influencer", "subversions": ["Visible Broker", "Ethical Broker", "Temporary Broker"]}
        ]
        
        for archetype in archetypes:
            session.run("""
                MERGE (a:Archetype {name: $name})
                SET a.cliche_risk = $cliche_risk,
                    a.description = $description,
                    a.subversions = $subversions
            """, **archetype)
    
    def _create_base_origins(self, session):
        """Create character origin types"""
        origins = [
            {"name": "Nootropic_Enhanced", "cliche_risk": 0.1, "description": "Enhanced through experimental cognitive drugs"},
            {"name": "Self_Made_Entrepreneur", "cliche_risk": 0.2, "description": "Built success through strategic thinking"},
            {"name": "Street_Smart_Survivor", "cliche_risk": 0.3, "description": "Learned through harsh urban experience"},
            {"name": "Corporate_Infiltrator", "cliche_risk": 0.25, "description": "Operates within system to change it"},
            {"name": "Underground_Network", "cliche_risk": 0.15, "description": "Connected to shadow power structures"}
        ]
        
        for origin in origins:
            session.run("""
                MERGE (o:Origin {name: $name})
                SET o.cliche_risk = $cliche_risk,
                    o.description = $description
            """, **origin)
    
    def _create_base_powers(self, session):
        """Create realistic power types"""
        powers = [
            {"name": "Hypercognitive_Processing", "cost_level": 8, "category": "Cognitive", "realistic": True},
            {"name": "Social_Network_Mapping", "cost_level": 6, "category": "Social", "realistic": True},
            {"name": "Pattern_Recognition", "cost_level": 5, "category": "Cognitive", "realistic": True},
            {"name": "Strategic_Foresight", "cost_level": 7, "category": "Cognitive", "realistic": True},
            {"name": "Accelerated_Learning", "cost_level": 6, "category": "Cognitive", "realistic": True},
            {"name": "System_Analysis", "cost_level": 7, "category": "Analytical", "realistic": True}
        ]
        
        for power in powers:
            session.run("""
                MERGE (p:Power {name: $name})
                SET p.cost_level = $cost_level,
                    p.category = $category,
                    p.realistic = $realistic
            """, **power)
    
    def _create_compatibility_rules(self, session):
        """Create archetype-origin-power compatibility relationships"""
        compatibilities = [
            # System_Changer + Nootropic_Enhanced + Hypercognitive = High compatibility, low cliche
            ("System_Changer", "Nootropic_Enhanced", "Hypercognitive_Processing", 0.95, 0.15),
            ("System_Changer", "Self_Made_Entrepreneur", "Strategic_Foresight", 0.9, 0.2),
            ("Power_Broker", "Corporate_Infiltrator", "Social_Network_Mapping", 0.85, 0.25),
            ("Power_Broker", "Underground_Network", "System_Analysis", 0.8, 0.3),
            
            # Traditional combinations with higher cliche risk
            ("Hero", "Street_Smart_Survivor", "Pattern_Recognition", 0.7, 0.6),
            ("Mentor", "Self_Made_Entrepreneur", "Accelerated_Learning", 0.75, 0.5)
        ]
        
        for archetype, origin, power, compatibility, cliche in compatibilities:
            session.run("""
                MATCH (a:Archetype {name: $archetype})
                MATCH (o:Origin {name: $origin})
                MATCH (p:Power {name: $power})
                MERGE (a)-[r:COMPATIBLE_WITH]->(o)
                MERGE (o)-[r2:ENABLES]->(p)
                MERGE (a)-[r3:CAN_USE {compatibility: $compatibility, cliche_risk: $cliche}]->(p)
            """, archetype=archetype, origin=origin, power=power, 
                compatibility=compatibility, cliche=cliche)
    
    def get_character_compatibility(self, archetype: str, origin: str, power: str) -> Dict[str, Any]:
        """Get compatibility score and cliche risk for character combination"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a:Archetype {name: $archetype})-[r:CAN_USE]->(p:Power {name: $power})
                MATCH (o:Origin {name: $origin})-[r2:ENABLES]->(p)
                RETURN r.compatibility as compatibility, 
                       r.cliche_risk as cliche_risk,
                       a.subversions as subversions
            """, archetype=archetype, origin=origin, power=power)
            
            record = result.single()
            if record:
                return {
                    "compatibility": record["compatibility"],
                    "cliche_risk": record["cliche_risk"],
                    "subversion_suggestions": record["subversions"],
                    "recommendation": "excellent" if record["compatibility"] > 0.8 and record["cliche_risk"] < 0.3 else "good"
                }
            return {"compatibility": 0.5, "cliche_risk": 0.7, "subversion_suggestions": [], "recommendation": "unknown"}
    
    def get_subversion_suggestions(self, archetype: str, high_cliche_threshold: float = 0.5) -> List[str]:
        """Get subversion suggestions for high-cliche archetypes"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a:Archetype {name: $archetype})
                WHERE a.cliche_risk > $threshold
                RETURN a.subversions as suggestions, a.cliche_risk as risk
            """, archetype=archetype, threshold=high_cliche_threshold)
            
            record = result.single()
            if record:
                return record["suggestions"]
            return []
    
    def check_power_conflicts(self, powers: List[str]) -> List[RuleViolation]:
        """Check for conflicts between selected powers"""
        violations = []
        
        # Rule: No more than 2 high-cost powers (cost_level > 7)
        with self.driver.session() as session:
            high_cost_powers = []
            for power in powers:
                result = session.run("""
                    MATCH (p:Power {name: $power})
                    WHERE p.cost_level > 7
                    RETURN p.name as name, p.cost_level as cost
                """, power=power)
                
                record = result.single()
                if record:
                    high_cost_powers.append((record["name"], record["cost"]))
            
            if len(high_cost_powers) > 2:
                violations.append(RuleViolation(
                    rule_type="power_cost_limit",
                    severity="error",
                    message=f"Too many high-cost powers: {[p[0] for p in high_cost_powers]}",
                    suggested_fix="Remove one high-cost power or reduce power levels"
                ))
        
        return violations
    
    def get_character_recommendations(self, partial_character: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendations for completing a character"""
        archetype = partial_character.get("archetype")
        origin = partial_character.get("origin")
        
        recommendations = {
            "compatible_powers": [],
            "subversion_suggestions": [],
            "cliche_warnings": [],
            "optimization_tips": []
        }
        
        if archetype and origin:
            # Find compatible powers
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (a:Archetype {name: $archetype})-[r:CAN_USE]->(p:Power)
                    MATCH (o:Origin {name: $origin})-[r2:ENABLES]->(p)
                    WHERE r.compatibility > 0.7
                    RETURN p.name as power, r.compatibility as compatibility, r.cliche_risk as risk
                    ORDER BY r.compatibility DESC
                    LIMIT 5
                """, archetype=archetype, origin=origin)
                
                for record in result:
                    recommendations["compatible_powers"].append({
                        "name": record["power"],
                        "compatibility": record["compatibility"],
                        "cliche_risk": record["risk"]
                    })
            
            # Get subversion suggestions if cliche risk is high
            subversions = self.get_subversion_suggestions(archetype)
            if subversions:
                recommendations["subversion_suggestions"] = subversions
        
        return recommendations

# Singleton instance
knowledge_graph = None

def get_knowledge_graph():
    """Get or create knowledge graph instance"""
    global knowledge_graph
    if knowledge_graph is None:
        # For now, we'll initialize with dummy credentials since Neo4j isn't running
        # In production, these would come from environment variables
        knowledge_graph = VisionForgeKnowledgeGraph("bolt://localhost:7687", "neo4j", "visionforge123")
    return knowledge_graph

def initialize_knowledge_graph():
    """Initialize knowledge graph for the application"""
    try:
        graph = get_knowledge_graph()
        logger.info("Knowledge graph initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize knowledge graph: {e}")
        return False