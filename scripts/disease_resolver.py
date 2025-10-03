"""
Disease Name to MONDO ID Resolver
Queries the Name Resolution Service API to find MONDO identifiers for disease names
"""

import requests
import json
import argparse
import logging
from typing import Optional, Dict, List, Any
from urllib.parse import quote

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DiseaseResolver:
    """
    Resolver for disease names to MONDO identifiers using the Name Resolution Service
    """
    
    def __init__(self, base_url: str = "https://name-resolution-sri.renci.org/lookup"):
        """
        Initialize the disease resolver
        
        Args:
            base_url: Base URL for the name resolution service
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GIRAFFE-Agent/1.0',
            'Accept': 'application/json'
        })
    
    def resolve_disease(self, 
                       disease_name: str, 
                       autocomplete: bool = True,
                       highlighting: bool = False,
                       offset: int = 0,
                       limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        Resolve a disease name to its MONDO identifier
        
        Args:
            disease_name: Full disease name to resolve
            autocomplete: Enable autocomplete matching
            highlighting: Enable result highlighting
            offset: Result offset for pagination
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing the highest scoring MONDO result, or None if not found
        """
        try:
            # Construct the query parameters
            params = {
                'string': disease_name,
                'autocomplete': str(autocomplete).lower(),
                'highlighting': str(highlighting).lower(),
                'offset': offset,
                'limit': limit
            }
            
            # Make the API request
            logger.info(f"Querying for disease: '{disease_name}'")
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Extract MONDO results
            mondo_results = self._extract_mondo_results(data)
            
            if not mondo_results:
                logger.warning(f"No MONDO results found for '{disease_name}'")
                return None
            
            # Get the highest scoring result
            top_result = self._get_top_result(mondo_results)
            
            logger.info(f"Found MONDO ID: {top_result['curie']} (score: {top_result.get('score', 'N/A')})")
            
            return top_result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    def _extract_mondo_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract MONDO results from the API response
        
        Args:
            data: Raw API response data
            
        Returns:
            List of MONDO results
        """
        mondo_results = []
        
        def find_mondo_curies(obj):
            """Recursively find all MONDO CURIEs in the response"""
            if isinstance(obj, dict):
                # Check if this dict has a MONDO curie
                curie = obj.get('curie', '')
                if curie and curie.startswith('MONDO:'):
                    mondo_results.append(obj)
                # Recursively search in all values
                for value in obj.values():
                    find_mondo_curies(value)
            elif isinstance(obj, list):
                # Recursively search in all list items
                for item in obj:
                    find_mondo_curies(item)
        
        find_mondo_curies(data)
        return mondo_results
    
    def _get_top_result(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get the highest scoring result from a list of results
        
        Args:
            results: List of result dictionaries
            
        Returns:
            The highest scoring result
        """
        if not results:
            return None
        
        # Sort by score if available (descending order)
        sorted_results = sorted(
            results, 
            key=lambda x: x.get('score', 0), 
            reverse=True
        )
        
        return sorted_results[0]
    
    def resolve_multiple_diseases(self, disease_names: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Resolve multiple disease names to MONDO identifiers
        
        Args:
            disease_names: List of disease names to resolve
            
        Returns:
            Dictionary mapping disease names to their MONDO results
        """
        results = {}
        
        for disease_name in disease_names:
            results[disease_name] = self.resolve_disease(disease_name)
        
        return results
    
    def get_curie_only(self, disease_name: str) -> Optional[str]:
        """
        Convenience method to get only the CURIE/MONDO ID
        
        Args:
            disease_name: Disease name to resolve
            
        Returns:
            MONDO CURIE string or None
        """
        result = self.resolve_disease(disease_name)
        
        if result:
            return result.get('curie')
        
        return None


def main():
    """
    Main function for command-line usage
    """
    parser = argparse.ArgumentParser(
        description='Resolve disease names to MONDO identifiers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python disease_resolver.py "breast cancer"
  python disease_resolver.py "colorectal adenocarcinoma" --limit 5
  python disease_resolver.py "lung cancer" --json
  python disease_resolver.py "ovarian cancer" --verbose
        """
    )
    
    parser.add_argument(
        'disease',
        type=str,
        help='Disease name to resolve (e.g., "breast cancer")'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Maximum number of results to retrieve (default: 10)'
    )
    
    parser.add_argument(
        '--offset',
        type=int,
        default=0,
        help='Result offset for pagination (default: 0)'
    )
    
    parser.add_argument(
        '--no-autocomplete',
        action='store_true',
        help='Disable autocomplete matching'
    )
    
    parser.add_argument(
        '--highlighting',
        action='store_true',
        help='Enable result highlighting'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output full result as JSON'
    )
    
    parser.add_argument(
        '--curie-only',
        action='store_true',
        help='Output only the CURIE/MONDO ID'
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
    resolver = DiseaseResolver()
    
    # Resolve the disease
    if args.curie_only:
        curie = resolver.get_curie_only(args.disease)
        if curie:
            print(curie)
        else:
            logger.error("No MONDO ID found")
            exit(1)
    else:
        result = resolver.resolve_disease(
            disease_name=args.disease,
            autocomplete=not args.no_autocomplete,
            highlighting=args.highlighting,
            offset=args.offset,
            limit=args.limit
        )
        
        if result:
            if args.json:
                # Output full JSON result
                print(json.dumps(result, indent=2))
            else:
                # Output formatted result
                print("\n" + "="*60)
                print(f"Disease Query: {args.disease}")
                print("="*60)
                print(f"MONDO ID (CURIE): {result.get('curie', 'N/A')}")
                print(f"Label: {result.get('label', 'N/A')}")
                print(f"Score: {result.get('score', 'N/A')}")
                
                if 'types' in result:
                    print(f"Types: {', '.join(result['types'])}")
                
                if 'synonyms' in result:
                    print(f"Synonyms: {', '.join(result['synonyms'][:5])}")  # Show first 5
                
                print("="*60)
        else:
            logger.error(f"Failed to resolve disease: {args.disease}")
            exit(1)


if __name__ == "__main__":
    main()
