🧬 GIRAFFE Agent Pipeline: Flow Chart with Descriptions
1. Existing samples from TCGA
    Download cancer genome data and clinical information from The Cancer Genome Atlas (TCGA) for initial analysis.
2. Mapping those samples using GIRAFFE View tool
    Use the GIRAFFE View tool to align genome data and detect variations across multiple sites.
3. Identifying mutation locations (loci) in the genome
    Extract precise genomic positions where mutations occur in each sample.
4. Annotating those mutations using dbSNP
    Query the dbSNP database to enrich each mutation with rsID, frequency, gene info, and clinical significance.
5. Categorize the mapped data – Clustering Methods
    Group similar mutation profiles across samples using clustering techniques to find patterns.
6. Create a Knowledge Graph (KG) with the mapped data
    Build a graph connecting cancer types with specific genetic variants and their relationships using LLM agents (call it GIRAFFE Agent).
7. Eventually using the pipeline on new/unseen cancer genome data
    Apply the full pipeline to new cancer genome samples for rapid annotation, categorization, and insight generation.

