# IMD Gridded Rainfall Data (0.25°)

## 📁 Data Description
- **Source**: Indian Meteorological Department (IMD), Pune
- **Portal**: [IMD Long Range Forecast Portal](https://imdpune.gov.in/lrfindex.php)
- **Product Type**: Satellite-based (GPM) rainfall estimates
- **Resolution**: 0.25° × 0.25° (~27 km × 27 km)
- **Format**: NetCDF (.nc)
- **Coverage**: Indian subregion (66.5°E-100°E, 6.5°N-38.5°N)

## 🗂️ File Naming Convention
 
 to be decided

## 📊 Dataset Structure
```python
<xarray.Dataset>
Dimensions:  (time: 365/366, lat: 129, lon: 135)
Coordinates:
  * time     (time) datetime64[ns] YYYY-01-01 ... YYYY-12-31
  * lat      (lat) float64 6.5 6.75 7.0 ... 38.25 38.5
  * lon      (lon) float64 66.5 66.75 67.0 ... 99.75 100.0
Data variables:
    rf       (time, lat, lon) float32  # Rainfall (mm)
Attributes:
    Conventions: CF-1.6
    history:     Created by CDO from binary source

```python
import xarray as xr

# Load single file
ds = xr.open_dataset('rainfall_2024.nc', engine='netcdf4')

# Load multiple years
dataset = xr.open_mfdataset('rainfall_*.nc', 
                           engine='netcdf4', 
                           combine='by_coords')

```