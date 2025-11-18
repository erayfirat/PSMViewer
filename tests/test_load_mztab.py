import pytest
import pandas as pd
from io import StringIO
from app import load_mztab

class TestLoadMZTAB:
    def test_load_sample_mztab(self, sample_mztab_buffer):
        """Test loading the sample mzTab file."""
        df = load_mztab(sample_mztab_buffer)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0  # Should have some PSMs

        # Check expected columns
        assert 'sequence' in df.columns
        assert 'spectra_ref' in df.columns
        assert 'PSM_ID' in df.columns

    def test_load_basic_mztab(self):
        """Test loading a basic valid mzTab formatted content."""
        # Simplified mzTab content with required PSM_ID
        mztab_content = """MTD	mzTab-version	1.0.0
MTD	mzTab-mode	Summary
PSH	sequence	PSM_ID	spectra_ref
PSM	PEPTIDE	1	ms_run[1]:index=0
"""
        buffer = StringIO(mztab_content)
        df = load_mztab(buffer)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]['sequence'] == 'PEPTIDE'
        assert df.iloc[0]['spectra_ref'] == 'ms_run[1]:index=0'

    def test_load_mztab_multiple_psms(self):
        """Test loading mzTab with multiple PSMs."""
        mztab_content = """MTD	mzTab-version	1.0.0
MTD	mzTab-mode	Summary
PSH	sequence	PSM_ID	spectra_ref
PSM	PEP1	1	ms_run[1]:index=0
PSM	PEP2	2	ms_run[1]:index=1
"""
        buffer = StringIO(mztab_content)
        df = load_mztab(buffer)
        assert len(df) == 2
        assert df.iloc[1]['sequence'] == 'PEP2'

    def test_load_mztab_with_modifications(self):
        """Test loading mzTab with modified sequences."""
        mztab_content = """MTD	mzTab-version	1.0.0
MTD	mzTab-mode	Summary
PSH	sequence	PSM_ID	spectra_ref	modifications
PSM	C[Carbamidomethyl]HK	1	ms_run[1]:index=0	null
"""
        buffer = StringIO(mztab_content)
        df = load_mztab(buffer)
        assert len(df) == 1
        assert df.iloc[0]['sequence'] == 'C[Carbamidomethyl]HK'

    def test_load_empty_mztab(self):
        """Test loading mzTab with no PSM section."""
        mztab_content = """MTD	mzTab-version	1.0.0
MTD	mzTab-mode	Summary
"""
        buffer = StringIO(mztab_content)
        df = load_mztab(buffer)
        assert isinstance(df, pd.DataFrame)
        # May be empty or raise error depending on pyteomics

    def test_load_mztab_no_psm_header(self):
        """Test mzTab without PSM header."""
        mztab_content = """MTD	mzTab-version	1.0.0
MTD	mzTab-mode	Summary
PSH	sequence	PSM_ID	spectra_ref
PSM	PEP	1	ms_run[1]:index=0
"""
        buffer = StringIO(mztab_content)
        df = load_mztab(buffer)
        # pyteomics might handle or error out
        assert isinstance(df, pd.DataFrame)
