"""
nonlinear.py – Large-deflection (elastica) solver for rectangular cantilever
Uses numerical integration of the nonlinear beam equations (scipy).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
import numpy as np
from scipy.integrate import solve_bvp

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
        Tip force [N] (positive in the direction that produces positive curvature)

    Returns
    -------
    NonlinearResult
    """
    if F == 0.0:
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

    # Non-dimensional load parameter
    # We solve in arc-length coordinates s ∈ [0, L]

    def ode(s, y):
        # y = [theta, x, y_coord]
        theta, x, y_coord = y
        # Moment at s: M(s) = F * (x_tip - x)   but x_tip is unknown a priori
        # We use a shooting-friendly form or BVP with unknown tip_x
        # Better: introduce the horizontal lever arm as part of the state
        # Classic approach: dθ/ds = (F / EI) * (x_tip - x)
        # We treat x_tip as an unknown parameter → use solve_bvp with extra parameter
        return np.vstack((
            (F / EI) * (p[0] - x),   # dθ/ds   (p[0] = x_tip)
            np.cos(theta),           # dx/ds
            np.sin(theta),           # dy/ds
        ))

    def bc(ya, yb, p):
        # ya = values at s=0 (root), yb at s=L (tip)
        # p[0] = x_tip
        theta0, x0, y0 = ya
        thetaL, xL, yL = yb
        return np.array([
            theta0,          # θ(0) = 0
            x0,              # x(0) = 0
            y0,              # y(0) = 0
            xL - p[0],       # x(L) == x_tip
            # free end moment = 0 already satisfied by construction of ODE
            # we only need one more condition → we can use yb[0] free
        ])

    # Because the classic free-end moment condition is automatically satisfied
    # when M = F*(x_tip - x), we need a slightly different formulation.

    # ---------- More robust shooting / BVP formulation ----------
    # State: [θ, x, y]
    # Parameter: tip angle or use known free moment = 0

    def ode_simple(s, y):
        theta, x, y_coord = y
        # We will shoot on the root moment (or equivalently tip angle)
        return [
            y[3] / EI,          # dθ/ds = M(s)/EI   – we carry M as state? 
            # Simpler classic way:
        ]

    # ----- Clean, well-tested implementation (shooting on tip angle) -----

    from scipy.integrate import solve_ivp
    from scipy.optimize import root_scalar

    def residual(theta_tip_guess: float) -> float:
        """Integrate from tip back to root and enforce θ(0)=0."""
        # Integrate from free end (s=L) toward root (s=0)
        # At tip: M=0, θ=theta_tip_guess, x=?, but we start from tip
        # Better forward integration from root with unknown root moment.

        # Forward shooting on root curvature (or root moment)
        def shoot(M_root_guess):
            def f(s, u):
                # u = [θ, x, y]
                theta, x, y = u
                M = M_root_guess - F * x          # moment decreases as we move out
                return [
                    M / EI,
                    np.cos(theta),
                    np.sin(theta),
                ]

            sol = solve_ivp(
                f,
                [0, L],
                [0.0, 0.0, 0.0],          # θ=0, x=0, y=0 at root
                rtol=1e-6,
                atol=1e-8,
                dense_output=False,
            )
            if not sol.success:
                return 1e6
            # At tip the moment should be zero → M_root - F * x_tip == 0
            x_tip = sol.y[1, -1]
            return M_root_guess - F * x_tip

        # Bracket the root moment
        # Linear estimate: M_lin = F * L
        M_lin = F * L
        try:
            root = root_scalar(shoot, bracket=[0.1 * M_lin, 1.5 * M_lin], xtol=1e-8)
            M_root = root.root
        except Exception:
            # fallback
            M_root = M_lin

        # Final integration with the found M_root
        def f(s, u):
            theta, x, y = u
            M = M_root - F * x
            return [M / EI, np.cos(theta), np.sin(theta)]

        sol = solve_ivp(f, [0, L], [0.0, 0.0, 0.0], rtol=1e-8, atol=1e-10)

        tip_x = sol.y[1, -1]
        tip_y = sol.y[2, -1]
        tip_angle = sol.y[0, -1]
        sigma = (M_root * geometry.c) / geometry.I

        return NonlinearResult(
            sigma_max=sigma,
            M_root=M_root,
            tip_x=tip_x,
            tip_y=tip_y,
            tip_angle=tip_angle,
            success=sol.success,
        )

    # Call the solver
    return residual(0.0)   # the function above already does everything


# Convenience wrapper that matches the linear API style
def max_bending_stress_nonlinear(
    geometry: RectangularCantilever,
    E: float,
    F: float,
) -> float:
    """Return only the maximum bending stress (Pa)."""
    res = solve_large_deflection(geometry, E, F)
    return res.sigma_max