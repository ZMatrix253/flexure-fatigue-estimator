"""
config.py – Load analysis configuration from YAML
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml

from .geometry import RectangularCantilever, CircularCantilever
from .fatigue import MaterialFatigue


@dataclass
class AnalysisConfig:
    geometry: RectangularCantilever | CircularCantilever
    material: MaterialFatigue
    E: float
    F_a: float
    R: float
    method: str
    N_design: float


def load_config(path: str | Path) -> AnalysisConfig:
    """Load a YAML configuration file and return an AnalysisConfig."""
    path = Path(path)
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    # --- Geometry ---
    geo = data["geometry"]
    geo_type = geo["type"].lower()

    if geo_type == "rectangular":
        geometry = RectangularCantilever(
            L=float(geo["L"]),
            b=float(geo["b"]),
            h=float(geo["h"]),
        )
    elif geo_type == "circular":
        geometry = CircularCantilever(
            L=float(geo["L"]),
            d=float(geo["d"]),
        )
    else:
        raise ValueError(f"Unknown geometry type: {geo_type}")

    # --- Material ---
    mat = data["material"]
    material = MaterialFatigue(
        sigma_f_prime=float(mat["sigma_f_prime"]),
        b=float(mat["b"]),
        sigma_uts=float(mat["sigma_uts"]),
    )
    E = float(mat["E"])

    # --- Load ---
    load = data["load"]
    F_a = float(load["F_a"])
    R = float(load["R"])

    # --- Analysis options ---
    analysis = data.get("analysis", {})
    method = analysis.get("method", "linear").lower()
    N_design = float(analysis.get("N_design", 1e6))

    if method not in ("linear", "nonlinear"):
        raise ValueError("method must be 'linear' or 'nonlinear'")

    return AnalysisConfig(
        geometry=geometry,
        material=material,
        E=E,
        F_a=F_a,
        R=R,
        method=method,
        N_design=N_design,
    )