# 🏠 Rooftop Detection and Area Calculation

📌 **Overview**

This project provides a Python-based solution for automatically detecting and calculating rooftop areas from satellite imagery. The system:

- Fetches high-resolution satellite imagery from ArcGIS World Imagery service
- Retrieves building footprint data from OpenStreetMap via Overpass API
- Identifies the nearest building to a given coordinate
- Calculates accurate rooftop area using geodetic measurements
- Provides visual output with highlighted building polygons

## 🎯 **Key Features**

- **Satellite Image Integration**: Downloads real-time satellite tiles from ArcGIS services
- **Building Data Extraction**: Queries OpenStreetMap for building footprints within 200m radius
- **Nearest Building Detection**: Automatically identifies the closest building to user coordinates
- **Accurate Area Calculation**: Uses WGS84 ellipsoid for precise area measurements
- **Visual Overlay**: Highlights detected buildings with color-coded polygons
- **Flexible Zoom Levels**: Configurable zoom for different detail requirements

## 🛠️ **Dependencies**

```bash
pip install opencv-python numpy requests shapely pyproj
```

### Required Libraries:
- `cv2` (OpenCV) - Image processing and visualization
- `numpy` - Numerical operations and array handling
- `urllib.request` - Fetching satellite imagery
- `requests` - API calls to Overpass
- `shapely.geometry` - Geometric operations on building polygons
- `pyproj` - Geodetic calculations for accurate area measurement

## 📊 **Core Functions**

### `deg2num(latDeg, lonDeg, zoom)`
Converts geographic coordinates to tile coordinates for the given zoom level.

### `num2deg(xTile, yTile, zoom)`
Converts tile coordinates back to geographic coordinates.

### `fetchImage(lat, lon, zoom)`
Downloads satellite imagery tile from ArcGIS World Imagery service for the specified location.

### `fetchBuildings(lat, lon)`
Queries Overpass API to retrieve building footprints within 200m of the target coordinates.

### `findNearestBuilding(buildings, lat, lon)`
Identifies the building polygon closest to the user-specified coordinates.

### `detectRooftops(lat, lon, zoom)`
Main processing function that:
- Fetches satellite imagery
- Retrieves building data
- Projects building polygons onto the image
- Highlights the nearest building in red/blue
- Marks other buildings in green/yellow
- Calculates accurate area using geodetic methods

### `getRooftop(lat, lon, zoom=19)`
Simplified interface function that returns the rooftop area and annotated image.

## 🚀 **Usage**

### Basic Usage:
```python
# Get rooftop area and visualization
area, marked_image = getRooftop(12.9716, 77.5946)  # Bengaluru coordinates
print(f"Rooftop area: {area:.2f} square meters")

# Display the result
import matplotlib.pyplot as plt
plt.imshow(marked_image)
plt.title(f"Detected Rooftop - Area: {area:.2f} m²")
plt.show()
```

### Advanced Usage:
```python
# Custom zoom level for higher detail
area, image = getRooftop(lat=12.9716, lon=77.5946, zoom=20)

# Access intermediate results
original, marked, area = detectRooftops(12.9716, 77.5946, 19)
```

## 🎨 **Visual Output**

The system provides color-coded visualization:
- **Red outline + Blue fill**: Nearest building to the target coordinates
- **Green outline + Yellow fill**: Other buildings in the vicinity
- **Accurate area calculation**: Displayed in square meters using geodetic precision

## ⚙️ **Technical Implementation**

### Coordinate System Handling:
- Uses Web Mercator projection for tile fetching
- Converts between geographic (WGS84) and pixel coordinates
- Maintains geodetic accuracy for area calculations

### Data Sources:
- **Imagery**: ArcGIS World Imagery (high-resolution satellite)
- **Building Data**: OpenStreetMap via Overpass API
- **Projection**: WGS84 ellipsoid for precise measurements

### Error Handling:
- Validates polygon geometry from OSM data
- Handles cases with no buildings found
- Manages API request failures gracefully

## 🔍 **Applications**

This tool is particularly useful for:
- **Rainwater Harvesting Planning**: Calculate rooftop collection area
- **Solar Panel Installation**: Determine available roof space
- **Urban Planning**: Analyze building density and coverage
- **Property Assessment**: Measure roof areas for various applications
- **Environmental Studies**: Assess impervious surface coverage

## ⚠️ **Limitations & Considerations**

- **Data Accuracy**: Depends on OpenStreetMap building data quality
- **API Rate Limits**: Overpass API has usage restrictions
- **Coverage**: Limited to areas with OSM building data
- **Resolution**: Satellite imagery resolution varies by location
- **Network Dependency**: Requires internet connection for data fetching

## 🗺️ **Integration Notes**

This module can be easily integrated into larger applications:
- Returns standardized area measurements (square meters)
- Provides both numerical results and visual output
- Compatible with GIS workflows and mapping applications
- Suitable for batch processing multiple locations

## 📈 **Performance Considerations**

- Default zoom level 19 provides good balance of detail vs. processing time
- Higher zoom levels (20-21) offer more detail but larger image processing
- Building query radius of 200m balances coverage vs. API response time
- Image processing is optimized for typical residential/commercial building sizes

## 🔧 **Customization Options**

Users can modify:
- Query radius for building detection (currently 200m)
- Zoom level for different detail requirements
- Color schemes for polygon visualization
- Coordinate systems and projections as needed