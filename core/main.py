"""
main.py – Simple end-to-end example for Flexure Fatigue Estimator (v0.1)
"""

from core.geometry import RectangularCantilever
from core.solver import solve_stress_cycle
from core.fatigue import MaterialFatigue, calculate_fatigue


def main():
    # ------------------------------------------------------------------
    # 1. Geometry (rectangular cantilever leaf spring)
    # ------------------------------------------------------------------
    geometry = RectangularCantilever(
        L=0.100,   # 100 mm
        b=0.020,   # 20 mm
        h=0.002    # 2 mm
    )

    # ------------------------------------------------------------------
    # 2. Loading (constant amplitude cyclic tip force)
    # ------------------------------------------------------------------
    F_a = 10.0    # Force amplitude in Newtons
    R = -1.0      # Fully reversed (R = -1)

    # ------------------------------------------------------------------
    # 3. Material (example values – replace with real data)
    # ------------------------------------------------------------------
    material = MaterialFatigue(
        sigma_f_prime=800e6,  # 800 MPa
        b=-0.12,
        sigma_uts=600e6       # 600 MPa
    )

    N_design = 1_000_000      # Target design life

    # ------------------------------------------------------------------
    # 4. Run analysis
    # ------------------------------------------------------------------
    cycle = solve_stress_cycle(geometry, F_a=F_a, R=R)
    result = calculate_fatigue(cycle, material, N_design=N_design)

    # ------------------------------------------------------------------
    # 5. Print summary
    # ------------------------------------------------------------------
    print("=" * 60)
    print("       FLEXURE FATIGUE ESTIMATOR – v0.1 Results")
    print("=" * 60)

    print("\nGeometry:")
    print(f"  L = {geometry.L*1000:.1f} mm")
    print(f"  b = {geometry.b*1000:.1f} mm")
    print(f"  h = {geometry.h*1000:.1f} mm")

    print("\nLoading:")
    print(f"  F_a = {F_a:.1f} N")
    print(f"  R   = {R}")

    print("\nStress Cycle:")
    print(f"  σ_max = {cycle.sigma_max/1e6:7.1f} MPa")
    print(f"  σ_min = {cycle.sigma_min/1e6:7.1f} MPa")
    print(f"  σ_a   = {cycle.sigma_a/1e6:7.1f} MPa")
    print(f"  σ_m   = {cycle.sigma_m/1e6:7.1f} MPa")

    print("\nFatigue Result (Basquin + Goodman):")
    print(f"  Equivalent stress σ_ar = {result.sigma_ar/1e6:.1f} MPa")
    print(f"  Estimated life N_f     = {result.N_f:.3e} cycles")
    print(f"  Safety factor (life)   = {result.safety_factor_life:.2f}")
    print(f"  Safety factor (stress) = {result.safety_factor_stress:.2f}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()