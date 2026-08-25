"""
solver.py – Compute stress cycle for a rectangular cantilever
under constant-amplitude cyclic tip force.
"""

from dataclasses import dataclass
from typing import Union
from .geometry import RectangularCantilever

Number = Union[int, float]


@dataclass(frozen=True)
class StressCycle:
    """Results of a constant-amplitude stress cycle."""
    sigma_max: float   # Pa
    sigma_min: float   # Pa
    sigma_a: float     # Stress amplitude (Pa)
    sigma_m: float     # Mean stress (Pa)
    R: float           # Stress ratio


def solve_stress_cycle(
    geometry: RectangularCantilever,
    F_a: Number,
    R: Number = -1.0,
) -> StressCycle:
    """
    Calculate the stress cycle at the root of the cantilever.

    Parameters
    ----------
    geometry : RectangularCantilever
        The leaf spring geometry
    F_a : float
        Force amplitude (N). Must be > 0.
        F_max = F_a * (1 + R) / (1 - R)   if R ≠ 1
        (For R = -1 → F_max = F_a, F_min = -F_a)
    R : float
        Load ratio R = F_min / F_max
        Common values: -1 (fully reversed), 0 (pulsating)

    Returns
    -------
    StressCycle
    """
    if F_a <= 0:
        raise ValueError("Force amplitude F_a must be positive")
    if R >= 1.0:
        raise ValueError("R-ratio must be < 1")

    # Convert force amplitude + R into max and min forces
    if abs(R + 1.0) < 1e-9:          # R ≈ -1 (fully reversed)
        F_max = F_a
        F_min = -F_a
    else:
        F_max = F_a * (1 + R) / (1 - R) * 2 / (1 + abs((1 + R)/(1 - R)))  
        # Cleaner formulation:
        # F_max = 2 * F_a / (1 - R)
        # F_min = R * F_max
        F_max = 2 * F_a / (1 - R)
        F_min = R * F_max

    # Stresses (linear)
    sigma_max = geometry.max_bending_stress(F_max)
    sigma_min = geometry.max_bending_stress(F_min)

    sigma_a = (sigma_max - sigma_min) / 2.0
    sigma_m = (sigma_max + sigma_min) / 2.0

    return StressCycle(
        sigma_max=sigma_max,
        sigma_min=sigma_min,
        sigma_a=sigma_a,
        sigma_m=sigma_m,
        R=R,
    )