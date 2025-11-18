"""
Visualization module for PSM Viewer.
Contains functions for generating annotated spectrum plots.
"""

import matplotlib.pyplot as plt
from spectrum_utils import spectrum as sus
from spectrum_utils import plot as sup




def draw_spectrum(row, mz, inten):
    """
    Generate annotated spectrum plot with b/y-ion fragment annotations.

    Args:
        row (pd.Series): PSM row with spectrum data.
        mz (numpy.ndarray): Mass-to-charge ratios.
        inten (numpy.ndarray): Peak intensities.

    Returns:
        matplotlib.figure.Figure: Annotated spectrum plot.
    """
    # Create matplotlib figure with standard size for spectrum visualization
    fig, ax = plt.subplots(figsize=(12, 6))

    # Set descriptive title combining spectrum identifier and peptide sequence
    title = row.get('matched_title', 'Unknown')
    sequence = row.get('sequence', 'Unknown')
    ax.set_title(f"Spectrum {title} — Sequence: {sequence}")

    # Apply clean styling: remove top and right spines for modern appearance
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    # Extract precursor ion mass-to-charge ratio for processing
    precursor_mz = float(row['pepmass'][0])
    # Charge (default 2)
    charge = 2

    # Create spectrum-utils MsmsSpectrum object for advanced processing
    spec = sus.MsmsSpectrum(row['matched_title'], precursor_mz, charge, mz, inten)

    # Process spectrum for optimal visualization:
    # Limit m/z range to typical peptide fragment masses
    # Remove precursor peak (within tolerance)
    # Filter to most intense peaks for clarity
    # Apply scaling to compress dynamic range
    # Annotate theoretical b and y fragment ions
    fragment_tol_mass = 10
    fragment_tol_mode = "ppm"
    mz_min = 100
    mz_max = 1400
    min_intensity = 0.05
    max_num_peaks = 50
    scale_intensity = "root"
    ion_types = "aby"

    spec = (
        spec.set_mz_range(min_mz=mz_min, max_mz=mz_max)
        .remove_precursor_peak(fragment_tol_mass, fragment_tol_mode)
        .filter_intensity(min_intensity=min_intensity, max_num_peaks=max_num_peaks)
        .scale_intensity(scale_intensity)
        .annotate_proforma(row['sequence'], fragment_tol_mass, fragment_tol_mode, ion_types=ion_types)
    )

    # Render the processed spectrum using spectrum-utils plotting interface
    sup.spectrum(spec, grid=False, ax=ax)
    return fig
