from plugins.sales.models import Dim


def chargeable_kg(
    actual_kg: float,
    dims: list[Dim],
    *,
    divisor: int = 6000,
) -> tuple[float, float | None]:
    if not dims:
        return actual_kg, None

    vol = sum(
        (d.length_cm * d.width_cm * d.height_cm * d.pieces) / divisor for d in dims
    )
    return max(actual_kg, vol), vol or None
