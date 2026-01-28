import io
import pytest
import pandas as pd
from data_loading import load_mgf, load_mztab

class TestStreamingIO:
    """
    Test suite to ensure that data loading functions support streaming I/O.
    This validates the optimization of using TextIOWrapper instead of reading
    entire files into memory.
    """

    def test_load_mgf_streaming(self):
        """Test load_mgf with io.TextIOWrapper wrapping a binary stream."""
        mgf_content = b"""BEGIN IONS
TITLE=test_spectrum
PEPMASS=450.25
1.0 10.0
2.0 20.0
END IONS
"""
        # Simulate binary stream (like Streamlit's UploadedFile)
        binary_stream = io.BytesIO(mgf_content)

        # Wrap with TextIOWrapper to simulate streaming text decoding
        text_stream = io.TextIOWrapper(binary_stream, encoding='utf-8')

        # This should not raise an error
        spectra = load_mgf(text_stream)

        assert len(spectra) == 1
        assert spectra[0]['title'] == 'test_spectrum'
        assert spectra[0]['pepmass'] == (450.25, None)
        assert len(spectra[0]['mz_array']) == 2

    def test_load_mztab_streaming(self):
        """Test load_mztab with io.TextIOWrapper wrapping a binary stream."""
        mztab_content = b"""MTD\tmzTab-version\t1.0.0
MTD\tmzTab-mode\tSummary
PSH\tsequence\tPSM_ID\tspectra_ref
PSM\tPEPTIDE_SEQ\t1\tms_run[1]:index=0
"""
        # Simulate binary stream
        binary_stream = io.BytesIO(mztab_content)

        # Wrap with TextIOWrapper
        text_stream = io.TextIOWrapper(binary_stream, encoding='utf-8')

        # This should not raise an error
        df = load_mztab(text_stream)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]['sequence'] == 'PEPTIDE_SEQ'
        assert df.iloc[0]['spectra_ref'] == 'ms_run[1]:index=0'
