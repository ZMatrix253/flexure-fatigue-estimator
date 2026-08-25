import pytest
from core.geometry import RectangularCantilever


def test_second_moment_of_area():
    # Test A
    g = RectangularCantilever(L=0.200, b=0.030, h=0.005)
    assert g.I == pytest.approx(3.125e-10, rel=1e-6)


def test_max_bending_stress_A():
    # Test A: L=200 mm, b=30 mm, h=5 mm, F=50 N → 80 MPa
    g = RectangularCantilever(L=0.200, b=0.030, h=0.005)
    stress = g.max_bending_stress(50)
    assert stress == pytest.approx(80e6, rel=1e-6)


def test_max_bending_stress_B():
    # Test B: L=100 mm, b=20 mm, h=1 mm, F=5 N → 150 MPa
    g = RectangularCantilever(L=0.100, b=0.020, h=0.001)
    stress = g.max_bending_stress(5)
    assert stress == pytest.approx(150e6, rel=1e-6)


def test_zero_force():
    g = RectangularCantilever(L=0.1, b=0.02, h=0.002)
    assert g.max_bending_stress(0) == 0.0


def test_invalid_dimensions():
    with pytest.raises(ValueError):
        RectangularCantilever(L=-0.1, b=0.02, h=0.002)