"""
main.py – End-to-end example for Flexure Fatigue Estimator (v0.1 + nonlinear)
"""

from core.geometry import RectangularCantilever
from core.solver import solve_stress_cycle
from core.fatigue import MaterialFatigue, calculate_fatigue


def main():
    # ------------------------------------------------------------------
    # 1. Geometry
    # ------------------------------------------------------------------
    geometry = RectangularCantilever(
        L=0.100,   # 100 mm
        b=0.020,   # 20 mm
        h=0.002    # 2 mm
    )

    # ------------------------------------------------------------------
    # 2. Loading
    # ------------------------------------------------------------------
    F_a = 40.0     # Force amplitude [N]  (increased to show nonlinearity)
    R = -1.0       # Fully reversed

    # ------------------------------------------------------------------
    # 3. Material
    # ------------------------------------------------------------------
    E = 200e9      # Young’s modulus [Pa] – required for nonlinear
    material = MaterialFatigue(
        sigma_f_prime=800e6,  # 800 MPa
        b=-0.12,
        sigma_uts=600e6       # 600 MPa
    )
    N_design = 1_000_000

    # ------------------------------------------------------------------
    # 4. Run both analyses
    # ------------------------------------------------------------------
    cycle_lin = solve_stress_cycle(geometry, F_a=F_a, R=R, method="linear")
    result_lin = calculate_fatigue(cycle_lin, material, N_design=N_design)

    cycle_nl = solve_stress_cycle(
        geometry, F_a=F_a, R=R, method="nonlinear", E=E
    )
    result_nl = calculate_fatigue(cycle_nl, material, N_design=N_design)

    # ------------------------------------------------------------------
    # 5. Print comparison
    # ------------------------------------------------------------------
    print("=" * 70)
    print("          FLEXURE FATIGUE ESTIMATOR – Linear vs Nonlinear")
    print("=" * 70)

    print("\nGeometry:")
    print(f"  L = {geometry.L*1000:.1f} mm,  b = {geometry.b*1000:.1f} mm,  h = {geometry.h*1000:.1f} mm")
    print(f"  E = {E/1e9:.0f} GPa")

    print("\nLoading:")
    print(f"  F_a = {F_a:.1f} N,   R = {R}")

    print("\n" + "-" * 70)
    print(f"{'Quantity':<28} {'Linear':>15} {'Nonlinear':>15}")
    print("-" * 70)

    print(f"{'σ_max (MPa)':<28} {cycle_lin.sigma_max/1e6:15.1f} {cycle_nl.sigma_max/1e6:15.1f}")
    print(f"{'σ_min (MPa)':<28} {cycle_lin.sigma_min/1e6:15.1f} {cycle_nl.sigma_min/1e6:15.1f}")
    print(f"{'σ_a   (MPa)':<28} {cycle_lin.sigma_a/1e6:15.1f} {cycle_nl.sigma_a/1e6:15.1f}")
    print(f"{'σ_m   (MPa)':<28} {cycle_lin.sigma_m/1e6:15.1f} {cycle_nl.sigma_m/1e6:15.1f}")
    print(f"{'σ_ar  (MPa)':<28} {result_lin.sigma_ar/1e6:15.1f} {result_nl.sigma_ar/1e6:15.1f}")
    print(f"{'Life N_f (cycles)':<28} {result_lin.N_f:15.3e} {result_nl.N_f:15.3e}")
    print(f"{'Safety factor (life)':<28} {result_lin.safety_factor_life:15.2f} {result_nl.safety_factor_life:15.2f}")
    print(f"{'Safety factor (stress)':<28} {result_lin.safety_factor_stress:15.2f} {result_nl.safety_factor_stress:15.2f}")

    print("-" * 70)
    print()


if __name__ == "__main__":
    main()