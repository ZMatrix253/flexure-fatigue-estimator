import pytest
from core.geometry import RectangularCantilever
from core.solver import solve_stress_cycle
from core.fatigue import MaterialFatigue, calculate_fatigue, goodman_equivalent_stress


@pytest.fixture
def material():
    return MaterialFatigue(
        sigma_f_prime=1000e6,  # 1000 MPa
        b=-0.1,
        sigma_uts=800e6        # 800 MPa
    )


@pytest.fixture
def geometry_A():
    return RectangularCantilever(L=0.200, b=0.030, h=0.005)


def test_goodman_fully_reversed(geometry_A, material):
    cycle = solve_stress_cycle(geometry_A, F_a=50, R=-1)
    sigma_ar = goodman_equivalent_stress(cycle, material.sigma_uts)
    assert sigma_ar == pytest.approx(80e6, rel=1e-6)


def test_goodman_with_mean_stress(geometry_A, material):
    # Test H
    cycle = solve_stress_cycle(geometry_A, F_a=50, R=0)
    sigma_ar = goodman_equivalent_stress(cycle, material.sigma_uts)
    assert sigma_ar == pytest.approx(80e6 / 0.9, rel=1e-6)  # ≈ 88.89 MPa


def test_basquin_life(geometry_A, material):
    # Test G
    cycle = solve_stress_cycle(geometry_A, F_a=50, R=-1)
    result = calculate_fatigue(cycle, material, N_design=1e6)
    assert result.sigma_ar == pytest.approx(80e6, rel=1e-6)
    # N_f ≈ 4.768 × 10^10
    assert result.N_f == pytest.approx(4.768e10, rel=1e-3)