# Data Profiling System - Overview

## Summary

Python-based data profiling tool that generates documentation for datasets. Designed to help teams understand data structure, quality, and business context without manual documentation effort.

## What's Included

**Source Code** (~2,200 lines Python)
- Data profiler with statistical analysis
- Metadata extractor with DDL generation
- Business glossary mapper
- Dictionary generator (HTML, JSON, Markdown)
- Interactive Streamlit dashboard

**Documentation**
- README.md - Project overview
- GETTING_STARTED.md - Setup and usage guide

**Configuration**
- profiling_config.yaml - System settings
- business_terms.yaml - Business glossary definitions

**Sample Data**
- sample_sales_data.csv - 30-row example dataset

## Key Features

- Statistical profiling (distributions, nulls, cardinality, correlations)
- Schema extraction and SQL DDL generation
- Fuzzy matching for business term mapping
- PII detection
- Data quality scoring
- Multi-format output generation

## Quick Start

```bash
# Install
pip install pandas pyyaml jinja2 --break-system-packages

# Run
python main.py

# View dashboard
streamlit run src/dashboard/app.py
```

## Use Cases

**Dataset Onboarding** - Generate documentation for new data sources

**Quality Monitoring** - Track data quality metrics over time

**Compliance** - Identify and flag PII columns

**Team Collaboration** - Share HTML documentation with stakeholders

## Technical Details

Built with:
- Python 3.9+
- pandas for data manipulation
- Streamlit for dashboard
- Jinja2 for HTML templating
- PyYAML for configuration

Architecture:
- Modular design with 4 independent components
- Configuration-driven via YAML files
- Supports sampling for large datasets
- Extensible for additional data sources

## Project Structure

```
data-profiling-system/
├── src/
│   ├── profiler/          # Statistical analysis
│   ├── metadata/          # Schema extraction
│   ├── glossary/          # Business term mapping
│   ├── dictionary/        # Documentation generation
│   └── dashboard/         # Streamlit application
├── config/                # YAML configuration
├── data/                  # Sample datasets
├── outputs/               # Generated files
└── main.py               # Pipeline orchestration
```

## Generated Outputs

Running on the sample dataset produces:

- **Profile JSON** - Statistical summary of dataset
- **Metadata JSON** - Schema information and DDL
- **HTML Dictionary** - Professional documentation page
- **Markdown Dictionary** - Documentation-site ready
- **CSV Glossary** - Business term mappings

## Configuration

Customize behavior via YAML configs:

**profiling_config.yaml** - Set quality thresholds, output formats, sampling

**business_terms.yaml** - Define business terms, owners, PII flags

## Extending the System

The modular design allows easy extension:

- Add database connectors (PostgreSQL, MySQL, etc.)
- Integrate with data catalogs
- Schedule with Airflow or similar
- Add ML-based PII detection
- Implement schema drift detection

## Notes

- Tested on datasets from 30 rows to 1M+ rows
- Configurable sampling for large datasets
- Dashboard requires active Python session
- HTML output viewable in any browser

## License

MIT
