def solve_large_deflection(
    geometry: RectangularCantilever,
    E: float,          # Young’s modulus [Pa]
    F: float,          # tip force [N] (positive downward)
) -> dict:
    """
    Returns:
        sigma_max   – max bending stress at root [Pa]
        tip_x, tip_y – tip coordinates
        tip_angle   – tip rotation [rad]
        M_root      – root moment [N·m]
    """
    