# Data Profiling System

Python tool for profiling datasets and generating documentation. Helps teams understand data structure, quality, and business context.

This tool was a side project I worked on while at Nokia, for automated data profiling and documentation generation. It Extracts metadata, maps business terms, identifies PII, and generates HTML/JSON/Markdown documentation.

## Features

- Statistical profiling (distributions, nulls, cardinality)
- Schema extraction and DDL generation
- Business term mapping with fuzzy matching
- PII detection
- Data quality assessment
- Multi-format output (HTML, JSON, Markdown, CSV)
- Interactive dashboard

## Quick Start

Install dependencies:
```bash
pip install pandas pyyaml jinja2 --break-system-packages
```

Run profiling:
```bash
python main.py
```

View dashboard:
```bash
streamlit run src/dashboard/app.py
```

## How It Works

The system processes data through four main components:

1. **Profiler** - Analyzes data and computes statistics
2. **Metadata Extractor** - Pulls schema and generates DDL
3. **Glossary Mapper** - Links technical names to business terms
4. **Dictionary Generator** - Creates documentation in multiple formats

## Configuration

Edit `config/profiling_config.yaml` to adjust settings:
- Quality thresholds
- Output formats
- Sampling size
- Alert conditions

Edit `config/business_terms.yaml` to define business terms:
- Column definitions
- Data owners
- PII flags
- Valid values

## Output Files

After running, check the `outputs/` directory:

- `profiles/` - JSON profiles with statistics
- `metadata/` - Schema information and DDL
- `dictionaries/` - HTML, Markdown, and CSV documentation

## Using Your Data

1. Place your CSV in the `data/` directory
2. Update `main.py` to point to your file
3. Optionally add business terms in `config/business_terms.yaml`
4. Run `python main.py`

## Example Output

The sample run on sales data (30 rows, 15 columns) produces:
- Complete statistical profile in <10 seconds
- 100% column mapping to business terms
- Identification of 2 PII columns
- Professional HTML documentation

## Tech Stack

- Python 3.9+
- pandas for data manipulation
- Streamlit for dashboard
- Jinja2 for templating
- PyYAML for configuration

## Project Structure

```
data-profiling-system/
├── src/
│   ├── profiler/          # Statistical profiling
│   ├── metadata/          # Schema extraction
│   ├── glossary/          # Term mapping
│   ├── dictionary/        # Doc generation
│   └── dashboard/         # Streamlit app
├── config/                # YAML configs
├── data/                  # Sample data
├── outputs/               # Generated files
└── main.py               # Main script
```

## Use Cases

**Dataset Onboarding** - Generate complete documentation for new data sources

**Quality Monitoring** - Track metrics over time and identify issues

**Compliance** - Detect and flag PII automatically

**Team Collaboration** - Share documentation with non-technical stakeholders

## Notes

- For large datasets (>1M rows), configure sampling in `profiling_config.yaml`
- Dashboard requires `streamlit` package (optional)
- HTML reports require no additional dependencies

## License

MIT
