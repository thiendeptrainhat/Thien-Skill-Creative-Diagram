"""D-105 connector-port and route policy shared by P-19 renderers."""
from __future__ import annotations


CONNECTOR_POLICY_ID = "D-105-centered-even-straight-first"
ROUTE_PRIORITY = "straight-first"


def evenly_distributed_ports(edge_start: float, edge_end: float, count: int) -> tuple[float, ...]:
    """Return centered/even ports with equal edge margins and equal intervals."""
    if count < 1:
        raise ValueError("Connector port count must be positive")
    if edge_end <= edge_start:
        raise ValueError("Connector edge must have positive length")
    step = (edge_end - edge_start) / (count + 1)
    return tuple(edge_start + step * index for index in range(1, count + 1))


def centered_port(edge_start: float, edge_end: float) -> float:
    return evenly_distributed_ports(edge_start, edge_end, 1)[0]


def straight_path(source: tuple[float, float], target: tuple[float, float]) -> str:
    """Prefer one straight horizontal/vertical segment, otherwise one line segment."""
    sx, sy = source
    tx, ty = target
    if sy == ty:
        return f"M{sx:g} {sy:g} H{tx:g}"
    if sx == tx:
        return f"M{sx:g} {sy:g} V{ty:g}"
    return f"M{sx:g} {sy:g} L{tx:g} {ty:g}"


def validate_even_ports(edge_start: float, edge_end: float, ports: tuple[float, ...], *, tolerance: float = 1e-9) -> None:
    expected = evenly_distributed_ports(edge_start, edge_end, len(ports))
    if any(abs(actual - target) > tolerance for actual, target in zip(ports, expected)):
        raise ValueError("Connector ports are not evenly distributed on the node edge")

