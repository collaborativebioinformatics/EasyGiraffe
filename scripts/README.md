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

### 4. Running Tests

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
6. **Enable semantic queries** across disease concepts and variants

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
