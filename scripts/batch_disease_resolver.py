"""
Batch Disease Resolver
Process multiple diseases from a file or list
"""

import json
import csv
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any
from disease_resolver import DiseaseResolver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def read_diseases_from_file(filepath: str) -> List[str]:
    """
    Read disease names from a file (one per line)
    
    Args:
        filepath: Path to the input file
        
    Returns:
        List of disease names
    """
    diseases = []
    
    with open(filepath, 'r') as f:
        for line in f:
            disease = line.strip()
            if disease and not disease.startswith('#'):  # Skip empty lines and comments
                diseases.append(disease)
    
    return diseases


def save_results_json(results: Dict[str, Any], output_file: str):
    """
    Save results to JSON file
    
    Args:
        results: Dictionary of results
        output_file: Path to output file
    """
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to {output_file}")


def save_results_csv(results: Dict[str, Any], output_file: str):
    """
    Save results to CSV file
    
    Args:
        results: Dictionary of results
        output_file: Path to output file
    """
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow(['Disease Name', 'MONDO ID', 'Label', 'Score', 'Status'])
        
        # Write data
        for disease_name, result in results.items():
            if result:
                writer.writerow([
                    disease_name,
                    result.get('curie', ''),
                    result.get('label', ''),
                    result.get('score', ''),
                    'Found'
                ])
            else:
                writer.writerow([disease_name, '', '', '', 'Not Found'])
    
    logger.info(f"Results saved to {output_file}")


def process_batch(disease_names: List[str], 
                 output_format: str = 'json',
                 output_file: str = None) -> Dict[str, Any]:
    """
    Process a batch of disease names
    
    Args:
        disease_names: List of disease names
        output_format: Output format ('json' or 'csv')
        output_file: Output file path
        
    Returns:
        Dictionary of results
    """
    resolver = DiseaseResolver()
    results = {}
    
    logger.info(f"Processing {len(disease_names)} diseases...")
    
    for i, disease_name in enumerate(disease_names, 1):
        logger.info(f"[{i}/{len(disease_names)}] Processing: {disease_name}")
        result = resolver.resolve_disease(disease_name)
        results[disease_name] = result
    
    # Save results if output file specified
    if output_file:
        if output_format == 'json':
            save_results_json(results, output_file)
        elif output_format == 'csv':
            save_results_csv(results, output_file)
    
    # Print summary
    found_count = sum(1 for r in results.values() if r is not None)
    logger.info(f"Summary: {found_count}/{len(disease_names)} diseases resolved successfully")
    
    return results


def main():
    """
    Main function for batch processing
    """
    parser = argparse.ArgumentParser(
        description='Batch resolve disease names to MONDO identifiers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From file
  python batch_disease_resolver.py --input diseases.txt --output results.json
  
  # From command line list
  python batch_disease_resolver.py --diseases "breast cancer" "lung cancer" "colorectal cancer"
  
  # Save as CSV
  python batch_disease_resolver.py --input diseases.txt --output results.csv --format csv
        """
    )
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--input',
        '-i',
        type=str,
        help='Input file containing disease names (one per line)'
    )
    
    input_group.add_argument(
        '--diseases',
        '-d',
        nargs='+',
        help='List of disease names to process'
    )
    
    parser.add_argument(
        '--output',
        '-o',
        type=str,
        required=True,
        help='Output file path'
    )
    
    parser.add_argument(
        '--format',
        '-f',
        choices=['json', 'csv'],
        default='json',
        help='Output format (default: json)'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get disease names
    if args.input:
        disease_names = read_diseases_from_file(args.input)
        logger.info(f"Loaded {len(disease_names)} diseases from {args.input}")
    else:
        disease_names = args.diseases
    
    # Process diseases
    results = process_batch(
        disease_names=disease_names,
        output_format=args.format,
        output_file=args.output
    )
    
    # Display results
    print("\n" + "="*60)
    print("BATCH PROCESSING RESULTS")
    print("="*60)
    
    for disease_name, result in results.items():
        if result:
            print(f"✓ {disease_name:40s} → {result.get('curie', 'N/A')}")
        else:
            print(f"✗ {disease_name:40s} → Not Found")
    
    print("="*60)


if __name__ == "__main__":
    main()
