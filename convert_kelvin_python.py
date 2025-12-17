#!/usr/bin/env python3
"""
使用xarray将Kelvin波3D数据从层编号插值到标准气压层

由于数据缺少CDO ml2pl所需的混合坐标系数，我们使用Python直接进行插值。
假设层编号与气压层有对应关系，或者需要从其他数据源获取气压信息。
"""

import xarray as xr
import numpy as np
import os
import sys
from pathlib import Path

# 配置
KELVIN_3D_DIR = "/work/mh1498/m301257/cache/kelvin_wave_3d"
OUTPUT_DIR = "/work/mh1498/m301257/cache/kelvin_wave_3d_pressure"
EXPERIMENTS = ['cntl', 'p4k', '4co2']
VARIABLES = ['ua', 'va', 'omega']

# 27层标准气压（Pa）
TARGET_PRESSURE_LEVELS = np.array([
    100000, 97500, 95000, 92500, 90000, 87500, 85000, 82500, 80000, 77500, 75000,
    70000, 65000, 60000, 55000, 50000, 45000, 40000, 35000, 30000, 25000, 20000,
    17500, 15000, 12500, 10000
])

# 原始模式层编号
ORIGINAL_LEVELS = np.array([31, 35, 38, 41, 46, 51, 55, 58, 63, 67, 71, 74, 76, 78, 80, 81, 83, 84, 85, 87, 89, 90])

# 模式层到气压的映射（需要根据实际模式层定义调整）
# 这是一个示例映射，您需要根据实际的pfull数据调整
def get_level_to_pressure_mapping():
    """
    获取模式层编号到气压的映射关系
    
    需要根据实际的pfull_*_layers数据来确定
    """
    # 示例：假设线性映射（实际应该从pfull数据读取）
    # 第90层 ≈ 100 hPa, 第31层 ≈ 1000 hPa
    
    # 读取pfull数据获取实际压力
    try:
        pfull_file = "/work/mh1498/m301257/pfull_cntl_layers/pfull_all_levels.nc"
        if os.path.exists(pfull_file):
            ds_pfull = xr.open_dataset(pfull_file)
            if 'pfull' in ds_pfull:
                # 假设pfull维度是(time, level, lat, lon)
                # 取时间和空间平均得到每层的平均气压
                pfull = ds_pfull['pfull'].mean(dim=['time', 'lat', 'lon']).values
                levels = ds_pfull['level'].values
                
                # 创建映射字典
                level_to_pressure = dict(zip(levels, pfull))
                print(f"✅ Successfully loaded pressure mapping from pfull data")
                return level_to_pressure
    except Exception as e:
        print(f"⚠️  Could not load pfull data: {e}")
    
    # 如果无法读取pfull，使用近似映射
    print("⚠️  Using approximate pressure mapping!")
    print("   Please verify with actual pfull data!")
    
    # 近似的对数线性映射
    # 假设：90层 ≈ 10000 Pa (100 hPa), 31层 ≈ 100000 Pa (1000 hPa)
    pressures = np.logspace(np.log10(100000), np.log10(10000), len(ORIGINAL_LEVELS))[::-1]
    
    level_to_pressure = dict(zip(ORIGINAL_LEVELS, pressures))
    
    return level_to_pressure

def interpolate_to_pressure(data, level_to_pressure, target_pressures):
    """
    将数据从模式层插值到标准气压层
    
    Parameters:
    -----------
    data : xr.DataArray
        输入数据，维度为 (time, level, lat, lon)
    level_to_pressure : dict
        模式层到气压的映射
    target_pressures : array
        目标气压层（Pa）
    
    Returns:
    --------
    interpolated : xr.DataArray
        插值后的数据，维度为 (time, plev, lat, lon)
    """
    print("  Interpolating to pressure coordinates...")
    
    # 获取原始层编号
    original_levels = data.level.values
    
    # 转换为气压
    source_pressures = np.array([level_to_pressure[int(lev)] for lev in original_levels])
    
    print(f"    Source pressure range: {source_pressures.min()/100:.0f} - {source_pressures.max()/100:.0f} hPa")
    print(f"    Target pressure range: {target_pressures.min()/100:.0f} - {target_pressures.max()/100:.0f} hPa")
    
    # 创建新的压力坐标
    data_with_pressure = data.assign_coords(plev=('level', source_pressures))
    data_with_pressure = data_with_pressure.swap_dims({'level': 'plev'})
    
    # 插值到目标气压层
    # 使用线性插值
    interpolated = data_with_pressure.interp(
        plev=target_pressures,
        method='linear',
        kwargs={'fill_value': 'extrapolate'}  # 外推边界值
    )
    
    print(f"    Output shape: {interpolated.shape}")
    
    return interpolated

