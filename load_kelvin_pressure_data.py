"""
使用气压坐标的Kelvin波数据进行合成分析

这个脚本提供了更新后的数据加载函数，用于读取转换为气压坐标的Kelvin波风场数据。
可以直接复制到 Cal_composite_kelvin.ipynb 中使用。
"""

import xarray as xr
import numpy as np
import os

# ============================================================================
# 数据路径配置
# ============================================================================

# 气压坐标数据目录
KELVIN_PRESSURE_DIR = "/work/mh1498/m301257/cache/kelvin_wave_3d_pressure"

# 原始sigma坐标数据目录（备用）
KELVIN_SIGMA_DIR = "/work/mh1498/m301257/cache/kelvin_wave_3d"

# ============================================================================
# 数据加载函数（气压坐标版本）
# ============================================================================

def load_kelvin_wind_pressure(experiments=['CNTL', 'P4K', '4CO2'], 
                              variables=['ua', 'va'],
                              data_dir=None,
                              verbose=True):
    """
    加载气压坐标的Kelvin波风场数据
    
    Parameters:
    -----------
    experiments : list
        实验列表，如 ['CNTL', 'P4K', '4CO2']
    variables : list
        变量列表，如 ['ua', 'va', 'omega']
    data_dir : str, optional
        数据目录路径。如果为None，使用默认路径
    verbose : bool
        是否打印详细信息
    
    Returns:
    --------
    data_dict : dict
        嵌套字典 {variable: {experiment: xr.DataArray}}
        例如: data_dict['ua']['CNTL'] 返回 CNTL实验的ua数据
    
    Example:
    --------
    >>> wind_data = load_kelvin_wind_pressure()
    >>> ua_cntl = wind_data['ua']['CNTL']
    >>> print(ua_cntl.dims)  # ('time', 'plev', 'lat', 'lon')
    >>> print(ua_cntl.plev.values / 100)  # 气压层（hPa）- 27层从1000到100 hPa
    """
    if data_dir is None:
        data_dir = KELVIN_PRESSURE_DIR
    
    if verbose:
        print("="*80)
        print("Loading Kelvin Wave Wind Data (Pressure Coordinates)")
        print("="*80)
        print(f"Data directory: {data_dir}")
        print(f"Experiments: {experiments}")
        print(f"Variables: {variables}")
        print("="*80)
    
    # 初始化结果字典
    data_dict = {var: {} for var in variables}
    
    # 加载每个变量和实验的数据
    for var in variables:
        if verbose:
            print(f"\n📊 Loading {var.upper()}...")
        
        for exp in experiments:
            # 构建文件路径
            filename = f"kelvin_{var}_{exp.lower()}_pressure.nc"
            filepath = os.path.join(data_dir, filename)
            
            if not os.path.exists(filepath):
                print(f"  ⚠️  {exp}: File not found - {filename}")
                continue
            
            try:
                # 加载数据
                ds = xr.open_dataset(filepath)
                
                # 获取数据变量（可能名称不同）
                if var in ds:
                    data = ds[var]
                elif '__xarray_dataarray_variable__' in ds:
                    data = ds['__xarray_dataarray_variable__']
                else:
                    # 获取第一个数据变量
                    data_vars = [v for v in ds.data_vars]
                    data = ds[data_vars[0]]
                
                # 确保有plev维度
                if 'plev' not in data.dims and 'level' in data.dims:
                    data = data.rename({'level': 'plev'})
                
                data_dict[var][exp] = data
                
                if verbose:
                    print(f"  ✅ {exp}: {data.shape} | "
                          f"Pressure: {data.plev.min().values/100:.0f}-{data.plev.max().values/100:.0f} hPa | "
                          f"{os.path.getsize(filepath)/1e9:.2f} GB")
                
            except Exception as e:
                print(f"  ❌ {exp}: Failed to load - {e}")
    
    if verbose:
        print("\n" + "="*80)
        print("✅ Data loading complete!")
        print("="*80)
        
        # 打印使用示例
        if len(data_dict.get('ua', {})) > 0:
            example_exp = list(data_dict['ua'].keys())[0]
            print(f"\nUsage example:")
            print(f"  ua_data = wind_data['ua']['{example_exp}']")
            print(f"  # Select 850 hPa level:")
            print(f"  ua_850 = ua_data.sel(plev=85000)")
            print(f"  # Select lower troposphere (1000-700 hPa):")
            print(f"  ua_lower = ua_data.sel(plev=slice(100000, 70000))")
    
    return data_dict


