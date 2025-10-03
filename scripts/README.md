# Disease Resolver Scripts

Python scripts for resolving disease names to MONDO identifiers using the Name Resolution Service API.

## Overview

These scripts query the Name Resolution Service (https://name-resolution-sri.renci.org) to map human-readable disease names to standardized MONDO (Monarch Disease Ontology) identifiers.

## Files

- **`disease_resolver.py`** - Main script for single disease resolution
- **`variant_resolver.py`** - Resolve MONDO IDs to sequence variants using GWAS Catalog
- **`batch_disease_resolver.py`** - Batch processing for multiple diseases
- **`test_disease_resolver.py`** - Test suite with examples
- **`sample_diseases.txt`** - Sample disease names for testing

## Installation

No additional dependencies required beyond the base requirements:

```bash
pip install requests
```

## Usage

### 1. Single Disease Resolution

```bash
# Basic usage
python scripts/disease_resolver.py "breast cancer"

# Get only the MONDO ID
python scripts/disease_resolver.py "lung cancer" --curie-only

# Full JSON output
python scripts/disease_resolver.py "colorectal cancer" --json

# With custom limit
python scripts/disease_resolver.py "ovarian cancer" --limit 5
```

**Example Output:**
```
============================================================
Disease Query: breast cancer
============================================================
MONDO ID (CURIE): MONDO:0007254
Label: breast carcinoma
Score: 3208.0525
Types: biolink:Disease
============================================================
```

**CURIE-only Output:**
```bash
python scripts/disease_resolver.py "sickle cell disease" --curie-only
# Output: MONDO:0011382
```

### 2. Variant Resolution (Disease → MONDO → Variants)

```bash
# Get variants for a MONDO ID
python scripts/variant_resolver.py --mondo "MONDO:0011382"

# Complete pipeline: disease name to variants
python scripts/variant_resolver.py --disease "sickle cell disease"

# JSON output with variant details
python scripts/variant_resolver.py --disease "sickle cell disease" --json

# Get only ROBO_VARIANT identifiers
python scripts/variant_resolver.py --disease "sickle cell disease" --robo-only

# Get FASTA sequences with 100bp padding
python scripts/variant_resolver.py --disease "sickle cell disease" --fasta-only

# Limit number of variants displayed
python scripts/variant_resolver.py --mondo "MONDO:0011382" --limit 3
```

**Example Output:**
```
============================================================
Sequence Variants for Disease: sickle cell disease
============================================================
Found 7 variants:

1. Variant ID: CAID:CA217071073

2. Variant ID: CAID:CA11319306

3. Variant ID: CAID:CA13407889

4. Variant ID: CAID:CA276424642

5. Variant ID: CAID:CA1949461566

6. Variant ID: CAID:CA1254900203

7. Variant ID: CAID:CA1254900202

============================================================
```

**ROBO_VARIANT Output:**
```bash
python scripts/variant_resolver.py --disease "sickle cell disease" --robo-only
# Output:
ROBO_VARIANT:HG38|11|5008472|5008473|C|T
ROBO_VARIANT:HG38|2|60492834|60492835|C|A
ROBO_VARIANT:HG38|11|5450515|5450516|G|A
```

**FASTA Sequence Output:**
```bash
python scripts/variant_resolver.py --disease "sickle cell disease" --fasta-only --limit 1
# Output:
>hg38:chr11:5008372-5008573
AATTGGGCTTAATGATGATGTTGTCTTTCTGTGACCACACAAGAGCTTCTCAGATCACAC
ACACACACAAACACACACAAACATTAGCTTACTCTTTCTTACACTATGAATTAATAACAA
GATATTTTAAAAGTGTGGATGACATTAAAATCTAAAAAAGAAATATCTCAATGTATCCAT
TTTAATACACTTCAATCATTTT
```

**JSON Output Example:**
```json
[
  {
    "name": "rs2445284",
    "id": "CAID:CA217071073",
    "equivalent_identifiers": [
      "HGVS:NC_000011.10:g.5008473C>T",
      "DBSNP:rs2445284",
      "ROBO_VARIANT:HG38|11|5008472|5008473|C|T"
    ]
  }
]
```

### 3. Batch Processing

```bash
# From file
python scripts/batch_disease_resolver.py --input scripts/sample_diseases.txt --output results.json

# From command line list
python scripts/batch_disease_resolver.py \
  --diseases "breast cancer" "lung cancer" "melanoma" \
  --output results.json

# Save as CSV
python scripts/batch_disease_resolver.py \
  --input scripts/sample_diseases.txt \
  --output results.csv \
  --format csv
```

**Example Output (CSV):**
```csv
Disease Name,MONDO ID,Label,Score,Status
breast cancer,MONDO:0007254,breast carcinoma,28.5,Found
lung cancer,MONDO:0008903,lung cancer,30.2,Found
melanoma,MONDO:0005105,melanoma,32.1,Found
```

### 4. VG Toolkit Integration (Disease → Variants → Sequence Graph)

**Prerequisites**: VG toolkit and art_illumina must be installed. Run the installation scripts:
```bash
bash bootstrap-scripts/install_vg.sh
bash bootstrap-scripts/install-tools.sh  # Installs art_illumina and other tools
```

#### Complete Pipeline: Disease to Variant Graph

```bash
# Step 1: Create working directory
mkdir -p variant_graphs
cd variant_graphs

# Step 2: Get FASTA sequences for all variants of a disease
python ../scripts/variant_resolver.py --disease "sickle cell disease" --fasta-only > sickle_cell_variants.fasta

# Step 3: Convert FASTA to FASTQ using art_illumina (simulates sequencing reads)
art_illumina -ss HS25 -i sickle_cell_variants.fasta -l 150 -f 10 -o sickle_cell_reads
# This creates sickle_cell_reads1.fq and sickle_cell_reads2.fq (paired-end reads)

# Step 4: Create a sequence graph from the FASTA sequences
vg construct -r sickle_cell_variants.fasta -v sickle_cell_variants.vcf > sickle_cell_graph.vg

# Alternative: If you don't have VCF, create graph from FASTA only
vg construct -r sickle_cell_variants.fasta > sickle_cell_graph.vg

# Step 5: Convert to other formats if needed
vg view sickle_cell_graph.vg > sickle_cell_graph.gfa  # GFA format
vg view -j sickle_cell_graph.vg > sickle_cell_graph.json  # JSON format

# Step 6: Index the graph for alignment
vg index -x sickle_cell_graph.xg sickle_cell_graph.vg
vg prune sickle_cell_graph.vg > sickle_cell_pruned.vg
vg index -g sickle_cell_gcsa.gcsa -k 16 sickle_cell_pruned.vg

# Step 7: Align the simulated reads to the variant graph
vg map -x sickle_cell_graph.xg -g sickle_cell_gcsa.gcsa -f sickle_cell_reads1.fq -f sickle_cell_reads2.fq > sickle_cell_alignments.gam

# Step 8: Call variants from the alignments
vg call sickle_cell_graph.vg sickle_cell_alignments.gam > sickle_cell_called_variants.vcf

# Step 9: Visualize the graph (optional)
vg view -d sickle_cell_graph.vg | dot -Tpng -o sickle_cell_graph.png
```

#### Automated Script Example

Create a script `disease_to_graph.sh`:

```bash
#!/bin/bash
# Usage: ./disease_to_graph.sh "disease name"

DISEASE="$1"
SAFE_NAME=$(echo "$DISEASE" | tr ' ' '_' | tr '[:upper:]' '[:lower:]')

echo "Processing disease: $DISEASE"
echo "Output prefix: $SAFE_NAME"

# Create output directory
mkdir -p "graphs/$SAFE_NAME"
cd "graphs/$SAFE_NAME"

# Step 1: Get FASTA sequences
echo "Fetching FASTA sequences..."
python ../../scripts/variant_resolver.py --disease "$DISEASE" --fasta-only > "${SAFE_NAME}_variants.fasta"

# Check if FASTA file has content
if [ ! -s "${SAFE_NAME}_variants.fasta" ]; then
    echo "No variants found for $DISEASE"
    exit 1
fi

echo "Found $(grep -c '^>' "${SAFE_NAME}_variants.fasta") variant sequences"

# Step 2: Convert FASTA to FASTQ using art_illumina
echo "Converting FASTA to FASTQ with art_illumina..."
art_illumina -ss HS25 -i "${SAFE_NAME}_variants.fasta" -l 150 -f 10 -o "${SAFE_NAME}_reads"

# Step 3: Create sequence graph
echo "Building sequence graph..."
vg construct -r "${SAFE_NAME}_variants.fasta" > "${SAFE_NAME}_graph.vg"

# Step 4: Create indexes
echo "Creating graph indexes..."
vg index -x "${SAFE_NAME}_graph.xg" "${SAFE_NAME}_graph.vg"
vg prune "${SAFE_NAME}_graph.vg" > "${SAFE_NAME}_pruned.vg"
vg index -g "${SAFE_NAME}_gcsa.gcsa" -k 16 "${SAFE_NAME}_pruned.vg"

# Step 5: Align reads to graph
echo "Aligning reads to variant graph..."
vg map -x "${SAFE_NAME}_graph.xg" -g "${SAFE_NAME}_gcsa.gcsa" -f "${SAFE_NAME}_reads1.fq" -f "${SAFE_NAME}_reads2.fq" > "${SAFE_NAME}_alignments.gam"

# Step 6: Call variants
echo "Calling variants from alignments..."
vg call "${SAFE_NAME}_graph.vg" "${SAFE_NAME}_alignments.gam" > "${SAFE_NAME}_called_variants.vcf"

# Step 7: Export formats
echo "Exporting graph formats..."
vg view "${SAFE_NAME}_graph.vg" > "${SAFE_NAME}_graph.gfa"
vg view -j "${SAFE_NAME}_graph.vg" > "${SAFE_NAME}_graph.json"

# Step 5: Generate statistics
echo "Graph statistics:"
vg stats -l "${SAFE_NAME}_graph.vg"

echo "Complete! Files created in graphs/$SAFE_NAME/"
echo "  - ${SAFE_NAME}_variants.fasta (input sequences)"
echo "  - ${SAFE_NAME}_reads1.fq, ${SAFE_NAME}_reads2.fq (simulated reads)"
echo "  - ${SAFE_NAME}_graph.vg (variation graph)"
echo "  - ${SAFE_NAME}_graph.xg (indexed graph)"
echo "  - ${SAFE_NAME}_alignments.gam (read alignments)"
echo "  - ${SAFE_NAME}_called_variants.vcf (called variants)"
echo "  - ${SAFE_NAME}_graph.gfa (GFA format)"
echo "  - ${SAFE_NAME}_graph.json (JSON format)"
```

Make it executable and run:
```bash
chmod +x disease_to_graph.sh
./disease_to_graph.sh "sickle cell disease"
./disease_to_graph.sh "breast cancer"
```

#### art_illumina Parameters

```bash
# art_illumina options for read simulation:
# -ss HS25: Illumina HiSeq 2500 sequencing system
# -i: input FASTA file
# -l 150: read length (150bp)
# -f 10: fold coverage (10x)
# -o: output prefix
# -p: paired-end reads
# -m 200: mean fragment size
# -s 20: standard deviation of fragment size

# Example with more options:
art_illumina -ss HS25 -i variants.fasta -p -l 150 -f 20 -m 300 -s 50 -o reads_prefix
```

#### Working with the Generated Graphs

```bash
# Generate consensus paths
vg find -x graph.xg -p > paths.txt

# Extract specific paths
vg find -x graph.xg -P path_name -K > path_sequence.fasta

# Convert alignments to different formats
vg view -a alignments.gam > alignments.json
vg surject -x graph.xg -b alignments.gam > alignments.bam

# Generate statistics
vg stats -a alignments.gam
vg stats -l graph.vg
```

#### Integration with GIRAFFE Pipeline

```python
# Example: Automated graph generation in Python
import subprocess
import os
from scripts.variant_resolver import resolve_disease_to_variants, fetch_fasta_for_robo_variant

def create_disease_variant_graph(disease_name, output_dir="graphs"):
    """
    Complete pipeline: disease -> variants -> FASTA -> VG graph
    """
    safe_name = disease_name.replace(' ', '_').lower()
    graph_dir = os.path.join(output_dir, safe_name)
    os.makedirs(graph_dir, exist_ok=True)
    
    # Get variants
    variants = resolve_disease_to_variants(disease_name)
    if not variants:
        print(f"No variants found for {disease_name}")
        return None
    
    # Extract FASTA sequences
    fasta_file = os.path.join(graph_dir, f"{safe_name}_variants.fasta")
    with open(fasta_file, 'w') as f:
        for variant in variants:
            robo_variants = [id for id in variant.get('equivalent_identifiers', []) 
                           if id.startswith('ROBO_VARIANT:')]
            for robo_variant in robo_variants:
                fasta_seq = fetch_fasta_for_robo_variant(robo_variant)
                if fasta_seq:
                    f.write(fasta_seq + '\n')
    
    # Convert FASTA to FASTQ using art_illumina
    reads_prefix = os.path.join(graph_dir, f"{safe_name}_reads")
    subprocess.run([
        'art_illumina', '-ss', 'HS25', '-i', fasta_file, 
        '-l', '150', '-f', '10', '-o', reads_prefix
    ], check=True)
    
    # Build VG graph
    graph_file = os.path.join(graph_dir, f"{safe_name}_graph.vg")
    subprocess.run([
        'vg', 'construct', '-r', fasta_file, '-o', graph_file
    ], check=True)
    
    # Create indexes
    xg_file = os.path.join(graph_dir, f"{safe_name}_graph.xg")
    subprocess.run([
        'vg', 'index', '-x', xg_file, graph_file
    ], check=True)
    
    # Align reads to graph
    alignments_file = os.path.join(graph_dir, f"{safe_name}_alignments.gam")
    reads1_file = f"{reads_prefix}1.fq"
    reads2_file = f"{reads_prefix}2.fq"
    
    # Create GCSA index for alignment
    pruned_file = os.path.join(graph_dir, f"{safe_name}_pruned.vg")
    gcsa_file = os.path.join(graph_dir, f"{safe_name}_gcsa.gcsa")
    
    subprocess.run(['vg', 'prune', graph_file], 
                  stdout=open(pruned_file, 'w'), check=True)
    subprocess.run(['vg', 'index', '-g', gcsa_file, '-k', '16', pruned_file], 
                  check=True)
    
    # Perform alignment
    subprocess.run([
        'vg', 'map', '-x', xg_file, '-g', gcsa_file, 
        '-f', reads1_file, '-f', reads2_file
    ], stdout=open(alignments_file, 'w'), check=True)
    
    return graph_file

# Usage
graph_file = create_disease_variant_graph("sickle cell disease")
print(f"Created variant graph: {graph_file}")
```

### 5. Running Tests

```bash
python scripts/test_disease_resolver.py
```

This will run a comprehensive test suite including:
- Single disease resolution
- CURIE-only extraction
- Multiple disease processing
- TCGA cancer type resolution
- API response structure inspection

## API Integration

### Complete Disease-to-Variants Pipeline

```python
from scripts.variant_resolver import resolve_disease_to_variants

# Complete pipeline in one call
variants = resolve_disease_to_variants("sickle cell disease")

for variant in variants:
    print(f"Variant: {variant['name']} (ID: {variant['id']})")
    print(f"RS ID: {variant['name']}")
    for identifier in variant['equivalent_identifiers']:
        if identifier.startswith('DBSNP:'):
            print(f"dbSNP: {identifier}")
        elif identifier.startswith('HGVS:'):
            print(f"HGVS: {identifier}")
```

### DiseaseResolver Class

```python
from scripts.disease_resolver import DiseaseResolver

# Initialize resolver
resolver = DiseaseResolver()

# Resolve a single disease
result = resolver.resolve_disease("breast cancer")
print(result['curie'])  # Output: MONDO:0007254

# Get only the CURIE (full MONDO identifier)
curie = resolver.get_curie_only("lung cancer")
print(curie)  # Output: MONDO:0008903

# Resolve multiple diseases
diseases = ["breast cancer", "lung cancer", "melanoma"]
results = resolver.resolve_multiple_diseases(diseases)

for disease, result in results.items():
    if result:
        print(f"{disease}: {result['curie']}")
```

### API Parameters

The Name Resolution Service API accepts the following parameters:

- **`string`** (required): Disease name to search for
- **`autocomplete`**: Enable autocomplete matching (default: true)
- **`highlighting`**: Enable result highlighting (default: false)
- **`offset`**: Pagination offset (default: 0)
- **`limit`**: Maximum results to return (default: 10)

### Response Structure

The API returns a complex nested JSON structure. The script recursively searches through all objects to find those with MONDO CURIEs. A typical MONDO result has this structure:

```json
{
  "curie": "MONDO:0007254",
  "label": "breast carcinoma",
  "score": 3208.0525,
  "types": ["biolink:Disease"],
  "synonyms": ["breast cancer", "carcinoma of breast", ...],
  "taxon": null,
  "description": "A carcinoma that arises from epithelial cells of the breast"
}
```

### Improved JSON Parsing

The script now uses recursive parsing to handle the complex nested structure of the API response, ensuring all MONDO identifiers are found regardless of their position in the JSON hierarchy.

## Command-Line Options

### disease_resolver.py

```
positional arguments:
  disease              Disease name to resolve

optional arguments:
  --limit LIMIT        Maximum number of results (default: 10)
  --offset OFFSET      Result offset for pagination (default: 0)
  --no-autocomplete    Disable autocomplete matching
  --highlighting       Enable result highlighting
  --json               Output full result as JSON
  --curie-only         Output only the CURIE/MONDO ID
  --verbose            Enable verbose logging
```

### variant_resolver.py

```
required arguments (mutually exclusive):
  --mondo MONDO_ID     MONDO ID to query (e.g., "MONDO:0011382")
  --disease DISEASE    Disease name to resolve and query

optional arguments:
  --json               Output full results as JSON
  --robo-only          Output only ROBO_VARIANT identifiers
  --fasta-only         Fetch and output FASTA sequences (with 100bp padding)
  --limit LIMIT        Limit number of variants to display
  --verbose            Enable verbose logging
```

### batch_disease_resolver.py

```
required arguments:
  --input, -i FILE     Input file with disease names (one per line)
  --diseases, -d ...   List of disease names
  --output, -o FILE    Output file path

optional arguments:
  --format, -f {json,csv}  Output format (default: json)
  --verbose, -v            Enable verbose logging
```

## Input File Format

The input file for batch processing should contain one disease name per line:

```text
# Comments start with #
breast cancer
lung cancer
colorectal adenocarcinoma

# Empty lines are ignored
pancreatic cancer
```

## Integration with GIRAFFE Pipeline

These scripts can be integrated into the GIRAFFE knowledge graph pipeline to:

1. **Normalize disease names** from TCGA samples
2. **Map variants to standardized disease ontologies**
3. **Enrich knowledge graph** with MONDO identifiers
4. **Discover disease-associated genetic variants** from GWAS data
5. **Extract genomic sequences** with TogoWS API integration
6. **Generate variant graphs** using VG toolkit
7. **Enable semantic queries** across disease concepts and variants

### Example Integration

```python
from knowledge_graph import GiraffeKnowledgeGraph
from scripts.disease_resolver import DiseaseResolver
from scripts.variant_resolver import VariantResolver, resolve_disease_to_variants

# Initialize components
kg = GiraffeKnowledgeGraph()
disease_resolver = DiseaseResolver()
variant_resolver = VariantResolver()

# Process TCGA sample with disease resolution
sample_data = {
    'sample_id': 'TCGA-A1-A0SB',
    'cancer_type': 'Breast Invasive Carcinoma',
    'mutations': [...]
}

# Resolve disease to MONDO ID
mondo_result = disease_resolver.resolve_disease(sample_data['cancer_type'])

if mondo_result:
    # Add disease to knowledge graph
    disease_id = f"disease_{mondo_result['curie'].replace(':', '_')}"
    kg.add_entity(disease_id, "disease", {
        'name': sample_data['cancer_type'],
        'mondo_id': mondo_result['curie'],
        'mondo_label': mondo_result['label'],
        'ontology': 'MONDO'
    })
    
    # Get associated variants from GWAS
    variants = variant_resolver.get_variants_for_mondo(mondo_result['curie'])
    
    # Add variants to knowledge graph
    for variant in variants:
        variant_id = f"variant_{variant['id'].replace(':', '_')}"
        kg.add_entity(variant_id, "variant", {
            'name': variant.get('name'),
            'caid_id': variant['id'],
            'equivalent_identifiers': variant.get('equivalent_identifiers', [])
        })
        
        # Create relationship between disease and variant
        kg.add_relationship(
            disease_id, variant_id, "associated_with",
            {'source': 'GWAS_Catalog', 'evidence_type': 'statistical_association'}
        )
        
        # Optionally fetch genomic sequences
        robo_variants = [id for id in variant.get('equivalent_identifiers', []) 
                        if id.startswith('ROBO_VARIANT:')]
        
        for robo_variant in robo_variants:
            from scripts.variant_resolver import fetch_fasta_for_robo_variant
            fasta_sequence = fetch_fasta_for_robo_variant(robo_variant)
            if fasta_sequence:
                # Add sequence data to variant entity
                kg.entities[variant_id]['properties']['fasta_sequence'] = fasta_sequence
                kg.entities[variant_id]['properties']['sequence_source'] = 'TogoWS_UCSC'
```

## Error Handling

The scripts include comprehensive error handling for:

- Network failures
- Invalid API responses
- Missing data
- Malformed JSON
- File I/O errors

All errors are logged with appropriate detail levels.

## Logging

Configure logging verbosity with the `--verbose` flag:

```bash
# Normal logging (INFO level)
python scripts/disease_resolver.py "breast cancer"

# Verbose logging (DEBUG level)
python scripts/disease_resolver.py "breast cancer" --verbose
```

## Performance

- **API Rate Limits**: No explicit rate limits documented
- **Timeout**: 10 seconds per request
- **Caching**: Not implemented (add if needed for production)
- **Batch Size**: No hard limit, but recommend < 100 per batch

## Troubleshooting

### No results found

```bash
# Try without autocomplete
python scripts/disease_resolver.py "rare disease" --no-autocomplete

# Increase result limit
python scripts/disease_resolver.py "rare disease" --limit 20

# Check API response structure
python scripts/disease_resolver.py "disease name" --json
```

### API connection errors

- Check internet connectivity
- Verify API endpoint is accessible
- Check for firewall/proxy issues

### Unexpected results

- Verify disease name spelling
- Try alternative disease names
- Check synonyms in full JSON output

## Future Enhancements

- [ ] Add caching for repeated queries
- [ ] Implement retry logic with exponential backoff
- [ ] Support additional ontologies (DOID, HPO, etc.)
- [ ] Add fuzzy matching for misspelled names
- [ ] Parallel processing for large batches
- [ ] Export to additional formats (Excel, RDF, etc.)

## API Endpoints

### Name Resolution Service
- **Base URL**: https://name-resolution-sri.renci.org/lookup
- **Purpose**: Resolve disease names to MONDO identifiers
- **Method**: GET with query parameters

### GWAS Catalog (Automat)
- **Base URL**: https://automat.renci.org/gwas-catalog/cypher
- **Purpose**: Query disease-variant associations
- **Method**: POST with Cypher queries
- **Query Format**: `MATCH (disease{id:"MONDO:XXXXX"})--(sequence_variant:\`biolink:SequenceVariant\`) RETURN sequence_variant`

### TogoWS UCSC API
- **Base URL**: https://togows.org/api/ucsc
- **Purpose**: Fetch genomic sequences
- **Method**: GET
- **URL Format**: `https://togows.org/api/ucsc/{genome}/chr{chromosome}:{start}-{end}.fasta`
- **Example**: `https://togows.org/api/ucsc/hg38/chr11:5008372-5008573.fasta`

## References

- **Name Resolution Service**: https://name-resolution-sri.renci.org
- **MONDO**: https://mondo.monarchinitiative.org/
- **Biolink Model**: https://biolink.github.io/biolink-model/
- **GWAS Catalog**: https://www.ebi.ac.uk/gwas/
- **TogoWS**: http://togows.org/
- **UCSC Genome Browser**: https://genome.ucsc.edu/

---

*Part of the GIRAFFE Agent Knowledge Graph project*
