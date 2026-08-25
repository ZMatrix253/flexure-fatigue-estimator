"""
Unit tests for the large-deflection (nonlinear) solver.
"""

import pytest
import numpy as np
from core.geometry import RectangularCantilever
from core.nonlinear import solve_large_deflection, max_bending_stress_nonlinear
from core.solver import solve_stress_cycle


@pytest.fixture
def geometry():
    """Standard test geometry: 100 mm × 20 mm × 2 mm"""
    return RectangularCantilever(L=0.100, b=0.020, h=0.002)


@pytest.fixture
def E():
    """Young’s modulus of steel"""
    return 200e9  # Pa


def test_zero_force(geometry, E):
    """Zero force must return zero stress and undeformed shape."""
    res = solve_large_deflection(geometry, E, F=0.0)
    assert res.sigma_max == 0.0
    assert res.M_root == 0.0
    assert res.tip_x == pytest.approx(geometry.L)
    assert res.tip_y == pytest.approx(0.0)
    assert res.tip_angle == pytest.approx(0.0)
    assert res.success is True


def test_small_load_matches_linear(geometry, E):
    """At small loads the nonlinear result must closely match linear theory."""
    F = 10.0  # N → linear stress = 75 MPa

    # Linear reference
    sigma_linear = geometry.max_bending_stress(F)

    # Nonlinear
    res = solve_large_deflection(geometry, E, F)

    # Stress should match within 0.2 %
    assert res.sigma_max == pytest.approx(sigma_linear, rel=0.002)

    # Tip deflection should also be close to linear theory
    # δ = F L³ / (3 EI)
    I = geometry.I
    delta_linear = F * geometry.L**3 / (3 * E * I)
    assert res.tip_y == pytest.approx(delta_linear, rel=0.01)


def test_large_load_diverges_from_linear(geometry, E):
    """At larger loads the nonlinear stress must be lower than linear prediction."""
    F = 100.0  # N → linear stress = 750 MPa

    sigma_linear = geometry.max_bending_stress(F)
    res = solve_large_deflection(geometry, E, F)

    # Nonlinear stress must be lower than linear
    assert res.sigma_max < sigma_linear

    # Difference should be noticeable (> 0.5 %)
    relative_diff = (sigma_linear - res.sigma_max) / sigma_linear
    assert relative_diff > 0.005

    # Tip should have moved inward (x_tip < L)
    assert res.tip_x < geometry.L


def test_stress_cycle_nonlinear(geometry, E):
    """Full stress-cycle calculation with nonlinear method must work."""
    cycle = solve_stress_cycle(
        geometry,
        F_a=40.0,
        R=-1.0,
        method="nonlinear",
        E=E,
    )

    assert cycle.method == "nonlinear"
    assert cycle.sigma_a > 0
    assert abs(cycle.sigma_m) < 1e-6  # fully reversed
    assert cycle.R == -1.0


def test_convenience_function(geometry, E):
    """max_bending_stress_nonlinear should match the full solver."""
    F = 25.0
    res = solve_large_deflection(geometry, E, F)
    sigma = max_bending_stress_nonlinear(geometry, E, F)
    assert sigma == pytest.approx(res.sigma_max)