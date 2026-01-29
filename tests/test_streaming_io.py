import io
import pytest
from data_loading import load_mgf, load_mztab

def test_load_mgf_with_textiowrapper():
    mgf_content = b"""BEGIN IONS
TITLE=Spectrum 1
PEPMASS=1000.0
100.0 10.0
200.0 20.0
END IONS
"""
    # Simulate Streamlit file upload (BytesIO) wrapped in TextIOWrapper
    bytes_io = io.BytesIO(mgf_content)
    text_io = io.TextIOWrapper(bytes_io, encoding='utf-8')

    specs = load_mgf(text_io)
    assert len(specs) == 1
    assert specs[0]['title'] == 'Spectrum 1'

def test_load_mztab_with_textiowrapper():
    mztab_content = b"""MTD\tmzTab-version\t1.0.0
MTD\tmode\tComplete
MTD\ttype\tIdentification
PSH\tsequence\tPSM_ID\taccession\tunique\tdatabase\tdatabase_version\tsearch_engine\tsearch_engine_score[1]\tmodifications\tretention_time\tcharge\texp_mass_to_charge\tcalc_mass_to_charge\tspectra_ref\tpre\tpost\tstart\tend
PSM\tPEPTIDE\t1\tP12345\t0\tDB\t1.0\tMascot\t100\tnull\t100.0\t2\t1000.0\t1000.0\tindex=0\t-\t-\t1\t10
"""
    bytes_io = io.BytesIO(mztab_content)
    text_io = io.TextIOWrapper(bytes_io, encoding='utf-8')

    df = load_mztab(text_io)
    assert len(df) == 1
    assert df.iloc[0]['sequence'] == 'PEPTIDE'

if __name__ == "__main__":
    try:
        test_load_mgf_with_textiowrapper()
        print("MGF test passed")
    except Exception as e:
        print(f"MGF test failed: {e}")

    try:
        test_load_mztab_with_textiowrapper()
        print("MzTab test passed")
    except Exception as e:
        print(f"MzTab test failed: {e}")
