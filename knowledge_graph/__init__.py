"""
GIRAFFE Agent Knowledge Graph Package
Cancer Genomics Knowledge Graph with Amazon Bedrock Integration
"""

from .bedrock_client import BedrockClient, create_bedrock_client
from .giraffe_kg import GiraffeKnowledgeGraph
from .mutation_processor import MutationAnnotationProcessor
from .llm_extractor import GenomicsEntityExtractor
from .visualizer import KnowledgeGraphVisualizer, KnowledgeGraphExporter

__version__ = "1.0.0"
__author__ = "GIRAFFE Agent Team"
__description__ = "Cancer Genomics Knowledge Graph with Amazon Bedrock Integration"

__all__ = [
    "BedrockClient",
    "create_bedrock_client", 
    "GiraffeKnowledgeGraph",
    "MutationAnnotationProcessor",
    "GenomicsEntityExtractor",
    "KnowledgeGraphVisualizer",
    "KnowledgeGraphExporter"
]