"""
geometry.py – Supported flexure geometries for Flexure Fatigue Estimator
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, runtime_checkable
import math


@runtime_checkable
class FlexureGeometry(Protocol):
    L: float

    @property
    def I(self) -> float: ...
    @property
    def c(self) -> float: ...
    @property
    def section_modulus(self) -> float: ...
    def max_bending_stress(self, F: float) -> float: ...


@dataclass(frozen=True, slots=True)
class RectangularCantilever:
    L: float
    b: float
    h: float

    def __post_init__(self) -> None:
        if self.L <= 0 or self.b <= 0 or self.h <= 0:
            raise ValueError("L, b and h must all be positive")

    @property
    def area(self) -> float:
        return self.b * self.h

    @property
    def I(self) -> float:
        return self.b * self.h**3 / 12.0

    @property
    def c(self) -> float:
        return self.h / 2.0

    @property
    def section_modulus(self) -> float:
        return self.I / self.c

    def max_bending_stress(self, F: float) -> float:
        return 6.0 * F * self.L / (self.b * self.h**2)

    def __repr__(self) -> str:
        return (f"RectangularCantilever(L={self.L*1e3:.1f} mm, "
                f"b={self.b*1e3:.1f} mm, h={self.h*1e3:.1f} mm)")


@dataclass(frozen=True, slots=True)
class CircularCantilever:
    L: float
    d: float

    def __post_init__(self) -> None:
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
        return math.pi * self.d**4 / 64.0

    @property
    def c(self) -> float:
        return self.radius

    @property
    def section_modulus(self) -> float:
        return self.I / self.c

    def max_bending_stress(self, F: float) -> float:
        return 32.0 * F * self.L / (math.pi * self.d**3)

    def __repr__(self) -> str:
        return (f"CircularCantilever(L={self.L*1e3:.1f} mm, "
                f"d={self.d*1e3:.1f} mm)")