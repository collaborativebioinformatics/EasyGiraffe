"""
GIRAFFE Agent Mutation Annotation Integration
Processes dbSNP annotated mutations and integrates them with AWS Bedrock for entity extraction
"""

import pandas as pd
import json
import logging
from typing import Dict, List, Any, Optional
import re
from .bedrock_client import BedrockClient
from .giraffe_kg import GiraffeKnowledgeGraph

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MutationAnnotationProcessor:
    """
    Process mutation annotation data and integrate with knowledge graph
    """
    
    def __init__(self, bedrock_client: BedrockClient):
        """
        Initialize the processor with Bedrock client
        
        Args:
            bedrock_client: Configured Bedrock client for LLM interactions
        """
        self.bedrock_client = bedrock_client
        self.supported_formats = ['vcf', 'tsv', 'json', 'csv']
        
    def parse_vcf_line(self, vcf_line: str) -> Dict[str, Any]:
        """
        Parse a single VCF line and extract mutation information
        
        Args:
            vcf_line: VCF format line
            
        Returns:
            Dictionary containing parsed mutation data
        """
        if vcf_line.startswith('#'):
            return None
        
        fields = vcf_line.strip().split('\t')
        
        if len(fields) < 8:
            return None
        
        # Basic VCF fields
        chrom = fields[0]
        pos = fields[1]
        id_field = fields[2]
        ref = fields[3]
        alt = fields[4]
        qual = fields[5]
        filter_field = fields[6]
        info = fields[7]
        
        # Parse INFO field for additional annotations
        info_dict = {}
        for item in info.split(';'):
            if '=' in item:
                key, value = item.split('=', 1)
                info_dict[key] = value
            else:
                info_dict[item] = True
        
        return {
            'chromosome': chrom,
            'position': pos,
            'rsid': id_field if id_field != '.' else None,
            'ref_allele': ref,
            'alt_allele': alt,
            'quality': qual,
            'filter': filter_field,
            'info': info_dict,
            'raw_line': vcf_line
        }
    
    def parse_dbsnp_annotation(self, annotation_data: str) -> Dict[str, Any]:
        """
        Parse dbSNP annotation data and extract relevant information
        
        Args:
            annotation_data: Raw dbSNP annotation text
            
        Returns:
            Structured annotation dictionary
        """
        annotation = {
            'rsid': None,
            'gene': None,
            'clinical_significance': None,
            'diseases': [],
            'frequency': None,
            'functional_consequence': None,
            'protein_change': None,
            'pathway': None
        }
        
        # Extract rsID
        rsid_match = re.search(r'rs\d+', annotation_data)
        if rsid_match:
            annotation['rsid'] = rsid_match.group()
        
        # Extract gene names (simple pattern matching)
        gene_patterns = [
            r'Gene:\s*([A-Z][A-Z0-9_-]+)',
            r'GENE=([A-Z][A-Z0-9_-]+)',
            r'gene:\s*([A-Z][A-Z0-9_-]+)'
        ]
        
        for pattern in gene_patterns:
            gene_match = re.search(pattern, annotation_data, re.IGNORECASE)
            if gene_match:
                annotation['gene'] = gene_match.group(1)
                break
        
        # Extract clinical significance
        clinical_keywords = ['pathogenic', 'benign', 'uncertain', 'likely pathogenic', 'likely benign']
        for keyword in clinical_keywords:
            if keyword.lower() in annotation_data.lower():
                annotation['clinical_significance'] = keyword.title()
                break
        
        # Extract diseases/conditions
        disease_patterns = [
            r'cancer',
            r'carcinoma',
            r'tumor',
            r'breast cancer',
            r'ovarian cancer',
            r'colorectal cancer',
            r'lung cancer'
        ]
        
        for pattern in disease_patterns:
            if re.search(pattern, annotation_data, re.IGNORECASE):
                annotation['diseases'].append(pattern.title())
        
        # Extract frequency information
        freq_match = re.search(r'frequency:\s*([\d.]+)', annotation_data, re.IGNORECASE)
        if freq_match:
            annotation['frequency'] = float(freq_match.group(1))
        
        return annotation
    
    def enhance_with_bedrock(self, mutation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Bedrock to enhance mutation data with additional entities and relationships
        
        Args:
            mutation_data: Basic mutation information
            
        Returns:
            Enhanced mutation data with LLM-extracted information
        """
        # Prepare input text for Bedrock
        input_text = f"""
        Mutation Information:
        Chromosome: {mutation_data.get('chromosome', 'Unknown')}
        Position: {mutation_data.get('position', 'Unknown')}
        Reference Allele: {mutation_data.get('ref_allele', 'Unknown')}
        Alternate Allele: {mutation_data.get('alt_allele', 'Unknown')}
        Gene: {mutation_data.get('gene', 'Unknown')}
        rsID: {mutation_data.get('rsid', 'Unknown')}
        Clinical Significance: {mutation_data.get('clinical_significance', 'Unknown')}
        Diseases: {', '.join(mutation_data.get('diseases', []))}
        Frequency: {mutation_data.get('frequency', 'Unknown')}
        
        Additional Context: {mutation_data.get('raw_annotation', '')}
        """
        
        try:
            # Extract entities and relationships using Bedrock
            enhanced_data = self.bedrock_client.extract_entities_and_relationships(input_text)
            
            # Merge with original data
            mutation_data['bedrock_entities'] = enhanced_data.get('entities', [])
            mutation_data['bedrock_relationships'] = enhanced_data.get('relationships', [])
            
            return mutation_data
            
        except Exception as e:
            logger.error(f"Failed to enhance mutation data with Bedrock: {e}")
            return mutation_data
    
    def process_mutation_file(self, filepath: str, file_format: str = 'auto') -> List[Dict[str, Any]]:
        """
        Process a file containing mutation data
        
        Args:
            filepath: Path to the mutation data file
            file_format: Format of the file (vcf, tsv, csv, json, or auto)
            
        Returns:
            List of processed mutation dictionaries
        """
        if file_format == 'auto':
            # Detect format from file extension
            if filepath.endswith('.vcf'):
                file_format = 'vcf'
            elif filepath.endswith('.tsv'):
                file_format = 'tsv'
            elif filepath.endswith('.csv'):
                file_format = 'csv'
            elif filepath.endswith('.json'):
                file_format = 'json'
            else:
                logger.error(f"Cannot auto-detect format for {filepath}")
                return []
        
        mutations = []
        
        try:
            if file_format == 'vcf':
                mutations = self._process_vcf_file(filepath)
            elif file_format in ['tsv', 'csv']:
                mutations = self._process_tabular_file(filepath, file_format)
            elif file_format == 'json':
                mutations = self._process_json_file(filepath)
            else:
                logger.error(f"Unsupported file format: {file_format}")
                return []
                
        except Exception as e:
            logger.error(f"Error processing file {filepath}: {e}")
            return []
        
        return mutations
    
    def _process_vcf_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Process VCF format file"""
        mutations = []
        
        with open(filepath, 'r') as f:
            for line in f:
                mutation_data = self.parse_vcf_line(line)
                if mutation_data:
                    mutations.append(mutation_data)
        
        return mutations
    
    def _process_tabular_file(self, filepath: str, file_format: str) -> List[Dict[str, Any]]:
        """Process TSV or CSV format file"""
        separator = '\t' if file_format == 'tsv' else ','
        
        df = pd.read_csv(filepath, sep=separator)
        mutations = []
        
        # Map common column names
        column_mapping = {
            'chr': 'chromosome',
            'chrom': 'chromosome',
            'chromosome': 'chromosome',
            'pos': 'position',
            'position': 'position',
            'ref': 'ref_allele',
            'reference': 'ref_allele',
            'alt': 'alt_allele',
            'alternate': 'alt_allele',
            'gene': 'gene',
            'gene_name': 'gene',
            'rsid': 'rsid',
            'rs_id': 'rsid',
            'clinical_significance': 'clinical_significance',
            'frequency': 'frequency',
            'af': 'frequency'
        }
        
        for _, row in df.iterrows():
            mutation_data = {}
            
            for col in df.columns:
                mapped_col = column_mapping.get(col.lower(), col.lower())
                mutation_data[mapped_col] = row[col]
            
            mutations.append(mutation_data)
        
        return mutations
    
    def _process_json_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Process JSON format file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        else:
            logger.error("Invalid JSON format for mutations")
            return []
    
    def integrate_with_knowledge_graph(self, mutations: List[Dict[str, Any]], 
                                     knowledge_graph: GiraffeKnowledgeGraph,
                                     enhance_with_llm: bool = True) -> int:
        """
        Integrate processed mutations into the knowledge graph
        
        Args:
            mutations: List of processed mutation data
            knowledge_graph: Target knowledge graph
            enhance_with_llm: Whether to enhance with Bedrock LLM
            
        Returns:
            Number of mutations successfully integrated
        """
        integrated_count = 0
        
        for mutation in mutations:
            try:
                # Enhance with Bedrock if requested
                if enhance_with_llm:
                    mutation = self.enhance_with_bedrock(mutation)
                
                # Add mutation to knowledge graph
                variant_id = knowledge_graph.add_mutation_data(mutation)
                
                # Add Bedrock-extracted entities and relationships
                if 'bedrock_entities' in mutation:
                    for entity in mutation['bedrock_entities']:
                        entity_id = f"{entity['type']}_{entity['name'].replace(' ', '_').lower()}"
                        knowledge_graph.add_entity(entity_id, entity['type'], entity.get('properties', {}))
                        
                        # Connect to the variant
                        if entity['type'] != 'variant':
                            knowledge_graph.add_relationship(variant_id, entity_id, "associated_with", {
                                "source": "bedrock_llm",
                                "confidence": "medium"
                            })
                
                if 'bedrock_relationships' in mutation:
                    for relationship in mutation['bedrock_relationships']:
                        source_id = f"entity_{relationship['source'].replace(' ', '_').lower()}"
                        target_id = f"entity_{relationship['target'].replace(' ', '_').lower()}"
                        
                        # Only add if both entities exist
                        if (knowledge_graph.graph.has_node(source_id) and 
                            knowledge_graph.graph.has_node(target_id)):
                            knowledge_graph.add_relationship(
                                source_id, target_id, relationship['type'],
                                relationship.get('properties', {})
                            )
                
                integrated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to integrate mutation: {e}")
                continue
        
        logger.info(f"Successfully integrated {integrated_count} mutations into knowledge graph")
        return integrated_count


# Utility functions for common annotation tasks
def create_sample_mutation_data() -> List[Dict[str, Any]]:
    """
    Create sample mutation data for testing
    
    Returns:
        List of sample mutation dictionaries
    """
    return [
        {
            'chromosome': 'chr17',
            'position': '41234470',
            'ref_allele': 'A',
            'alt_allele': 'G',
            'gene': 'BRCA1',
            'rsid': 'rs80357382',
            'clinical_significance': 'Pathogenic',
            'diseases': ['Breast Cancer', 'Ovarian Cancer'],
            'frequency': 0.0001,
            'raw_annotation': 'BRCA1 pathogenic variant associated with hereditary breast and ovarian cancer syndrome'
        },
        {
            'chromosome': 'chr13',
            'position': '32913055',
            'ref_allele': 'G',
            'alt_allele': 'A',
            'gene': 'BRCA2',
            'rsid': 'rs80359550',
            'clinical_significance': 'Pathogenic',
            'diseases': ['Breast Cancer', 'Ovarian Cancer', 'Pancreatic Cancer'],
            'frequency': 0.00005,
            'raw_annotation': 'BRCA2 truncating mutation leading to loss of DNA repair function'
        },
        {
            'chromosome': 'chr3',
            'position': '178916961',
            'ref_allele': 'C',
            'alt_allele': 'T',
            'gene': 'PIK3CA',
            'rsid': 'rs121913273',
            'clinical_significance': 'Pathogenic',
            'diseases': ['Colorectal Cancer', 'Breast Cancer'],
            'frequency': 0.001,
            'raw_annotation': 'PIK3CA activating mutation in PI3K-AKT pathway'
        }
    ]


# Example usage
if __name__ == "__main__":
    from .bedrock_client import create_bedrock_client
    
    # Initialize components
    bedrock_client = create_bedrock_client()
    processor = MutationAnnotationProcessor(bedrock_client)
    kg = GiraffeKnowledgeGraph("GIRAFFE_Annotation_Demo")
    
    # Process sample mutations
    sample_mutations = create_sample_mutation_data()
    
    # Integrate with knowledge graph
    integrated_count = processor.integrate_with_knowledge_graph(
        sample_mutations, kg, enhance_with_llm=True
    )
    
    print(f"Integrated {integrated_count} mutations")
    
    # Display graph statistics
    stats = kg.get_graph_statistics()
    print("Knowledge Graph Statistics:")
    print(json.dumps(stats, indent=2))