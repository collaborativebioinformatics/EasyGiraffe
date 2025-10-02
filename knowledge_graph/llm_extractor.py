"""
GIRAFFE Agent LLM-Powered Entity and Relationship Extraction
Advanced natural language processing using Amazon Bedrock for genomics knowledge extraction
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import re
from .bedrock_client import BedrockClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenomicsEntityExtractor:
    """
    Advanced entity and relationship extraction for genomics data using LLMs
    """
    
    def __init__(self, bedrock_client: BedrockClient):
        """
        Initialize the extractor with Bedrock client
        
        Args:
            bedrock_client: Configured Bedrock client
        """
        self.bedrock_client = bedrock_client
        
        # Genomics-specific entity types and their properties
        self.entity_schemas = {
            "gene": {
                "required": ["symbol"],
                "optional": ["full_name", "chromosome", "start_pos", "end_pos", "strand", "function"]
            },
            "variant": {
                "required": ["chromosome", "position"],
                "optional": ["ref_allele", "alt_allele", "rsid", "type", "consequence"]
            },
            "disease": {
                "required": ["name"],
                "optional": ["category", "icd_code", "inheritance_pattern", "prevalence"]
            },
            "protein": {
                "required": ["name"],
                "optional": ["uniprot_id", "domain", "function", "molecular_weight"]
            },
            "pathway": {
                "required": ["name"],
                "optional": ["database_id", "category", "organism", "key_proteins"]
            },
            "drug": {
                "required": ["name"],
                "optional": ["mechanism", "target", "indication", "side_effects"]
            }
        }
        
        # Relationship types with their semantic meanings
        self.relationship_types = {
            "causes": "Direct causal relationship",
            "associated_with": "Statistical or observed association",
            "regulates": "Gene regulation relationship",
            "interacts_with": "Physical or functional interaction",
            "located_in": "Physical location relationship",
            "encodes": "Gene-protein encoding relationship",
            "participates_in": "Involvement in biological process",
            "treats": "Therapeutic relationship",
            "targets": "Drug-target relationship",
            "mutated_in": "Mutation occurrence in condition"
        }
    
    def extract_entities_from_literature(self, literature_text: str) -> Dict[str, Any]:
        """
        Extract genomics entities from literature or research abstracts
        
        Args:
            literature_text: Scientific literature text
            
        Returns:
            Dictionary containing extracted entities and relationships
        """
        prompt = f"""
        You are a genomics and bioinformatics expert. Analyze the following scientific text and extract structured genomics information.
        
        Text to analyze:
        {literature_text}
        
        Extract entities and relationships following this JSON schema:
        
        {{
            "entities": [
                {{
                    "id": "unique_identifier",
                    "type": "gene|variant|disease|protein|pathway|drug",
                    "name": "entity_name",
                    "properties": {{
                        // Type-specific properties based on entity type
                        "confidence": "high|medium|low",
                        "evidence_type": "experimental|computational|literature",
                        "source_sentence": "relevant_sentence_from_text"
                    }}
                }}
            ],
            "relationships": [
                {{
                    "source": "entity_id_1",
                    "target": "entity_id_2",
                    "type": "causes|associated_with|regulates|interacts_with|encodes|participates_in|treats|targets|mutated_in",
                    "properties": {{
                        "confidence": "high|medium|low",
                        "evidence": "specific_evidence_from_text",
                        "effect": "positive|negative|neutral",
                        "mechanism": "brief_mechanism_description"
                    }}
                }}
            ],
            "summary": "Brief summary of key genomics findings"
        }}
        
        Focus on extracting:
        1. Gene names and symbols
        2. Genetic variants (SNPs, mutations, CNVs)
        3. Diseases and phenotypes
        4. Proteins and their functions
        5. Biological pathways
        6. Therapeutic compounds
        7. Relationships between these entities
        
        Be precise with entity identification and relationship types. Only extract information that is explicitly mentioned or strongly implied in the text.
        
        Return only valid JSON, no additional text.
        """
        
        response = self.bedrock_client.invoke_claude_3(prompt, max_tokens=4000, temperature=0.1)
        
        try:
            result = json.loads(response)
            return self._validate_and_clean_extraction(result)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response for literature extraction")
            return {"entities": [], "relationships": [], "summary": ""}
    
    def extract_from_clinical_report(self, clinical_text: str) -> Dict[str, Any]:
        """
        Extract entities from clinical genomics reports
        
        Args:
            clinical_text: Clinical report text
            
        Returns:
            Dictionary containing extracted clinical genomics information
        """
        prompt = f"""
        You are a clinical genomics specialist. Analyze this clinical genomics report and extract structured information.
        
        Clinical Report:
        {clinical_text}
        
        Extract the following information in JSON format:
        
        {{
            "patient_info": {{
                "demographics": "age, gender, ethnicity if mentioned",
                "clinical_indication": "reason for testing",
                "family_history": "relevant family history"
            }},
            "variants": [
                {{
                    "id": "variant_identifier",
                    "gene": "gene_symbol",
                    "transcript": "transcript_id",
                    "hgvs_dna": "DNA_change_notation",
                    "hgvs_protein": "protein_change_notation",
                    "classification": "pathogenic|likely_pathogenic|vus|likely_benign|benign",
                    "evidence": "evidence_supporting_classification",
                    "inheritance": "inheritance_pattern",
                    "penetrance": "penetrance_information"
                }}
            ],
            "phenotypes": [
                {{
                    "name": "phenotype_name",
                    "hpo_term": "HPO_term_if_available",
                    "severity": "mild|moderate|severe",
                    "age_of_onset": "onset_information"
                }}
            ],
            "recommendations": [
                {{
                    "type": "surveillance|treatment|genetic_counseling|family_testing",
                    "description": "specific_recommendation",
                    "urgency": "immediate|routine|consider"
                }}
            ],
            "summary": "Clinical interpretation summary"
        }}
        
        Focus on extracting clinically actionable information and follow standard clinical genomics terminology.
        
        Return only valid JSON.
        """
        
        response = self.bedrock_client.invoke_claude_3(prompt, max_tokens=4000, temperature=0.1)
        
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response for clinical report extraction")
            return {"patient_info": {}, "variants": [], "phenotypes": [], "recommendations": [], "summary": ""}
    
    def extract_pathway_information(self, pathway_description: str) -> Dict[str, Any]:
        """
        Extract detailed pathway information and interactions
        
        Args:
            pathway_description: Description of biological pathway
            
        Returns:
            Structured pathway information
        """
        prompt = f"""
        You are a systems biology expert. Analyze this biological pathway description and extract detailed structural information.
        
        Pathway Description:
        {pathway_description}
        
        Extract information in this JSON format:
        
        {{
            "pathway": {{
                "name": "pathway_name",
                "category": "signaling|metabolic|regulatory|cell_cycle|dna_repair|apoptosis",
                "description": "brief_description",
                "key_functions": ["function1", "function2"],
                "diseases_associated": ["disease1", "disease2"]
            }},
            "components": [
                {{
                    "type": "protein|enzyme|receptor|transcription_factor|small_molecule",
                    "name": "component_name",
                    "role": "activator|inhibitor|substrate|product|regulator",
                    "location": "cellular_location",
                    "modifications": ["modification_types"]
                }}
            ],
            "interactions": [
                {{
                    "source": "component_name_1",
                    "target": "component_name_2",
                    "type": "phosphorylation|binding|transcription|degradation|transport",
                    "effect": "activation|inhibition|neutral",
                    "mechanism": "brief_mechanism",
                    "regulation": "constitutive|inducible|tissue_specific"
                }}
            ],
            "regulation": {{
                "upstream_signals": ["signal1", "signal2"],
                "downstream_effects": ["effect1", "effect2"],
                "feedback_loops": ["loop_description"],
                "crosstalk": ["pathway_crosstalk"]
            }}
        }}
        
        Be detailed about molecular interactions and regulatory mechanisms.
        
        Return only valid JSON.
        """
        
        response = self.bedrock_client.invoke_claude_3(prompt, max_tokens=4000, temperature=0.1)
        
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response for pathway extraction")
            return {"pathway": {}, "components": [], "interactions": [], "regulation": {}}
    
    def extract_drug_target_relationships(self, drug_info: str) -> Dict[str, Any]:
        """
        Extract drug-target relationships and mechanisms
        
        Args:
            drug_info: Information about drug and its targets
            
        Returns:
            Structured drug-target information
        """
        prompt = f"""
        You are a pharmacogenomics expert. Analyze this drug information and extract detailed target relationships.
        
        Drug Information:
        {drug_info}
        
        Extract information in this JSON format:
        
        {{
            "drug": {{
                "name": "drug_name",
                "generic_name": "generic_name",
                "class": "drug_class",
                "mechanism": "mechanism_of_action",
                "indications": ["indication1", "indication2"],
                "administration": "route_and_dosing"
            }},
            "targets": [
                {{
                    "type": "protein|enzyme|receptor|channel|transporter",
                    "name": "target_name",
                    "gene": "gene_symbol",
                    "interaction_type": "agonist|antagonist|inhibitor|activator|modulator",
                    "binding_site": "binding_location",
                    "affinity": "high|medium|low",
                    "selectivity": "selective|non_selective"
                }}
            ],
            "pharmacokinetics": {{
                "absorption": "absorption_info",
                "distribution": "distribution_info",
                "metabolism": "metabolic_pathways",
                "elimination": "elimination_route"
            }},
            "genomic_variants": [
                {{
                    "gene": "gene_symbol",
                    "variant": "variant_description",
                    "effect": "increased|decreased|altered_response",
                    "clinical_relevance": "dosing|efficacy|toxicity"
                }}
            ],
            "side_effects": [
                {{
                    "effect": "side_effect_name",
                    "frequency": "common|uncommon|rare",
                    "mechanism": "mechanism_if_known"
                }}
            ]
        }}
        
        Focus on clinically relevant pharmacogenomic relationships.
        
        Return only valid JSON.
        """
        
        response = self.bedrock_client.invoke_claude_3(prompt, max_tokens=4000, temperature=0.1)
        
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response for drug-target extraction")
            return {"drug": {}, "targets": [], "pharmacokinetics": {}, "genomic_variants": [], "side_effects": []}
    
    def generate_embeddings_for_entities(self, entities: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """
        Generate embeddings for entities using Titan Embeddings
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            Dictionary mapping entity IDs to embedding vectors
        """
        embeddings = {}
        
        for entity in entities:
            # Create text representation of entity
            entity_text = f"{entity.get('type', '')} {entity.get('name', '')}"
            
            # Add properties to text
            if 'properties' in entity:
                for key, value in entity['properties'].items():
                    entity_text += f" {key}: {value}"
            
            # Generate embedding
            try:
                embedding = self.bedrock_client.invoke_titan_embed(entity_text)
                embeddings[entity.get('id', entity.get('name', ''))] = embedding
            except Exception as e:
                logger.error(f"Failed to generate embedding for entity {entity.get('name', '')}: {e}")
        
        return embeddings
    
    def _validate_and_clean_extraction(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean extraction results
        
        Args:
            extraction_result: Raw extraction result
            
        Returns:
            Validated and cleaned result
        """
        cleaned_result = {
            "entities": [],
            "relationships": [],
            "summary": extraction_result.get("summary", "")
        }
        
        # Validate entities
        for entity in extraction_result.get("entities", []):
            if self._validate_entity(entity):
                cleaned_result["entities"].append(entity)
        
        # Validate relationships
        entity_ids = {e.get("id", e.get("name", "")) for e in cleaned_result["entities"]}
        
        for relationship in extraction_result.get("relationships", []):
            if self._validate_relationship(relationship, entity_ids):
                cleaned_result["relationships"].append(relationship)
        
        return cleaned_result
    
    def _validate_entity(self, entity: Dict[str, Any]) -> bool:
        """Validate entity structure"""
        required_fields = ["type", "name"]
        
        for field in required_fields:
            if field not in entity:
                logger.warning(f"Entity missing required field: {field}")
                return False
        
        # Check if entity type is valid
        if entity["type"] not in self.entity_schemas:
            logger.warning(f"Unknown entity type: {entity['type']}")
        
        return True
    
    def _validate_relationship(self, relationship: Dict[str, Any], valid_entity_ids: set) -> bool:
        """Validate relationship structure"""
        required_fields = ["source", "target", "type"]
        
        for field in required_fields:
            if field not in relationship:
                logger.warning(f"Relationship missing required field: {field}")
                return False
        
        # Check if relationship type is valid
        if relationship["type"] not in self.relationship_types:
            logger.warning(f"Unknown relationship type: {relationship['type']}")
        
        return True


# Example usage and testing functions
def test_literature_extraction():
    """Test literature extraction functionality"""
    sample_abstract = """
    BRCA1 and BRCA2 mutations are associated with hereditary breast and ovarian cancer syndrome.
    These genes encode proteins involved in DNA repair through homologous recombination.
    Pathogenic variants in BRCA1 (located on chromosome 17) and BRCA2 (chromosome 13) 
    significantly increase the risk of breast cancer by up to 80% and ovarian cancer by up to 40%.
    PARP inhibitors such as olaparib target BRCA-deficient tumors through synthetic lethality.
    The PI3K/AKT/mTOR pathway is frequently dysregulated in BRCA-associated cancers.
    """
    
    from .bedrock_client import create_bedrock_client
    
    bedrock_client = create_bedrock_client()
    extractor = GenomicsEntityExtractor(bedrock_client)
    
    result = extractor.extract_entities_from_literature(sample_abstract)
    
    print("Literature Extraction Results:")
    print(json.dumps(result, indent=2))
    
    return result


if __name__ == "__main__":
    # Run test
    test_literature_extraction()