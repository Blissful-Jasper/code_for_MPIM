#!/usr/bin/env python3
"""Quick test to verify data access from intake catalog."""
import hdf5plugin  # Register compression filters
import intake
import xarray as xr

print("Opening catalog...")
cat = intake.open_catalog("https://data.nextgems-h2020.eu/catalog.yaml")

print("Loading AMIP_CNTL dataset...")
ds = cat.ICON.C5['AMIP_CNTL'].to_dask()

print("Selecting time slice 1980-01-01 to 1980-01-31...")
ds_subset = ds.sel(time=slice("1980-01-01", "1980-01-31"))

print("\nDataset info:")
print(ds_subset)

print("\nVariables available:")
print(list(ds_subset.data_vars))

print("\nTrying to access a small chunk of 'ua'...")
if 'ua' in ds_subset:
    ua_test = ds_subset['ua'].isel(time=0, level_half=0).values
    print(f"Successfully accessed ua data. Shape at time=0, level=0: {ua_test.shape}")
    print("✓ Data access works!")
else:
    print("✗ Variable 'ua' not found")

print("\nDone!")
