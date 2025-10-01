# GIRAFFE Agent AWS Architecture - Visual Flow

## Complete Pipeline Flow Chart

```mermaid
flowchart TD
    subgraph DataIngestion["📥 Data Ingestion Layer"]
        A[Reference FASTA + VCF/GFF<br/>+ Assembly Data]
    end
    
    subgraph S3Raw["☁️ S3 Raw Data Storage"]
        B1[FASTA files]
        B2[VCF files]
        B3[GTF/GFF annotations]
        B4[FASTQ reads]
    end
    
    subgraph VGProcessing["⚙️ EC2/Batch Processing - VG Pipeline"]
        C1[vg autoindex<br/>Build graph indexes]
        C2[vg construct<br/>Create variation graphs]
        C3[vg rna<br/>Handle splicing]
        C4[vg giraffe<br/>Mapping reads]
        C5[vg call<br/>Call variants]
    end
    
    subgraph S3Output["💾 S3 VG Output Storage"]
        D1[.gbz graphs]
        D2[.xg indexes]
        D3[.gam alignments]
        D4[.gfa exports]
    end
    
    subgraph Neptune["🔷 Neptune Graph Database"]
        E1[Gene nodes]
        E2[Path metadata]
        E3[Annotations]
        E4[Sample information]
    end
    
    subgraph Bedrock["🤖 AWS Bedrock AI"]
        F1[Claude 3.5<br/>Query generation & Analysis]
        F2[Titan Embeddings<br/>Path vectors]
    end
    
    subgraph API["🌐 API Gateway + Lambda"]
        G[REST API Endpoints]
    end
    
    subgraph Application["💻 Application Layer"]
        H1[Variant Browser]
        H2[Alignment Viewer]
        H3[Graph Visualization]
    end
    
    A --> B1 & B2 & B3 & B4
    B1 & B2 & B3 & B4 --> C1
    C1 --> C2 --> C3 --> C4 --> C5
    
    C5 --> D1 & D2 & D3 & D4
    D1 & D2 & D3 & D4 -.sync.-> E1
    D1 & D2 & D3 & D4 --> E2 & E3 & E4
    
    E1 & E2 & E3 & E4 --> F1 & F2
    F1 & F2 --> G
    G --> H1 & H2 & H3
    
    style DataIngestion fill:#e1f5fe
    style S3Raw fill:#fff3e0
    style VGProcessing fill:#f3e5f5
    style S3Output fill:#e8f5e9
    style Neptune fill:#e0f2f1
    style Bedrock fill:#fce4ec
    style API fill:#f1f8e9
    style Application fill:#fff9c4
```

## Detailed Architecture Diagram

```mermaid
graph TB
    subgraph Input["Data Sources"]
        direction LR
        IN1[🧬 Reference Genome<br/>FASTA]
        IN2[📊 Variants<br/>VCF]
        IN3[📋 Annotations<br/>GTF/GFF]
        IN4[🔬 Sequencing Reads<br/>FASTQ]
    end
    
    subgraph Storage1["S3 Raw Data Bucket"]
        S3A[s3://giraffe-raw-data/]
    end
    
    subgraph Compute["EC2/AWS Batch - VG Pipeline"]
        direction TB
        VG1[vg autoindex]
        VG2[vg construct]
        VG3[vg rna]
        VG4[vg giraffe]
        VG5[vg call]
        VG1 --> VG2 --> VG3 --> VG4 --> VG5
    end
    
    subgraph Storage2["S3 Output Bucket"]
        S3B[s3://giraffe-output/]
        OUT1[Graph Files .gbz]
        OUT2[Index Files .xg]
        OUT3[Alignments .gam]
        OUT4[GFA Exports .gfa]
    end
    
    subgraph KG["Neptune Knowledge Graph"]
        direction TB
        N1[(Genes)]
        N2[(Variants)]
        N3[(Paths)]
        N4[(Samples)]
        N5[(Annotations)]
        N1 --- N2
        N2 --- N3
        N3 --- N4
        N4 --- N5
    end
    
    subgraph AI["AWS Bedrock - AI Layer"]
        direction LR
        AI1[🧠 Claude 3.5 Sonnet<br/>NL Query Processing<br/>Variant Analysis]
        AI2[🔢 Titan Embeddings<br/>Semantic Search<br/>Path Similarity]
    end
    
    subgraph Backend["API & Compute"]
        direction TB
        API1[API Gateway]
        LM1[Lambda: Query Handler]
        LM2[Lambda: Variant Lookup]
        LM3[Lambda: Graph Query]
        API1 --> LM1 & LM2 & LM3
    end
    
    subgraph Frontend["User Interface"]
        UI1[🌐 Variant Browser]
        UI2[🔍 Alignment Viewer]
        UI3[📊 Graph Visualizer]
        UI4[💬 Chat Interface]
    end
    
    IN1 & IN2 & IN3 & IN4 --> S3A
    S3A --> Compute
    Compute --> S3B
    S3B --> OUT1 & OUT2 & OUT3 & OUT4
    OUT1 & OUT2 & OUT3 & OUT4 --> KG
    KG <--> AI
    AI <--> Backend
    Backend <--> Frontend
    
    style Input fill:#e3f2fd
    style Storage1 fill:#fff8e1
    style Compute fill:#f3e5f5
    style Storage2 fill:#e8f5e9
    style KG fill:#e0f2f1
    style AI fill:#fce4ec
    style Backend fill:#f1f8e9
    style Frontend fill:#fff3e0
```