def select_pressure_levels(data, levels_hpa):
    """
    选择特定的气压层
    
    Parameters:
    -----------
    data : xr.DataArray
        包含plev维度的数据
    levels_hpa : list or float
        气压层（单位：hPa）
        例如: [850, 500, 200] 或 850
    
    Returns:
    --------
    selected : xr.DataArray
        选择的气压层数据
    
    Example:
    --------
    >>> ua_850 = select_pressure_levels(ua_data, 850)
    >>> ua_mid = select_pressure_levels(ua_data, [850, 500, 200])
    """
    if isinstance(levels_hpa, (int, float)):
        levels_hpa = [levels_hpa]
    
    # 转换hPa到Pa
    levels_pa = [lev * 100 for lev in levels_hpa]
    
    # 选择最接近的层次
    selected = data.sel(plev=levels_pa, method='nearest')
    
    return selected


def compute_vertical_mean(data, plev_range_hpa=(1000, 200)):
    """
    计算垂直平均
    
    Parameters:
    -----------
    data : xr.DataArray
        包含plev维度的数据
    plev_range_hpa : tuple
        气压范围（单位：hPa），例如 (1000, 200) 表示1000-200hPa
    
    Returns:
    --------
    mean : xr.DataArray
        垂直平均后的数据（不含plev维度）
    """
    plev_min = min(plev_range_hpa) * 100  # 转换到Pa
    plev_max = max(plev_range_hpa) * 100
    
    # 选择范围并计算平均
    data_range = data.sel(plev=slice(plev_max, plev_min))  # slice是递减的
    mean = data_range.mean(dim='plev')
    
    return mean


# ============================================================================
# 合成分析函数（更新版）
# ============================================================================

def compute_wind_composite_pressure(ua_data, va_data, event_dates, lags, 
                                   plev_levels_hpa=None):
    """
    基于气压坐标数据计算风场合成
    
    Parameters:
    -----------
    ua_data, va_data : xr.DataArray
        风场数据，维度为 (time, plev, lat, lon)
    event_dates : list
        事件时间索引列表
    lags : range or list
        lag天数
    plev_levels_hpa : list, optional
        选择特定气压层（hPa）。如果为None，使用所有层次
    
    Returns:
    --------
    ua_composite : xr.DataArray
        ua合成结果
    va_composite : xr.DataArray
        va合成结果
    """
    # 如果指定了气压层，先选择
    if plev_levels_hpa is not None:
        ua_data = select_pressure_levels(ua_data, plev_levels_hpa)
        va_data = select_pressure_levels(va_data, plev_levels_hpa)
    
    # 使用原有的合成函数
    from your_composite_module import compute_composite_optimized
    
    ua_composite, _, _ = compute_composite_optimized(ua_data, event_dates, lags)
    va_composite, _, _ = compute_composite_optimized(va_data, event_dates, lags)
    
    return ua_composite, va_composite


# ============================================================================
# 快速上手代码
# ============================================================================

