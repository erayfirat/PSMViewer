
import io
import pytest
import pandas as pd
from data_loading import load_mgf, load_mztab

def test_load_mgf_streaming():
    """Test loading MGF from a streaming TextIOWrapper."""
    mgf_content = """BEGIN IONS
TITLE=test
PEPMASS=450.25
1.0 10.0
2.0 20.0
END IONS
"""
    # Create a BytesIO buffer (simulating uploaded file)
    bytes_buffer = io.BytesIO(mgf_content.encode('utf-8'))

    # Wrap in TextIOWrapper
    text_wrapper = io.TextIOWrapper(bytes_buffer, encoding='utf-8')

    spectra = load_mgf(text_wrapper)
    assert len(spectra) == 1
    spec = spectra[0]
    assert spec['title'] == 'test'
    assert spec['pepmass'] == (450.25, None)

def test_load_mztab_streaming():
    """Test loading mzTab from a streaming TextIOWrapper."""
    # Use explicit newlines and no indentation for the content
    mztab_content = (
"MTD\tmzTab-version\t1.0.0\n"
"MTD\tmzTab-mode\tSummary\n"
"MTD\tmzTab-type\tIdentification\n"
"PSH\tsequence\tPSM_ID\taccession\tunique\tdatabase\tdatabase_version\tsearch_engine\tsearch_engine_score[1]\tmodifications\tretention_time\tcharge\texp_mass_to_charge\tcalc_mass_to_charge\tspectra_ref\tpre\tpost\tstart\tend\n"
"PSM\tPEPTIDE\t1\tACC\t0\tDB\t1.0\tSE\t10.0\tNULL\t100.0\t2\t500.0\t500.0\tindex=1\t-\t-\t1\t10\n"
)
    # Note: I changed PSM header to PSH based on mzTab spec?
    # Wait, mzTab spec uses PSH for header? Or PSM line with specific columns.
    # Pyteomics mztab.py documentation says: "The PSM section (starting with 'PSH')..."
    # Let's try PSH for the header line.

    # Create a BytesIO buffer
    bytes_buffer = io.BytesIO(mztab_content.encode('utf-8'))

    # Wrap in TextIOWrapper
    text_wrapper = io.TextIOWrapper(bytes_buffer, encoding='utf-8')

    # Verify strict mock data first with StringIO (current behavior)
    df_orig = load_mztab(io.StringIO(mztab_content))
    assert len(df_orig) == 1

    # Re-create buffer for the streaming test
    bytes_buffer_2 = io.BytesIO(mztab_content.encode('utf-8'))
    text_wrapper = io.TextIOWrapper(bytes_buffer_2, encoding='utf-8')

    df = load_mztab(text_wrapper)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]['sequence'] == 'PEPTIDE'
