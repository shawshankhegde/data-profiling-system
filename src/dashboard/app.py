"""
Interactive Data Profiling Dashboard
Streamlit application for exploring profiling results.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.profiler.data_profiler import DataProfiler
from src.metadata.extractor import MetadataExtractor
from src.glossary.term_mapper import TermMapper
from src.dictionary.generator import DictionaryGenerator
import yaml


def load_config():
    """Load configuration files."""
    base_path = Path(__file__).parent.parent.parent
    config_path = base_path / 'config' / 'profiling_config.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_results():
    """Load profiling results from outputs directory."""
    base_path = Path(__file__).parent.parent.parent
    outputs_path = base_path / 'outputs'
    
    results = {
        'profiles': {},
        'metadata': {},
        'dictionaries': {}
    }
    
    # Load profiles
    profiles_path = outputs_path / 'profiles'
    if profiles_path.exists():
        for file in profiles_path.glob('*_profile.json'):
            with open(file, 'r') as f:
                dataset_name = file.stem.replace('_profile', '')
                results['profiles'][dataset_name] = json.load(f)
    
    # Load metadata
    metadata_path = outputs_path / 'metadata'
    if metadata_path.exists():
        for file in metadata_path.glob('*_metadata.json'):
            with open(file, 'r') as f:
                dataset_name = file.stem.replace('_metadata', '')
                results['metadata'][dataset_name] = json.load(f)
    
    # Load dictionaries
    dicts_path = outputs_path / 'dictionaries'
    if dicts_path.exists():
        for file in dicts_path.glob('*_data_dictionary.json'):
            with open(file, 'r') as f:
                dataset_name = file.stem.replace('_data_dictionary', '')
                results['dictionaries'][dataset_name] = json.load(f)
    
    return results


def main():
    """Main dashboard function."""
    st.set_page_config(
        page_title="Data Profiling Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Title
    st.title("Data Profiling Dashboard")
    st.markdown("---")
    
    # Load results
    results = load_results()
    
    if not results['profiles']:
        st.warning("⚠️ No profiling results found. Please run main.py first to generate profiles.")
        st.code("python main.py", language="bash")
        return
    
    # Sidebar - Dataset Selection
    st.sidebar.title("Navigation")
    dataset_names = list(results['profiles'].keys())
    selected_dataset = st.sidebar.selectbox("Select Dataset", dataset_names)
    
    # Sidebar - View Selection
    view = st.sidebar.radio(
        "Select View",
        ["Overview", "Data Quality", "Column Details", "Business Glossary", "Metadata"]
    )
    
    # Get selected dataset data
    profile = results['profiles'].get(selected_dataset, {})
    metadata = results['metadata'].get(selected_dataset, {})
    dictionary = results['dictionaries'].get(selected_dataset, {})
    
    # Display selected view
    if view == "Overview":
        show_overview(profile, metadata, dictionary)
    elif view == "Data Quality":
        show_data_quality(profile)
    elif view == "Column Details":
        show_column_details(profile, dictionary)
    elif view == "Business Glossary":
        show_business_glossary(dictionary)
    elif view == "Metadata":
        show_metadata(metadata)


def show_overview(profile, metadata, dictionary):
    """Display overview dashboard."""
    st.header("Dataset Overview")
    
    basic_info = profile.get('basic_info', {})
    quality = profile.get('data_quality', {})
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rows", f"{basic_info.get('row_count', 0):,}")
    
    with col2:
        st.metric("Total Columns", basic_info.get('column_count', 0))
    
    with col3:
        st.metric("Memory Usage", f"{basic_info.get('memory_usage_mb', 0):.2f} MB")
    
    with col4:
        st.metric("Completeness", f"{quality.get('overall_completeness', 0):.1f}%")
    
    st.markdown("---")
    
    # Data Type Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Data Type Distribution")
        dtypes = basic_info.get('dtypes', {})
        if dtypes:
            dtype_df = pd.DataFrame([
                {'Data Type': dtype, 'Count': list(dtypes.values()).count(dtype)}
                for dtype in set(dtypes.values())
            ])
            
            fig = px.pie(dtype_df, values='Count', names='Data Type', 
                        title="Column Data Types")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Data Quality Metrics")
        
        quality_metrics = {
            'Completeness': quality.get('overall_completeness', 0),
            'Uniqueness': 100 - (basic_info.get('duplicate_rows', 0) / basic_info.get('row_count', 1) * 100),
        }
        
        fig = go.Figure(data=[
            go.Bar(x=list(quality_metrics.keys()), 
                   y=list(quality_metrics.values()),
                   marker_color=['#667eea', '#51cf66'])
        ])
        fig.update_layout(title="Quality Scores (%)", yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
    
    # Column Statistics
    st.subheader("📋 Column Statistics")
    column_profiles = profile.get('column_profiles', {})
    
    if column_profiles:
        col_stats = []
        for col_name, col_prof in column_profiles.items():
            col_stats.append({
                'Column': col_name,
                'Data Type': col_prof.get('data_type', ''),
                'Null %': f"{col_prof.get('null_percentage', 0):.1f}%",
                'Unique': col_prof.get('unique_count', 0),
                'Unique %': f"{col_prof.get('unique_percentage', 0):.1f}%",
            })
        
        df_stats = pd.DataFrame(col_stats)
        st.dataframe(df_stats, use_container_width=True, hide_index=True)


def show_data_quality(profile):
    """Display data quality analysis."""
    st.header("🔍 Data Quality Analysis")
    
    quality = profile.get('data_quality', {})
    column_profiles = profile.get('column_profiles', {})
    
    # Quality Issues
    st.subheader("⚠️ Quality Issues")
    issues = quality.get('quality_issues', [])
    
    if issues:
        for issue in issues:
            severity_color = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(issue.get('severity', 'low'), '⚪')
            
            st.warning(f"{severity_color} **{issue['column']}**: {issue['issue']} - {issue.get('value', '')}")
    else:
        st.success("✅ No data quality issues detected!")
    
    st.markdown("---")
    
    # Null Analysis
    st.subheader("📊 Null Value Analysis")
    
    null_data = []
    for col_name, col_prof in column_profiles.items():
        null_pct = col_prof.get('null_percentage', 0)
        if null_pct > 0:
            null_data.append({
                'Column': col_name,
                'Null Count': col_prof.get('null_count', 0),
                'Null Percentage': null_pct
            })
    
    if null_data:
        df_nulls = pd.DataFrame(null_data).sort_values('Null Percentage', ascending=False)
        
        fig = px.bar(df_nulls, x='Column', y='Null Percentage',
                     title='Null Percentage by Column',
                     color='Null Percentage',
                     color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df_nulls, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No null values detected in the dataset!")
    
    # Duplicate Analysis
    st.markdown("---")
    st.subheader("🔄 Duplicate Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        dup_count = quality.get('duplicate_rows_count', 0)
        dup_pct = quality.get('duplicate_rows_percentage', 0)
        st.metric("Duplicate Rows", f"{dup_count:,}", f"{dup_pct:.2f}%")
    
    with col2:
        if dup_count > 0:
            st.warning(f"Found {dup_count:,} duplicate rows ({dup_pct:.2f}% of total)")
        else:
            st.success("No duplicate rows detected")


def show_column_details(profile, dictionary):
    """Display detailed column information."""
    st.header("📋 Column Details")
    
    columns_dict = dictionary.get('columns', [])
    column_profiles = profile.get('column_profiles', {})
    
    if not columns_dict:
        st.warning("No column information available")
        return
    
    # Column selector
    column_names = [col['technical_name'] for col in columns_dict]
    selected_column = st.selectbox("Select Column", column_names)
    
    # Find selected column data
    col_data = next((col for col in columns_dict if col['technical_name'] == selected_column), None)
    col_profile = column_profiles.get(selected_column, {})
    
    if col_data:
        st.markdown("---")
        
        # Column Header
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(f"📌 {col_data['business_name']}")
            st.caption(f"Technical Name: `{col_data['technical_name']}`")
        
        with col2:
            st.info(f"**Type**: {col_data['data_type']['sql']}")
        
        # Description
        if col_data.get('description'):
            st.markdown(f"*{col_data['description']}*")
        
        # Badges
        badges = []
        if col_data.get('is_pii'):
            badges.append("🔒 PII")
        if col_data.get('is_unique'):
            badges.append("🔑 UNIQUE")
        if col_data.get('nullable'):
            badges.append("⚠️ NULLABLE")
        
        if badges:
            st.markdown(" | ".join(badges))
        
        st.markdown("---")
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        stats = col_data.get('statistics', {})
        
        with col1:
            st.metric("Null Rate", stats.get('null_percentage', 'N/A'))
        
        with col2:
            st.metric("Unique Values", f"{stats.get('unique_count', 0):,}")
        
        with col3:
            st.metric("Unique Rate", stats.get('unique_percentage', 'N/A'))
        
        with col4:
            if col_data.get('owner'):
                st.metric("Owner", col_data['owner'])
        
        # Numeric Statistics
        if 'min' in stats:
            st.markdown("---")
            st.subheader("📊 Numeric Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Minimum", f"{stats.get('min', 0):.2f}")
            with col2:
                st.metric("Maximum", f"{stats.get('max', 0):.2f}")
            with col3:
                st.metric("Mean", f"{stats.get('mean', 0):.2f}")
            with col4:
                st.metric("Median", f"{stats.get('median', 0):.2f}")
        
        # Sample Values
        if col_data.get('sample_values'):
            st.markdown("---")
            st.subheader("📝 Sample Values")
            samples = col_data['sample_values']
            st.code(", ".join(str(s) for s in samples))
        
        # Top Values (for categorical)
        if col_profile.get('top_values'):
            st.markdown("---")
            st.subheader("📈 Top Values")
            
            top_vals = col_profile['top_values']
            df_top = pd.DataFrame([
                {'Value': k, 'Count': v}
                for k, v in list(top_vals.items())[:10]
            ])
            
            fig = px.bar(df_top, x='Value', y='Count', title='Top 10 Values')
            st.plotly_chart(fig, use_container_width=True)


def show_business_glossary(dictionary):
    """Display business glossary."""
    st.header("📚 Business Glossary")
    
    columns = dictionary.get('columns', [])
    
    if not columns:
        st.warning("No glossary information available")
        return
    
    # Summary metrics
    total = len(columns)
    mapped = sum(1 for col in columns if col.get('description') and 
                 col['description'] != 'No description available')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Terms", total)
    
    with col2:
        st.metric("Mapped Terms", mapped)
    
    with col3:
        st.metric("Coverage", f"{(mapped/total*100):.1f}%")
    
    st.markdown("---")
    
    # Glossary table
    st.subheader("📖 Term Definitions")
    
    glossary_data = []
    for col in columns:
        glossary_data.append({
            'Technical Name': col['technical_name'],
            'Business Name': col['business_name'],
            'Definition': col.get('description', 'N/A'),
            'Owner': col.get('owner', 'Unassigned'),
            'PII': '🔒' if col.get('is_pii') else ''
        })
    
    df_glossary = pd.DataFrame(glossary_data)
    st.dataframe(df_glossary, use_container_width=True, hide_index=True)
    
    # PII columns
    pii_columns = [col['technical_name'] for col in columns if col.get('is_pii')]
    
    if pii_columns:
        st.markdown("---")
        st.subheader("🔒 PII Columns")
        st.warning(f"The following columns contain Personally Identifiable Information (PII):")
        for col in pii_columns:
            st.write(f"- {col}")


def show_metadata(metadata):
    """Display technical metadata."""
    st.header("⚙️ Technical Metadata")
    
    # Schema Information
    st.subheader("📐 Schema")
    
    schema = metadata.get('schema', [])
    if schema:
        schema_data = []
        for col in schema:
            schema_data.append({
                'Column': col['column_name'],
                'Data Type': col['data_type'],
                'SQL Type': col['sql_type'],
                'Nullable': '✓' if col['nullable'] else '✗',
                'Unique': '✓' if col['is_unique'] else '✗',
                'Position': col['position']
            })
        
        df_schema = pd.DataFrame(schema_data)
        st.dataframe(df_schema, use_container_width=True, hide_index=True)
    
    # Statistics
    st.markdown("---")
    st.subheader("📊 Dataset Statistics")
    
    stats = metadata.get('statistics', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Row Count", f"{stats.get('row_count', 0):,}")
    
    with col2:
        st.metric("Column Count", stats.get('column_count', 0))
    
    with col3:
        memory_mb = stats.get('memory_usage_bytes', 0) / (1024 * 1024)
        st.metric("Memory Usage", f"{memory_mb:.2f} MB")
    
    # Lineage
    if metadata.get('lineage'):
        st.markdown("---")
        st.subheader("🔗 Data Lineage")
        
        lineage = metadata['lineage']
        
        if lineage.get('upstream_sources'):
            st.write("**Upstream Sources:**")
            for source in lineage['upstream_sources']:
                st.write(f"- {source.get('source_system', 'Unknown')}: {source.get('source_table', 'N/A')}")


if __name__ == "__main__":
    main()
