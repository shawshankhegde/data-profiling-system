"""
Data Profiler Module
Statistical analysis and profiling of datasets.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Any, Optional
# from ydata_profiling import ProfileReport  # Optional: install separately


class DataProfiler:
    """
    Profiles datasets and generates statistical insights and quality metrics.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the DataProfiler with configuration settings.
        
        Args:
            config: Configuration dictionary with profiling settings
        """
        self.config = config
        self.profile_results = {}
        
    def profile_dataset(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        """
        Generate comprehensive profile for a dataset.
        
        Args:
            df: pandas DataFrame to profile
            dataset_name: Name identifier for the dataset
            
        Returns:
            Dictionary containing profiling results
        """
        print(f"Profiling dataset: {dataset_name}")
        
        profile = {
            'dataset_name': dataset_name,
            'timestamp': datetime.now().isoformat(),
            'basic_info': self._get_basic_info(df),
            'column_profiles': self._profile_columns(df),
            'data_quality': self._assess_quality(df),
            'patterns': self._detect_patterns(df),
        }
        
        if self.config.get('profiling', {}).get('correlation_analysis', True):
            profile['correlations'] = self._analyze_correlations(df)
        
        self.profile_results[dataset_name] = profile
        return profile
    
    def _get_basic_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract basic dataset information."""
        return {
            'row_count': len(df),
            'column_count': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
            'duplicate_rows': df.duplicated().sum(),
            'columns': list(df.columns),
            'dtypes': df.dtypes.astype(str).to_dict()
        }
    
    def _profile_columns(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Generate detailed profile for each column."""
        column_profiles = {}
        
        for col in df.columns:
            col_data = df[col]
            
            profile = {
                'data_type': str(col_data.dtype),
                'null_count': int(col_data.isnull().sum()),
                'null_percentage': float(col_data.isnull().sum() / len(df) * 100),
                'unique_count': int(col_data.nunique()),
                'unique_percentage': float(col_data.nunique() / len(df) * 100),
            }
            
            # Add statistics for numeric columns
            if pd.api.types.is_numeric_dtype(col_data):
                profile.update({
                    'min': float(col_data.min()) if not col_data.isnull().all() else None,
                    'max': float(col_data.max()) if not col_data.isnull().all() else None,
                    'mean': float(col_data.mean()) if not col_data.isnull().all() else None,
                    'median': float(col_data.median()) if not col_data.isnull().all() else None,
                    'std': float(col_data.std()) if not col_data.isnull().all() else None,
                    'zeros_count': int((col_data == 0).sum()),
                })
            
            # Add information for categorical/object columns
            if pd.api.types.is_object_dtype(col_data) or pd.api.types.is_categorical_dtype(col_data):
                value_counts = col_data.value_counts()
                profile.update({
                    'top_values': value_counts.head(10).to_dict(),
                    'is_categorical': col_data.nunique() < 50,  # Heuristic for categorical
                })
            
            # Add date-specific information
            if pd.api.types.is_datetime64_any_dtype(col_data):
                profile.update({
                    'min_date': col_data.min().isoformat() if not col_data.isnull().all() else None,
                    'max_date': col_data.max().isoformat() if not col_data.isnull().all() else None,
                    'date_range_days': (col_data.max() - col_data.min()).days if not col_data.isnull().all() else None,
                })
            
            # Sample values (non-null)
            sample_values = col_data.dropna().head(5).tolist()
            profile['sample_values'] = [str(v) for v in sample_values]
            
            column_profiles[col] = profile
        
        return column_profiles
    
    def _assess_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess overall data quality."""
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isnull().sum().sum()
        
        quality_metrics = {
            'overall_completeness': float((total_cells - null_cells) / total_cells * 100),
            'columns_with_nulls': int((df.isnull().sum() > 0).sum()),
            'total_null_cells': int(null_cells),
            'duplicate_rows_count': int(df.duplicated().sum()),
            'duplicate_rows_percentage': float(df.duplicated().sum() / len(df) * 100),
        }
        
        # Column-level quality issues
        quality_issues = []
        threshold = self.config.get('profiling', {}).get('quality_thresholds', {})
        max_null_pct = threshold.get('max_null_percentage', 10)
        
        for col in df.columns:
            null_pct = df[col].isnull().sum() / len(df) * 100
            
            if null_pct > max_null_pct:
                quality_issues.append({
                    'column': col,
                    'issue': 'high_null_percentage',
                    'value': f"{null_pct:.2f}%",
                    'severity': 'high' if null_pct > 50 else 'medium'
                })
            
            # Check for potential data type issues
            if pd.api.types.is_object_dtype(df[col]):
                # Check if column might be numeric but stored as string
                try:
                    pd.to_numeric(df[col].dropna(), errors='raise')
                    quality_issues.append({
                        'column': col,
                        'issue': 'numeric_stored_as_string',
                        'severity': 'low'
                    })
                except (ValueError, TypeError):
                    pass
        
        quality_metrics['quality_issues'] = quality_issues
        
        return quality_metrics
    
    def _detect_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect common patterns in the data."""
        patterns = {}
        
        for col in df.columns:
            if pd.api.types.is_object_dtype(df[col]):
                col_patterns = self._detect_column_patterns(df[col])
                if col_patterns:
                    patterns[col] = col_patterns
        
        return patterns
    
    def _detect_column_patterns(self, series: pd.Series) -> Dict[str, Any]:
        """Detect patterns in a single column."""
        import re
        
        sample = series.dropna().astype(str).head(100)
        
        patterns_detected = {}
        
        # Email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if sample.str.match(email_pattern).any():
            matches = sample.str.match(email_pattern).sum()
            patterns_detected['email'] = f"{matches}/{len(sample)} matches"
        
        # Phone pattern
        phone_pattern = r'^\+?1?\d{9,15}$'
        if sample.str.match(phone_pattern).any():
            matches = sample.str.match(phone_pattern).sum()
            patterns_detected['phone'] = f"{matches}/{len(sample)} matches"
        
        # ID patterns (e.g., CUST1001, ORD001)
        id_pattern = r'^[A-Z]{3,4}\d{3,4}$'
        if sample.str.match(id_pattern).any():
            matches = sample.str.match(id_pattern).sum()
            patterns_detected['id_code'] = f"{matches}/{len(sample)} matches"
        
        # URL pattern
        url_pattern = r'^https?://[^\s]+$'
        if sample.str.match(url_pattern).any():
            matches = sample.str.match(url_pattern).sum()
            patterns_detected['url'] = f"{matches}/{len(sample)} matches"
        
        return patterns_detected
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations between numeric columns."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {'message': 'Insufficient numeric columns for correlation analysis'}
        
        corr_matrix = df[numeric_cols].corr()
        
        # Find strong correlations (|r| > 0.7)
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        'column_1': corr_matrix.columns[i],
                        'column_2': corr_matrix.columns[j],
                        'correlation': float(corr_value)
                    })
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'strong_correlations': strong_correlations
        }
    
    def generate_ydata_profile(self, df: pd.DataFrame, output_path: Path, 
                                dataset_name: str) -> None:
        """
        Generate comprehensive HTML profile report using ydata-profiling.
        
        Args:
            df: DataFrame to profile
            output_path: Path to save the HTML report
            dataset_name: Name of the dataset
        """
        try:
            from ydata_profiling import ProfileReport
            print(f"Generating ydata profile report for {dataset_name}...")
            
            profile = ProfileReport(
                df,
                title=f"Data Profile Report - {dataset_name}",
                explorative=True,
                minimal=False
            )
            
            output_file = output_path / f"{dataset_name}_profile_report.html"
            profile.to_file(output_file)
            print(f"Profile report saved to: {output_file}")
        except ImportError:
            print(f"ydata-profiling not installed. Skipping HTML report generation.")
            print(f"To install: pip install ydata-profiling --break-system-packages")
    
    def save_profile(self, dataset_name: str, output_path: Path) -> None:
        """
        Save profile results to JSON file.
        
        Args:
            dataset_name: Name of the dataset
            output_path: Directory to save the profile
        """
        if dataset_name not in self.profile_results:
            raise ValueError(f"No profile found for dataset: {dataset_name}")
        
        output_file = output_path / f"{dataset_name}_profile.json"
        
        # Custom JSON encoder for numpy types
        def convert_numpy(obj):
            if isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        # Convert numpy types in the profile
        import json
        profile_json = json.loads(
            json.dumps(self.profile_results[dataset_name], default=convert_numpy)
        )
        
        with open(output_file, 'w') as f:
            json.dump(profile_json, f, indent=2)
        
        print(f"Profile saved to: {output_file}")
    
    def get_summary(self, dataset_name: str) -> str:
        """Generate a text summary of the profile."""
        if dataset_name not in self.profile_results:
            return f"No profile found for dataset: {dataset_name}"
        
        profile = self.profile_results[dataset_name]
        basic = profile['basic_info']
        quality = profile['data_quality']
        
        summary = f"""
Data Profile Summary: {dataset_name}
{'=' * 60}
Dataset Information:
  - Rows: {basic['row_count']:,}
  - Columns: {basic['column_count']}
  - Memory Usage: {basic['memory_usage_mb']:.2f} MB
  - Duplicate Rows: {basic['duplicate_rows']:,}

Data Quality:
  - Overall Completeness: {quality['overall_completeness']:.2f}%
  - Columns with Nulls: {quality['columns_with_nulls']}
  - Total Null Cells: {quality['total_null_cells']:,}
  - Quality Issues Found: {len(quality['quality_issues'])}

{'=' * 60}
"""
        return summary


def profile_csv_file(file_path: str, config: Dict[str, Any]) -> DataProfiler:
    """
    Convenience function to profile a CSV file.
    
    Args:
        file_path: Path to CSV file
        config: Configuration dictionary
        
    Returns:
        DataProfiler instance with results
    """
    df = pd.read_csv(file_path)
    dataset_name = Path(file_path).stem
    
    profiler = DataProfiler(config)
    profiler.profile_dataset(df, dataset_name)
    
    return profiler