def process_single_file(exp, var, level_to_pressure):
    """处理单个文件"""
    input_file = f"{KELVIN_3D_DIR}/kelvin_{var}_{exp}.nc"
    output_file = f"{OUTPUT_DIR}/kelvin_{var}_{exp}_pressure.nc"
    
    print(f"\n{'='*70}")
    print(f"Processing: kelvin_{var}_{exp}")
    print(f"{'='*70}")
    
    # 检查输入文件
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False
    
    # 检查输出文件
    if os.path.exists(output_file):
        print(f"⚠️  Output file exists: {output_file}")
        response = input("   Overwrite? [y/N]: ")
        if response.lower() != 'y':
            print("   Skipping...")
            return True
    
    try:
        # 读取数据
        print(f"  Reading: {input_file}")
        ds = xr.open_dataset(input_file)
        
        # 获取数据变量
        if var in ds:
            data = ds[var]
        elif '__xarray_dataarray_variable__' in ds:
            data = ds['__xarray_dataarray_variable__']
        else:
            data_vars = [v for v in ds.data_vars]
            data = ds[data_vars[0]]
        
        print(f"    Input shape: {data.shape}")
        print(f"    Dimensions: {list(data.dims)}")
        
        # 插值到气压坐标
        interpolated = interpolate_to_pressure(data, level_to_pressure, TARGET_PRESSURE_LEVELS)
        
        # 保存属性
        interpolated.attrs.update(data.attrs)
        interpolated.attrs['interpolation_method'] = 'linear'
        interpolated.attrs['pressure_unit'] = 'Pa'
        interpolated.attrs['note'] = 'Interpolated from model levels to pressure levels'
        
        # 保存到NetCDF
        print(f"  Saving: {output_file}")
        
        # 创建数据集
        ds_out = xr.Dataset({
            var: interpolated
        })
        
        # 添加坐标属性
        ds_out['plev'].attrs['long_name'] = 'pressure level'
        ds_out['plev'].attrs['units'] = 'Pa'
        ds_out['plev'].attrs['positive'] = 'down'
        
        # 保存（使用压缩）
        encoding = {
            var: {'zlib': True, 'complevel': 5, 'dtype': 'float32'}
        }
        ds_out.to_netcdf(output_file, encoding=encoding)
        
        # 检查输出文件大小
        output_size = os.path.getsize(output_file) / 1e9
        print(f"  ✅ Saved successfully! ({output_size:.2f} GB)")
        
        # 关闭数据集
        ds.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("="*80)
    print("  Kelvin Wave 3D Data: Model Levels → Pressure Coordinates")
    print("  Using Python xarray interpolation")
    print("="*80)
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/logs", exist_ok=True)
    
    # 获取层到气压的映射
    print("\n" + "="*80)
    print("Loading pressure level mapping...")
    print("="*80)
    level_to_pressure = get_level_to_pressure_mapping()
    
    # 显示映射信息
    print("\nModel level to pressure mapping:")
    print("  Level | Pressure (hPa)")
    print("  ------|---------------")
    for level in sorted(level_to_pressure.keys()):
        pressure_hpa = level_to_pressure[level] / 100
        print(f"  {level:5d} | {pressure_hpa:10.1f}")
    
    print(f"\nTarget pressure levels ({len(TARGET_PRESSURE_LEVELS)} levels):")
    print(f"  {TARGET_PRESSURE_LEVELS / 100}")
    
    # 处理所有文件
    total = 0
    success = 0
    failed = 0
    
    for exp in EXPERIMENTS:
        for var in VARIABLES:
            total += 1
            if process_single_file(exp, var, level_to_pressure):
                success += 1
            else:
                failed += 1
    
    # 总结
    print("\n" + "="*80)
    print("  Conversion Summary")
    print("="*80)
    print(f"Total files: {total}")
    print(f"Success: {success}")
    print(f"Failed: {failed}")
    print("="*80)
    
    if failed == 0:
        print("\n✅ All conversions completed successfully!")
        print(f"\nOutput directory: {OUTPUT_DIR}")
        print("\nNext steps:")
        print("  1. Verify the data: python verify_pressure_conversion.py")
        print("  2. Use in notebook: from load_kelvin_pressure_data import load_kelvin_wind_pressure")
        return 0
    else:
        print(f"\n⚠️  {failed} file(s) failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
