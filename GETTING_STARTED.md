# Getting Started

## Installation

1. Install Python dependencies:
```bash
cd data-profiling-system
pip install -r requirements.txt
```

2. Verify installation:
```bash
python --version  # Should be 3.9+
```

## Running the System

### Option 1: Full Pipeline

Run the complete profiling process:

```bash
python main.py
```

This will:
- Profile the sample sales dataset
- Extract technical metadata
- Map columns to business terms
- Generate data dictionaries in HTML, JSON, and Markdown
- Save all outputs to the `outputs/` directory

Takes about 10-30 seconds on the sample data.

### Option 2: Interactive Dashboard

Launch the dashboard to explore results:

```bash
streamlit run src/dashboard/app.py
```

Opens in your browser at `http://localhost:8501`

The dashboard includes:
- Dataset overview and stats
- Data quality analysis
- Column details
- Business glossary viewer
- Technical metadata

## Understanding the Output

After running `main.py`, check the `outputs/` directory:

### Data Profiles (`outputs/profiles/`)
- `sample_sales_data_profile.json` - Statistical analysis

### Metadata (`outputs/metadata/`)
- `sample_sales_data_metadata.json` - Schema information and DDL

### Data Dictionaries (`outputs/dictionaries/`)
- `sample_sales_data_data_dictionary.html` - Main documentation (open this in browser)
- `sample_sales_data_data_dictionary.json` - Machine-readable format
- `sample_sales_data_data_dictionary.md` - Markdown version
- `sample_sales_data_glossary.csv` - Business term mappings

## Using Your Own Data

1. Add your CSV file to the `data/` directory:
```bash
cp your_data.csv data/
```

2. Update `main.py` to point to your file (line 43):
```python
data_path = base_path / 'data' / 'your_data.csv'
```

3. (Optional) Add business definitions in `config/business_terms.yaml`:

```yaml
terms:
  your_column_name:
    business_name: "Your Business Term"
    definition: "What this column means"
    data_type: "String"
    owner: "Team Name"
    is_pii: false
    examples:
      - "Example 1"
      - "Example 2"
```

4. Run profiling:
```bash
python main.py
```

## Configuration

### Profiling Settings (`config/profiling_config.yaml`)

```yaml
profiling:
  statistical_analysis: true
  data_quality_checks: true
  pattern_detection: true
  
  quality_thresholds:
    max_null_percentage: 10
    min_unique_values: 2
    max_cardinality: 1000
```

### Business Terms (`config/business_terms.yaml`)

Add your domain-specific terms and definitions here.

## Common Tasks

### Generate Documentation for New Dataset
```bash
# Add your data
cp new_data.csv data/

# Update main.py path
# Run profiling
python main.py

# Share the HTML dictionary
open outputs/dictionaries/*_data_dictionary.html
```

### Monitor Data Quality
```bash
# Run profiling
python main.py

# Review issues in dashboard
streamlit run src/dashboard/app.py
# Navigate to "Data Quality" tab
```

### Find PII Columns
```bash
# Run profiling
python main.py

# Check dashboard or review the HTML dictionary
# PII columns are marked with 🔒
```

## Troubleshooting

### Module Not Found Error

Make sure you're in the project directory:
```bash
cd data-profiling-system
pip install -r requirements.txt
```

### YAML Syntax Errors

Check your `business_terms.yaml`:
- Use spaces for indentation, not tabs
- Quote strings with special characters
- Validate at yamllint.com

### Memory Issues with Large Datasets

Adjust sampling in `config/profiling_config.yaml`:
```yaml
profiling:
  sample_size: 100000  # Profile first 100k rows
```

### Dashboard Shows No Data

Run profiling first to generate outputs:
```bash
python main.py
streamlit run src/dashboard/app.py
```

## Example Workflow

Typical usage for a new dataset:

1. Add data file to `data/` directory
2. Run `python main.py` to profile
3. Review HTML dictionary for overview
4. Add business terms to `config/business_terms.yaml` if needed
5. Re-run to update documentation
6. Share HTML dictionary with team

## Notes

- Sample data is included in `data/sample_sales_data.csv`
- All outputs go to `outputs/` directory
- HTML dictionaries can be opened directly in any browser
- Dashboard requires active Python session
