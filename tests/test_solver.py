import pytest
from core.geometry import RectangularCantilever
from core.solver import solve_stress_cycle


@pytest.fixture
def geometry_A():
    return RectangularCantilever(L=0.200, b=0.030, h=0.005)


def test_fully_reversed(geometry_A):
    # Test D: Fa=50 N, R=-1
    cycle = solve_stress_cycle(geometry_A, F_a=50, R=-1)
    assert cycle.sigma_max == pytest.approx(80e6, rel=1e-6)
    assert cycle.sigma_min == pytest.approx(-80e6, rel=1e-6)
    assert cycle.sigma_a == pytest.approx(80e6, rel=1e-6)
    assert cycle.sigma_m == pytest.approx(0.0, abs=1e-6)
    assert cycle.R == -1


def test_pulsating(geometry_A):
    # Test E: Fa=50 N, R=0
    cycle = solve_stress_cycle(geometry_A, F_a=50, R=0)
    assert cycle.sigma_max == pytest.approx(160e6, rel=1e-6)
    assert cycle.sigma_min == pytest.approx(0.0, abs=1e-6)
    assert cycle.sigma_a == pytest.approx(80e6, rel=1e-6)
    assert cycle.sigma_m == pytest.approx(80e6, rel=1e-6)
    assert cycle.R == 0


def test_R_0_5(geometry_A):
    # Test F: Fa=40 N, R=0.5
    cycle = solve_stress_cycle(geometry_A, F_a=40, R=0.5)
    assert cycle.sigma_max == pytest.approx(256e6, rel=1e-6)
    assert cycle.sigma_min == pytest.approx(128e6, rel=1e-6)
    assert cycle.sigma_a == pytest.approx(64e6, rel=1e-6)
    assert cycle.sigma_m == pytest.approx(192e6, rel=1e-6)