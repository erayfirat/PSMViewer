"""
PSM Viewer - A Streamlit web app for visualizing peptide-spectrum matches.
Run with: streamlit run app.py
"""

import re
import io
from typing import List, Dict, Any

import pandas as pd
from pyteomics import mgf, mztab

from spectrum_utils import plot as sup
from spectrum_utils import spectrum as sus
from matplotlib import pyplot as plt

import streamlit as st


# ---- Data loading functions ----

def load_mgf(file_buffer: Any) -> List[Dict[str, Any]]:
    """
    Load and parse MGF spectral data into dictionaries.

    Args:
        file_buffer (Any): File buffer containing MGF data.

    Returns:
        List[Dict]: List of spectrum dicts with title, pepmass, mz_array, intensity_array.
    """
    specs = []
    with mgf.read(file_buffer, use_index=False) as reader:
        # Iterate through each spectrum in the MGF file
        for s in reader:
            # Extract header parameters (TITLE, PEPMASS, etc.)
            params = s.get('params', {})
            # Get the spectrum title/identifier
            title = params.get('title')
            # Get the precursor ion mass information
            pepmass = params.get('pepmass')

            # Store spectrum data in a standardized dictionary format
            specs.append({
                'title': str(title) if title else None,
                'pepmass': pepmass,
                'mz_array': s.get('m/z array'),  # Mass-to-charge ratios
                'intensity_array': s.get('intensity array')  # Peak intensities
            })
    return specs


def load_mztab(file_buffer: Any) -> pd.DataFrame:
    """
    Load and parse mzTab PSM results into a DataFrame.

    Args:
        file_buffer (Any): File buffer containing mzTab data.

    Returns:
        pd.DataFrame: DataFrame with PSM columns (sequence, spectra_ref, etc.).
    """
    # Parse the mzTab file using pyteomics
    tab = mztab.MzTab(file_buffer)
    # Extract the PSM section as a DataFrame for easy manipulation
    return pd.DataFrame(tab['psm'])


def extract_index_from_spectra_ref(s: str) -> str:
    """
    Extract numeric spectrum identifier from various reference formats.

    Args:
        s (str): Spectrum reference string.

    Returns:
        str or None: Extracted numeric identifier or None.
    """
    if s is None:
        return None

    # Pattern 1: Look for "index=123" format
    match = re.search(r'index=(\d+)', s)
    if match:
        return match.group(1)

    # Pattern 2: Look for "scan=456" format
    match = re.search(r'scan=(\d+)', s)
    if match:
        return match.group(1)

    # Pattern 3: Look for ":789" suffix format
    match = re.search(r':(\d+)$', s)
    if match:
        return match.group(1)

    # Pattern 4: Check if the entire string is numeric
    match = re.match(r'^\d+$', s)
    if match:
        return s

    # No numeric identifier found
    return None


# ---- High-level pipeline ----

