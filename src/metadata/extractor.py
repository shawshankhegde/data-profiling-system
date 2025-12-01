"""
Metadata Extractor Module
Extracts and manages technical metadata from datasets.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json


class MetadataExtractor:
    """
    Extracts metadata from datasets including schema, statistics, and lineage.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize MetadataExtractor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.metadata_store = {}
    
    def extract_metadata(self, df: pd.DataFrame, dataset_name: str, 
                        source_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from a dataset.
        
        Args:
            df: pandas DataFrame
            dataset_name: Name of the dataset
            source_info: Optional dictionary with source system information
            
        Returns:
            Dictionary containing metadata
        """
        print(f"Extracting metadata for: {dataset_name}")
        
        metadata = {
            'dataset_name': dataset_name,
            'extraction_timestamp': datetime.now().isoformat(),
            'schema': self._extract_schema(df),
            'statistics': self._extract_statistics(df),
            'technical_metadata': self._extract_technical_metadata(df),
        }
        
        if source_info:
            metadata['source_info'] = source_info
        
        if self.config.get('metadata', {}).get('include_lineage', True):
            metadata['lineage'] = self._extract_lineage(dataset_name, source_info)
        
        # Add custom metadata fields if configured
        custom_fields = self.config.get('metadata', {}).get('custom_fields', [])
        if custom_fields:
            metadata['custom_attributes'] = {field: None for field in custom_fields}
        
        self.metadata_store[dataset_name] = metadata
        return metadata
    
    def _extract_schema(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract schema information for each column."""
        schema = []
        
        for col in df.columns:
            col_info = {
                'column_name': col,
                'data_type': str(df[col].dtype),
                'nullable': bool(df[col].isnull().any()),
                'is_unique': bool(df[col].is_unique),
                'position': list(df.columns).index(col) + 1,
            }
            
            # Infer additional type information
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info['python_type'] = 'numeric'
                col_info['sql_type'] = self._infer_sql_type(df[col])
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                col_info['python_type'] = 'datetime'
                col_info['sql_type'] = 'TIMESTAMP'
            elif pd.api.types.is_bool_dtype(df[col]):
                col_info['python_type'] = 'boolean'
                col_info['sql_type'] = 'BOOLEAN'
            else:
                col_info['python_type'] = 'string'
                max_length = df[col].astype(str).str.len().max()
                col_info['sql_type'] = f'VARCHAR({int(max_length)})' if max_length else 'VARCHAR(255)'
                col_info['max_length'] = int(max_length) if max_length else None
            
            schema.append(col_info)
        
        return schema
    
    def _infer_sql_type(self, series: pd.Series) -> str:
        """Infer SQL data type from pandas series."""
        dtype = str(series.dtype)
        
        if 'int' in dtype:
            max_val = series.max()
            if max_val <= 32767:
                return 'SMALLINT'
            elif max_val <= 2147483647:
                return 'INTEGER'
            else:
                return 'BIGINT'
        elif 'float' in dtype:
            return 'DECIMAL(18,2)'
        else:
            return 'NUMERIC'
    
    def _extract_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract statistical metadata."""
        stats = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'total_cells': df.shape[0] * df.shape[1],
            'memory_usage_bytes': int(df.memory_usage(deep=True).sum()),
            'column_statistics': {}
        }
        
        for col in df.columns:
            col_stats = {
                'count': int(df[col].count()),
                'null_count': int(df[col].isnull().sum()),
                'unique_count': int(df[col].nunique()),
            }
            
            if pd.api.types.is_numeric_dtype(df[col]):
                col_stats.update({
                    'min': float(df[col].min()) if not df[col].isnull().all() else None,
                    'max': float(df[col].max()) if not df[col].isnull().all() else None,
                    'mean': float(df[col].mean()) if not df[col].isnull().all() else None,
                    'median': float(df[col].median()) if not df[col].isnull().all() else None,
                    'std': float(df[col].std()) if not df[col].isnull().all() else None,
                })
            
            stats['column_statistics'][col] = col_stats
        
        return stats
    
    def _extract_technical_metadata(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract technical metadata about the dataset."""
        return {
            'pandas_version': pd.__version__,
            'index_type': str(type(df.index)),
            'index_name': df.index.name,
            'has_duplicates': bool(df.duplicated().any()),
            'is_sorted': self._check_if_sorted(df),
            'encoding': 'UTF-8',  # Assume UTF-8 for pandas DataFrames
        }
    
    def _check_if_sorted(self, df: pd.DataFrame) -> Optional[str]:
        """Check if DataFrame is sorted by any column."""
        for col in df.columns:
            try:
                if df[col].is_monotonic_increasing:
                    return f"ascending by {col}"
                elif df[col].is_monotonic_decreasing:
                    return f"descending by {col}"
            except TypeError:
                continue
        return None
    
    def _extract_lineage(self, dataset_name: str, 
                        source_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract data lineage information.
        
        Args:
            dataset_name: Name of the dataset
            source_info: Source system information
            
        Returns:
            Dictionary containing lineage information
        """
        lineage = {
            'dataset': dataset_name,
            'upstream_sources': [],
            'downstream_targets': [],
            'transformations': []
        }
        
        if source_info:
            lineage['upstream_sources'].append({
                'source_system': source_info.get('system', 'unknown'),
                'source_table': source_info.get('table', dataset_name),
                'load_timestamp': datetime.now().isoformat(),
                'load_type': source_info.get('load_type', 'full'),
            })
        
        return lineage
    
    def enrich_with_business_context(self, dataset_name: str, 
                                    business_terms: Dict[str, Any]) -> None:
        """
        Enrich technical metadata with business context.
        
        Args:
            dataset_name: Name of the dataset
            business_terms: Dictionary of business term definitions
        """
        if dataset_name not in self.metadata_store:
            raise ValueError(f"No metadata found for dataset: {dataset_name}")
        
        metadata = self.metadata_store[dataset_name]
        
        # Add business context to schema
        for col_schema in metadata['schema']:
            col_name = col_schema['column_name']
            
            if col_name in business_terms.get('terms', {}):
                business_info = business_terms['terms'][col_name]
                col_schema['business_name'] = business_info.get('business_name')
                col_schema['business_definition'] = business_info.get('definition')
                col_schema['data_owner'] = business_info.get('owner')
                col_schema['is_pii'] = business_info.get('pii', False)
                col_schema['related_terms'] = business_info.get('related_terms', [])
        
        print(f"Enriched metadata for {dataset_name} with business context")
    
    def generate_schema_ddl(self, dataset_name: str, table_name: str, 
                           dialect: str = 'postgresql') -> str:
        """
        Generate CREATE TABLE DDL statement from metadata.
        
        Args:
            dataset_name: Name of the dataset
            table_name: Target table name
            dialect: SQL dialect (postgresql, mysql, mssql)
            
        Returns:
            DDL statement as string
        """
        if dataset_name not in self.metadata_store:
            raise ValueError(f"No metadata found for dataset: {dataset_name}")
        
        schema = self.metadata_store[dataset_name]['schema']
        
        ddl_lines = [f"CREATE TABLE {table_name} ("]
        
        for col in schema:
            col_def = f"  {col['column_name']} {col['sql_type']}"
            
            if not col['nullable']:
                col_def += " NOT NULL"
            
            ddl_lines.append(col_def + ",")
        
        # Remove trailing comma from last column
        ddl_lines[-1] = ddl_lines[-1].rstrip(',')
        
        ddl_lines.append(");")
        
        return '\n'.join(ddl_lines)
    
    def save_metadata(self, dataset_name: str, output_path: Path) -> None:
        """
        Save metadata to JSON file.
        
        Args:
            dataset_name: Name of the dataset
            output_path: Directory to save metadata
        """
        if dataset_name not in self.metadata_store:
            raise ValueError(f"No metadata found for dataset: {dataset_name}")
        
        output_file = output_path / f"{dataset_name}_metadata.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.metadata_store[dataset_name], f, indent=2)
        
        print(f"Metadata saved to: {output_file}")
    
    def export_to_catalog(self, dataset_name: str, catalog_format: str = 'json') -> Dict[str, Any]:
        """
        Export metadata in data catalog format.
        
        Args:
            dataset_name: Name of the dataset
            catalog_format: Format for export (json, yaml, etc.)
            
        Returns:
            Metadata in catalog format
        """
        if dataset_name not in self.metadata_store:
            raise ValueError(f"No metadata found for dataset: {dataset_name}")
        
        metadata = self.metadata_store[dataset_name]
        
        # Format for data catalog
        catalog_entry = {
            'name': dataset_name,
            'type': 'table',
            'description': f"Dataset: {dataset_name}",
            'schema': metadata['schema'],
            'statistics': {
                'row_count': metadata['statistics']['row_count'],
                'column_count': metadata['statistics']['column_count'],
            },
            'tags': [],
            'owners': [],
            'last_updated': metadata['extraction_timestamp'],
        }
        
        return catalog_entry