## Sequential Processing Flow

```mermaid
sequenceDiagram
    actor User
    participant UI as Application UI
    participant API as API Gateway
    participant Lambda as Lambda Functions
    participant Bedrock as AWS Bedrock
    participant Neptune as Neptune Graph
    participant S3 as S3 Storage
    participant VG as VG Pipeline
    
    Note over User,VG: Data Processing Phase
    User->>S3: Upload genomic data
    S3->>VG: Trigger processing
    VG->>VG: vg autoindex
    VG->>VG: vg construct
    VG->>VG: vg rna (splicing)
    VG->>VG: vg giraffe (mapping)
    VG->>VG: vg call (variants)
    VG->>S3: Store graph outputs
    S3->>Neptune: Sync graph data
    Neptune->>Neptune: Build knowledge graph
    
    Note over User,VG: Query Phase
    User->>UI: Enter natural language query
    UI->>API: Forward query
    API->>Lambda: Route request
    Lambda->>Bedrock: Process with Claude
    Bedrock->>Bedrock: Generate structured query
    Bedrock->>Neptune: Execute graph query
    Neptune->>Bedrock: Return results
    Bedrock->>Bedrock: Generate embeddings
    Bedrock->>Lambda: Formatted response
    Lambda->>API: Return data
    API->>UI: Display results
    UI->>User: Show visualization
```

## Component Interaction Diagram

```mermaid
graph LR
    subgraph AWS["AWS Cloud Infrastructure"]
        subgraph Storage["Data Storage"]
            S3R[S3 Raw]
            S3O[S3 Output]
            NEP[Neptune DB]
        end
        
        subgraph Processing["Compute"]
            EC2[EC2/Batch<br/>VG Pipeline]
            LBD[Lambda<br/>Functions]
        end
        
        subgraph AI["AI Services"]
            BR1[Claude 3.5]
            BR2[Titan Embed]
        end
        
        subgraph Interface["Gateway"]
            APG[API Gateway]
        end
    end
    
    subgraph External["External Access"]
        WEB[Web Application]
        CLI[CLI Tools]
        SDK[SDKs]
    end
    
    S3R --> EC2
    EC2 --> S3O
    S3O --> NEP
    NEP <--> BR1
    NEP <--> BR2
    BR1 <--> LBD
    BR2 <--> LBD
    LBD <--> APG
    APG <--> WEB
    APG <--> CLI
    APG <--> SDK
    
    style Storage fill:#e8f5e9
    style Processing fill:#f3e5f5
    style AI fill:#fce4ec
    style Interface fill:#fff9c4
    style External fill:#e1f5fe
```

## Data Flow by Stage

```mermaid
flowchart LR
    subgraph Stage1["Stage 1: Ingestion"]
        A1[Raw Genomic Data]
    end
    
    subgraph Stage2["Stage 2: Graph Construction"]
        B1[VG Build]
        B2[Index Creation]
    end
    
    subgraph Stage3["Stage 3: Mapping"]
        C1[Read Alignment]
        C2[Variant Calling]
    end
    
    subgraph Stage4["Stage 4: Knowledge Graph"]
        D1[Graph Population]
        D2[Relationship Building]
    end
    
    subgraph Stage5["Stage 5: AI Enhancement"]
        E1[Embedding Generation]
        E2[Semantic Indexing]
    end
    
    subgraph Stage6["Stage 6: Query & Analysis"]
        F1[User Queries]
        F2[AI-Powered Insights]
    end
    
    A1 ==> B1
    B1 ==> B2
    B2 ==> C1
    C1 ==> C2
    C2 ==> D1
    D1 ==> D2
    D2 ==> E1
    E1 ==> E2
    E2 ==> F1
    F1 ==> F2
    
    style Stage1 fill:#e3f2fd
    style Stage2 fill:#f3e5f5
    style Stage3 fill:#e8f5e9
    style Stage4 fill:#e0f2f1
    style Stage5 fill:#fce4ec
    style Stage6 fill:#fff9c4
```

## Technology Stack Overview

```mermaid
mindmap
  root((GIRAFFE<br/>Agent))
    Storage
      S3 Buckets
        Raw Data
        Processed Output
      Neptune Graph DB
        Nodes
        Edges
        Queries
    Compute
      EC2 Instances
      AWS Batch
        VG Tools
          autoindex
          construct
          giraffe
          call
    AI/ML
      AWS Bedrock
        Claude 3.5
          NLP
          Analysis
        Titan
          Embeddings
          Vectors
    API
      API Gateway
      Lambda Functions
        Query Handler
        Data Retriever
        Format Converter
    Frontend
      Web Interface
        Variant Browser
        Alignment Viewer
        Graph Viz
      Chat Interface
        Natural Language
        AI Responses
```

---

## Key Features Illustrated

### 🔄 **Bidirectional Sync**
S3 Output ↔ Neptune Graph ensures data consistency

### 🤖 **AI Integration**
Claude 3.5 processes natural language queries and generates insights

### 📊 **Multi-Format Support**
`.gbz`, `.xg`, `.gam`, `.gfa` - comprehensive VG output handling

### 🔍 **Semantic Search**
Titan Embeddings enable intelligent path and variant discovery

### 🌐 **REST API**
Standard API Gateway + Lambda for scalable access

### 💻 **Rich UI**
Multiple specialized viewers for different data types

---

*All diagrams are rendered using Mermaid syntax and can be viewed in GitHub, VS Code, or any Mermaid-compatible viewer.*
