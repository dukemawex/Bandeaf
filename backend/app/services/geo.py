from __future__ import annotations

from math import atan2, cos, radians, sin, sqrt


def geojson_point(lat: float, lon: float) -> dict[str, object]:
    return {"type": "Point", "coordinates": [lon, lat]}


def geojson_linestring(points: list[dict[str, float]]) -> dict[str, object]:
    return {"type": "LineString", "coordinates": [[point["lon"], point["lat"]] for point in points]}


def geojson_polygon(coordinates: list[list[list[float]]]) -> dict[str, object]:
    return {"type": "Polygon", "coordinates": coordinates}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    a = sin(delta_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(delta_lon / 2) ** 2
    return 2 * radius_km * atan2(sqrt(a), sqrt(1 - a))
