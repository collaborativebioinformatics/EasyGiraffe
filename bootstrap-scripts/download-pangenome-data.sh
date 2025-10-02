#!/bin/bash
set -euo pipefail

# Output directory
OUTDIR="./hprc_mc_data"
mkdir -p "$OUTDIR"

# Base S3 path
S3_PATH="s3://human-pangenomics/pangenomes/freeze/freeze1/minigraph-cactus/filtered"

# Download files
aws s3 cp $S3_PATH "$OUTDIR" \
  --no-sign-request --recursive \
  --exclude "*" \
  --include "hprc-v1.0-mc-grch38-minaf.0.1.dist" \
  --include "hprc-v1.0-mc-grch38-minaf.0.1.gg" \
  --include "hprc-v1.0-mc-grch38-minaf.0.1.min" \
  --include "hprc-v1.0-mc-grch38-minaf.0.1.xg"

echo "✅ Download complete. Files saved in $OUTDIR"
