
import io
import unittest
from data_loading import load_mgf, load_mztab

class TestStreamingIO(unittest.TestCase):
    """
    Test that data loading functions support streaming input (TextIOWrapper).
    This ensures that the memory optimization in app.py remains valid.
    """
    def test_load_mgf_with_textiowrapper(self):
        mgf_content = b"""BEGIN IONS
TITLE=Spectrum 1
PEPMASS=1000.0
100.0 10.0
200.0 20.0
END IONS
"""
        # Simulate Streamlit UploadedFile (BytesIO)
        mgf_file = io.BytesIO(mgf_content)

        # Wrap with TextIOWrapper
        text_wrapper = io.TextIOWrapper(mgf_file, encoding='utf-8')

        # Test load_mgf
        spectra = load_mgf(text_wrapper)
        self.assertEqual(len(spectra), 1)
        self.assertEqual(spectra[0]['title'], 'Spectrum 1')

    def test_load_mztab_with_textiowrapper(self):
        mztab_content = b"""MTD\tmzTab-version\t1.0.0
MTD\tmzTab-mode\tSummary
MTD\tmzTab-type\tQuantification
PSH\tsequence\tPSM_ID\taccession\tunique\tdatabase\tdatabase_version\tsearch_engine\tsearch_engine_score[1]\tmodifications\tretention_time\tcharge\texp_mass_to_charge\tcalc_mass_to_charge\tspectra_ref\tpre\tpost\tstart\tend\topt_global_cv_MS:1002217_decoy_peptide
PSM\tPEPTIDE\tpsm1\tP12345\t0\tDB\t1.0\tMS:1001207\t100.0\t\t100.0\t2\t1000.0\t1000.0\tindex=1\t-\t-\t-\t-\t0
"""
        # Simulate Streamlit UploadedFile (BytesIO)
        mztab_file = io.BytesIO(mztab_content)

        # Wrap with TextIOWrapper
        text_wrapper = io.TextIOWrapper(mztab_file, encoding='utf-8')

        # Test load_mztab
        psm_df = load_mztab(text_wrapper)
        self.assertFalse(psm_df.empty)
        self.assertEqual(len(psm_df), 1)
        self.assertEqual(psm_df.iloc[0]['sequence'], 'PEPTIDE')

if __name__ == '__main__':
    unittest.main()
