"""
solver.py – Compute stress cycle for a rectangular cantilever
under constant-amplitude cyclic tip force.
Supports both linear and large-deflection (nonlinear) analysis.
"""

from dataclasses import dataclass
from typing import Union, Literal
from .geometry import RectangularCantilever
from .nonlinear import max_bending_stress_nonlinear

Number = Union[int, float]
Method = Literal["linear", "nonlinear"]


@dataclass(frozen=True)
class StressCycle:
    """Results of a constant-amplitude stress cycle."""
    sigma_max: float   # Pa
    sigma_min: float   # Pa
    sigma_a: float     # Stress amplitude (Pa)
    sigma_m: float     # Mean stress (Pa)
    R: float           # Stress ratio
    method: str = "linear"


def solve_stress_cycle(
    geometry: RectangularCantilever,
    F_a: Number,
    R: Number = -1.0,
    method: Method = "linear",
    E: float | None = None,
) -> StressCycle:
    """
    Calculate the stress cycle at the root of the cantilever.

    Parameters
    ----------
    geometry : RectangularCantilever
    F_a : float
        Force amplitude (N). Must be > 0.
    R : float
        Load ratio R = F_min / F_max
    method : "linear" | "nonlinear"
        Analysis method
    E : float, optional
        Young’s modulus [Pa]. Required when method="nonlinear".

    Returns
    -------
    StressCycle
    """
    if F_a <= 0:
        raise ValueError("Force amplitude F_a must be positive")
    if R >= 1.0:
        raise ValueError("R-ratio must be < 1")
    if method == "nonlinear" and E is None:
        raise ValueError("Young’s modulus E must be provided for nonlinear analysis")

    # Convert force amplitude + R into max and min forces
    if abs(R + 1.0) < 1e-9:          # R ≈ -1 (fully reversed)
        F_max = F_a
        F_min = -F_a
    else:
        F_max = 2 * F_a / (1 - R)
        F_min = R * F_max

    # Calculate stresses
    if method == "linear":
        sigma_max = geometry.max_bending_stress(F_max)
        sigma_min = geometry.max_bending_stress(F_min)
    else:
        # Nonlinear (large-deflection)
        sigma_max = max_bending_stress_nonlinear(geometry, E, F_max)
        sigma_min = max_bending_stress_nonlinear(geometry, E, F_min)

    sigma_a = (sigma_max - sigma_min) / 2.0
    sigma_m = (sigma_max + sigma_min) / 2.0

    return StressCycle(
        sigma_max=sigma_max,
        sigma_min=sigma_min,
        sigma_a=sigma_a,
        sigma_m=sigma_m,
        R=R,
        method=method,
    )