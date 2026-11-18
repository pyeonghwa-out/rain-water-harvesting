"""Rooftop area estimation from OSM footprints with a raster-tile fallback."""

from functools import lru_cache
import math

import cv2
import numpy as np
import requests
import shapely.geometry as geom
from pyproj import Geod


GEOD = Geod(ellps="WGS84")
USER_AGENT = "Zenkai-Rainwater-Planner/1.0"
OVERPASS_ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
)


def deg2num(latDeg, lonDeg, zoom):
    latRad = np.radians(latDeg)
    n = 2.0 ** zoom
    xTile = int((lonDeg + 180.0) / 360.0 * n)
    yTile = int((1.0 - np.arcsinh(np.tan(latRad)) / np.pi) / 2.0 * n)
    return xTile, yTile


def num2deg(xTile, yTile, zoom):
    n = 2.0 ** zoom
    lonDeg = xTile / n * 360.0 - 180.0
    latRad = np.arctan(np.sinh(np.pi * (1 - 2 * yTile / n)))
    return np.degrees(latRad), lonDeg


def _validate_coordinates(lat, lon, zoom):
    if not math.isfinite(float(lat)) or not math.isfinite(float(lon)):
        raise ValueError("Latitude and longitude must be finite numbers")
    if not -85.0511 <= float(lat) <= 85.0511 or not -180 <= float(lon) <= 180:
        raise ValueError("Coordinates are outside Web Mercator bounds")
    if not 14 <= int(zoom) <= 21:
        raise ValueError("Zoom must be between 14 and 21")