def quick_start_example():
    """
    快速上手示例代码
    """
    print("""
# ============================================================================
# 快速上手：使用气压坐标数据
# ============================================================================

# 1. 加载数据
wind_data = load_kelvin_wind_pressure(
    experiments=['CNTL', 'P4K', '4CO2'],
    variables=['ua', 'va']
)

# 2. 访问特定实验的数据
ua_cntl = wind_data['ua']['CNTL']
va_cntl = wind_data['va']['CNTL']

print(f"Data shape: {ua_cntl.shape}")
print(f"Dimensions: {ua_cntl.dims}")
print(f"Pressure levels (hPa): {ua_cntl.plev.values / 100}")

# 3. 选择特定气压层
ua_850 = ua_cntl.sel(plev=85000)  # 850 hPa
ua_500 = ua_cntl.sel(plev=50000)  # 500 hPa
ua_200 = ua_cntl.sel(plev=20000)  # 200 hPa

# 或选择多个层次
ua_trop = ua_cntl.sel(plev=[85000, 70000, 50000, 30000, 20000])

# 4. 计算垂直平均（例如：1000-200 hPa）
ua_vmean = compute_vertical_mean(ua_cntl, plev_range_hpa=(1000, 200))

# 5. 进行合成分析（使用之前检测到的事件）
# 假设已经有了 all_events 字典
ua_composite, va_composite = compute_wind_composite_pressure(
    ua_cntl, va_cntl,
    event_dates=all_events['CNTL']['event_dates'],
    lags=range(-4, 5),
    plev_levels_hpa=[850, 500, 200]  # 只分析这几个层次
)

# 6. 绘制特定层次的风场合成
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

fig, axes = plt.subplots(1, 3, figsize=(15, 4),
                         subplot_kw={'projection': ccrs.PlateCarree()})

for i, lag in enumerate([-1, 0, 1]):
    ax = axes[i]
    
    # 选择850hPa，lag天
    ua_plot = ua_composite.sel(plev=85000, lag=lag)
    va_plot = va_composite.sel(plev=85000, lag=lag)
    
    # 绘制风场
    speed = np.sqrt(ua_plot**2 + va_plot**2)
    speed.plot(ax=ax, transform=ccrs.PlateCarree())
    
    # 叠加风矢量
    skip = 3
    ax.quiver(ua_plot.lon[::skip], ua_plot.lat[::skip],
              ua_plot[::skip, ::skip], va_plot[::skip, ::skip],
              transform=ccrs.PlateCarree())
    
    ax.coastlines()
    ax.set_title(f'Day {lag:+d}')

plt.tight_layout()
plt.savefig('wind_composite_850hPa.png', dpi=150, bbox_inches='tight')
plt.show()

# ============================================================================
""")


# ============================================================================
# 数据验证函数
# ============================================================================

def validate_converted_data():
    """
    验证转换后的数据是否正确
    """
    print("="*80)
    print("Validating Converted Pressure Coordinate Data")
    print("="*80)
    
    for exp in ['cntl', 'p4k', '4co2']:
        print(f"\nExperiment: {exp.upper()}")
        print("-"*80)
        
        for var in ['ua', 'va']:
            sigma_file = f"{KELVIN_SIGMA_DIR}/kelvin_{var}_{exp}.nc"
            pressure_file = f"{KELVIN_PRESSURE_DIR}/kelvin_{var}_{exp}_pressure.nc"
            
            if not os.path.exists(pressure_file):
                print(f"  ⚠️  {var}: Pressure file not found")
                continue
            
            # 读取数据
            ds_pressure = xr.open_dataset(pressure_file)
            
            # 获取数据变量
            if var in ds_pressure:
                data = ds_pressure[var]
            else:
                data = ds_pressure['__xarray_dataarray_variable__']
            
            print(f"  ✅ {var}:")
            print(f"     Shape: {data.shape}")
            print(f"     Dimensions: {list(data.dims)}")
            
            if 'plev' in data.dims:
                print(f"     Pressure levels: {len(data.plev)} levels")
                print(f"     Range: {data.plev.min().values/100:.0f} - {data.plev.max().values/100:.0f} hPa")
            
            print(f"     Value range: {float(data.min()):.2f} to {float(data.max()):.2f}")
            print(f"     File size: {os.path.getsize(pressure_file)/1e9:.2f} GB")
    
    print("\n" + "="*80)
    print("Validation complete!")
    print("="*80)


if __name__ == "__main__":
    # 如果直接运行此脚本，显示快速上手指南
    quick_start_example()
    
    # 取消注释以验证数据
    # validate_converted_data()
