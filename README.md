# PSM Viewer

A minimal tool for viewing and analyzing Peptide-Spectrum Matches (PSMs) from mass spectrometry data. This application loads MGF spectra files and mzTab PSM results, maps them together, and provides both command-line and web-based interfaces for visualization.

## Features

- Load and parse MGF mass spectrometry spectra files
- Parse mzTab format PSM results
- Map PSMs to corresponding spectra using various matching strategies
- Compute theoretical b and y ion fragments for peptide sequences
- Annotate spectra with matched theoretical fragments
- Command-line interface for batch processing
- Interactive Streamlit web app with spectrum visualization plots

## Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

## Usage

### Command Line Interface

Run the CLI version to process data and get summary statistics:
```bash
python3 app.py
```

This will load the default data files (`data/sample_preprocessed_spectra.mgf` and `data/casanovo_20251029091517.mztab`) and display mapping results.

### Streamlit Web App

Launch the interactive web application:
```bash
python3 -m streamlit run app.py -- --streamlit
```

The web app allows you to:
- Upload your own MGF and mzTab files
- View PSM-to-spectrum mappings in a table
- Select individual PSMs to visualize their spectra
- See annotated peaks for theoretical b and y ions

## Data Formats

- **MGF (Mascot Generic Format)**: Contains mass spectrometry spectra with m/z and intensity values
- **mzTab**: Tab-separated format for proteomics results, containing PSM information including peptide sequences and spectrum references

## Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`:
  - streamlit
  - pyteomics
  - matplotlib
  - numpy
  - pandas
  - spectrum-utils
  - lxml

## Project Structure

```
├── app.py                 # Main application script
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── data/
    ├── sample_preprocessed_spectra.mgf    # Example MGF file
    └── casanovo_20251029091517.mztab      # Example mzTab file
```

## License

MIT License - see LICENSE file for details (if applicable)
