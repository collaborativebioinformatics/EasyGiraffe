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