"""
GIRAFFE Agent Knowledge Graph - Complete Example Usage
Demonstrates the full pipeline integration with sample cancer genome data
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add the parent directory to path to import knowledge_graph module
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from knowledge_graph.bedrock_client import create_bedrock_client
from knowledge_graph.giraffe_kg import GiraffeKnowledgeGraph
from knowledge_graph.mutation_processor import MutationAnnotationProcessor, create_sample_mutation_data
from knowledge_graph.llm_extractor import GenomicsEntityExtractor
from knowledge_graph.visualizer import KnowledgeGraphVisualizer, KnowledgeGraphExporter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_tcga_data():
    """
    Create sample TCGA-like data for demonstration
    
    Returns:
        List of sample data dictionaries
    """
    return [
        {
            'sample_id': 'TCGA-A1-A0SB-01A',
            'patient_id': 'TCGA-A1-A0SB',
            'cancer_type': 'Breast Invasive Carcinoma',
            'age': 65,
            'gender': 'Female',
            'stage': 'Stage IIA',
            'mutations': [
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
                    'vaf': 0.42  # Variant allele frequency
                },
                {
                    'chromosome': 'chr3',
                    'position': '178916961',
                    'ref_allele': 'C',
                    'alt_allele': 'T',
                    'gene': 'PIK3CA',
                    'rsid': 'rs121913273',
                    'clinical_significance': 'Pathogenic',
                    'diseases': ['Breast Cancer', 'Colorectal Cancer'],
                    'frequency': 0.001,
                    'vaf': 0.38
                }
            ]
        },
        {
            'sample_id': 'TCGA-A2-A0T2-01A',
            'patient_id': 'TCGA-A2-A0T2',
            'cancer_type': 'Breast Invasive Carcinoma',
            'age': 58,
            'gender': 'Female',
            'stage': 'Stage IIIA',
            'mutations': [
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
                    'vaf': 0.45
                },
                {
                    'chromosome': 'chr17',
                    'position': '7577121',
                    'ref_allele': 'C',
                    'alt_allele': 'T',
                    'gene': 'TP53',
                    'rsid': 'rs28934576',
                    'clinical_significance': 'Pathogenic',
                    'diseases': ['Li-Fraumeni Syndrome', 'Breast Cancer', 'Sarcoma'],
                    'frequency': 0.0002,
                    'vaf': 0.51
                }
            ]
        },
        {
            'sample_id': 'TCGA-A3-A01C-01A',
            'patient_id': 'TCGA-A3-A01C',
            'cancer_type': 'Colorectal Adenocarcinoma',
            'age': 72,
            'gender': 'Male',
            'stage': 'Stage II',
            'mutations': [
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
                    'vaf': 0.33
                },
                {
                    'chromosome': 'chr18',
                    'position': '48581173',
                    'ref_allele': 'G',
                    'alt_allele': 'A',
                    'gene': 'SMAD4',
                    'rsid': 'rs121908377',
                    'clinical_significance': 'Pathogenic',
                    'diseases': ['Colorectal Cancer', 'Pancreatic Cancer'],
                    'frequency': 0.0003,
                    'vaf': 0.47
                }
            ]
        }
    ]

def create_sample_literature_abstracts():
    """
    Create sample literature abstracts for entity extraction
    
    Returns:
        List of literature abstracts
    """
    return [
        {
            'pmid': '12345678',
            'title': 'BRCA1 and BRCA2 mutations in hereditary breast cancer',
            'abstract': """
            BRCA1 and BRCA2 mutations are associated with hereditary breast and ovarian cancer syndrome.
            These genes encode proteins involved in DNA repair through homologous recombination.
            Pathogenic variants in BRCA1 (located on chromosome 17) and BRCA2 (chromosome 13) 
            significantly increase the risk of breast cancer by up to 80% and ovarian cancer by up to 40%.
            PARP inhibitors such as olaparib target BRCA-deficient tumors through synthetic lethality.
            The PI3K/AKT/mTOR pathway is frequently dysregulated in BRCA-associated cancers.
            """
        },
        {
            'pmid': '23456789',
            'title': 'PIK3CA mutations in colorectal cancer progression',
            'abstract': """
            PIK3CA mutations are found in approximately 15-20% of colorectal cancers.
            The most common mutations occur in exons 9 and 20, affecting the helical and kinase domains.
            PIK3CA encodes the p110α catalytic subunit of phosphoinositide 3-kinase (PI3K).
            Activating mutations lead to enhanced AKT signaling and promote cell survival and proliferation.
            PI3K inhibitors and combination therapies targeting the PI3K/AKT pathway show promise in treatment.
            KRAS and PIK3CA mutations often co-occur and may influence response to targeted therapies.
            """
        },
        {
            'pmid': '34567890',
            'title': 'TP53 mutations across cancer types',
            'abstract': """
            TP53 is the most frequently mutated gene in human cancers, with mutations found in over 50% of cases.
            The TP53 gene encodes the p53 tumor suppressor protein, known as the "guardian of the genome".
            Loss of p53 function disrupts cell cycle checkpoints and apoptosis pathways.
            Different mutation types have varying effects on protein stability and transcriptional activity.
            MDM2 amplification provides an alternative mechanism for p53 inactivation.
            Therapeutic strategies targeting mutant p53 include protein refolding agents and synthetic lethality approaches.
            """
        }
    ]

def run_complete_example():
    """
    Run the complete GIRAFFE Agent knowledge graph example
    """
    logger.info("Starting GIRAFFE Agent Knowledge Graph Example")
    
    # Create output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Step 1: Initialize components
        logger.info("Step 1: Initializing AWS Bedrock and components...")
        bedrock_client = create_bedrock_client(region_name="us-east-1")
        
        # Initialize knowledge graph
        kg = GiraffeKnowledgeGraph("GIRAFFE_Demo_Cancer_Genomics")
        
        # Initialize processors
        mutation_processor = MutationAnnotationProcessor(bedrock_client)
        entity_extractor = GenomicsEntityExtractor(bedrock_client)
        
        # Step 2: Process sample TCGA data
        logger.info("Step 2: Processing sample TCGA data...")
        tcga_samples = create_sample_tcga_data()
        
        all_mutations = []
        for sample in tcga_samples:
            # Add sample to knowledge graph
            sample_mutations = []
            
            for mutation in sample['mutations']:
                # Add mutation to knowledge graph
                variant_id = kg.add_mutation_data(mutation)
                sample_mutations.append(variant_id)
                all_mutations.append(mutation)
            
            # Add sample data
            kg.add_sample_data(
                sample['sample_id'],
                sample['patient_id'],
                sample['cancer_type'],
                sample_mutations
            )
            
            # Add patient metadata
            if not kg.graph.has_node(sample['patient_id']):
                kg.add_entity(sample['patient_id'], "patient", {
                    'age': sample['age'],
                    'gender': sample['gender'],
                    'cancer_type': sample['cancer_type'],
                    'stage': sample['stage']
                })
        
        logger.info(f"Processed {len(tcga_samples)} TCGA samples with {len(all_mutations)} mutations")
        
        # Step 3: Enhance with literature-based entity extraction
        logger.info("Step 3: Enhancing with literature-based entity extraction...")
        literature_abstracts = create_sample_literature_abstracts()
        
        for abstract in literature_abstracts:
            # Extract entities from literature
            literature_entities = entity_extractor.extract_entities_from_literature(
                abstract['abstract']
            )
            
            # Add publication entity
            pub_id = f"pmid_{abstract['pmid']}"
            kg.add_entity(pub_id, "publication", {
                'pmid': abstract['pmid'],
                'title': abstract['title'],
                'type': 'research_article'
            })
            
            # Add extracted entities and connect to publication
            for entity in literature_entities.get('entities', []):
                entity_id = f"{entity['type']}_{entity['name'].replace(' ', '_').lower()}"
                
                # Add entity if it doesn't exist
                if not kg.graph.has_node(entity_id):
                    kg.add_entity(entity_id, entity['type'], entity.get('properties', {}))
                
                # Connect to publication
                kg.add_relationship(entity_id, pub_id, "mentioned_in", {
                    'confidence': entity.get('properties', {}).get('confidence', 'medium'),
                    'evidence_type': 'literature'
                })
            
            # Add extracted relationships
            for relationship in literature_entities.get('relationships', []):
                source_id = f"entity_{relationship['source'].replace(' ', '_').lower()}"
                target_id = f"entity_{relationship['target'].replace(' ', '_').lower()}"
                
                # Only add if both entities exist
                if (kg.graph.has_node(source_id) and kg.graph.has_node(target_id)):
                    kg.add_relationship(
                        source_id, target_id, relationship['type'],
                        {**relationship.get('properties', {}), 'source': 'literature'}
                    )
        
        # Step 4: Create visualizations
        logger.info("Step 4: Creating visualizations...")
        visualizer = KnowledgeGraphVisualizer(kg)
        
        # Interactive visualization
        interactive_fig = visualizer.create_interactive_plot(
            layout='spring',
            output_file=os.path.join(output_dir, 'giraffe_kg_interactive.html')
        )
        
        # Static visualization
        static_fig = visualizer.create_static_plot(
            layout='spring',
            output_file=os.path.join(output_dir, 'giraffe_kg_static.png')
        )
        
        # Statistics dashboard
        dashboard_fig = visualizer.create_statistics_dashboard(
            output_file=os.path.join(output_dir, 'giraffe_kg_dashboard.html')
        )
        
        # Subgraph around BRCA1
        brca1_subgraph = visualizer.create_subgraph_visualization(
            center_node='gene_BRCA1',
            radius=2,
            output_file=os.path.join(output_dir, 'brca1_subgraph.html')
        )
        
        # Step 5: Export knowledge graph
        logger.info("Step 5: Exporting knowledge graph...")
        exporter = KnowledgeGraphExporter(kg)
        
        # Export to various formats
        kg.export_to_json(os.path.join(output_dir, 'giraffe_kg.json'))
        kg.save_graph(os.path.join(output_dir, 'giraffe_kg.pkl'))
        
        exporter.export_to_csv(os.path.join(output_dir, 'csv_export'))
        exporter.export_summary_report(os.path.join(output_dir, 'giraffe_kg_report.txt'))
        
        visualizer.export_to_cytoscape(os.path.join(output_dir, 'giraffe_kg_cytoscape.json'))
        visualizer.export_to_gephi(os.path.join(output_dir, 'giraffe_kg.gexf'))
        
        # Step 6: Generate summary statistics
        logger.info("Step 6: Generating summary statistics...")
        stats = kg.get_graph_statistics()
        
        print("\n" + "="*60)
        print("GIRAFFE AGENT KNOWLEDGE GRAPH SUMMARY")
        print("="*60)
        print(f"Graph Name: {kg.name}")
        print(f"Total Nodes: {stats['total_nodes']}")
        print(f"Total Edges: {stats['total_edges']}")
        print(f"Graph Density: {stats['density']:.4f}")
        print(f"Is Connected: {stats['is_connected']}")
        
        print("\nEntity Distribution:")
        for entity_type, count in stats['entity_counts'].items():
            percentage = (count / stats['total_nodes']) * 100
            print(f"  {entity_type.title()}: {count} ({percentage:.1f}%)")
        
        print("\nRelationship Distribution:")
        for rel_type, count in stats['relationship_counts'].items():
            percentage = (count / stats['total_edges']) * 100
            print(f"  {rel_type.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
        
        # Show some example queries
        print("\n" + "="*60)
        print("EXAMPLE KNOWLEDGE GRAPH QUERIES")
        print("="*60)
        
        # Find genes
        genes = kg.find_entities_by_type('gene')
        print(f"\nGenes in the graph: {genes}")
        
        # Find diseases
        diseases = kg.find_entities_by_type('disease')
        print(f"Diseases in the graph: {diseases}")
        
        # Find neighbors of BRCA1
        if 'gene_BRCA1' in [node for node in kg.graph.nodes()]:
            brca1_neighbors = kg.get_entity_neighbors('gene_BRCA1')
            print(f"\nEntities connected to BRCA1: {brca1_neighbors}")
        
        # Find shortest path between two entities
        if len(genes) >= 2:
            path = kg.get_shortest_path(genes[0], genes[1])
            print(f"\nShortest path between {genes[0]} and {genes[1]}: {path}")
        
        print(f"\nAll outputs saved to: {os.path.abspath(output_dir)}")
        print("="*60)
        
        logger.info("GIRAFFE Agent Knowledge Graph example completed successfully!")
        
        return kg, stats
        
    except Exception as e:
        logger.error(f"Error in example execution: {e}")
        raise


def demonstrate_bedrock_features():
    """
    Demonstrate specific Bedrock features without full graph creation
    """
    logger.info("Demonstrating Bedrock features...")
    
    try:
        # Initialize Bedrock client
        bedrock_client = create_bedrock_client()
        
        # Test model listing
        models = bedrock_client.list_foundation_models()
        print(f"\nAvailable Bedrock models: {len(models)}")
        
        # Test entity extraction
        sample_text = """
        BRCA1 mutations cause hereditary breast and ovarian cancer.
        The PIK3CA gene encodes the p110α subunit of PI3K kinase.
        Olaparib is a PARP inhibitor used to treat BRCA-deficient cancers.
        """
        
        entities = bedrock_client.extract_entities_and_relationships(sample_text)
        print("\nExtracted entities and relationships:")
        print(json.dumps(entities, indent=2))
        
        # Test embedding generation
        embedding = bedrock_client.invoke_titan_embed("BRCA1 breast cancer gene")
        print(f"\nGenerated embedding dimension: {len(embedding)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error demonstrating Bedrock features: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='GIRAFFE Agent Knowledge Graph Example')
    parser.add_argument('--demo-only', action='store_true', 
                       help='Run Bedrock demo only (no full graph creation)')
    parser.add_argument('--output-dir', default='output',
                       help='Output directory for generated files')
    
    args = parser.parse_args()
    
    if args.demo_only:
        # Run Bedrock demonstration only
        success = demonstrate_bedrock_features()
        if success:
            print("Bedrock demonstration completed successfully!")
        else:
            print("Bedrock demonstration failed. Please check your AWS credentials and region.")
    else:
        # Run complete example
        try:
            kg, stats = run_complete_example()
            print("\nExample completed successfully!")
            print("Check the 'output' directory for generated visualizations and exports.")
        except Exception as e:
            print(f"Example failed: {e}")
            print("\nTroubleshooting tips:")
            print("1. Ensure AWS credentials are configured")
            print("2. Verify Bedrock access in your AWS region")
            print("3. Check that all required packages are installed")
            print("4. Try running with --demo-only flag first")