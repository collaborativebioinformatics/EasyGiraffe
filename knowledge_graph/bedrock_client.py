"""
AWS Bedrock Configuration and Client Setup for GIRAFFE Agent Knowledge Graph
"""

import boto3
import json
import logging
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BedrockClient:
    """
    AWS Bedrock client for interacting with foundation models
    """
    
    def __init__(self, region_name: str = "us-east-1"):
        """
        Initialize Bedrock client
        
        Args:
            region_name: AWS region for Bedrock service
        """
        self.region_name = region_name
        self.bedrock_runtime = None
        self.bedrock_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Bedrock runtime and client"""
        try:
            # Initialize Bedrock Runtime client for model invocation
            self.bedrock_runtime = boto3.client(
                service_name='bedrock-runtime',
                region_name=self.region_name
            )
            
            # Initialize Bedrock client for model management
            self.bedrock_client = boto3.client(
                service_name='bedrock',
                region_name=self.region_name
            )
            
            logger.info(f"Successfully initialized Bedrock clients in region: {self.region_name}")
            
        except ClientError as e:
            logger.error(f"Failed to initialize Bedrock clients: {e}")
            raise
    
    def list_foundation_models(self) -> list:
        """
        List available foundation models
        
        Returns:
            List of available models
        """
        try:
            response = self.bedrock_client.list_foundation_models()
            return response.get('modelSummaries', [])
        except ClientError as e:
            logger.error(f"Error listing foundation models: {e}")
            return []
    
    def invoke_claude_3(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.1) -> str:
        """
        Invoke Claude 3 model for text generation
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text response
        """
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=json.dumps(body),
                contentType="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except ClientError as e:
            logger.error(f"Error invoking Claude 3: {e}")
            return ""
    
    def invoke_titan_embed(self, text: str) -> list:
        """
        Generate embeddings using Amazon Titan Embeddings
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector
        """
        try:
            body = {
                "inputText": text
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId="amazon.titan-embed-text-v1",
                body=json.dumps(body),
                contentType="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['embedding']
            
        except ClientError as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    def extract_entities_and_relationships(self, mutation_data: str) -> Dict[str, Any]:
        """
        Use Claude 3 to extract entities and relationships from mutation data
        
        Args:
            mutation_data: Raw mutation annotation data
            
        Returns:
            Dictionary containing extracted entities and relationships
        """
        prompt = f"""
        You are a genomics expert. Analyze the following mutation data and extract structured information.
        
        Mutation Data:
        {mutation_data}
        
        Please extract and return a JSON object with the following structure:
        {{
            "entities": [
                {{
                    "type": "gene|variant|disease|pathway|protein",
                    "name": "entity_name",
                    "id": "unique_identifier",
                    "properties": {{
                        "chromosome": "chr1",
                        "position": "12345",
                        "ref_allele": "A",
                        "alt_allele": "T",
                        "rsid": "rs123456",
                        "frequency": "0.01",
                        "clinical_significance": "pathogenic|benign|uncertain"
                    }}
                }}
            ],
            "relationships": [
                {{
                    "source": "entity_name_1",
                    "target": "entity_name_2",
                    "type": "associated_with|causes|regulates|interacts_with",
                    "properties": {{
                        "confidence": "high|medium|low",
                        "evidence": "literature|database|prediction"
                    }}
                }}
            ]
        }}
        
        Focus on extracting:
        1. Genes affected by mutations
        2. Variant information (SNPs, indels)
        3. Associated diseases or cancer types
        4. Pathways involved
        5. Protein effects
        6. Relationships between these entities
        
        Return only the JSON object, no additional text.
        """
        
        response = self.invoke_claude_3(prompt, max_tokens=4000, temperature=0.1)
        
        try:
            # Try to parse the JSON response
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response from Claude 3")
            return {"entities": [], "relationships": []}


def create_bedrock_client(region_name: str = "us-east-1") -> BedrockClient:
    """
    Factory function to create a Bedrock client
    
    Args:
        region_name: AWS region for Bedrock service
        
    Returns:
        Configured BedrockClient instance
    """
    return BedrockClient(region_name=region_name)


# Example usage and testing
if __name__ == "__main__":
    # Test the Bedrock client
    bedrock = create_bedrock_client()
    
    # List available models
    models = bedrock.list_foundation_models()
    print(f"Available models: {len(models)}")
    
    # Test entity extraction
    sample_mutation_data = """
    Gene: BRCA1
    Chromosome: 17
    Position: 41234470
    Reference Allele: A
    Alternate Allele: G
    rsID: rs80357382
    Clinical Significance: Pathogenic
    Disease Association: Breast Cancer, Ovarian Cancer
    Population Frequency: 0.0001
    """
    
    entities_relationships = bedrock.extract_entities_and_relationships(sample_mutation_data)
    print("Extracted entities and relationships:")
    print(json.dumps(entities_relationships, indent=2))