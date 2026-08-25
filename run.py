"""
run.py – Run an analysis from a YAML configuration file
Usage:  python run.py examples/rectangular_leaf.yaml
"""

import sys
from core.config import load_config
from core.solver import solve_stress_cycle
from core.fatigue import calculate_fatigue


def main(config_path: str):
    cfg = load_config(config_path)

    cycle = solve_stress_cycle(
        geometry=cfg.geometry,
        F_a=cfg.F_a,
        R=cfg.R,
        method=cfg.method,
        E=cfg.E,
    )

    result = calculate_fatigue(cycle, cfg.material, N_design=cfg.N_design)

    print("=" * 60)
    print(f"  Flexure Fatigue Estimator – {cfg.method.upper()} analysis")
    print("=" * 60)
    print(f"Geometry : {cfg.geometry}")
    print(f"F_a      : {cfg.F_a} N")
    print(f"R        : {cfg.R}")
    print()
    print(f"σ_a      : {cycle.sigma_a/1e6:.2f} MPa")
    print(f"σ_m      : {cycle.sigma_m/1e6:.2f} MPa")
    print(f"σ_ar     : {result.sigma_ar/1e6:.2f} MPa")
    print(f"N_f      : {result.N_f:.3e} cycles")
    print(f"SF_life  : {result.safety_factor_life:.2f}")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run.py <config.yaml>")
        sys.exit(1)
    main(sys.argv[1])