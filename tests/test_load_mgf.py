import pytest
from io import StringIO
from app import load_mgf

class TestLoadMGF:
    def test_load_sample_mgf(self, sample_mgf_buffer):
        """Test loading the sample MGF file."""
        spectra = load_mgf(sample_mgf_buffer)
        assert isinstance(spectra, list)
        assert len(spectra) > 0  # Should have some spectra

        # Check structure of first spectrum
        spec = spectra[0]
        assert 'title' in spec
        assert 'pepmass' in spec
        assert 'mz_array' in spec
        assert 'intensity_array' in spec

    def test_load_basic_mgf(self):
        """Test loading a basic valid MGF."""
        mgf_content = """BEGIN IONS
TITLE=test
PEPMASS=450.25
1.0 10.0
2.0 20.0
END IONS
"""
        buffer = StringIO(mgf_content)
        spectra = load_mgf(buffer)
        assert len(spectra) == 1
        spec = spectra[0]
        assert spec['title'] == 'test'
        assert spec['pepmass'] == (450.25, None)  # pyteomics format
        assert len(spec['mz_array']) == 2
        assert len(spec['intensity_array']) == 2

    def test_load_mgf_missing_title(self):
        """Test MGF with missing TITLE."""
        mgf_content = """BEGIN IONS
PEPMASS=450.25
1.0 10.0
END IONS
"""
        buffer = StringIO(mgf_content)
        spectra = load_mgf(buffer)
        assert len(spectra) == 1
        assert spectra[0]['title'] is None

    def test_load_mgf_missing_pepmass(self):
        """Test MGF with missing PEPMASS."""
        mgf_content = """BEGIN IONS
TITLE=test
1.0 10.0
END IONS
"""
        buffer = StringIO(mgf_content)
        spectra = load_mgf(buffer)
        assert len(spectra) == 1
        assert spectra[0]['pepmass'] is None

    def test_load_mgf_empty_spectrum(self):
        """Test MGF with empty spectrum (no peaks)."""
        mgf_content = """BEGIN IONS
TITLE=empty
PEPMASS=450.25
END IONS
"""
        buffer = StringIO(mgf_content)
        spectra = load_mgf(buffer)
        assert len(spectra) == 1
        spec = spectra[0]
        assert spec['title'] == 'empty'
        assert spec['mz_array'] is not None
        assert spec['intensity_array'] is not None
        assert len(spec['mz_array']) == 0  # Empty arrays

    def test_load_multiple_spectra(self):
        """Test loading multiple spectra in one file."""
        mgf_content = """BEGIN IONS
TITLE=spec1
PEPMASS=450.25
1.0 10.0
END IONS
BEGIN IONS
TITLE=spec2
PEPMASS=550.35
2.0 20.0
END IONS
"""
        buffer = StringIO(mgf_content)
        spectra = load_mgf(buffer)
        assert len(spectra) == 2
        assert spectra[0]['title'] == 'spec1'
        assert spectra[1]['title'] == 'spec2'

    def test_load_mgf_malformed(self):
        """Test loading malformed MGF."""
        # Missing END IONS
        mgf_content = """BEGIN IONS
TITLE=malformed
PEPMASS=450.25
1.0 10.0
"""
        buffer = StringIO(mgf_content)
        # pyteomics may raise AttributeError when parsing fails
        with pytest.raises(AttributeError):
            spectra = load_mgf(buffer)

    def test_load_mgf_invalid_pepmass(self):
        """Test MGF with invalid PEPMASS."""
        mgf_content = """BEGIN IONS
TITLE=test
PEPMASS=invalid
1.0 10.0
END IONS
"""
        buffer = StringIO(mgf_content)
        with pytest.raises(ValueError):
            spectra = load_mgf(buffer)

    def test_load_empty_file(self):
        """Test loading empty file."""
        buffer = StringIO("")
        spectra = load_mgf(buffer)
        assert isinstance(spectra, list)
        assert len(spectra) == 0
