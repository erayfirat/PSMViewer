
import pytest
import io
import pandas as pd
from data_loading import load_mgf, load_mztab

def test_streaming_io_compatibility():
    """
    Test that data loading functions can handle io.TextIOWrapper (streaming).
    This ensures we don't regress on memory optimization where we avoid reading
    the entire file into memory before parsing.
    """
    # Sample MGF content (bytes)
    mgf_content = b"""BEGIN IONS
TITLE=spec1
PEPMASS=450.25
1.0 10.0
END IONS
"""
    # Sample mzTab content (bytes)
    mztab_content = b"""MTD\tmzTab-version\t1.0.0
MTD\tmzTab-mode\tSummary
PSH\tsequence\tPSM_ID\tspectra_ref
PSM\tPEP1\t1\tms_run[1]:index=0
"""

    # Simulate Streamlit UploadedFile (which provides a binary stream) for MGF
    mgf_file = io.BytesIO(mgf_content)
    # Wrap in TextIOWrapper as we do in the app
    mgf_wrapper = io.TextIOWrapper(mgf_file, encoding='utf-8')

    spectra = load_mgf(mgf_wrapper)
    assert len(spectra) == 1
    assert spectra[0]['title'] == 'spec1'

    # Simulate Streamlit UploadedFile for mzTab
    mztab_file = io.BytesIO(mztab_content)
    # Wrap in TextIOWrapper
    mztab_wrapper = io.TextIOWrapper(mztab_file, encoding='utf-8')

    psm_df = load_mztab(mztab_wrapper)
    assert isinstance(psm_df, pd.DataFrame)
    assert len(psm_df) == 1
    assert psm_df.iloc[0]['sequence'] == 'PEP1'
