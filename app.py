"""
app.py – Minimal Streamlit interface for Flexure Fatigue Estimator
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from core.geometry import RectangularCantilever, CircularCantilever
from core.solver import solve_stress_cycle
from core.fatigue import MaterialFatigue, calculate_fatigue


st.set_page_config(page_title="Flexure Fatigue Estimator", layout="wide")
st.title("Flexure Fatigue Estimator")
st.markdown("Simple stress-life fatigue analysis for compliant flexures")

# ------------------------------------------------------------------
# Sidebar – Inputs
# ------------------------------------------------------------------
st.sidebar.header("Geometry")

geo_type = st.sidebar.selectbox("Type", ["Rectangular", "Circular"])

if geo_type == "Rectangular":
    L = st.sidebar.number_input("Length L [mm]", value=100.0, min_value=1.0)
    b = st.sidebar.number_input("Width b [mm]", value=20.0, min_value=0.1)
    h = st.sidebar.number_input("Thickness h [mm]", value=2.0, min_value=0.1)
    geometry = RectangularCantilever(L=L/1000, b=b/1000, h=h/1000)
else:
    L = st.sidebar.number_input("Length L [mm]", value=150.0, min_value=1.0)
    d = st.sidebar.number_input("Diameter d [mm]", value=8.0, min_value=0.1)
    geometry = CircularCantilever(L=L/1000, d=d/1000)

st.sidebar.header("Material")
E = st.sidebar.number_input("Young's modulus E [GPa]", value=200.0, min_value=1.0)
sigma_f = st.sidebar.number_input("σ_f' [MPa]", value=800.0, min_value=1.0)
b_exp = st.sidebar.number_input("Basquin exponent b", value=-0.12, max_value=-0.01)
sigma_uts = st.sidebar.number_input("σ_uts [MPa]", value=600.0, min_value=1.0)

material = MaterialFatigue(
    sigma_f_prime=sigma_f * 1e6,
    b=b_exp,
    sigma_uts=sigma_uts * 1e6,
)

st.sidebar.header("Loading")
F_a = st.sidebar.number_input("Force amplitude F_a [N]", value=40.0, min_value=0.1)
R = st.sidebar.number_input("R-ratio", value=-1.0, min_value=-1.0, max_value=0.99)

st.sidebar.header("Analysis")
method = st.sidebar.selectbox("Method", ["linear", "nonlinear"])
N_design = st.sidebar.number_input("Target life N_design", value=1_000_000, min_value=1000)

# ------------------------------------------------------------------
# Run button
# ------------------------------------------------------------------
if st.sidebar.button("Run Analysis", type="primary"):
    with st.spinner("Running analysis..."):
        cycle = solve_stress_cycle(
            geometry=geometry,
            F_a=F_a,
            R=R,
            method=method,
            E=E * 1e9,
        )
        result = calculate_fatigue(cycle, material, N_design=N_design)

    # Results
    st.subheader("Results")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("σ_a", f"{cycle.sigma_a/1e6:.1f} MPa")
    col2.metric("σ_m", f"{cycle.sigma_m/1e6:.1f} MPa")
    col3.metric("Predicted life", f"{result.N_f:.2e} cycles")
    col4.metric("Safety factor (life)", f"{result.safety_factor_life:.2f}")

    from core.report import generate_markdown_report

    # ... after calculation ...

    report_md = generate_markdown_report(
        geometry=geometry,
        material=material,
        cycle=cycle,
        result=result,
        E=E * 1e9,
        F_a=F_a,
        R=R,
        method=method,
        N_design=N_design,
        project_title="Flexure Fatigue Analysis",
        author="Your Name",          # change this
    )

    st.download_button(
        label="Download Engineering Report (Markdown)",
        data=report_md,
        file_name="ffe_report.md",
        mime="text/markdown",
    )

    # Pass / Fail
    if result.N_f >= N_design:
        st.success(f"PASS – Life exceeds target ({N_design:.0e} cycles)")
    else:
        st.error(f"FAIL – Life is below target ({N_design:.0e} cycles)")

    # Simple stress history plot (constant amplitude)
    st.subheader("Stress History (schematic)")
    t = np.linspace(0, 4, 400)          # 2 cycles
    sigma = cycle.sigma_m + cycle.sigma_a * np.sin(2 * np.pi * t)

    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(t, sigma / 1e6, color="#1f77b4", linewidth=2)
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_xlabel("Cycles")
    ax.set_ylabel("Stress [MPa]")
    ax.set_title("Constant-amplitude stress cycle")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

    # Details
    with st.expander("Detailed results"):
        st.write(f"**Geometry:** {geometry}")
        st.write(f"**Method:** {method}")
        st.write(f"**σ_max:** {cycle.sigma_max/1e6:.2f} MPa")
        st.write(f"**σ_min:** {cycle.sigma_min/1e6:.2f} MPa")
        st.write(f"**σ_ar (Goodman):** {result.sigma_ar/1e6:.2f} MPa")
        st.write(f"**Safety factor (stress):** {result.safety_factor_stress:.2f}")

else:
    st.info("Adjust the parameters in the sidebar and click **Run Analysis**.")