def map_psms_to_spectra(spectra: List[Dict], psm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Map PSMs to their corresponding spectra by title or index.

    Args:
        spectra (List[Dict]): List of spectrum dictionaries.
        psm_df (pd.DataFrame): DataFrame with PSM data.

    Returns:
        pd.DataFrame: Mapping with psm_index, sequence, spectra_ref, matched_title, etc.
    """
    # Create lookup dictionaries for efficient title and index-based matching
    # Title lookup: Map spectrum titles to spectrum objects (skip spectra without titles)
    title_to_spec = {s['title']: s for s in spectra if s['title']}
    # Index lookup: Map array indices to spectra for index-based matching
    index_to_spec = {str(i): spectra[i] for i in range(len(spectra))}

    mappings = []
    # Process each PSM in the identification results
    for i, row in psm_df.iterrows():
        # Extract spectrum reference from PSM data
        spec_ref = str(row.get('spectra_ref', ''))

        # Attempt matching: first by title (direct string match)
        matched_spec = title_to_spec.get(spec_ref) or \
                      index_to_spec.get(extract_index_from_spectra_ref(spec_ref))

        # Create mapping entry with all relevant data
        mappings.append({
            'psm_index': i,
            'sequence': str(row.get('sequence', '')),
            'spectra_ref': spec_ref,
            'matched_title': matched_spec['title'] if matched_spec else None,
            'mz_array': matched_spec.get('mz_array') if matched_spec else None,
            'intensity_array': matched_spec.get('intensity_array') if matched_spec else None,
            'pepmass': matched_spec.get('pepmass') if matched_spec else None
        })
    return pd.DataFrame(mappings)


def draw_spectrum(row, mz, inten):
    """
    Generate annotated spectrum plot with b/y-ion fragment annotations.

    Args:
        row (pd.Series): PSM row with spectrum data.
        mz (numpy.ndarray): Mass-to-charge ratios.
        inten (numpy.ndarray): Peak intensities.

    Returns:
        matplotlib.figure.Figure: Annotated spectrum plot.
    """
    # Create matplotlib figure with standard size for spectrum visualization
    fig, ax = plt.subplots(figsize=(12, 6))

    # Set descriptive title combining spectrum identifier and peptide sequence
    ax.set_title(f"Spectrum {row['matched_title']} — Sequence: {row['sequence']}")

    # Apply clean styling: remove top and right spines for modern appearance
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    # Extract precursor ion mass-to-charge ratio for processing
    precursor_mz = float(row['pepmass'][0])
    # Assume doubly charged precursor (common for tryptic peptides)
    charge = 2

    # Create spectrum-utils MsmsSpectrum object for advanced processing
    spec = sus.MsmsSpectrum(row['matched_title'], precursor_mz, charge, mz, inten)

    # Process spectrum for optimal visualization:
    # 1. Limit m/z range to typical peptide fragment masses (100-1400 Da)
    # 2. Remove precursor peak (within 10 ppm tolerance) to reduce interference
    # 3. Filter to most intense peaks for clarity (max 50 peaks)
    # 4. Apply square root scaling to compress dynamic range
    # 5. Annotate theoretical b and y fragment ions (10 ppm tolerance)
    fragment_tol_mass, fragment_tol_mode = 10, "ppm"
    spec = (
        spec.set_mz_range(min_mz=100, max_mz=1400)
        .remove_precursor_peak(fragment_tol_mass, fragment_tol_mode)
        .filter_intensity(min_intensity=0.05, max_num_peaks=50)
        .scale_intensity("root")
        .annotate_proforma(row['sequence'], fragment_tol_mass, fragment_tol_mode, ion_types="aby")
    )

    # Render the processed spectrum using spectrum-utils plotting interface
    sup.spectrum(spec, grid=False, ax=ax)
    return fig


# ---- Streamlit app ----

def run_streamlit_app():
    """
    Main Streamlit application for interactive PSM visualization.

    Handles file uploads, data processing, and spectrum visualization.
    Provides web interface for PSM-spectrum matching and plotting.
    """
    # Set application title
    st.title('PSM Viewer App')

    # File upload widgets for MGF (spectra) and mzTab (identifications)
    mgf_file = st.file_uploader('Upload MGF file', type=['mgf'])
    mztab_file = st.file_uploader('Upload mzTab file', type=['mztab', 'mztab.txt'])

    # Process files only when both are uploaded
    if mgf_file and mztab_file:
        # Decode uploaded file contents (Streamlit files are bytes by default)
        # Use StringIO to create file-like objects for pyteomics parsers
        spectra = load_mgf(io.StringIO(mgf_file.read().decode('utf-8')))
        psm_df = load_mztab(io.StringIO(mztab_file.read().decode('utf-8')))

        # Create mappings between PSMs and spectra
        mapped = map_psms_to_spectra(spectra, psm_df)

        # Display summary statistics
        st.write(f"Loaded {len(spectra)} spectra and {len(psm_df)} PSMs. Matches: {mapped['matched_title'].notnull().sum()}")

        # Show interactive table of PSM-to-spectrum mappings
        # Display only key columns for readability
        st.dataframe(mapped[['psm_index', 'sequence', 'matched_title']])

        # PSM selection widget (numeric index from the mapping table)
        sel = st.number_input(
            'Select PSM index',
            min_value=0,
            max_value=len(mapped)-1,
            value=0
        )

        # Extract selected PSM row
        row = mapped.iloc[int(sel)]

        # Visualize spectrum if a matching spectrum was found
        if row['matched_title']:
            # Generate annotated spectrum plot
            fig = draw_spectrum(row, row['mz_array'], row['intensity_array'])
            # Display in Streamlit app
            st.pyplot(fig)
        else:
            # Handle case where no matching spectrum was found
            st.warning('No matching spectrum found')


# ---- Application entry point ----

if __name__ == '__main__':
    run_streamlit_app()
