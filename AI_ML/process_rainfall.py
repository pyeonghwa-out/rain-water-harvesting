import xarray as xr
import geopandas as gpd
import os
import glob
import rioxarray

print("Starting enhanced rainfall data processing for Karnataka...")

RAW_DATA_DIR = "data/raw/rainfall/"
PROCESSED_DATA_DIR = "data/processed/"
BOUNDARIES_DIR = "data/raw/boundaries/"
OUTPUT_FILENAME = "karnataka_mean_annual_rainfall.nc"
STATE_SHAPEFILE = os.path.join(BOUNDARIES_DIR, "IND_adm1.shp")
STATE_NAME = "Karnataka"

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

try:
    files = sorted(glob.glob(os.path.join(RAW_DATA_DIR, "*.nc")))
    print(f"Found {len(files)} NetCDF files to process.")

    datasets = []
    for f in files:
        ds = xr.open_dataset(f, engine='netcdf4')
        ds = ds.rename({'TIME': 'time', 'RAINFALL': 'rf', 'LONGITUDE': 'lon', 'LATITUDE': 'lat'})
        datasets.append(ds)

    ds = xr.concat(datasets, dim='time')
    print("Successfully loaded all NetCDF files into a single dataset.")

    yearly_rainfall = ds['rf'].resample(time='Y').sum(dim='time') 
    mean_annual_rainfall = yearly_rainfall.mean(dim='time')
    print("Calculated long-term mean annual rainfall for India.")

    india_states = gpd.read_file(STATE_SHAPEFILE)
    karnataka = india_states[india_states['NAME_1'] == STATE_NAME]

    if karnataka.empty:
        raise ValueError(f"State '{STATE_NAME}' not found in shapefile.")

    print(f"Clipping rainfall data to the boundaries of {STATE_NAME}...")
    mean_annual_rainfall.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    mean_annual_rainfall.rio.write_crs("epsg:4326", inplace=True)

    karnataka_rainfall = mean_annual_rainfall.rio.clip(
        karnataka.geometry, karnataka.crs, drop=True, all_touched=True
    )
    print("Successfully clipped data to Karnataka.")
    output_path = os.path.join(PROCESSED_DATA_DIR, OUTPUT_FILENAME)
    karnataka_rainfall.to_netcdf(output_path)

    print(f"SUCCESS! Processed data saved to: {output_path}")

except Exception as e:
    print(f" An error occurred: {e}")
