# PSM Viewer

A Streamlit web application for viewing and analyzing Peptide-Spectrum Matches (PSMs) from mass spectrometry data. This application allows users to upload MGF spectra files and mzTab PSM results, maps them together, and provides interactive visualization of spectra with annotated peptide fragments.

## Features

- Upload and parse MGF mass spectrometry spectra files
- Upload and parse mzTab format PSM results
- Map PSMs to corresponding spectra using title or index matching
- Display PSM-to-spectrum mappings in an interactive table
- Visualize individual spectra with annotated b and y ion fragments
- Interactive spectrum plots showing precursor peaks and theoretical fragments

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

Launch the interactive web application:
```bash
streamlit run app.py
```

The web app allows you to:
- Upload your own MGF and mzTab files
- View PSM-to-spectrum mappings in an interactive table
- Select individual PSMs by index to visualize their spectra
- See annotated spectrum plots with theoretical b and y ion fragments

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
└── README.md             # This file
```

## License

MIT License - see LICENSE file for details (if applicable)
