import re
import io
from typing import List, Dict, Any, Tuple

import numpy as np
import pandas as pd
from pyteomics import mgf, mass, mztab

# Optional UI
try:
    import streamlit as st
    from matplotlib import pyplot as plt
except Exception:
    st = None

# ---- Data loading functions ----
def load_mgf(file_buffer: Any) -> List[Dict[str, Any]]:
    """Read MGF using pyteomics and return list of spectra dicts."""
    specs = []
    with mgf.read(file_buffer, use_index=False) as reader:
        for s in reader:
            # normalize title to string
            params = s.get('params', {})
            title = params.get('title')
            scans = params.get('scans')
            pepmass = params.get('pepmass')
            specs.append({
                'title': str(title) if title is not None else None,
                'scans': str(scans) if scans is not None else None,
                'pepmass': pepmass,
                'mz_array': s.get('m/z array'),
                'intensity_array': s.get('intensity array'),
                'params': params
            })
    return specs

def load_mztab(file_buffer: Any) -> pd.DataFrame:
    """
    Parse mzTab from a file or buffer using pyteomics and return the PSM section
    as a pandas DataFrame.
    """
    tab = mztab.MzTab(file_buffer)
    psm_data = tab['psm'] 
    psm_df = pd.DataFrame(psm_data)
    
    return psm_df

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

def theoretical_fragments(peptide: str) -> List[Tuple[str, float]]:
    """
    Compute simple b and y ion m/zs (at z=1) for a peptide sequence using pyteomics.
    This function strips modifications in square brackets.
    """
    # remove modifications in brackets
    seq = re.sub(r"\[.*?\]", "", peptide)
    seq = seq.replace('I', 'L')
    
    fragments = []
    
    # calculate b-ions (z=1)
    for i in range(1, len(seq)):
        try:
            mz = mass.calculate_mass(sequence=seq[:i], ion_type='b', charge=1)
            fragments.append((f'b{i}', mz))
        except KeyError:
            pass # pass if unknown amino acid

    # calculate y-ions (z=1)
    for i in range(1, len(seq)):
        try:
            mz = mass.calculate_mass(sequence=seq[-i:], ion_type='y', charge=1)
            fragments.append((f'y{i}', mz))
        except KeyError:
            pass # ass if unknown amino acid
            
    return fragments

def ppm(m1, m2):
    return abs(m1-m2)/m2*1e6


def annotate_spectrum(mz_array: np.ndarray, intensity_array: np.ndarray, theo_mzs: List[Tuple[str, float]], tol_ppm: float=20.0):
    """For each theoretical mz, find the observed peak index within tol_ppm.
    Returns list of matched indices and unmatched.
    """
    matches = []
    mzs = mz_array
    for label, theo in theo_mzs:
        # compute diffs in ppm
        diffs = np.abs(mzs - theo) / theo * 1e6
        idx = np.argmin(diffs)
        if diffs[idx] <= tol_ppm:
            matches.append((label, theo, mzs[idx], intensity_array[idx], idx, diffs[idx]))
    return matches


# ---- High-level pipeline ----

