# GIRAFFE Agent Knowledge Graph

A comprehensive knowledge graph implementation for cancer genomics analysis using Amazon Bedrock and the GIRAFFE pipeline.

## Overview

This project implements a sophisticated knowledge graph system that integrates with Amazon Bedrock to create, analyze, and visualize relationships between cancer genome data, mutations, genes, diseases, and therapeutic compounds.

## Features

### 🧬 Core Knowledge Graph
- **Multi-entity support**: Genes, variants, diseases, proteins, pathways, drugs, samples, patients
- **Flexible relationships**: Multiple relationship types with properties and evidence tracking
- **NetworkX backend**: Robust graph operations and algorithms
- **Persistence**: JSON and pickle serialization support

### 🤖 Amazon Bedrock Integration
- **Claude 3 integration**: Advanced entity and relationship extraction
- **Titan Embeddings**: Vector representations for semantic search
- **Literature processing**: Extract knowledge from research abstracts
- **Clinical report analysis**: Process genomic test reports

### 📊 Advanced Visualization
- **Interactive plots**: Plotly-based web visualizations
- **Static plots**: High-quality matplotlib figures
- **Statistics dashboards**: Comprehensive graph metrics
- **Subgraph exploration**: Focus on specific entities and neighborhoods

### 🔄 Data Processing Pipeline
- **VCF/CSV/JSON support**: Multiple input formats
- **dbSNP integration**: Automated mutation annotation
- **TCGA compatibility**: Process cancer genome atlas data
- **Batch processing**: Handle large datasets efficiently

### 📤 Export Capabilities
- **Multiple formats**: Cytoscape, Gephi, CSV, JSON
- **Summary reports**: Detailed text-based analysis
- **Visualization exports**: HTML, PNG, PDF outputs

## Installation

### Prerequisites
- Python 3.8+
- AWS Account with Bedrock access
- AWS CLI configured or environment variables set

### Install Dependencies
```bash
pip install -r requirements.txt
```

### AWS Configuration
1. Copy `.env.example` to `.env`
2. Configure your AWS credentials:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

## Quick Start

### 1. Basic Knowledge Graph Creation
```python
from knowledge_graph import GiraffeKnowledgeGraph, create_bedrock_client

# Initialize components
bedrock_client = create_bedrock_client()
kg = GiraffeKnowledgeGraph("My_Cancer_KG")

# Add mutation data
mutation_data = {
    'chromosome': 'chr17',
    'position': '41234470',
    'gene': 'BRCA1',
    'rsid': 'rs80357382',
    'clinical_significance': 'Pathogenic',
    'diseases': ['Breast Cancer', 'Ovarian Cancer']
}

variant_id = kg.add_mutation_data(mutation_data)
```

### 2. Literature-based Entity Extraction
```python
from knowledge_graph import GenomicsEntityExtractor

extractor = GenomicsEntityExtractor(bedrock_client)

abstract = """
BRCA1 mutations are associated with hereditary breast cancer.
PARP inhibitors target BRCA-deficient tumors effectively.
"""

entities = extractor.extract_entities_from_literature(abstract)
```

### 3. Visualization
```python
from knowledge_graph import KnowledgeGraphVisualizer

visualizer = KnowledgeGraphVisualizer(kg)

# Create interactive visualization
fig = visualizer.create_interactive_plot(
    layout='spring',
    output_file='cancer_kg.html'
)

# Create statistics dashboard
dashboard = visualizer.create_statistics_dashboard(
    output_file='kg_dashboard.html'
)
```

### 4. Complete Pipeline Example
```bash
cd examples
python complete_example.py
```

This will:
- Process sample TCGA data
- Extract entities from literature
- Create visualizations
- Export to multiple formats
- Generate summary statistics

## Project Structure

```
GiraffeAgent2/
├── knowledge_graph/
│   ├── __init__.py
│   ├── bedrock_client.py      # AWS Bedrock integration
│   ├── giraffe_kg.py          # Core knowledge graph
│   ├── mutation_processor.py  # Mutation data processing
│   ├── llm_extractor.py       # LLM-powered extraction
│   └── visualizer.py          # Visualization tools
├── examples/
│   └── complete_example.py    # Full pipeline demonstration
├── requirements.txt
├── .env.example
└── README.md
```

## GIRAFFE Pipeline Integration

This knowledge graph integrates seamlessly with the GIRAFFE pipeline:

1. **TCGA Data Processing** → Load cancer genome samples
2. **GIRAFFE Mapping** → Process alignment and variation data
3. **Mutation Identification** → Extract genomic positions
4. **dbSNP Annotation** → Enrich with clinical significance
5. **Clustering** → Group similar mutation profiles
6. **Knowledge Graph Creation** → Build relationships using Bedrock
7. **Analysis & Visualization** → Generate insights and visualizations

## Advanced Usage

### Custom Entity Types
```python
# Add custom entity types
kg.entity_types.add("biomarker")
kg.relationship_types.add("predicts_response")

kg.add_entity("biomarker_her2", "biomarker", {
    "name": "HER2",
    "type": "protein_expression",
    "clinical_utility": "therapeutic_target"
})
```

### Bedrock Model Configuration
```python
# Use different Bedrock models
bedrock_client = create_bedrock_client(region_name="us-west-2")

# Custom prompts for entity extraction
custom_entities = bedrock_client.extract_entities_and_relationships(
    mutation_data, 
    model_id="anthropic.claude-3-haiku-20240307-v1:0"
)
```

### Graph Analytics
```python
# Find shortest paths
path = kg.get_shortest_path("gene_BRCA1", "disease_breast_cancer")

# Get entity neighborhoods
neighbors = kg.get_entity_neighbors("variant_chr17_41234470_A_G")

# Graph statistics
stats = kg.get_graph_statistics()
```

## Output Files

The system generates various output files:

- **Interactive visualizations**: HTML files with Plotly graphs
- **Static plots**: High-resolution PNG/PDF images
- **Export formats**: Cytoscape JSON, Gephi GEXF, CSV tables
- **Analysis reports**: Text summaries with statistics
- **Serialized graphs**: JSON and pickle formats for persistence

## Troubleshooting

### Common Issues

1. **AWS Bedrock Access**: Ensure your AWS account has Bedrock permissions
2. **Region Availability**: Bedrock is available in specific regions (us-east-1, us-west-2)
3. **Model Access**: Request access to Claude 3 and Titan models in AWS console
4. **Memory Usage**: Large graphs may require increased memory allocation

### Testing Bedrock Connection
```bash
python examples/complete_example.py --demo-only
```

## API Reference

### Core Classes

- **`GiraffeKnowledgeGraph`**: Main knowledge graph class
- **`BedrockClient`**: AWS Bedrock integration
- **`MutationAnnotationProcessor`**: Process mutation data
- **`GenomicsEntityExtractor`**: LLM-powered entity extraction
- **`KnowledgeGraphVisualizer`**: Visualization tools

### Key Methods

- `add_mutation_data()`: Add genomic variants
- `add_sample_data()`: Add TCGA samples
- `extract_entities_from_literature()`: Process research abstracts
- `create_interactive_plot()`: Generate visualizations
- `export_to_json()`: Save graph data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this knowledge graph in your research, please cite:

```
GIRAFFE Agent Knowledge Graph: Cancer Genomics Analysis with Amazon Bedrock
GitHub: https://github.com/collaborativebioinformatics/GiraffeAgent2
```

## Support

For questions and support:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the example scripts
- Consult AWS Bedrock documentation
Giraffe Agent -- Multisite polygenicity extraction from cancer genomes

