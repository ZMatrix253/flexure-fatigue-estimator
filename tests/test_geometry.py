import pytest
import math
from core.geometry import RectangularCantilever, CircularCantilever


def test_rectangular_second_moment_of_area():
    g = RectangularCantilever(L=0.200, b=0.030, h=0.005)
    assert g.I == pytest.approx(3.125e-10, rel=1e-6)


def test_rectangular_max_bending_stress_A():
    g = RectangularCantilever(L=0.200, b=0.030, h=0.005)
    assert g.max_bending_stress(50) == pytest.approx(80e6, rel=1e-6)


def test_rectangular_max_bending_stress_B():
    g = RectangularCantilever(L=0.100, b=0.020, h=0.001)
    assert g.max_bending_stress(5) == pytest.approx(150e6, rel=1e-6)


def test_rectangular_zero_force():
    g = RectangularCantilever(L=0.1, b=0.02, h=0.002)
    assert g.max_bending_stress(0) == 0.0


def test_rectangular_invalid_dimensions():
    with pytest.raises(ValueError):
        RectangularCantilever(L=-0.1, b=0.02, h=0.002)


def test_circular_second_moment():
    g = CircularCantilever(L=0.2, d=0.010)
    expected_I = math.pi * (0.010)**4 / 64.0
    assert g.I == pytest.approx(expected_I, rel=1e-6)


def test_circular_max_bending_stress():
    g = CircularCantilever(L=0.200, d=0.010)
    expected = (32 * 50 * 0.2) / (math.pi * 0.01**3)
    assert g.max_bending_stress(50) == pytest.approx(expected, rel=1e-6)


def test_circular_zero_force():
    g = CircularCantilever(L=0.15, d=0.008)
    assert g.max_bending_stress(0) == 0.0


def test_circular_invalid_dimensions():
    with pytest.raises(ValueError):
        CircularCantilever(L=-0.1, d=0.01)
    with pytest.raises(ValueError):
        CircularCantilever(L=0.1, d=0.0)