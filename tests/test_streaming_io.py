
import io
import unittest
from pyteomics import mgf, mztab
import pandas as pd

class TestStreamingIO(unittest.TestCase):
    def test_mgf_streaming(self):
        # Create a mock MGF content as bytes
        mgf_content = b"""BEGIN IONS
TITLE=Spectrum 1
PEPMASS=1000.0
CHARGE=2+
100.0 1000.0
200.0 500.0
END IONS
"""
        # Wrap in BytesIO to simulate Streamlit's UploadedFile
        binary_stream = io.BytesIO(mgf_content)

        # Wrap in TextIOWrapper for streaming decoding
        text_stream = io.TextIOWrapper(binary_stream, encoding='utf-8')

        # Verify pyteomics can read from it
        with mgf.read(text_stream, use_index=False) as reader:
            spectra = list(reader)

        self.assertEqual(len(spectra), 1)
        self.assertEqual(spectra[0]['params']['title'], 'Spectrum 1')

        # Check if underlying stream is closed
        # TextIOWrapper might define closed property
        self.assertFalse(binary_stream.closed, "Binary stream should not be closed implicitly if possible, but strict ownership might vary")

    def test_mztab_streaming(self):
        # Create a mock mzTab content as bytes
        mztab_content = b"""MTD\tmzTab-version\t1.0.0
MTD\tmzTab-mode\tSummary
MTD\tmzTab-type\tIdentification
PSH\tsequence\tPSM_ID\taccession\tunique\tdatabase\tdatabase_version\tsearch_engine\tsearch_engine_score[1]\tmodifications\tretention_time\tcharge\texp_mass_to_charge\tcalc_mass_to_charge\tspectra_ref\tpre\tpost\tstart\tend\topt_global_cv_MS:1002217_decoy_peptide\topt_global_cv_MS:1000889_peptidoform_sequence\topt_global_spec_evalue
PSM\tPEPTIDE\t1\tACC\t0\tDB\t1.0\tSE\t0.99\tnull\t100.0\t2\t1000.0\t1000.0\tindex=1\t-\t-\t1\t10\t0\tPEPTIDE\t0.01
"""
        # Wrap in BytesIO to simulate Streamlit's UploadedFile
        binary_stream = io.BytesIO(mztab_content)

        # Wrap in TextIOWrapper for streaming decoding
        text_stream = io.TextIOWrapper(binary_stream, encoding='utf-8')

        # Verify pyteomics can read from it
        # pyteomics.mztab.MzTab reads the whole file, but it should accept a file-like object
        tab = mztab.MzTab(text_stream)
        psm_df = pd.DataFrame(tab['psm'])

        self.assertEqual(len(psm_df), 1)
        self.assertEqual(psm_df.iloc[0]['sequence'], 'PEPTIDE')

if __name__ == '__main__':
    unittest.main()
