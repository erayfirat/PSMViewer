
import io
from data_loading import load_mgf


class TestStreamingLoading:
    def test_mgf_streaming_wrapper(self):
        """Verify load_mgf works with TextIOWrapper (app.py optimization)."""
        content = b"""BEGIN IONS
TITLE=Spectrum 1
PEPMASS=1000.0
100.0 10.0
200.0 20.0
END IONS
"""
        uploaded = io.BytesIO(content)
        # Simulate app.py logic
        wrapped = io.TextIOWrapper(uploaded, encoding='utf-8')

        spectra = load_mgf(wrapped)
        assert len(spectra) == 1
        assert spectra[0]['title'] == 'Spectrum 1'
