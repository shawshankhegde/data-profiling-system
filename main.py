"""
Main script for data profiling pipeline.
Orchestrates profiling, metadata extraction, glossary mapping, and dictionary generation.
"""

import sys
from pathlib import Path
import yaml
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from profiler.data_profiler import DataProfiler
from metadata.extractor import MetadataExtractor
from glossary.term_mapper import TermMapper
from dictionary.generator import DictionaryGenerator


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    """Main execution function."""
    print("=" * 80)
    print("DATA PROFILING SYSTEM")
    print("=" * 80)
    print()
    
    # Setup paths
    base_path = Path(__file__).parent
    config_path = base_path / 'config' / 'profiling_config.yaml'
    business_terms_path = base_path / 'config' / 'business_terms.yaml'
    data_path = base_path / 'data' / 'sample_sales_data.csv'
    
    # Create output directories
    outputs_path = base_path / 'outputs'
    profiles_path = outputs_path / 'profiles'
    metadata_path = outputs_path / 'metadata'
    dictionaries_path = outputs_path / 'dictionaries'
    
    for path in [outputs_path, profiles_path, metadata_path, dictionaries_path]:
        path.mkdir(parents=True, exist_ok=True)
    
    # Load configuration
    print("Loading configuration...")
    config = load_config(config_path)
    
    # Load data
    print(f"Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    dataset_name = data_path.stem
    print(f"Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
    print()
    
    # Step 1: Data Profiling
    print("STEP 1: DATA PROFILING")
    print("-" * 80)
    profiler = DataProfiler(config)
    profile = profiler.profile_dataset(df, dataset_name)
    
    # Print summary
    print(profiler.get_summary(dataset_name))
    
    # Save profile
    profiler.save_profile(dataset_name, profiles_path)
    
    # Generate comprehensive HTML profile report
    profiler.generate_ydata_profile(df, profiles_path, dataset_name)
    print()
    
    # Step 2: Metadata Extraction
    print("STEP 2: METADATA EXTRACTION")
    print("-" * 80)
    metadata_extractor = MetadataExtractor(config)
    
    # Extract metadata with source information
    source_info = {
        'system': 'CSV File',
        'table': dataset_name,
        'load_type': 'full'
    }
    
    metadata = metadata_extractor.extract_metadata(df, dataset_name, source_info)
    
    # Load business terms and enrich metadata
    with open(business_terms_path, 'r') as f:
        business_terms = yaml.safe_load(f)
    
    metadata_extractor.enrich_with_business_context(dataset_name, business_terms)
    
    # Generate DDL
    ddl = metadata_extractor.generate_schema_ddl(dataset_name, dataset_name, 'postgresql')
    print(f"\nGenerated DDL:\n{ddl}\n")
    
    # Save metadata
    metadata_extractor.save_metadata(dataset_name, metadata_path)
    print()
    
    # Step 3: Business Glossary Mapping
    print("STEP 3: BUSINESS GLOSSARY MAPPING")
    print("-" * 80)
    term_mapper = TermMapper(business_terms_path, config)
    
    # Map columns to business terms
    mappings = term_mapper.map_columns(list(df.columns), dataset_name)
    
    # Validate mappings
    validation = term_mapper.validate_mappings(dataset_name)
    print(f"Mapping Coverage: {validation['mapping_coverage']}")
    print(f"Quality Score: {validation['quality_score']:.1f}/100")
    
    # Identify PII columns
    pii_columns = term_mapper.identify_pii_columns(dataset_name)
    if pii_columns:
        print(f"\nPII Columns Detected: {', '.join(pii_columns)}")
    
    # Export glossary
    term_mapper.export_glossary(dataset_name, dictionaries_path, format='json')
    term_mapper.export_glossary(dataset_name, dictionaries_path, format='csv')
    
    # Print glossary report
    print(term_mapper.generate_glossary_report(dataset_name))
    print()
    
    # Step 4: Data Dictionary Generation
    print("STEP 4: DATA DICTIONARY GENERATION")
    print("-" * 80)
    dict_generator = DictionaryGenerator(config)
    
    # Get glossary for dictionary
    glossary = term_mapper.get_business_glossary(dataset_name)
    
    # Generate comprehensive dictionary
    dictionary = dict_generator.generate_dictionary(
        dataset_name, profile, metadata, glossary
    )
    
    # Export in multiple formats
    dict_generator.export_html(dataset_name, dictionaries_path)
    dict_generator.export_json(dataset_name, dictionaries_path)
    dict_generator.export_markdown(dataset_name, dictionaries_path)
    
    print(f"Data dictionary generated successfully!")
    print()
    
    # Summary
    print("=" * 80)
    print("PROFILING COMPLETE")
    print("=" * 80)
    print("\nGenerated Outputs:")
    print(f"  - Data Profile: {profiles_path}")
    print(f"  - Metadata: {metadata_path}")
    print(f"  - Data Dictionaries: {dictionaries_path}")
    print()
    print("Next Steps:")
    print("  1. Review the HTML data dictionary for comprehensive documentation")
    print("  2. Check the profile report for data quality issues")
    print("  3. Validate business glossary mappings")
    print("  4. Run the dashboard: streamlit run src/dashboard/app.py")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
