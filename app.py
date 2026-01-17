"""
PSM Viewer - A Streamlit web app for visualizing peptide-spectrum matches.
Run with: streamlit run app.py

This is the main entry point that imports and orchestrates the modular components.
"""

import io
import streamlit as st

from data_loading import load_mgf, load_mztab
from processing import map_psms_to_spectra
from visualization import draw_spectrum


# ---- Streamlit app ----

def run_streamlit_app():
    """
    Main Streamlit application for interactive PSM visualization.

    Handles file uploads, data processing, and spectrum visualization.
    Provides web interface for PSM-spectrum matching and plotting.
    """
    # Set application title
    st.title('PSM Viewer App')

    # File upload widgets for MGF (spectra) and mzTab (identifications)
    mgf_file = st.file_uploader('Upload MGF file', type=['mgf'])
    mztab_file = st.file_uploader('Upload mzTab file', type=['mztab', 'mztab.txt'])

    # Process files only when both are uploaded
    if mgf_file and mztab_file:
        # Decode uploaded file contents (Streamlit files are bytes by default)
        # Use TextIOWrapper to wrap the file buffer to avoid reading into memory
        spectra = load_mgf(io.TextIOWrapper(mgf_file, encoding='utf-8'))
        psm_df = load_mztab(io.TextIOWrapper(mztab_file, encoding='utf-8'))

        # Create mappings between PSMs and spectra
        mapped = map_psms_to_spectra(spectra, psm_df)

        # Display summary statistics
        st.write(f"Loaded {len(spectra)} spectra and {len(psm_df)} PSMs. Matches: {mapped['matched_title'].notnull().sum()}")

        # Show interactive table of PSM-to-spectrum mappings
        # Display only key columns for readability
        st.dataframe(mapped[['psm_index', 'sequence', 'matched_title']])

        # PSM selection widget (numeric index from the mapping table)
        sel = st.number_input(
            'Select PSM index',
            min_value=0,
            max_value=len(mapped)-1,
            value=0
        )

        # Extract selected PSM row
        row = mapped.iloc[int(sel)]

        # Visualize spectrum if a matching spectrum was found
        if row['matched_title']:
            # Generate annotated spectrum plot
            fig = draw_spectrum(row, row['mz_array'], row['intensity_array'])
            # Display in Streamlit app
            st.pyplot(fig)
        else:
            # Handle case where no matching spectrum was found
            st.warning('No matching spectrum found')


# ---- Application entry point ----

if __name__ == '__main__':
    run_streamlit_app()