def map_psms_to_spectra(spectra: List[Dict], psm_df: pd.DataFrame, title_field='title') -> pd.DataFrame:
    """Return a dataframe with mappings between spectra and PSMs.
    The function will try to match by exact title -> spectra_ref or by numeric index extraction."""
    # ensure spectra_ref column exists
    if 'spectra_ref' not in psm_df.columns and 'spectra_ref' not in [c.lower() for c in psm_df.columns]:
        # try to find a column that contains 'ms_run' or 'index' or 'spectra'
        candidates = [c for c in psm_df.columns if 'ms_run' in c or 'index' in c or 'spectra' in c or 'scan' in c]
        spectra_ref_col = candidates[0] if candidates else None
    else:
        # prefer exact match
        spectra_ref_col = 'spectra_ref' if 'spectra_ref' in psm_df.columns else [c for c in psm_df.columns if c.lower()=='spectra_ref'][0]

    # find peptide/sequence column
    seq_col = None
    for c in psm_df.columns:
        # peptide sequences are uppercase letters with possible brackets
        if psm_df[c].astype(str).str.match(r'^[A-Z\[].+').any():
            seq_col = c
            break
    if seq_col is None:
        # fallback to first column
        seq_col = psm_df.columns[0]

    mappings = []
    # build lookup from title to spectrum
    title_to_spec = {s.get('title'): s for s in spectra}
    # also build numeric index map for titles that are ints
    num_title_map = {}
    for t,s in title_to_spec.items():
        try:
            num_title_map[str(int(str(t)))] = s
        except Exception:
            pass

    for i, row in psm_df.iterrows():
        seq = str(row.get(seq_col))
        spec_ref = None
        if spectra_ref_col is not None:
            spec_ref = str(row.get(spectra_ref_col))
        # try exact match
        matched_spec = None
        if spec_ref is not None and spec_ref in title_to_spec:
            matched_spec = title_to_spec[spec_ref]
        # try numeric extraction
        if matched_spec is None and spec_ref is not None:
            idx = extract_index_from_spectra_ref(spec_ref)
            if idx and idx in num_title_map:
                matched_spec = num_title_map[idx]
        # also try matching by sequence's precursor m/z vs pepmass
        if matched_spec is None:
            # optional: compare calc_mass_to_charge columns if present
            if 'calc_mass_to_charge' in psm_df.columns:
                try:
                    calc_mz = float(row['calc_mass_to_charge'])
                    # search nearest in spectra by pepmass
                    best = None
                    bestdiff = 1e9
                    for s in spectra:
                        pep = s.get('pepmass')
                        if pep:
                            obs = pep[0] if isinstance(pep, (list, tuple)) else float(pep)
                            diff = abs(obs - calc_mz)
                            if diff < bestdiff:
                                bestdiff = diff; best = s
                    if best and bestdiff < 0.1:  # arbitrary tolerance
                        matched_spec = best
                except Exception:
                    pass
        mappings.append({
            'psm_index': i,
            'sequence': seq,
            'spectra_ref': spec_ref,
            'matched_title': matched_spec.get('title') if matched_spec else None,
            'matched_scans': matched_spec.get('scans') if matched_spec else None,
            'pepmass': matched_spec.get('pepmass') if matched_spec else None,
            'mz_array': matched_spec.get('mz_array') if matched_spec else None,
            'intensity_array': matched_spec.get('intensity_array') if matched_spec else None
        })
    return pd.DataFrame(mappings)


# ---- Streamlit app ----

def run_streamlit_app():
    st.title('PSM Viewer — minimal')
    mgf_file = st.file_uploader('Upload MGF file', type=['mgf'])
    mztab_file = st.file_uploader('Upload mzTab file', type=['mztab', 'mztab.txt'])
    if mgf_file and mztab_file:
        # read uploaded bytes into functions
        mgf_string = mgf_file.read().decode('utf-8')
        mgf_buffer = io.StringIO(mgf_string)
        spectra = load_mgf(mgf_buffer)

        mztab_string = mztab_file.read().decode('utf-8')
        mztab_buffer = io.StringIO(mztab_string)
        psm_df = load_mztab(mztab_buffer)

        mapped = map_psms_to_spectra(spectra, psm_df)

        st.write(f"Loaded {len(spectra)} spectra and {len(psm_df)} PSMs. Matches: {mapped['matched_title'].notnull().sum()}")

        # show table of mapped PSMs
        st.dataframe(mapped[['psm_index', 'sequence', 'spectra_ref', 'matched_title']])

        sel = st.number_input('Select PSM index to view (psm_index)', min_value=0, max_value=len(mapped)-1, value=0)
        row = mapped.iloc[int(sel)]
        st.write(row[['sequence', 'spectra_ref', 'matched_title']])
        if row['matched_title'] is not None:
            mz = row['mz_array']
            inten = row['intensity_array']
            # compute theoretical fragments
            theo = theoretical_fragments(row['sequence'])
            matches = annotate_spectrum(np.array(mz), np.array(inten), theo, tol_ppm=20.0)

            fig, ax = plt.subplots(figsize=(10,4))
            ax.vlines(mz, [0], inten, color='gray', zorder=1)
            ax.set_xlabel('m/z')
            ax.set_ylabel('intensity')
            ax.set_title(f"Spectrum {row['matched_title']} — Sequence: {row['sequence']}")
            matches_mz = [m[2] for m in matches] 
            matches_int = [m[3] for m in matches] 
            ax.vlines(matches_mz, [0], matches_int, color='red', zorder=2)
            # mark matched peaks
            for label, theo_mz, obs_mz, inten_val, idx, diff_ppm in matches:
                ax.plot([obs_mz], [inten_val], marker='o', color='red', zorder=3)
                y_position = inten_val + 0.015 
                ax.text(obs_mz, y_position, label, fontsize=8, zorder=3, ha='center', va='bottom')
            st.pyplot(fig)
        else:
            st.warning('No matching spectrum found for this PSM')


if __name__ == '__main__':
    if st is None:
        print('Streamlit not available. Install streamlit to use the UI.')
    else:
        run_streamlit_app()
