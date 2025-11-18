"""
Data loading module for PSM Viewer.
Handles loading and parsing of spectral data files (MGF) and identification results (mzTab).
"""

from typing import List, Dict, Any

import pandas as pd
from pyteomics import mgf, mztab


def load_mgf(file_buffer: Any) -> List[Dict[str, Any]]:
    """
    Load and parse MGF spectral data into dictionaries with error handling.

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
    Load and parse mzTab PSM results into a DataFrame with input validation.

    Args:
        file_buffer (Any): File buffer containing mzTab data.

    Returns:
        pd.DataFrame: DataFrame with PSM columns (sequence, spectra_ref, etc.).
    """
 # Parse the mzTab file using pyteomics
    tab = mztab.MzTab(file_buffer)
    # Extract the PSM section as a DataFrame for easy manipulation
    return pd.DataFrame(tab['psm'])

