import pytest
from io import BytesIO, StringIO
import pandas as pd
import streamlit as st
from app import load_mgf, load_mztab, map_psms_to_spectra

class TestIntegration:
    def test_full_pipeline(self, sample_mgf_buffer, sample_mztab_buffer):
        """Test the complete data processing pipeline."""
        # Load data
        spectra = load_mgf(sample_mgf_buffer)
        psm_df = load_mztab(sample_mztab_buffer)

        assert len(spectra) > 0
        assert len(psm_df) > 0

        # Map PSMs to spectra
        mapped = map_psms_to_spectra(spectra, psm_df)

        assert len(mapped) == len(psm_df)
        # Check that some mappings were successful
        matches = mapped['matched_title'].notnull().sum()
        assert matches > 0, "At least some PSMs should match spectra"

    @pytest.mark.streamlit
    def test_streamlit_integration(self):
        """Test the Streamlit app with mock file uploads."""
        # This would require setting up streamlit testing
        # For now, this is a placeholder since streamlit.testing might require more setup
        pass

class TestPipelineEdgeCases:
    def test_pipeline_with_empty_mgf(self, sample_mztab_buffer):
        """Test pipeline with empty MGF."""
        spectra = load_mgf(BytesIO(b""))
        psm_df = load_mztab(sample_mztab_buffer)

        mapped = map_psms_to_spectra(spectra, psm_df)

        # All should be unmatched
        assert all(mapped['matched_title'].isnull())

    def test_pipeline_with_empty_mztab(self, sample_mgf_buffer):
        """Test pipeline with empty mzTab."""
        spectra = load_mgf(sample_mgf_buffer)
        psm_df = load_mztab(StringIO("MTD\tmzTab-version\t1.0.0"))

        mapped = map_psms_to_spectra(spectra, psm_df)

        assert len(mapped) == 0 or len(mapped) == len(psm_df)  # Depending on pyteomics handling

    def test_mismatch_references(self):
        """Test when PSM references don't match any spectra."""
        spectra = [
            {'title': 'spec0', 'pepmass': (450.0, None), 'mz_array': [1.0, 2.0], 'intensity_array': [10.0, 20.0]},
        ]
        psm_df = pd.DataFrame([
            {'sequence': 'PEP1', 'spectra_ref': 'nonexistent'},
        ])

        mapped = map_psms_to_spectra(spectra, psm_df)

        assert mapped.iloc[0]['matched_title'] is None
