"""
geometry.py – Supported flexure geometries for FFE v0.1+
"""

from dataclasses import dataclass
from typing import Union
import math

Number = Union[int, float]


@dataclass(frozen=True)
class RectangularCantilever:
    """Rectangular cross-section cantilever leaf spring."""
    L: float   # length [m]
    b: float   # width [m]
    h: float   # thickness [m]

    def __post_init__(self):
        if self.L <= 0 or self.b <= 0 or self.h <= 0:
            raise ValueError("L, b and h must all be positive")

    @property
    def area(self) -> float:
        return self.b * self.h

    @property
    def I(self) -> float:
        """Second moment of area [m⁴]"""
        return (self.b * self.h**3) / 12.0

    @property
    def c(self) -> float:
        """Distance to outer fibre [m]"""
        return self.h / 2.0

    @property
    def section_modulus(self) -> float:
        return self.I / self.c

    def max_bending_stress(self, F: Number) -> float:
        """Max bending stress at root under tip force F [Pa]"""
        return (6.0 * F * self.L) / (self.b * self.h**2)

    def __repr__(self) -> str:
        return (f"RectangularCantilever(L={self.L:.4g} m, "
                f"b={self.b:.4g} m, h={self.h:.4g} m)")


@dataclass(frozen=True)
class CircularCantilever:
    """Circular cross-section cantilever."""
    L: float   # length [m]
    d: float   # diameter [m]

    def __post_init__(self):
        if self.L <= 0 or self.d <= 0:
            raise ValueError("L and d must be positive")

    @property
    def radius(self) -> float:
        return self.d / 2.0

    @property
    def area(self) -> float:
        return math.pi * self.radius**2

    @property
    def I(self) -> float:
        """Second moment of area [m⁴] – π d⁴ / 64"""
        return math.pi * self.d**4 / 64.0

    @property
    def c(self) -> float:
        return self.radius

    @property
    def section_modulus(self) -> float:
        return self.I / self.c

    def max_bending_stress(self, F: Number) -> float:
        """
        Max bending stress at root under tip force F [Pa]
        σ = 32 F L / (π d³)
        """
        return (32.0 * F * self.L) / (math.pi * self.d**3)

    def __repr__(self) -> str:
        return f"CircularCantilever(L={self.L:.4g} m, d={self.d:.4g} m)"