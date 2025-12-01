"""
Data Dictionary Generator
Generates data dictionaries combining technical metadata and business context.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
from jinja2 import Template


class DictionaryGenerator:
    """
    Generates data dictionaries with technical metadata, business context, and quality metrics.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize DictionaryGenerator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.dictionaries = {}
    
    def generate_dictionary(self, dataset_name: str, profile: Dict[str, Any],
                          metadata: Dict[str, Any], glossary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive data dictionary.
        
        Args:
            dataset_name: Name of the dataset
            profile: Data profiling results
            metadata: Technical metadata
            glossary: Business glossary mappings
            
        Returns:
            Complete data dictionary
        """
        print(f"Generating data dictionary for: {dataset_name}")
        
        dictionary = {
            'dataset_name': dataset_name,
            'generation_date': datetime.now().isoformat(),
            'overview': self._create_overview(profile, metadata),
            'columns': self._create_column_definitions(profile, metadata, glossary),
            'data_quality': self._create_quality_section(profile),
            'usage_notes': self._create_usage_notes(dataset_name),
        }
        
        self.dictionaries[dataset_name] = dictionary
        return dictionary
    
    def _create_overview(self, profile: Dict[str, Any], 
                        metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create overview section of dictionary."""
        basic_info = profile.get('basic_info', {})
        stats = metadata.get('statistics', {})
        
        return {
            'description': f"Dataset containing {basic_info.get('row_count', 0):,} records across {basic_info.get('column_count', 0)} fields",
            'record_count': basic_info.get('row_count', 0),
            'field_count': basic_info.get('column_count', 0),
            'size_mb': f"{basic_info.get('memory_usage_mb', 0):.2f} MB",
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'refresh_frequency': 'Daily',  # Could be configured
        }
    
    def _create_column_definitions(self, profile: Dict[str, Any],
                                  metadata: Dict[str, Any],
                                  glossary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create comprehensive column definitions."""
        column_profiles = profile.get('column_profiles', {})
        schema = metadata.get('schema', [])
        terms = glossary.get('terms', {})
        
        columns = []
        
        for col_schema in schema:
            col_name = col_schema['column_name']
            col_profile = column_profiles.get(col_name, {})
            col_term = terms.get(col_name, {})
            
            column_def = {
                'technical_name': col_name,
                'business_name': col_term.get('business_name', col_name),
                'position': col_schema.get('position', 0),
                'description': col_term.get('definition', ''),
                'data_type': {
                    'pandas': col_schema.get('data_type', ''),
                    'sql': col_schema.get('sql_type', ''),
                    'python': col_schema.get('python_type', ''),
                },
                'nullable': col_schema.get('nullable', True),
                'is_unique': col_schema.get('is_unique', False),
                'statistics': {
                    'null_count': col_profile.get('null_count', 0),
                    'null_percentage': f"{col_profile.get('null_percentage', 0):.2f}%",
                    'unique_count': col_profile.get('unique_count', 0),
                    'unique_percentage': f"{col_profile.get('unique_percentage', 0):.2f}%",
                }
            }
            
            # Add numeric statistics if available
            if 'min' in col_profile:
                column_def['statistics'].update({
                    'min': col_profile.get('min'),
                    'max': col_profile.get('max'),
                    'mean': col_profile.get('mean'),
                    'median': col_profile.get('median'),
                })
            
            # Add categorical information if available
            if 'top_values' in col_profile:
                column_def['top_values'] = col_profile['top_values']
            
            # Add sample values
            if self.config.get('dictionary', {}).get('include_samples', True):
                column_def['sample_values'] = col_profile.get('sample_values', [])
            
            # Add business context
            if col_term.get('owner'):
                column_def['owner'] = col_term['owner']
            
            if col_term.get('is_pii'):
                column_def['is_pii'] = True
                column_def['sensitivity'] = 'HIGH'
            
            if col_term.get('valid_values'):
                column_def['valid_values'] = col_term['valid_values']
            
            if col_term.get('examples'):
                column_def['business_examples'] = col_term['examples']
            
            if col_term.get('related_terms'):
                column_def['related_fields'] = col_term['related_terms']
            
            columns.append(column_def)
        
        return columns
    
    def _create_quality_section(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create data quality section."""
        quality = profile.get('data_quality', {})
        
        quality_section = {
            'overall_completeness': f"{quality.get('overall_completeness', 0):.2f}%",
            'duplicate_records': quality.get('duplicate_rows_count', 0),
            'quality_issues': quality.get('quality_issues', []),
            'quality_score': self._calculate_quality_score(quality),
        }
        
        return quality_section
    
    def _calculate_quality_score(self, quality: Dict[str, Any]) -> str:
        """Calculate overall quality score."""
        completeness = quality.get('overall_completeness', 0)
        issues_count = len(quality.get('quality_issues', []))
        
        # Simple scoring logic
        score = completeness
        score -= (issues_count * 5)  # Penalize for issues
        score = max(0, min(100, score))  # Clamp between 0-100
        
        if score >= 90:
            return f"{score:.0f}% (Excellent)"
        elif score >= 75:
            return f"{score:.0f}% (Good)"
        elif score >= 60:
            return f"{score:.0f}% (Fair)"
        else:
            return f"{score:.0f}% (Needs Improvement)"
    
    def _create_usage_notes(self, dataset_name: str) -> Dict[str, Any]:
        """Create usage notes and recommendations."""
        return {
            'primary_keys': [],  # Could be inferred from unique columns
            'foreign_keys': [],
            'recommended_joins': [],
            'common_queries': [],
            'notes': [
                "Review data quality issues before using in production",
                "Verify PII handling complies with privacy policies",
                "Contact data owner for questions about business logic"
            ]
        }
    
    def export_html(self, dataset_name: str, output_path: Path) -> None:
        """
        Export dictionary as HTML documentation.
        
        Args:
            dataset_name: Name of the dataset
            output_path: Directory to save HTML file
        """
        if dataset_name not in self.dictionaries:
            raise ValueError(f"No dictionary found for dataset: {dataset_name}")
        
        dictionary = self.dictionaries[dataset_name]
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Dictionary - {{ dataset_name }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .section {
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        .metric-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }
        .column-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            background: #fafafa;
        }
        .column-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .column-name {
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }
        .column-type {
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
        }
        .column-description {
            color: #555;
            margin-bottom: 15px;
            font-style: italic;
        }
        .column-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        .detail-item {
            font-size: 0.9em;
        }
        .detail-label {
            color: #666;
            font-weight: 600;
        }
        .detail-value {
            color: #333;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
            margin-right: 5px;
        }
        .badge-pii {
            background: #ff6b6b;
            color: white;
        }
        .badge-unique {
            background: #51cf66;
            color: white;
        }
        .badge-nullable {
            background: #ffd43b;
            color: #333;
        }
        .sample-values {
            background: white;
            padding: 10px;
            border-radius: 5px;
            border-left: 3px solid #667eea;
            margin-top: 10px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .quality-score {
            font-size: 2em;
            font-weight: bold;
            color: #51cf66;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Data Dictionary</h1>
        <p>{{ dataset_name }}</p>
        <p>Generated: {{ generation_date }}</p>
    </div>

    <div class="section">
        <h2>Overview</h2>
        <p>{{ overview.description }}</p>
        <div class="overview-grid">
            <div class="metric">
                <div class="metric-label">Total Records</div>
                <div class="metric-value">{{ "{:,}".format(overview.record_count) }}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Total Fields</div>
                <div class="metric-value">{{ overview.field_count }}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Dataset Size</div>
                <div class="metric-value">{{ overview.size_mb }}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Last Updated</div>
                <div class="metric-value">{{ overview.last_updated }}</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>Data Quality</h2>
        <div class="overview-grid">
            <div class="metric">
                <div class="metric-label">Completeness</div>
                <div class="metric-value">{{ data_quality.overall_completeness }}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Quality Score</div>
                <div class="quality-score">{{ data_quality.quality_score }}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Duplicate Records</div>
                <div class="metric-value">{{ data_quality.duplicate_records }}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Quality Issues</div>
                <div class="metric-value">{{ data_quality.quality_issues|length }}</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>Column Definitions</h2>
        {% for column in columns %}
        <div class="column-card">
            <div class="column-header">
                <div>
                    <div class="column-name">{{ column.business_name }}</div>
                    <div style="font-size: 0.9em; color: #666;">{{ column.technical_name }}</div>
                </div>
                <div class="column-type">{{ column.data_type.sql }}</div>
            </div>
            
            <div class="column-description">
                {{ column.description or "No description available" }}
            </div>
            
            <div>
                {% if column.is_unique %}
                <span class="badge badge-unique">UNIQUE</span>
                {% endif %}
                {% if column.nullable %}
                <span class="badge badge-nullable">NULLABLE</span>
                {% endif %}
                {% if column.is_pii %}
                <span class="badge badge-pii">⚠️ PII</span>
                {% endif %}
            </div>
            
            <div class="column-details">
                <div class="detail-item">
                    <div class="detail-label">Null Rate</div>
                    <div class="detail-value">{{ column.statistics.null_percentage }}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Unique Values</div>
                    <div class="detail-value">{{ "{:,}".format(column.statistics.unique_count) }}</div>
                </div>
                {% if column.owner %}
                <div class="detail-item">
                    <div class="detail-label">Owner</div>
                    <div class="detail-value">{{ column.owner }}</div>
                </div>
                {% endif %}
            </div>
            
            {% if column.sample_values %}
            <div class="sample-values">
                <strong>Sample Values:</strong> {{ column.sample_values|join(', ') }}
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>

    <div class="footer">
        <p>Generated by Automated Data Profiling System</p>
        <p>For questions or updates, contact the data governance team</p>
    </div>
</body>
</html>
        """
        
        template = Template(html_template)
        html_content = template.render(**dictionary)
        
        output_file = output_path / f"{dataset_name}_data_dictionary.html"
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"HTML dictionary saved to: {output_file}")
    
    def export_json(self, dataset_name: str, output_path: Path) -> None:
        """Export dictionary as JSON."""
        if dataset_name not in self.dictionaries:
            raise ValueError(f"No dictionary found for dataset: {dataset_name}")
        
        output_file = output_path / f"{dataset_name}_data_dictionary.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.dictionaries[dataset_name], f, indent=2)
        
        print(f"JSON dictionary saved to: {output_file}")
    
    def export_markdown(self, dataset_name: str, output_path: Path) -> None:
        """Export dictionary as Markdown."""
        if dataset_name not in self.dictionaries:
            raise ValueError(f"No dictionary found for dataset: {dataset_name}")
        
        dictionary = self.dictionaries[dataset_name]
        
        md_lines = [
            f"# Data Dictionary: {dataset_name}",
            f"\n*Generated: {dictionary['generation_date']}*\n",
            "## Overview",
            f"\n{dictionary['overview']['description']}\n",
            f"- **Records**: {dictionary['overview']['record_count']:,}",
            f"- **Fields**: {dictionary['overview']['field_count']}",
            f"- **Size**: {dictionary['overview']['size_mb']}",
            f"- **Last Updated**: {dictionary['overview']['last_updated']}",
            "\n## Data Quality",
            f"\n- **Completeness**: {dictionary['data_quality']['overall_completeness']}",
            f"- **Quality Score**: {dictionary['data_quality']['quality_score']}",
            f"- **Duplicate Records**: {dictionary['data_quality']['duplicate_records']}",
            "\n## Column Definitions\n"
        ]
        
        for col in dictionary['columns']:
            md_lines.extend([
                f"### {col['business_name']} (`{col['technical_name']}`)",
                f"\n{col['description']}\n",
                f"- **Data Type**: {col['data_type']['sql']}",
                f"- **Nullable**: {col['nullable']}",
                f"- **Null Rate**: {col['statistics']['null_percentage']}",
                f"- **Unique Values**: {col['statistics']['unique_count']:,}",
            ])
            
            if col.get('owner'):
                md_lines.append(f"- **Owner**: {col['owner']}")
            
            if col.get('is_pii'):
                md_lines.append(f"- **⚠️ Contains PII**")
            
            if col.get('sample_values'):
                samples = ', '.join(col['sample_values'])
                md_lines.append(f"- **Sample Values**: {samples}")
            
            md_lines.append("")
        
        output_file = output_path / f"{dataset_name}_data_dictionary.md"
        with open(output_file, 'w') as f:
            f.write('\n'.join(md_lines))
        
        print(f"Markdown dictionary saved to: {output_file}")
