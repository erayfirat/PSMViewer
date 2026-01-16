"""
Processing module for PSM Viewer.
Contains functions for extracting spectrum indices and mapping PSMs to spectra using vectorized operations.
"""

import re
import pandas as pd
from typing import List, Dict, Optional


# Pre-compile regex patterns for performance (re-used across calls)
# Pattern 1-3: index=, scan=, :suffix
_REF_PATTERN = re.compile(r'index=(\d+)|scan=(\d+)|:(\d+)$')
# Pattern 4: full numeric
_NUMERIC_PATTERN = re.compile(r'^\d+$')

# Default spectrum dictionary for missing matches (ensures consistent schema with None values)
_DEFAULT_SPEC = {'title': None, 'mz_array': None, 'intensity_array': None, 'pepmass': None}


def extract_index_from_spectra_ref(s: Optional[str]) -> Optional[str]:
    """
    Extract numeric spectrum identifier from various reference formats.

    Args:
        s (str): Spectrum reference string.

    Returns:
        str or None: Extracted numeric identifier or None.
    """
    if s is None:
        return None

    # Combined regex with prioritized patterns: index=, scan=, :suffix, full numeric
    match = _REF_PATTERN.search(s)
    if match:
        # Return the first non-None group (index and scan have their own groups)
        if match.group(1):  # index=
            return match.group(1)
        elif match.group(2):  # scan=
            return match.group(2)
        elif match.group(3):  # :suffix
            return match.group(3)

    # Pattern 4: Check if the entire string is numeric
    if _NUMERIC_PATTERN.match(s):
        return s

    # No numeric identifier found
    return None


def map_psms_to_spectra(spectra: List[Dict], psm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Map PSMs to their corresponding spectra by title or index, using vectorized operations where possible.

    Args:
        spectra (List[Dict]): List of spectrum dictionaries.
        psm_df (pd.DataFrame): DataFrame with PSM data.

    Returns:
        pd.DataFrame: Mapping with psm_index, sequence, spectra_ref, matched_title, etc.
    """
    # Handle empty DataFrame
    if psm_df.empty:
        return pd.DataFrame(columns=['psm_index', 'sequence', 'spectra_ref', 'matched_title', 'mz_array', 'intensity_array', 'pepmass'])

    # Ensure required columns exist
    if 'spectra_ref' not in psm_df.columns or 'sequence' not in psm_df.columns:
        raise ValueError("PSM DataFrame must have 'spectra_ref' and 'sequence' columns")

    # Create lookup dictionaries for efficient title and index-based matching
    # Title lookup: Map spectrum titles to spectrum objects (skip spectra without titles)
    title_to_spec = {s['title']: s for s in spectra if s['title']}
    # Index lookup: Map array indices to spectra for index-based matching
    index_to_spec = {str(i): spectra[i] for i in range(len(spectra))}

    # Workflow: PSM-to-Spectrum Mapping
    # 1. Extract numeric indices from spectra_ref strings
    psm_df = psm_df.copy()  # Avoid modifying original DataFrame

    # ⚡ OPTIMIZATION: Use vectorized regex extraction instead of row-by-row apply
    # Original: psm_df['extracted_index'] = psm_df['spectra_ref'].astype(str).apply(extract_index_from_spectra_ref)

    # Patterns: index=(\d+), scan=(\d+), :(\d+)$ or ^(\d+)$
    pattern = r'index=(\d+)|scan=(\d+)|:(\d+)$|^(\d+)$'
    extracted = psm_df['spectra_ref'].astype(str).str.extract(pattern)

    # Select first non-null match from the groups
    # bfill(axis=1) fills holes backward (right-to-left), ensuring the first match propagates to column 0
    psm_df['extracted_index'] = extracted.bfill(axis=1).iloc[:, 0]

    # 2. Match by title first, then by extracted index
    # title_match: direct title lookup
    # index_match: fallback to numeric index lookup
    # combine_first: use index_match only where title_match is NaN
    matched_spec_series = (
        psm_df['spectra_ref'].map(title_to_spec, na_action='ignore')
        .combine_first(psm_df['extracted_index'].map(index_to_spec, na_action='ignore'))
    )

    # ⚡ OPTIMIZATION: Convert list of dicts to DataFrame directly instead of repeated apply calls
    # Original: Multiple apply calls (4x iteration over full dataset)
    # Improvement: Use .tolist() for faster iteration and explicit columns to skip schema inference.
    # Also use _DEFAULT_SPEC to ensure missing rows have None instead of NaN for correct logic in app.py.

    # Convert matched Series to list, replacing NaNs with default dict for DataFrame construction
    specs_list = [x if isinstance(x, dict) else _DEFAULT_SPEC for x in matched_spec_series.tolist()]

    specs_df = pd.DataFrame(specs_list, columns=['title', 'mz_array', 'intensity_array', 'pepmass'])
    specs_df.index = psm_df.index  # Align index with original DataFrame

    mappings = pd.DataFrame({
        'psm_index': psm_df.index,
        'sequence': psm_df['sequence'].astype(str),
        'spectra_ref': psm_df['spectra_ref'].astype(str),
        'matched_title': specs_df['title'],
        'mz_array': specs_df['mz_array'],
        'intensity_array': specs_df['intensity_array'],
        'pepmass': specs_df['pepmass']
    })

    return mappings
