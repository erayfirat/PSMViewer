import pytest
from app import extract_index_from_spectra_ref

class TestExtractIndexFromSpectraRef:
    def test_extract_index_index_format(self):
        """Test extraction from 'index=N' format."""
        assert extract_index_from_spectra_ref("index=123") == "123"
        assert extract_index_from_spectra_ref("index=0") == "0"
        assert extract_index_from_spectra_ref("index=999") == "999"

    def test_extract_index_scan_format(self):
        """Test extraction from 'scan=N' format."""
        assert extract_index_from_spectra_ref("scan=456") == "456"
        assert extract_index_from_spectra_ref("scan=1") == "1"

    def test_extract_index_suffix_format(self):
        """Test extraction from 'something:N' format."""
        assert extract_index_from_spectra_ref("file.mgf:789") == "789"
        assert extract_index_from_spectra_ref("spectrum:1") == "1"

    def test_extract_index_numeric_only(self):
        """Test when input is just a number."""
        assert extract_index_from_spectra_ref("42") == "42"
        assert extract_index_from_spectra_ref("0") == "0"

    def test_extract_index_no_match(self):
        """Test when no numeric identifier found."""
        assert extract_index_from_spectra_ref("no_number_here") is None
        assert extract_index_from_spectra_ref("") is None
        assert extract_index_from_spectra_ref("abc123def") is None  # Embedded number not extracted
        assert extract_index_from_spectra_ref("mixed123") is None

    def test_extract_index_none_input(self):
        """Test None input."""
        assert extract_index_from_spectra_ref(None) is None

    def test_extract_index_case_sensitivity(self):
        """Test case sensitivity (assuming case sensitive)."""
        assert extract_index_from_spectra_ref("INDEX=123") is None  # Uppercase, no match
        assert extract_index_from_spectra_ref("Scan=456") is None  # Mixed case

    def test_extract_index_edge_cases(self):
        """Test edge cases."""
        # Leading/trailing spaces - the function should still extract
        assert extract_index_from_spectra_ref(" index=123 ") == "123"  # Actually extracts
        # Malformed
        assert extract_index_from_spectra_ref("index=abc") is None  # Invalid number
        assert extract_index_from_spectra_ref("index=") is None
        assert extract_index_from_spectra_ref(":") is None
        # Multiple formats
        assert extract_index_from_spectra_ref("index=123:456") == "123"  # First match wins
