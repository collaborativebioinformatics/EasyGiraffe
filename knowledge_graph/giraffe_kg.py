"""
GIRAFFE Agent Knowledge Graph Implementation
Core classes for building and managing cancer genomics knowledge graphs
"""

import networkx as nx
import pandas as pd
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pickle
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GiraffeKnowledgeGraph:
    """
    Main Knowledge Graph class for cancer genomics data
    Integrates with GIRAFFE pipeline for mutation analysis
    """
    
    def __init__(self, name: str = "GIRAFFE_KG"):
        """
        Initialize the knowledge graph
        
        Args:
            name: Name identifier for the knowledge graph
        """
        self.name = name
        self.graph = nx.MultiDiGraph()  # Directed multigraph for complex relationships
        self.metadata = {
            "created": datetime.now().isoformat(),
            "version": "1.0",
            "description": "GIRAFFE Agent Cancer Genomics Knowledge Graph"
        }
        self.entity_types = {
            "gene", "variant", "disease", "pathway", "protein", 
            "sample", "patient", "drug", "publication"
        }
        self.relationship_types = {
            "associated_with", "causes", "regulates", "interacts_with",
            "found_in", "treats", "inhibits", "activates", "mutated_in"
        }
        
        logger.info(f"Initialized knowledge graph: {self.name}")
    
    def add_entity(self, entity_id: str, entity_type: str, properties: Dict[str, Any] = None) -> bool:
        """
        Add an entity (node) to the knowledge graph
        
        Args:
            entity_id: Unique identifier for the entity
            entity_type: Type of entity (gene, variant, disease, etc.)
            properties: Additional properties for the entity
            
        Returns:
            True if entity was added successfully
        """
        if properties is None:
            properties = {}
        
        # Validate entity type
        if entity_type not in self.entity_types:
            logger.warning(f"Unknown entity type: {entity_type}")
        
        # Add node with properties
        node_data = {
            "type": entity_type,
            "id": entity_id,
            "added_timestamp": datetime.now().isoformat(),
            **properties
        }
        
        self.graph.add_node(entity_id, **node_data)
        logger.debug(f"Added entity: {entity_id} ({entity_type})")
        
        return True
    
    def add_relationship(self, source_id: str, target_id: str, relationship_type: str, 
                        properties: Dict[str, Any] = None) -> bool:
        """
        Add a relationship (edge) between two entities
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            relationship_type: Type of relationship
            properties: Additional properties for the relationship
            
        Returns:
            True if relationship was added successfully
        """
        if properties is None:
            properties = {}
        
        # Validate relationship type
        if relationship_type not in self.relationship_types:
            logger.warning(f"Unknown relationship type: {relationship_type}")
        
        # Check if both entities exist
        if not (self.graph.has_node(source_id) and self.graph.has_node(target_id)):
            logger.error(f"Cannot add relationship: missing entities {source_id} or {target_id}")
            return False
        
        # Add edge with properties
        edge_data = {
            "type": relationship_type,
            "added_timestamp": datetime.now().isoformat(),
            **properties
        }
        
        self.graph.add_edge(source_id, target_id, **edge_data)
        logger.debug(f"Added relationship: {source_id} -> {target_id} ({relationship_type})")
        
        return True
    
    def add_mutation_data(self, mutation_info: Dict[str, Any]) -> str:
        """
        Add mutation data to the knowledge graph
        
        Args:
            mutation_info: Dictionary containing mutation information
            
        Returns:
            Variant ID that was created
        """
        # Create variant entity
        variant_id = f"var_{mutation_info.get('chromosome', 'chr')}_{mutation_info.get('position', '0')}_{mutation_info.get('ref_allele', 'N')}_{mutation_info.get('alt_allele', 'N')}"
        
        variant_properties = {
            "chromosome": mutation_info.get('chromosome'),
            "position": mutation_info.get('position'),
            "ref_allele": mutation_info.get('ref_allele'),
            "alt_allele": mutation_info.get('alt_allele'),
            "rsid": mutation_info.get('rsid'),
            "frequency": mutation_info.get('frequency'),
            "clinical_significance": mutation_info.get('clinical_significance')
        }
        
        self.add_entity(variant_id, "variant", variant_properties)
        
        # Add gene entity if provided
        if mutation_info.get('gene'):
            gene_id = f"gene_{mutation_info['gene']}"
            gene_properties = {
                "symbol": mutation_info['gene'],
                "chromosome": mutation_info.get('chromosome')
            }
            
            self.add_entity(gene_id, "gene", gene_properties)
            self.add_relationship(variant_id, gene_id, "found_in", {
                "evidence": "genomic_annotation"
            })
        
        # Add disease associations
        diseases = mutation_info.get('diseases', [])
        if isinstance(diseases, str):
            diseases = [diseases]
        
        for disease in diseases:
            disease_id = f"disease_{disease.replace(' ', '_').lower()}"
            disease_properties = {
                "name": disease,
                "category": "cancer"  # Assuming cancer focus for GIRAFFE
            }
            
            self.add_entity(disease_id, "disease", disease_properties)
            self.add_relationship(variant_id, disease_id, "associated_with", {
                "clinical_significance": mutation_info.get('clinical_significance'),
                "evidence": "dbsnp_annotation"
            })
        
        return variant_id
    
    def add_sample_data(self, sample_id: str, patient_id: str, cancer_type: str, 
                       mutations: List[str]) -> bool:
        """
        Add sample data from TCGA or other sources
        
        Args:
            sample_id: Unique sample identifier
            patient_id: Patient identifier
            cancer_type: Type of cancer
            mutations: List of variant IDs found in this sample
            
        Returns:
            True if sample was added successfully
        """
        # Add sample entity
        sample_properties = {
            "cancer_type": cancer_type,
            "source": "TCGA",
            "patient_id": patient_id
        }
        
        self.add_entity(sample_id, "sample", sample_properties)
        
        # Add patient entity if not exists
        if not self.graph.has_node(patient_id):
            patient_properties = {
                "cancer_type": cancer_type
            }
            self.add_entity(patient_id, "patient", patient_properties)
        
        # Connect sample to patient
        self.add_relationship(sample_id, patient_id, "derived_from")
        
        # Connect sample to mutations
        for variant_id in mutations:
            if self.graph.has_node(variant_id):
                self.add_relationship(sample_id, variant_id, "contains", {
                    "detection_method": "sequencing"
                })
        
        return True
    
    def get_entity_neighbors(self, entity_id: str, relationship_type: str = None) -> List[str]:
        """
        Get neighboring entities of a given entity
        
        Args:
            entity_id: Entity to find neighbors for
            relationship_type: Filter by relationship type (optional)
            
        Returns:
            List of neighboring entity IDs
        """
        if not self.graph.has_node(entity_id):
            return []
        
        neighbors = []
        
        # Get all edges (incoming and outgoing)
        all_edges = list(self.graph.in_edges(entity_id, data=True)) + \
                   list(self.graph.out_edges(entity_id, data=True))
        
        for source, target, data in all_edges:
            if relationship_type is None or data.get('type') == relationship_type:
                neighbor = target if source == entity_id else source
                if neighbor != entity_id:
                    neighbors.append(neighbor)
        
        return list(set(neighbors))  # Remove duplicates
    
    def find_entities_by_type(self, entity_type: str) -> List[str]:
        """
        Find all entities of a specific type
        
        Args:
            entity_type: Type of entities to find
            
        Returns:
            List of entity IDs of the specified type
        """
        entities = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get('type') == entity_type:
                entities.append(node_id)
        
        return entities
    
    def get_shortest_path(self, source_id: str, target_id: str) -> List[str]:
        """
        Find shortest path between two entities
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            
        Returns:
            List of entity IDs representing the shortest path
        """
        try:
            path = nx.shortest_path(self.graph, source_id, target_id)
            return path
        except nx.NetworkXNoPath:
            logger.warning(f"No path found between {source_id} and {target_id}")
            return []
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get basic statistics about the knowledge graph
        
        Returns:
            Dictionary containing graph statistics
        """
        stats = {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "is_connected": nx.is_connected(self.graph.to_undirected()),
        }
        
        # Count entities by type
        entity_counts = {}
        for node_id, data in self.graph.nodes(data=True):
            entity_type = data.get('type', 'unknown')
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
        
        stats["entity_counts"] = entity_counts
        
        # Count relationships by type
        relationship_counts = {}
        for source, target, data in self.graph.edges(data=True):
            rel_type = data.get('type', 'unknown')
            relationship_counts[rel_type] = relationship_counts.get(rel_type, 0) + 1
        
        stats["relationship_counts"] = relationship_counts
        
        return stats
    
    def export_to_json(self, filepath: str) -> bool:
        """
        Export knowledge graph to JSON format
        
        Args:
            filepath: Path to save the JSON file
            
        Returns:
            True if export was successful
        """
        try:
            # Convert graph to JSON serializable format
            export_data = {
                "metadata": self.metadata,
                "nodes": [],
                "edges": []
            }
            
            # Add nodes
            for node_id, data in self.graph.nodes(data=True):
                node_info = {"id": node_id, **data}
                export_data["nodes"].append(node_info)
            
            # Add edges
            for source, target, data in self.graph.edges(data=True):
                edge_info = {"source": source, "target": target, **data}
                export_data["edges"].append(edge_info)
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Knowledge graph exported to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export knowledge graph: {e}")
            return False
    
    def load_from_json(self, filepath: str) -> bool:
        """
        Load knowledge graph from JSON format
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            True if loading was successful
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Clear existing graph
            self.graph.clear()
            
            # Load metadata
            self.metadata = data.get("metadata", self.metadata)
            
            # Load nodes
            for node_info in data.get("nodes", []):
                node_id = node_info.pop("id")
                self.graph.add_node(node_id, **node_info)
            
            # Load edges
            for edge_info in data.get("edges", []):
                source = edge_info.pop("source")
                target = edge_info.pop("target")
                self.graph.add_edge(source, target, **edge_info)
            
            logger.info(f"Knowledge graph loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load knowledge graph: {e}")
            return False
    
    def save_graph(self, filepath: str) -> bool:
        """
        Save knowledge graph using pickle for complete preservation
        
        Args:
            filepath: Path to save the graph
            
        Returns:
            True if saving was successful
        """
        try:
            graph_data = {
                "graph": self.graph,
                "metadata": self.metadata,
                "name": self.name
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(graph_data, f)
            
            logger.info(f"Knowledge graph saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save knowledge graph: {e}")
            return False
    
    def load_graph(self, filepath: str) -> bool:
        """
        Load knowledge graph from pickle file
        
        Args:
            filepath: Path to the saved graph
            
        Returns:
            True if loading was successful
        """
        try:
            with open(filepath, 'rb') as f:
                graph_data = pickle.load(f)
            
            self.graph = graph_data["graph"]
            self.metadata = graph_data["metadata"]
            self.name = graph_data["name"]
            
            logger.info(f"Knowledge graph loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load knowledge graph: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Create a knowledge graph
    kg = GiraffeKnowledgeGraph("GIRAFFE_Demo")
    
    # Add some sample mutation data
    mutation_data = {
        "chromosome": "chr17",
        "position": "41234470",
        "ref_allele": "A",
        "alt_allele": "G",
        "gene": "BRCA1",
        "rsid": "rs80357382",
        "frequency": "0.0001",
        "clinical_significance": "Pathogenic",
        "diseases": ["Breast Cancer", "Ovarian Cancer"]
    }
    
    variant_id = kg.add_mutation_data(mutation_data)
    
    # Add sample data
    kg.add_sample_data("TCGA-A1-A0SB", "patient_001", "Breast Cancer", [variant_id])
    
    # Get statistics
    stats = kg.get_graph_statistics()
    print("Knowledge Graph Statistics:")
    print(json.dumps(stats, indent=2))