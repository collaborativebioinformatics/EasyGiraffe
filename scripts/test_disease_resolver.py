"""
Test script for the Disease Resolver
Demonstrates various usage patterns
"""

import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

from disease_resolver import DiseaseResolver
import json


def test_single_disease():
    """Test resolving a single disease"""
    print("\n" + "="*60)
    print("TEST 1: Single Disease Resolution")
    print("="*60)
    
    resolver = DiseaseResolver()
    
    # Test with breast cancer
    disease = "breast cancer"
    result = resolver.resolve_disease(disease)
    
    if result:
        print(f"✓ Successfully resolved: {disease}")
        print(f"  MONDO ID: {result.get('curie')}")
        print(f"  Label: {result.get('label')}")
        print(f"  Score: {result.get('score')}")
    else:
        print(f"✗ Failed to resolve: {disease}")


def test_curie_only():
    """Test getting just the CURIE ID (without MONDO: prefix)"""
    print("\n" + "="*60)
    print("TEST 2: Get CURIE ID Only (without MONDO: prefix)")
    print("="*60)
    
    resolver = DiseaseResolver()
    
    diseases = [
        "sickle cell disease",
        "breast cancer", 
        "colorectal cancer",
        "lung adenocarcinoma",
        "ovarian cancer"
    ]
    
    for disease in diseases:
        curie = resolver.get_curie_only(disease)
        print(f"{disease:30s} → {curie or 'Not Found'}")
        
    print("\nNote: Output shows only the ID part (e.g., '0011382' instead of 'MONDO:0011382')")


def test_multiple_diseases():
    """Test resolving multiple diseases"""
    print("\n" + "="*60)
    print("TEST 3: Multiple Disease Resolution")
    print("="*60)
    
    resolver = DiseaseResolver()
    
    diseases = [
        "sickle cell disease",
        "breast cancer",
        "colorectal adenocarcinoma",
        "lung cancer",
        "ovarian cancer",
        "pancreatic cancer",
        "melanoma"
    ]
    
    results = resolver.resolve_multiple_diseases(diseases)
    
    print(f"\nProcessed {len(diseases)} diseases:")
    print(f"Found: {sum(1 for r in results.values() if r)} / {len(diseases)}\n")
    
    for disease, result in results.items():
        if result:
            print(f"✓ {disease:35s} → {result.get('curie')}")
        else:
            print(f"✗ {disease:35s} → Not Found")


def test_cancer_types():
    """Test various cancer types"""
    print("\n" + "="*60)
    print("TEST 4: Cancer Types from TCGA")
    print("="*60)
    
    resolver = DiseaseResolver()
    
    # Common TCGA cancer types
    tcga_cancers = [
        "Breast Invasive Carcinoma",
        "Lung Adenocarcinoma",
        "Colon Adenocarcinoma",
        "Glioblastoma Multiforme",
        "Prostate Adenocarcinoma",
        "Ovarian Serous Cystadenocarcinoma",
        "Thyroid Carcinoma",
        "Kidney Renal Clear Cell Carcinoma"
    ]
    
    results = {}
    
    for cancer in tcga_cancers:
        curie = resolver.get_curie_only(cancer)
        results[cancer] = curie
        status = "✓" if curie else "✗"
        print(f"{status} {cancer:45s} → {curie or 'Not Found'}")
    
    # Save results
    output_file = "test_tcga_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to {output_file}")


def test_api_response_structure():
    """Test and display the full API response structure"""
    print("\n" + "="*60)
    print("TEST 5: API Response Structure & Recursive Parsing")
    print("="*60)
    
    resolver = DiseaseResolver()
    
    disease = "sickle cell disease"
    result = resolver.resolve_disease(disease)
    
    if result:
        print(f"\nTop MONDO result for '{disease}':")
        print(json.dumps(result, indent=2))
        
        # Test the recursive parsing by showing multiple results
        print(f"\n\nTesting recursive JSON parsing...")
        try:
            import requests
            response = requests.get(
                resolver.base_url,
                params={'string': disease, 'autocomplete': 'true', 'limit': 10},
                timeout=10
            )
            data = response.json()
            mondo_results = resolver._extract_mondo_results(data)
            print(f"Found {len(mondo_results)} MONDO results in complex JSON structure")
            
            for i, result in enumerate(mondo_results[:3]):  # Show first 3
                print(f"  {i+1}. {result.get('curie')} - {result.get('label', 'No label')} (score: {result.get('score', 'N/A')})")
                
        except Exception as e:
            print(f"Error testing recursive parsing: {e}")
    else:
        print(f"No results found for '{disease}'")


def run_all_tests():
    """Run all tests"""
    print("\n" + "🧪 "*30)
    print("DISEASE RESOLVER TEST SUITE")
    print("🧪 "*30)
    
    try:
        test_single_disease()
        test_curie_only()
        test_multiple_diseases()
        test_cancer_types()
        test_api_response_structure()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS COMPLETED")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        raise


if __name__ == "__main__":
    run_all_tests()