@lru_cache(maxsize=128)
def _fetch_satellite_tile(x, y, zoom):
    url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y}/{x}"
    response = requests.get(url, timeout=(4, 12), headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    encoded = np.frombuffer(response.content, dtype=np.uint8)
    image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError("Satellite imagery service returned an unreadable tile")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def fetchImage(lat, lon, zoom):
    _validate_coordinates(lat, lon, zoom)
    x, y = deg2num(lat, lon, zoom)
    return _fetch_satellite_tile(x, y, int(zoom)).copy(), x, y


@lru_cache(maxsize=256)
def fetchBuildings(lat, lon):
    query = f"[out:json][timeout:5];way(around:65,{lat},{lon})[building];out geom;"
    for url in OVERPASS_ENDPOINTS:
        try:
            response = requests.post(
                url,
                data={"data": query},
                timeout=(2, 4),
                headers={"User-Agent": USER_AGENT},
            )
            response.raise_for_status()
            data = response.json()
            polygons = []
            for element in data.get("elements", []):
                geometry = element.get("geometry")
                if not geometry or len(geometry) < 4:
                    continue
                polygon = geom.Polygon([(point["lon"], point["lat"]) for point in geometry])
                if polygon.is_valid and polygon.area > 0:
                    polygons.append(polygon)
            return polygons
        except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
            continue
    # An empty list intentionally selects the cached raster-tile fallback.
    return []


def _distance_m(lat, lon, point):
    _, _, distance = GEOD.inv(lon, lat, point.x, point.y)
    return abs(distance)


def findNearestBuilding(buildings, lat, lon, max_distance_m=20):
    user_point = geom.Point(lon, lat)
    containing = [polygon for polygon in buildings if polygon.covers(user_point)]
    if containing:
        return min(containing, key=lambda polygon: polygon.area)
    nearest = min(buildings, key=lambda polygon: _distance_m(lat, lon, polygon.centroid), default=None)
    if nearest is None or _distance_m(lat, lon, nearest.centroid) > max_distance_m:
        return None
    return nearest


def _draw_projected_footprints(image, buildings, selected, tile_x, tile_y, zoom):
    lat_bottom, lon_left = num2deg(tile_x, tile_y + 1, zoom)
    lat_top, lon_right = num2deg(tile_x + 1, tile_y, zoom)
    height, width = image.shape[:2]
    result = image.copy()
    area_m2 = 0.0
    for polygon in buildings:
        points = []
        for lon_point, lat_point in polygon.exterior.coords:
            px = round((lon_point - lon_left) / (lon_right - lon_left) * width)
            py = round((lat_top - lat_point) / (lat_top - lat_bottom) * height)
            points.append([px, py])
        contour = np.asarray([points], dtype=np.int32)
        if polygon is selected:
            overlay = result.copy()
            cv2.fillPoly(overlay, contour, (45, 150, 235))
            result = cv2.addWeighted(overlay, 0.32, result, 0.68, 0)
            cv2.polylines(result, contour, True, (60, 190, 255), 2)
            area_m2 = abs(GEOD.geometry_area_perimeter(polygon)[0])
        else:
            cv2.polylines(result, contour, True, (111, 225, 174), 1)
    return result, area_m2


@lru_cache(maxsize=256)
def _fetch_osm_rendered_tile(x, y, zoom):
    url = f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
    response = requests.get(url, timeout=(4, 10), headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    image = cv2.imdecode(np.frombuffer(response.content, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError("OpenStreetMap returned an unreadable map tile")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def _detect_from_rendered_tile(lat, lon, zoom):
    tile_x, tile_y = deg2num(lat, lon, zoom)
    image = _fetch_osm_rendered_tile(tile_x, tile_y, int(zoom)).copy()

    # The standard OSM style draws mapped buildings in a warm grey fill.
    lower = np.array([205, 195, 185], dtype=np.uint8)
    upper = np.array([229, 221, 214], dtype=np.uint8)
    mask = cv2.inRange(image, lower, upper)
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, 8)

    world_pixels = (2 ** int(zoom)) * image.shape[1]
    global_x = (float(lon) + 180.0) / 360.0 * world_pixels
    lat_radians = math.radians(float(lat))
    global_y = (1.0 - math.asinh(math.tan(lat_radians)) / math.pi) / 2.0 * world_pixels
    point_x = int(global_x) - tile_x * image.shape[1]
    point_y = int(global_y) - tile_y * image.shape[0]
    point_x = min(max(point_x, 0), image.shape[1] - 1)
    point_y = min(max(point_y, 0), image.shape[0] - 1)

    label = int(labels[point_y, point_x])
    if label == 0:
        # Geocoded pins can land a few pixels beside the mapped roof edge.
        nearby = []
        for candidate in range(1, count):
            pixels = int(stats[candidate, cv2.CC_STAT_AREA])
            if 100 <= pixels <= 20000:
                cx, cy = centroids[candidate]
                distance = math.hypot(cx - point_x, cy - point_y)
                if distance <= 6:
                    nearby.append((distance, candidate))
        if nearby:
            label = min(nearby)[1]

    if label == 0:
        return image, image.copy(), 0.0

    pixel_count = int(stats[label, cv2.CC_STAT_AREA])
    if not 100 <= pixel_count <= 20000:
        return image, image.copy(), 0.0

    component = np.uint8(labels == label) * 255
    contours, _ = cv2.findContours(component, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image, image.copy(), 0.0

    contour = max(contours, key=cv2.contourArea)
    overlay = image.copy()
    cv2.drawContours(overlay, [contour], -1, (47, 150, 235), thickness=cv2.FILLED)
    result = cv2.addWeighted(overlay, 0.3, image, 0.7, 0)
    cv2.drawContours(result, [contour], -1, (45, 190, 255), thickness=2)

    meters_per_pixel = (math.cos(lat_radians) * 2 * math.pi * 6378137.0) / world_pixels
    area_m2 = pixel_count * meters_per_pixel ** 2
    return image, result, area_m2


def detectRooftopsDetailed(lat, lon, zoom=19):
    _validate_coordinates(lat, lon, zoom)
    buildings = fetchBuildings(lat, lon)
    selected = findNearestBuilding(buildings, lat, lon)
    if selected is not None:
        tile_x, tile_y = deg2num(lat, lon, zoom)
        try:
            image, _, _ = fetchImage(lat, lon, zoom)
            marked, area = _draw_projected_footprints(image, buildings, selected, tile_x, tile_y, zoom)
            if area > 0:
                return image, marked, area, "Esri satellite imagery with an OpenStreetMap building footprint"
        except requests.RequestException:
            pass
        except RuntimeError:
            pass

        # Keep the detected footprint usable when the satellite layer is down.
        map_image = _fetch_osm_rendered_tile(tile_x, tile_y, int(zoom)).copy()
        marked, area = _draw_projected_footprints(map_image, buildings, selected, tile_x, tile_y, zoom)
        if area > 0:
            return map_image, marked, area, "OpenStreetMap map tile with a building footprint"

    # Overpass public services can be unavailable. A rendered OSM tile provides
    # a local footprint mask that OpenCV can still measure and highlight.
    try:
        map_image, map_marked, map_area = _detect_from_rendered_tile(lat, lon, zoom)
    except requests.RequestException as exc:
        raise RuntimeError("Building-footprint services and the OpenStreetMap tile service are unavailable") from exc
    if map_area > 0:
        return map_image, map_marked, map_area, "OpenStreetMap map tile (OpenCV footprint mask)"
    return map_image, map_image.copy(), 0.0, "No mapped footprint at this coordinate"


def detectRooftops(lat, lon, zoom=19):
    image, marked, area, _ = detectRooftopsDetailed(lat, lon, zoom)
    return image, marked, area


def getRooftopDetailed(lat, lon, zoom=19):
    _, marked, area, source = detectRooftopsDetailed(lat, lon, zoom)
    return area, marked, source


def getRooftop(lat, lon, zoom=19):
    area, marked, _ = getRooftopDetailed(lat, lon, zoom)
    return area, marked
