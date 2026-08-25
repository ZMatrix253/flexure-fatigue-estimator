"""
geometry.py – Rectangular cross-section cantilever leaf spring
Only geometry allowed in FFE v0.1
"""

from dataclasses import dataclass
from typing import Union

Number = Union[int, float]


@dataclass(frozen=True)
class RectangularCantilever:
    """
    Rectangular cross-section cantilever leaf spring.

    Parameters
    ----------
    L : float
        Length (m)
    b : float
        Width (m)
    h : float
        Thickness (m)
    """
    L: float
    b: float
    h: float

    def __post_init__(self):
        if self.L <= 0 or self.b <= 0 or self.h <= 0:
            raise ValueError("L, b and h must all be positive")

    # ------------------------------------------------------------------
    # Geometric properties
    # ------------------------------------------------------------------
    @property
    def area(self) -> float:
        """Cross-sectional area (m²)"""
        return self.b * self.h

    @property
    def I(self) -> float:
        """Second moment of area about the bending axis (m⁴)
        I = (b * h³) / 12
        """
        return (self.b * self.h**3) / 12.0

    @property
    def c(self) -> float:
        """Distance from neutral axis to outer fibre (m)"""
        return self.h / 2.0

    @property
    def section_modulus(self) -> float:
        """Section modulus Z = I / c (m³)"""
        return self.I / self.c

    # ------------------------------------------------------------------
    # Stress calculation (linear elastic beam theory)
    # ------------------------------------------------------------------
    def max_bending_stress(self, F: Number) -> float:
        """
        Maximum bending stress at the root under tip force F.

        σ = M * c / I = (F * L) * (h/2) / I = 6 F L / (b h²)

        Parameters
        ----------
        F : float
            Tip force (N). Positive = causes tension on the top surface.

        Returns
        -------
        float
            Maximum bending stress (Pa)
        """
        return (6.0 * F * self.L) / (self.b * self.h**2)

    def __repr__(self) -> str:
        return (f"RectangularCantilever(L={self.L:.4g} m, "
                f"b={self.b:.4g} m, h={self.h:.4g} m)")