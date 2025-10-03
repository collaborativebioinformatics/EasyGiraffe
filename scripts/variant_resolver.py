"""
Variant Resolver Script
Queries the GWAS Catalog API to find sequence variants associated with MONDO disease identifiers
"""

import requests
import json
import argparse
import logging
from typing import Optional, Dict, List, Any
import subprocess
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VariantResolver:
    """
    Resolver for MONDO IDs to sequence variants using the GWAS Catalog API
    """
    
    def __init__(self, base_url: str = "https://automat.renci.org/gwas-catalog/cypher"):
        """
        Initialize the variant resolver
        
        Args:
            base_url: Base URL for the GWAS catalog cypher endpoint
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def get_variants_for_mondo(self, mondo_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get sequence variants associated with a MONDO disease ID
        
        Args:
            mondo_id: MONDO identifier (e.g., "MONDO:0011382")
            
        Returns:
            List of sequence variant dictionaries, or None if not found
        """
        try:
            # Construct the Cypher query
            query = f'MATCH (disease{{id:"{mondo_id}"}})--(sequence_variant:`biolink:SequenceVariant`) RETURN sequence_variant'
            
            payload = {
                "query": query
            }
            
            logger.info(f"Querying variants for MONDO ID: {mondo_id}")
            
            # Make the API request
            response = self.session.post(self.base_url, json=payload, timeout=30)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Extract sequence variants from the response
            variants = self._extract_variants(data)
            
            if variants:
                logger.info(f"Found {len(variants)} sequence variants for {mondo_id}")
            else:
                logger.warning(f"No sequence variants found for {mondo_id}")
            
            return variants
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    def _extract_variants(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract sequence variants from the API response
        
        Args:
            data: Raw API response data
            
        Returns:
            List of sequence variant dictionaries
        """
        variants = []
        
        try:
            # Parse the GWAS API response structure
            if isinstance(data, dict) and 'results' in data:
                results = data['results']
                
                for result in results:
                    if 'data' in result:
                        # Each data item contains rows with variant information
                        for data_item in result['data']:
                            if 'row' in data_item and data_item['row']:
                                # The first item in the row is the sequence_variant
                                variant = data_item['row'][0]
                                if variant and isinstance(variant, dict):
                                    variants.append(variant)
                
        except Exception as e:
            logger.error(f"Error extracting variants: {e}")
        
        return variants
    
    def _find_variants_recursive(self, obj: Any, variants: List[Dict[str, Any]]):
        """
        Recursively search for sequence variant data in the response
        
        Args:
            obj: Object to search
            variants: List to append found variants to
        """
        if isinstance(obj, dict):
            # Check if this looks like a sequence variant
            if 'id' in obj and any(key in obj for key in ['chromosome', 'position', 'allele', 'rsid']):
                variants.append(obj)
            
            # Recursively search in all values
            for value in obj.values():
                self._find_variants_recursive(value, variants)
                
        elif isinstance(obj, list):
            # Recursively search in all list items
            for item in obj:
                self._find_variants_recursive(item, variants)

def fetch_fasta_for_robo_variant(robo_variant: str, padding: int = 100) -> Optional[str]:
    """
    Fetch FASTA sequence for a ROBO_VARIANT from TogoWS API
    
    Args:
        robo_variant: ROBO_VARIANT identifier (e.g., "ROBO_VARIANT:HG38|2|60492834|60492835|C|A")
        padding: Number of base pairs to add on each side (default: 100)
        
    Returns:
        FASTA sequence string, or None if failed
    """
    try:
        # Parse ROBO_VARIANT format: ROBO_VARIANT:HG38|chromosome|start|end|ref|alt
        parts = robo_variant.split('|')
        if len(parts) < 4:
            logger.error(f"Invalid ROBO_VARIANT format: {robo_variant}")
            return None
        
        hg_version = parts[0].split(':')[1].lower()  # HG38 -> hg38
        chromosome = parts[1]
        start_pos = int(parts[2])
        end_pos = int(parts[3])
        
        # Add padding
        padded_start = max(1, start_pos - padding)  # Ensure position is at least 1
        padded_end = end_pos + padding
        
        # Construct TogoWS API URL
        url = f"https://togows.org/api/ucsc/{hg_version}/chr{chromosome}:{padded_start}-{padded_end}.fasta"
        
        logger.info(f"Fetching FASTA for {robo_variant} from {url}")
        
        # Make API request
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        return response.text.strip()
        
    except ValueError as e:
        logger.error(f"Error parsing ROBO_VARIANT positions: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"TogoWS API request failed for {robo_variant}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching FASTA for {robo_variant}: {e}")
        return None

def resolve_disease_to_variants(disease_name: str) -> Optional[List[Dict[str, Any]]]:
    """
    Complete pipeline: resolve disease name to MONDO ID, then get variants
    
    Args:
        disease_name: Human-readable disease name
        
    Returns:
        List of sequence variants, or None if not found
    """
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        disease_resolver_path = os.path.join(script_dir, 'disease_resolver.py')
        
        # Call the disease resolver to get MONDO ID
        result = subprocess.run([
            sys.executable, disease_resolver_path, disease_name, '--curie-only'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            logger.error(f"Disease resolver failed: {result.stderr}")
            return None
        
        mondo_id = result.stdout.strip()
        if not mondo_id:
            logger.error("No MONDO ID returned from disease resolver")
            return None
        
        logger.info(f"Resolved '{disease_name}' to {mondo_id}")
        
        # Now get variants for this MONDO ID
        resolver = VariantResolver()
        variants = resolver.get_variants_for_mondo(mondo_id)
        
        return variants
        
    except subprocess.TimeoutExpired:
        logger.error("Disease resolver timed out")
        return None
    except Exception as e:
        logger.error(f"Error in disease-to-variants pipeline: {e}")
        return None

def main():
    """
    Main function for command-line usage
    """
    parser = argparse.ArgumentParser(
        description='Resolve MONDO IDs to sequence variants using GWAS Catalog',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python variant_resolver.py --mondo "MONDO:0011382"
  python variant_resolver.py --disease "sickle cell disease"
  python variant_resolver.py --mondo "MONDO:0007254" --json
  python variant_resolver.py --disease "breast cancer" --limit 5
  python variant_resolver.py --disease "sickle cell disease" --robo-only
  python variant_resolver.py --mondo "MONDO:0011382" --fasta-only
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--mondo',
        type=str,
        help='MONDO ID to query (e.g., "MONDO:0011382")'
    )
    input_group.add_argument(
        '--disease',
        type=str,
        help='Disease name to resolve and query (e.g., "sickle cell disease")'
    )
    
    # Output options
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output full results as JSON'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of variants to display'
    )
    
    parser.add_argument(
        '--robo-only',
        action='store_true',
        help='Output only ROBO_VARIANT identifiers'
    )
    
    parser.add_argument(
        '--fasta-only',
        action='store_true',
        help='Fetch and output FASTA sequences for ROBO_VARIANTs (with 100bp padding)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize resolver
    resolver = VariantResolver()
    
    # Get variants
    if args.mondo:
        variants = resolver.get_variants_for_mondo(args.mondo)
        query_info = f"MONDO ID: {args.mondo}"
    else:
        variants = resolve_disease_to_variants(args.disease)
        query_info = f"Disease: {args.disease}"
    
    # Output results
    if variants:
        if args.limit:
            variants = variants[:args.limit]
        
        if args.robo_only:
            # Extract and output only ROBO_VARIANT identifiers
            robo_variants = []
            for variant in variants:
                equivalent_ids = variant.get('equivalent_identifiers', [])
                for identifier in equivalent_ids:
                    if identifier.startswith('ROBO_VARIANT:'):
                        robo_variants.append(identifier)
            
            if robo_variants:
                for robo_variant in robo_variants:
                    print(robo_variant)
            else:
                logger.error("No ROBO_VARIANT identifiers found")
                exit(1)
        elif args.fasta_only:
            # Extract ROBO_VARIANTs and fetch FASTA sequences
            robo_variants = []
            for variant in variants:
                equivalent_ids = variant.get('equivalent_identifiers', [])
                for identifier in equivalent_ids:
                    if identifier.startswith('ROBO_VARIANT:'):
                        robo_variants.append(identifier)
            
            if robo_variants:
                for robo_variant in robo_variants:
                    fasta_sequence = fetch_fasta_for_robo_variant(robo_variant)
                    if fasta_sequence:
                        print(fasta_sequence)
            else:
                logger.error("No ROBO_VARIANT identifiers found")
                exit(1)
        elif args.json:
            print(json.dumps(variants, indent=2))
        else:
            print("\n" + "="*60)
            print(f"Sequence Variants for {query_info}")
            print("="*60)
            print(f"Found {len(variants)} variants:\n")
            
            for i, variant in enumerate(variants, 1):
                print(f"{i}. Variant ID: {variant.get('id', 'N/A')}")
                
                # Display common variant fields
                if 'chromosome' in variant:
                    print(f"   Chromosome: {variant['chromosome']}")
                if 'position' in variant:
                    print(f"   Position: {variant['position']}")
                if 'allele' in variant:
                    print(f"   Allele: {variant['allele']}")
                if 'rsid' in variant:
                    print(f"   RS ID: {variant['rsid']}")
                
                print()
            
            print("="*60)
    else:
        logger.error(f"No variants found for {query_info}")
        exit(1)

if __name__ == "__main__":
    main()