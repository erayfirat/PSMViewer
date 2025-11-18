import pandas as pd
from processing import map_psms_to_spectra

class TestMapPSMsToSpectra:
    def test_map_basic(self):
        """Test basic mapping."""
        spectra = [
            {'title': 'spec0', 'pepmass': (450.0, None), 'mz_array': [1.0, 2.0], 'intensity_array': [10.0, 20.0]},
            {'title': 'spec1', 'pepmass': (550.0, None), 'mz_array': [3.0, 4.0], 'intensity_array': [30.0, 40.0]},
        ]
        psm_df = pd.DataFrame([
            {'sequence': 'PEP1', 'spectra_ref': 'ms_run[1]:index=0'},
            {'sequence': 'PEP2', 'spectra_ref': 'ms_run[1]:index=1'},
        ])
        result = map_psms_to_spectra(spectra, psm_df)
        assert len(result) == 2
        assert result.iloc[0]['sequence'] == 'PEP1'
        assert result.iloc[0]['matched_title'] == 'spec0'

    def test_map_by_title_direct(self):
        """Test mapping by direct title match."""
        spectra = [
            {'title': 'direct_match', 'pepmass': (450.0, None), 'mz_array': [1.0, 2.0], 'intensity_array': [10.0, 20.0]},
        ]
        psm_df = pd.DataFrame([
            {'sequence': 'PEP1', 'spectra_ref': 'direct_match'},
        ])
        result = map_psms_to_spectra(spectra, psm_df)
        assert len(result) == 1
        assert result.iloc[0]['matched_title'] == 'direct_match'

    def test_map_by_index(self):
        """Test mapping by index extraction."""
        spectra = [
            {'title': 'spec0', 'pepmass': (450.0, None), 'mz_array': [1.0, 2.0], 'intensity_array': [10.0, 20.0]},
            {'title': 'spec1', 'pepmass': (550.0, None), 'mz_array': [3.0, 4.0], 'intensity_array': [30.0, 40.0]},
        ]
        psm_df = pd.DataFrame([
            {'sequence': 'PEP1', 'spectra_ref': 'scan=0'},
            {'sequence': 'PEP2', 'spectra_ref': 'index=1'},
        ])
        result = map_psms_to_spectra(spectra, psm_df)
        assert len(result) == 2
        assert result.iloc[0]['matched_title'] == 'spec0'
        assert result.iloc[1]['matched_title'] == 'spec1'

    def test_map_no_match(self):
        """Test when no spectrum matches."""
        spectra = [
            {'title': 'spec0', 'pepmass': (450.0, None), 'mz_array': [1.0, 2.0], 'intensity_array': [10.0, 20.0]},
        ]
        psm_df = pd.DataFrame([
            {'sequence': 'PEP1', 'spectra_ref': 'nonexistent'},
        ])
        result = map_psms_to_spectra(spectra, psm_df)
        assert len(result) == 1
        assert result.iloc[0]['matched_title'] is None
        assert result.iloc[0]['mz_array'] is None

    def test_map_mixed_matching(self):
        """Test different matching types."""
        spectra = [
            {'title': 'direct', 'pepmass': (450.0, None), 'mz_array': [1.0, 2.0], 'intensity_array': [10.0, 20.0]},
            {'title': 'indexed', 'pepmass': (550.0, None), 'mz_array': [3.0, 4.0], 'intensity_array': [30.0, 40.0]},
        ]
        psm_df = pd.DataFrame([
            {'sequence': 'PEP1', 'spectra_ref': 'direct'},  # Title match
            {'sequence': 'PEP2', 'spectra_ref': 'index=1'},  # Index match
        ])
        result = map_psms_to_spectra(spectra, psm_df)
        assert result.iloc[0]['matched_title'] == 'direct'
        assert result.iloc[1]['matched_title'] == 'indexed'

    def test_map_title_precedence(self):
        """Test that title match takes precedence over index."""
        spectra = [
            {'title': 'spec0', 'pepmass': (450.0, None), 'mz_array': [1.0, 2.0], 'intensity_array': [10.0, 20.0]},
            {'title': 'direct', 'pepmass': (550.0, None), 'mz_array': [3.0, 4.0], 'intensity_array': [30.0, 40.0]},
        ]
        psm_df = pd.DataFrame([
            {'sequence': 'PEP1', 'spectra_ref': 'direct'},  # Title match to second spectrum
        ])
        result = map_psms_to_spectra(spectra, psm_df)
        assert result.iloc[0]['matched_title'] == 'direct'
        assert result.iloc[0]['pepmass'] == (550.0, None)  # Should match second spectrum

    def test_map_empty_input(self):
        """Test with empty inputs."""
        result = map_psms_to_spectra([], pd.DataFrame())
        assert len(result) == 0

    def test_map_spectra_without_title(self):
        """Test spectra without titles (should not be matched by title)."""
        spectra = [
            {'title': None, 'pepmass': (450.0, None), 'mz_array': [1.0, 2.0], 'intensity_array': [10.0, 20.0]},
            {'title': 'spec1', 'pepmass': (550.0, None), 'mz_array': [3.0, 4.0], 'intensity_array': [30.0, 40.0]},
        ]
        psm_df = pd.DataFrame([
            {'sequence': 'PEP1', 'spectra_ref': 'index=0'},  # Should match first spectrum by index
            {'sequence': 'PEP2', 'spectra_ref': 'spec1'},  # Should match second by title
        ])
        result = map_psms_to_spectra(spectra, psm_df)
        assert result.iloc[0]['matched_title'] is None  # No title, but matched by index
        assert result.iloc[1]['matched_title'] == 'spec1'

    def test_map_psm_columns(self):
        """Test that PSM columns are properly included."""
        spectra = [
            {'title': 'spec0', 'pepmass': (450.0, None), 'mz_array': [1.0, 2.0], 'intensity_array': [10.0, 20.0]},
        ]
        psm_df = pd.DataFrame([
            {'sequence': 'PEP1', 'spectra_ref': 'index=0', 'charge': 2, 'exp_mass_to_charge': 451.0},
        ])
        result = map_psms_to_spectra(spectra, psm_df)
        assert result.iloc[0]['sequence'] == 'PEP1'
        # The function creates specific columns for mapping, not copying all PSM columns
        assert result.iloc[0]['spectra_ref'] == 'index=0'
        assert result.iloc[0]['psm_index'] == 0
