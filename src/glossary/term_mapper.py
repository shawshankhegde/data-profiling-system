"""
Business Glossary Term Mapper
Maps technical column names to business terminology.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
from difflib import SequenceMatcher
import json


class TermMapper:
    """
    Maps technical database/file column names to business glossary terms.
    """
    
    def __init__(self, business_terms_path: str, config: Dict[str, Any]):
        """
        Initialize TermMapper with business glossary.
        
        Args:
            business_terms_path: Path to business terms YAML file
            config: Configuration dictionary
        """
        self.config = config
        self.business_terms = self._load_business_terms(business_terms_path)
        self.mappings = {}
    
    def _load_business_terms(self, terms_path: str) -> Dict[str, Any]:
        """Load business terms from YAML configuration."""
        with open(terms_path, 'r') as f:
            return yaml.safe_load(f)
    
    def map_columns(self, columns: List[str], dataset_name: str) -> Dict[str, Dict[str, Any]]:
        """
        Map technical column names to business terms.
        
        Args:
            columns: List of technical column names
            dataset_name: Name of the dataset
            
        Returns:
            Dictionary mapping column names to business information
        """
        print(f"Mapping columns for dataset: {dataset_name}")
        
        mappings = {}
        terms = self.business_terms.get('terms', {})
        
        for col in columns:
            # Direct match
            if col in terms:
                mappings[col] = self._create_mapping(col, terms[col], match_type='exact')
            else:
                # Try fuzzy matching
                if self.config.get('glossary', {}).get('auto_mapping', True):
                    fuzzy_match = self._find_fuzzy_match(col, terms)
                    if fuzzy_match:
                        mappings[col] = fuzzy_match
                    else:
                        mappings[col] = self._create_unmapped_entry(col)
                else:
                    mappings[col] = self._create_unmapped_entry(col)
        
        self.mappings[dataset_name] = mappings
        return mappings
    
    def _create_mapping(self, technical_name: str, business_info: Dict[str, Any], 
                       match_type: str = 'exact') -> Dict[str, Any]:
        """Create a complete mapping entry."""
        return {
            'technical_name': technical_name,
            'business_name': business_info.get('business_name', technical_name),
            'definition': business_info.get('definition', ''),
            'data_type': business_info.get('data_type', ''),
            'format': business_info.get('format', ''),
            'examples': business_info.get('examples', []),
            'owner': business_info.get('owner', ''),
            'related_terms': business_info.get('related_terms', []),
            'is_pii': business_info.get('pii', False),
            'valid_values': business_info.get('valid_values', []),
            'match_type': match_type,
            'mapped': True
        }
    
    def _find_fuzzy_match(self, technical_name: str, 
                         terms: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find fuzzy match for a technical column name.
        
        Args:
            technical_name: Technical column name
            terms: Dictionary of business terms
            
        Returns:
            Mapping dictionary if match found, None otherwise
        """
        threshold = self.config.get('glossary', {}).get('similarity_threshold', 0.8)
        
        best_match = None
        best_score = 0
        
        for term_key, term_info in terms.items():
            # Compare with term key
            score = SequenceMatcher(None, technical_name.lower(), term_key.lower()).ratio()
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = (term_key, term_info)
            
            # Also compare with business name if available
            business_name = term_info.get('business_name', '')
            if business_name:
                # Create comparable version (lowercase, remove spaces)
                comparable_name = business_name.lower().replace(' ', '_')
                score = SequenceMatcher(None, technical_name.lower(), comparable_name).ratio()
                
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = (term_key, term_info)
        
        if best_match:
            mapping = self._create_mapping(technical_name, best_match[1], match_type='fuzzy')
            mapping['fuzzy_match_score'] = best_score
            mapping['matched_term'] = best_match[0]
            return mapping
        
        return None
    
    def _create_unmapped_entry(self, technical_name: str) -> Dict[str, Any]:
        """Create entry for unmapped column."""
        return {
            'technical_name': technical_name,
            'business_name': technical_name.replace('_', ' ').title(),
            'definition': 'No business definition available',
            'mapped': False,
            'match_type': 'none'
        }
    
    def get_business_glossary(self, dataset_name: str) -> Dict[str, Any]:
        """
        Generate a complete business glossary for a dataset.
        
        Args:
            dataset_name: Name of the dataset
            
        Returns:
            Business glossary dictionary
        """
        if dataset_name not in self.mappings:
            raise ValueError(f"No mappings found for dataset: {dataset_name}")
        
        glossary = {
            'dataset_name': dataset_name,
            'total_columns': len(self.mappings[dataset_name]),
            'mapped_columns': sum(1 for m in self.mappings[dataset_name].values() if m['mapped']),
            'unmapped_columns': sum(1 for m in self.mappings[dataset_name].values() if not m['mapped']),
            'terms': self.mappings[dataset_name]
        }
        
        return glossary
    
    def generate_glossary_report(self, dataset_name: str) -> str:
        """
        Generate human-readable glossary report.
        
        Args:
            dataset_name: Name of the dataset
            
        Returns:
            Formatted glossary report as string
        """
        if dataset_name not in self.mappings:
            return f"No mappings found for dataset: {dataset_name}"
        
        mappings = self.mappings[dataset_name]
        
        report_lines = [
            f"\nBusiness Glossary Report: {dataset_name}",
            "=" * 80,
            f"\nTotal Columns: {len(mappings)}",
            f"Mapped: {sum(1 for m in mappings.values() if m['mapped'])}",
            f"Unmapped: {sum(1 for m in mappings.values() if not m['mapped'])}",
            "\n" + "=" * 80,
            "\nColumn Definitions:",
            "-" * 80,
        ]
        
        for col_name, mapping in mappings.items():
            report_lines.append(f"\n{mapping['business_name']} ({col_name})")
            report_lines.append(f"  Definition: {mapping['definition']}")
            
            if mapping.get('data_type'):
                report_lines.append(f"  Data Type: {mapping['data_type']}")
            
            if mapping.get('owner'):
                report_lines.append(f"  Owner: {mapping['owner']}")
            
            if mapping.get('examples'):
                examples = ', '.join(str(e) for e in mapping['examples'][:3])
                report_lines.append(f"  Examples: {examples}")
            
            if mapping.get('is_pii'):
                report_lines.append(f"  ⚠️  Contains PII")
            
            if mapping.get('match_type') == 'fuzzy':
                report_lines.append(f"  (Fuzzy match: {mapping.get('fuzzy_match_score', 0):.2f})")
            
            report_lines.append("-" * 80)
        
        return '\n'.join(report_lines)
    
    def identify_pii_columns(self, dataset_name: str) -> List[str]:
        """
        Identify columns containing PII.
        
        Args:
            dataset_name: Name of the dataset
            
        Returns:
            List of column names containing PII
        """
        if dataset_name not in self.mappings:
            return []
        
        pii_columns = [
            col for col, mapping in self.mappings[dataset_name].items()
            if mapping.get('is_pii', False)
        ]
        
        return pii_columns
    
    def get_columns_by_owner(self, dataset_name: str) -> Dict[str, List[str]]:
        """
        Group columns by data owner.
        
        Args:
            dataset_name: Name of the dataset
            
        Returns:
            Dictionary mapping owners to their columns
        """
        if dataset_name not in self.mappings:
            return {}
        
        owners = {}
        
        for col, mapping in self.mappings[dataset_name].items():
            owner = mapping.get('owner', 'Unassigned')
            if owner not in owners:
                owners[owner] = []
            owners[owner].append(col)
        
        return owners
    
    def export_glossary(self, dataset_name: str, output_path: Path, 
                       format: str = 'json') -> None:
        """
        Export glossary to file.
        
        Args:
            dataset_name: Name of the dataset
            output_path: Directory to save glossary
            format: Export format (json, yaml, csv)
        """
        if dataset_name not in self.mappings:
            raise ValueError(f"No mappings found for dataset: {dataset_name}")
        
        glossary = self.get_business_glossary(dataset_name)
        
        if format == 'json':
            output_file = output_path / f"{dataset_name}_glossary.json"
            with open(output_file, 'w') as f:
                json.dump(glossary, f, indent=2)
        
        elif format == 'yaml':
            output_file = output_path / f"{dataset_name}_glossary.yaml"
            with open(output_file, 'w') as f:
                yaml.dump(glossary, f, default_flow_style=False)
        
        elif format == 'csv':
            output_file = output_path / f"{dataset_name}_glossary.csv"
            
            # Flatten mappings for CSV
            rows = []
            for col, mapping in glossary['terms'].items():
                rows.append({
                    'Technical Name': mapping['technical_name'],
                    'Business Name': mapping['business_name'],
                    'Definition': mapping['definition'],
                    'Data Type': mapping.get('data_type', ''),
                    'Owner': mapping.get('owner', ''),
                    'Is PII': mapping.get('is_pii', False),
                    'Mapped': mapping['mapped']
                })
            
            df = pd.DataFrame(rows)
            df.to_csv(output_file, index=False)
        
        print(f"Glossary exported to: {output_file}")
    
    def validate_mappings(self, dataset_name: str) -> Dict[str, Any]:
        """
        Validate quality of mappings.
        
        Args:
            dataset_name: Name of the dataset
            
        Returns:
            Validation results
        """
        if dataset_name not in self.mappings:
            return {'error': f"No mappings found for dataset: {dataset_name}"}
        
        mappings = self.mappings[dataset_name]
        total = len(mappings)
        mapped = sum(1 for m in mappings.values() if m['mapped'])
        
        # Check for columns missing definitions
        missing_definitions = [
            col for col, m in mappings.items()
            if not m.get('definition') or m['definition'] == 'No business definition available'
        ]
        
        # Check for columns missing owners
        missing_owners = [
            col for col, m in mappings.items()
            if not m.get('owner')
        ]
        
        validation = {
            'total_columns': total,
            'mapped_columns': mapped,
            'mapping_coverage': f"{(mapped/total*100):.1f}%",
            'columns_missing_definitions': len(missing_definitions),
            'columns_missing_owners': len(missing_owners),
            'quality_score': (mapped / total) * 100,
            'issues': []
        }
        
        if len(missing_definitions) > 0:
            validation['issues'].append({
                'type': 'missing_definitions',
                'count': len(missing_definitions),
                'columns': missing_definitions[:5]  # Show first 5
            })
        
        if len(missing_owners) > 0:
            validation['issues'].append({
                'type': 'missing_owners',
                'count': len(missing_owners),
                'columns': missing_owners[:5]  # Show first 5
            })
        
        return validation
