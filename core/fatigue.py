"""
fatigue.py – Basquin + Goodman mean-stress correction
"""

from dataclasses import dataclass
from typing import Union
from .solver import StressCycle

Number = Union[int, float]


@dataclass(frozen=True)
class FatigueResult:
    """Result of a stress-life fatigue calculation."""
    sigma_ar: float      # Equivalent fully-reversed stress (Pa)
    N_f: float           # Estimated cycles to failure
    safety_factor_life: float   # N_f / N_design (if N_design given)
    safety_factor_stress: float # σ_allowable / σ_ar (simple)


@dataclass(frozen=True)
class MaterialFatigue:
    """
    Minimal material data needed for Basquin + Goodman.
    
    Parameters
    ----------
    sigma_f_prime : float
        Fatigue strength coefficient σ_f' (Pa)
    b : float
        Basquin exponent (usually negative, e.g. -0.12)
    sigma_uts : float
        Ultimate tensile strength (Pa)
    """
    sigma_f_prime: float
    b: float
    sigma_uts: float

    def __post_init__(self):
        if self.sigma_f_prime <= 0 or self.sigma_uts <= 0:
            raise ValueError("Strength values must be positive")
        if self.b >= 0:
            raise ValueError("Basquin exponent b should be negative")


def goodman_equivalent_stress(cycle: StressCycle, sigma_uts: Number) -> float:
    """
    Goodman mean-stress correction.
    
    σ_ar = σ_a / (1 - σ_m / σ_uts)
    
    Returns equivalent fully-reversed stress (Pa).
    """
    if cycle.sigma_m < 0:
        # Conservative: ignore beneficial compressive mean stress
        return cycle.sigma_a

    if cycle.sigma_m >= sigma_uts:
        raise ValueError("Mean stress ≥ UTS – static failure expected")

    return cycle.sigma_a / (1.0 - cycle.sigma_m / sigma_uts)


def basquin_life(sigma_ar: Number, material: MaterialFatigue) -> float:
    """
    Basquin equation solved for life:
    
    σ_ar = σ_f' * (2 N_f)^b
    → N_f = 0.5 * (σ_ar / σ_f')^(1/b)
    """
    if sigma_ar <= 0:
        raise ValueError("Equivalent stress must be positive")

    ratio = sigma_ar / material.sigma_f_prime
    N_f = 0.5 * (ratio ** (1.0 / material.b))
    return N_f


def calculate_fatigue(
    cycle: StressCycle,
    material: MaterialFatigue,
    N_design: Number = 1e6,
) -> FatigueResult:
    """
    Full fatigue calculation: Goodman → Basquin → safety factors.
    """
    sigma_ar = goodman_equivalent_stress(cycle, material.sigma_uts)
    N_f = basquin_life(sigma_ar, material)

    sf_life = N_f / N_design if N_design > 0 else float("inf")
    
    # Simple stress safety factor against the material's fatigue strength at N_design
    sigma_allow = material.sigma_f_prime * (2 * N_design) ** material.b
    sf_stress = sigma_allow / sigma_ar if sigma_ar > 0 else float("inf")

    return FatigueResult(
        sigma_ar=sigma_ar,
        N_f=N_f,
        safety_factor_life=sf_life,
        safety_factor_stress=sf_stress,
    )