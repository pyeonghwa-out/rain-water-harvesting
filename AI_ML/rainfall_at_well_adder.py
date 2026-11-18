import pandas as pd
import xarray as xr

df = pd.read_csv("data/processed/bengaluru_rural.csv") 

rainfall_ds = xr.open_dataset("data/processed/karnataka_mean_annual_rainfall.nc")

def get_rainfall(lat, lon):
    try:
        value = rainfall_ds['rf'].sel(lat=lat, lon=lon, method='nearest').item()
        return value
    except Exception as e:
        print(f"Error for lat={lat}, lon={lon}: {e}")
        return None

df['mean_annual_rainfall'] = df.apply(lambda row: get_rainfall(row['lat'], row['long']), axis=1)
df["soil_type"] = "Red Loamy Soil"
df["lithology_type"] = "Gneissic Complex"
df.to_csv("data/processed/wells_with_rainfall.csv", index=False)

print("done")