import pytest
from io import StringIO
from pathlib import Path

@pytest.fixture
def sample_mgf_path():
    """Path to sample MGF file."""
    return Path("data/sample_preprocessed_spectra.mgf")

@pytest.fixture
def sample_mztab_path():
    """Path to sample mzTab file."""
    return Path("data/casanovo_20251029091517.mztab")

@pytest.fixture
def sample_mgf_content():
    """Content of sample MGF file as string."""
    mgf_path = Path("data/sample_preprocessed_spectra.mgf")
    with open(mgf_path, 'r') as f:
        return f.read()

@pytest.fixture
def sample_mztab_content():
    """Content of sample mzTab file as string."""
    mztab_path = Path("data/casanovo_20251029091517.mztab")
    with open(mztab_path, 'r') as f:
        return f.read()

@pytest.fixture
def sample_mgf_buffer(sample_mgf_content):
    """MGF content as StringIO buffer."""
    return StringIO(sample_mgf_content)

@pytest.fixture
def sample_mztab_buffer(sample_mztab_content):
    """mzTab content as StringIO buffer."""
    return StringIO(sample_mztab_content)
