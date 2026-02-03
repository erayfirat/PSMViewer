import io
import pytest
from data_loading import load_mgf, load_mztab

def test_load_mgf_with_textiowrapper():
    """Verify that load_mgf works with io.TextIOWrapper (streaming)."""
    mgf_content = """BEGIN IONS
TITLE=test_stream
PEPMASS=100.0
10.0 1.0
20.0 2.0
END IONS
"""
    # Create a bytes stream (simulating file on disk or uploaded file)
    bytes_stream = io.BytesIO(mgf_content.encode('utf-8'))

    # Wrap with TextIOWrapper
    text_stream = io.TextIOWrapper(bytes_stream, encoding='utf-8')

    # Attempt to load
    spectra = load_mgf(text_stream)

    assert len(spectra) == 1
    assert spectra[0]['title'] == 'test_stream'
    assert len(spectra[0]['mz_array']) == 2

def test_load_mztab_with_textiowrapper():
    """Verify that load_mztab works with io.TextIOWrapper (streaming)."""
    # Minimal valid mzTab content
    mztab_content = """MTD\tmzTab-version\t1.0.0
MTD\tmzTab-mode\tSummary
PSH\tsequence\tPSM_ID\tspectra_ref
PSM\tK.LIVDTVSEK.Y\t1\tms_run[1]:index=0
"""
    # Create a bytes stream
    bytes_stream = io.BytesIO(mztab_content.encode('utf-8'))

    # Wrap with TextIOWrapper
    text_stream = io.TextIOWrapper(bytes_stream, encoding='utf-8')

    # Attempt to load
    df = load_mztab(text_stream)

    assert not df.empty
    assert 'sequence' in df.columns
    assert len(df) == 1
    assert df.iloc[0]['sequence'] == 'K.LIVDTVSEK.Y'
