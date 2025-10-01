# GiraffeAgent2
Giraffe Agent -- Multisite polygenicity extraction from cancer genomes

flowchart TD
    Start([Start: Cancer Genome Analysis Pipeline]) --> Step1
    
    Step1[Step 1: Download TCGA Data<br/>Cancer genome data and<br/>clinical information] --> Step2
    
    Step2[Step 2: GIRAFFE View Mapping<br/>Align genome data and<br/>detect variations] --> Step3
    
    Step3[Step 3: Identify Mutation Loci<br/>Extract genomic positions<br/>of mutations] --> Step4
    
    Step4[Step 4: dbSNP Annotation<br/>Query for rsID, frequency,<br/>gene info, clinical significance] --> Step5
    
    Step5[Step 5: Clustering Analysis<br/>Group similar mutation profiles<br/>to find patterns] --> Step6
    
    Step6[Step 6: Knowledge Graph Creation<br/>Build KG with GIRAFFE Agent<br/>Connect cancer types, variants,<br/>and relationships] --> Pipeline
    
    Pipeline{Pipeline<br/>Complete?}
    
    Pipeline -->|Yes| Step7
    Pipeline -->|No| Review[Review & Refine]
    Review --> Step5
    
    Step7[Step 7: Apply to New Data<br/>Process unseen cancer<br/>genome samples] --> Analysis
    
    Analysis[Rapid Annotation,<br/>Categorization &<br/>Insight Generation] --> End
    
    End([End: Actionable Insights])
    
    style Start fill:#e1f5e1
    style Step1 fill:#fff4e6
    style Step2 fill:#e3f2fd
    style Step3 fill:#f3e5f5
    style Step4 fill:#fff9c4
    style Step5 fill:#fce4ec
    style Step6 fill:#e0f2f1
    style Step7 fill:#f1f8e9
    style Pipeline fill:#ffebee
    style Analysis fill:#e8eaf6
    style End fill:#e1f5e1
    
    classDef dataStep fill:#bbdefb,stroke:#1976d2,stroke-width:2px
    classDef processStep fill:#c5e1a5,stroke:#558b2f,stroke-width:2px
    classDef aiStep fill:#ffcc80,stroke:#e65100,stroke-width:2px
    
    class Step1,Step3,Step4 dataStep
    class Step2,Step5,Step7 processStep
    class Step6,Analysis aiStep
