import re
import io
from typing import List, Dict, Any

import pandas as pd
from pyteomics import mgf, mztab

from spectrum_utils import plot as sup
from spectrum_utils import spectrum as sus
from matplotlib import pyplot as plt

import streamlit as st


# ---- Data loading functions ----
def load_mgf(file_buffer: Any) -> List[Dict[str, Any]]:
    """Read MGF using pyteomics and return list of spectra dicts."""
    specs = []
    with mgf.read(file_buffer, use_index=False) as reader:
        for s in reader:
            params = s.get('params', {})
            title = params.get('title')
            pepmass = params.get('pepmass')
            specs.append({
                'title': str(title) if title else None,
                'pepmass': pepmass,
                'mz_array': s.get('m/z array'),
                'intensity_array': s.get('intensity array')
            })
    return specs

def load_mztab(file_buffer: Any) -> pd.DataFrame:
    """
    Parse mzTab from a file or buffer using pyteomics and return the PSM section
    as a pandas DataFrame.
    """
    tab = mztab.MzTab(file_buffer)
    return pd.DataFrame(tab['psm'])

def extract_index_from_spectra_ref(s: str) -> str:
    """Try to extract a numeric index or id from a spectra_ref string."""
    if s is None:
        return None
    # direct numeric
    m = re.search(r'index=(\d+)', s)
    if m:
        return m.group(1)
    m = re.search(r'scan=(\d+)', s)
    if m:
        return m.group(1)
    # trailing number
    m = re.search(r':(\d+)$', s)
    if m:
        return m.group(1)
    # pure digits
    m = re.match(r'^\d+$', s)
    if m:
        return s
    return None


# ---- High-level pipeline ----

def map_psms_to_spectra(spectra: List[Dict], psm_df: pd.DataFrame) -> pd.DataFrame:
    """Map PSMs to spectra by title or index."""
    title_to_spec = {s['title']: s for s in spectra if s['title']}
    index_to_spec = {str(i): spectra[i] for i in range(len(spectra))}

    mappings = []
    for i, row in psm_df.iterrows():
        spec_ref = str(row.get('spectra_ref', ''))
        matched_spec = title_to_spec.get(spec_ref) or index_to_spec.get(extract_index_from_spectra_ref(spec_ref))
        mappings.append({
            'psm_index': i,
            'sequence': str(row.get('sequence', '')),
            'spectra_ref': spec_ref,
            'matched_title': matched_spec['title'] if matched_spec else None,
            'mz_array': matched_spec.get('mz_array') if matched_spec else None,
            'intensity_array': matched_spec.get('intensity_array') if matched_spec else None,
            'pepmass': matched_spec.get('pepmass') if matched_spec else None
        })
    return pd.DataFrame(mappings)


def draw_spectrum(row, mz, inten):
    """Draw spectrum using spectrum_utils."""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title(f"Spectrum {row['matched_title']} — Sequence: {row['sequence']}")
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    precursor_mz = float(row['pepmass'][0])
    charge = 2
    spec = sus.MsmsSpectrum(row['matched_title'], precursor_mz, charge, mz, inten)
    spec = (
        spec.set_mz_range(min_mz=100, max_mz=1400)
        .remove_precursor_peak(10, "ppm")
        .filter_intensity(min_intensity=0.05, max_num_peaks=50)
        .scale_intensity("root")
        .annotate_proforma(row['sequence'], 10, "ppm", ion_types="aby")
    )
    sup.spectrum(spec, grid=False, ax=ax)
    return fig


# ---- Streamlit app ----

def run_streamlit_app():
    st.title('PSM Viewer App')
    mgf_file = st.file_uploader('Upload MGF file', type=['mgf'])
    mztab_file = st.file_uploader('Upload mzTab file', type=['mztab', 'mztab.txt'])
    if mgf_file and mztab_file:
        # read uploaded bytes into functions
        spectra = load_mgf(io.StringIO(mgf_file.read().decode('utf-8')))
        psm_df = load_mztab(io.StringIO(mztab_file.read().decode('utf-8')))

        mapped = map_psms_to_spectra(spectra, psm_df)

        st.write(f"Loaded {len(spectra)} spectra and {len(psm_df)} PSMs. Matches: {mapped['matched_title'].notnull().sum()}")

        st.dataframe(mapped[['psm_index', 'sequence', 'matched_title']])

        sel = st.number_input('Select PSM index', min_value=0, max_value=len(mapped)-1, value=0)
        row = mapped.iloc[int(sel)]
        if row['matched_title']:
            fig = draw_spectrum(row, row['mz_array'], row['intensity_array'])
            st.pyplot(fig)
        else:
            st.warning('No matching spectrum found')


if __name__ == '__main__':
    run_streamlit_app()
