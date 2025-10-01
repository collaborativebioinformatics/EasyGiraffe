┌─────────────────────────────────────────────────────┐
│           Data Ingestion Layer                      │
│  Reference FASTA + VCF/GFF + Assembly Data          │
└──────────────────┬──────────────────────────────────┘
                   │
         ┌─────────▼──────────┐
         │  S3 Raw Data       │
         │  - FASTA files     │
         │  - VCF files       │
         │  - GTF/GFF         │
         │  - FASTQ reads     │
         └─────────┬──────────┘
                   │
         ┌─────────▼──────────────────┐
         │  EC2/Batch Processing      │
         │  VG Pipeline               │
         │  ┌──────────────────────┐  │
         │  │ vg autoindex        │  │
         │  │ vg construct        │  │
         │  │ vg rna (splicing)   │  │
         │  │ vg giraffe (map)    │  │
         │  │ vg call (variants)  │  │
         │  └──────────────────────┘  │
         └─────────┬──────────────────┘
                   │
    ┌──────────────┴────────────────┐
    │                               │
┌───▼─────────────┐        ┌────────▼─────────┐
│  S3 VG Output   │        │  Neptune Graph   │
│  - .gbz graphs  │◄──────►│  Knowledge Layer │
│  - .xg indexes  │ sync   │                  │
│  - .gam aligns  │        │ - Gene nodes     │
│  - .gfa export  │        │ - Path metadata  │
└───┬─────────────┘        │ - Annotations    │
    │                      │ - Sample info    │
    │                      └────────┬─────────┘
    │                               │
    └──────────────┬────────────────┘
                   │
         ┌─────────▼──────────────┐
         │   AWS Bedrock AI       │
         │   ┌────────────────┐   │
         │   │ Claude 3.5     │   │
         │   │ - Query gen    │   │
         │   │ - Analysis     │   │
         │   │ Titan Embed    │   │
         │   │ - Path vectors │   │
         │   └────────────────┘   │
         └─────────┬──────────────┘
                   │
         ┌─────────▼──────────────┐
         │   API Gateway          │
         │   + Lambda Functions   │
         └─────────┬──────────────┘
                   │
         ┌─────────▼──────────────┐
         │   Application Layer    │
         │   - Variant Browser    │
         │   - Alignment Viewer   │
         │   - Graph Viz          │
         └────────────────────────┘