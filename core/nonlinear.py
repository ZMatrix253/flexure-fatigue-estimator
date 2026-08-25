"""
nonlinear.py – Large-deflection (elastica) solver for rectangular cantilever
Uses numerical integration of the nonlinear beam equations (scipy).
"""

from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import root_scalar

from .geometry import RectangularCantilever


@dataclass(frozen=True)
class NonlinearResult:
    sigma_max: float      # Pa – maximum bending stress at root
    M_root: float         # N·m
    tip_x: float          # m – horizontal position of tip
    tip_y: float          # m – vertical deflection of tip
    tip_angle: float      # rad
    success: bool


def solve_large_deflection(
    geometry: RectangularCantilever,
    E: float,
    F: float,
) -> NonlinearResult:
    """
    Solve the large-deflection cantilever under a vertical tip force F.

    Parameters
    ----------
    geometry : RectangularCantilever
    E : float
        Young’s modulus [Pa]
    F : float
        Tip force [N] (positive produces positive curvature)

    Returns
    -------
    NonlinearResult
    """
    if abs(F) < 1e-12:
        return NonlinearResult(
            sigma_max=0.0,
            M_root=0.0,
            tip_x=geometry.L,
            tip_y=0.0,
            tip_angle=0.0,
            success=True,
        )

    L = geometry.L
    EI = E * geometry.I
    M_lin = F * L          # linear theory estimate (used for bracketing)

    def shoot(M_root_guess: float) -> float:
        """Integrate from root to tip and return residual of tip moment = 0."""
        def f(s, u):
            # u = [theta, x, y]
            theta, x, y = u
            M = M_root_guess - F * x
            return [
                M / EI,          # dθ/ds
                np.cos(theta),   # dx/ds
                np.sin(theta),   # dy/ds
            ]

        sol = solve_ivp(
            f,
            [0.0, L],
            [0.0, 0.0, 0.0],    # θ(0)=0, x(0)=0, y(0)=0
            rtol=1e-7,
            atol=1e-9,
            dense_output=False,
        )

        if not sol.success:
            return 1e6

        x_tip = sol.y[1, -1]
        # Residual: moment at tip should be zero → M_root - F * x_tip == 0
        return M_root_guess - F * x_tip

    # Find the correct root moment by shooting
    try:
        # Bracket around the linear estimate
        bracket = sorted([0.05 * M_lin, 1.8 * M_lin])
        root = root_scalar(shoot, bracket=bracket, xtol=1e-10)
        M_root = root.root
        success = root.converged
    except Exception:
        # Fallback to linear if shooting fails
        M_root = M_lin
        success = False

    # Final high-accuracy integration with the found M_root
    def f_final(s, u):
        theta, x, y = u
        M = M_root - F * x
        return [M / EI, np.cos(theta), np.sin(theta)]

    sol = solve_ivp(
        f_final,
        [0.0, L],
        [0.0, 0.0, 0.0],
        rtol=1e-8,
        atol=1e-10,
    )

    tip_x = float(sol.y[1, -1])
    tip_y = float(sol.y[2, -1])
    tip_angle = float(sol.y[0, -1])
    sigma_max = (M_root * geometry.c) / geometry.I

    return NonlinearResult(
        sigma_max=sigma_max,
        M_root=M_root,
        tip_x=tip_x,
        tip_y=tip_y,
        tip_angle=tip_angle,
        success=success and sol.success,
    )


def max_bending_stress_nonlinear(
    geometry: RectangularCantilever,
    E: float,
    F: float,
) -> float:
    """Convenience wrapper – returns only max bending stress [Pa]."""
    return solve_large_deflection(geometry, E, F).sigma_max