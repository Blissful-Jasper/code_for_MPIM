#!/usr/bin/env python3
"""
验证气压坐标转换结果

检查转换后的数据是否正确，包括：
- 文件完整性
- 气压层数量和数值
- 数据范围合理性
- 垂直结构一致性
"""

import xarray as xr
import numpy as np
import os
import sys

# 配置
KELVIN_PRESSURE_DIR = "/work/mh1498/m301257/cache/kelvin_wave_3d_pressure"
EXPERIMENTS = ['cntl', 'p4k', '4co2']
VARIABLES = ['ua', 'va', 'omega']

# 期望的27层气压值（Pa）
EXPECTED_LEVELS_PA = [
    100000, 97500, 95000, 92500, 90000, 87500, 85000, 82500, 80000, 77500, 75000,
    70000, 65000, 60000, 55000, 50000, 45000, 40000, 35000, 30000, 25000, 20000,
    17500, 15000, 12500, 10000
]

def print_header(text):
    """打印标题"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_section(text):
    """打印章节"""
    print("\n" + "-"*80)
    print(f"  {text}")
    print("-"*80)

def check_file_exists(filepath):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        size_gb = os.path.getsize(filepath) / 1e9
        print(f"  ✅ File exists ({size_gb:.2f} GB)")
        return True
    else:
        print(f"  ❌ File not found")
        return False

def verify_pressure_levels(data):
    """验证气压层"""
    print("\n  Pressure Level Verification:")
    
    # 获取气压维度名称
    if 'plev' in data.dims:
        plev_dim = 'plev'
    elif 'level' in data.dims:
        plev_dim = 'level'
    else:
        print("  ⚠️  No pressure dimension found!")
        return False
    
    plev = data[plev_dim].values
    n_levels = len(plev)
    
    print(f"    Number of levels: {n_levels}")
    print(f"    Expected: {len(EXPECTED_LEVELS_PA)}")
    
    if n_levels == len(EXPECTED_LEVELS_PA):
        print(f"    ✅ Level count matches!")
    else:
        print(f"    ⚠️  Level count mismatch!")
    
    # 检查数值
    print(f"    Range: {plev.min()/100:.0f} - {plev.max()/100:.0f} hPa")
    
    # 显示前5层和后5层
    print(f"    First 5 levels (hPa): {plev[:5]/100}")
    print(f"    Last 5 levels (hPa): {plev[-5:]/100}")
    
    # 检查是否匹配期望值
    if np.allclose(plev, EXPECTED_LEVELS_PA, rtol=1e-5):
        print(f"    ✅ Levels match expected values!")
        return True
    else:
        print(f"    ⚠️  Levels differ from expected!")
        return False

def verify_data_statistics(data, var_name):
    """验证数据统计特性"""
    print("\n  Data Statistics:")
    
    # 基本统计
    print(f"    Shape: {data.shape}")
    print(f"    Dimensions: {dict(data.dims)}")
    
    # 数值范围
    data_min = float(data.min())
    data_max = float(data.max())
    data_mean = float(data.mean())
    data_std = float(data.std())
    
    print(f"    Min:  {data_min:.4f}")
    print(f"    Max:  {data_max:.4f}")
    print(f"    Mean: {data_mean:.4f}")
    print(f"    Std:  {data_std:.4f}")
    
    # 检查合理性
    reasonable = True
    
    # 风场合理范围检查
    if var_name in ['ua', 'va']:
        if abs(data_max) > 100 or abs(data_min) > 100:
            print(f"    ⚠️  Wind values seem too large (>100 m/s)!")
            reasonable = False
        else:
            print(f"    ✅ Wind values in reasonable range")
    
    # omega合理范围检查
    elif var_name == 'omega':
        if abs(data_max) > 10 or abs(data_min) > 10:
            print(f"    ⚠️  Omega values seem too large!")
            reasonable = False
        else:
            print(f"    ✅ Omega values in reasonable range")
    
    # NaN检查
    nan_count = np.isnan(data.values).sum()
    total_count = data.size
    nan_pct = nan_count / total_count * 100
    
    print(f"    NaN: {nan_count} / {total_count} ({nan_pct:.2f}%)")
    
    if nan_pct > 10:
        print(f"    ⚠️  High NaN percentage!")
        reasonable = False
    else:
        print(f"    ✅ NaN percentage acceptable")
    
    return reasonable

def verify_vertical_structure(data, var_name):
    """验证垂直结构"""
    print("\n  Vertical Structure Check:")
    
    # 获取气压维度
    if 'plev' in data.dims:
        plev_dim = 'plev'
    elif 'level' in data.dims:
        plev_dim = 'level'
    else:
        print("    ⚠️  No pressure dimension found!")
        return False
    
    # 选择关键层次
    key_levels = {
        '850 hPa': 85000,
        '500 hPa': 50000,
        '200 hPa': 20000
    }
    
    for level_name, level_pa in key_levels.items():
        if level_pa in data[plev_dim].values:
            data_level = data.sel({plev_dim: level_pa})
            mean_val = float(data_level.mean())
            std_val = float(data_level.std())
            print(f"    {level_name}: mean={mean_val:.4f}, std={std_val:.4f}")
        else:
            print(f"    ⚠️  {level_name} not found!")
    
    # 检查垂直变化趋势
    if var_name == 'ua':
        # 西风应该在高层更强
        if 20000 in data[plev_dim].values and 85000 in data[plev_dim].values:
            ua_200 = data.sel({plev_dim: 20000}).mean().values
            ua_850 = data.sel({plev_dim: 85000}).mean().values
            print(f"\n    Vertical trend check (ua):")
            print(f"      200 hPa mean: {float(ua_200):.4f}")
            print(f"      850 hPa mean: {float(ua_850):.4f}")
            if abs(ua_200) > abs(ua_850):
                print(f"      ✅ Upper level wind stronger (expected)")
            else:
                print(f"      ⚠️  Lower level wind stronger (unusual)")
    
    return True

def verify_single_file(exp, var):
    """验证单个文件"""
    filename = f"kelvin_{var}_{exp}_pressure.nc"
    filepath = os.path.join(KELVIN_PRESSURE_DIR, filename)
    
    print_section(f"{var.upper()} - {exp.upper()}")
    print(f"  File: {filename}")
    
    # 检查文件存在
    if not check_file_exists(filepath):
        return False
    
    try:
        # 读取数据
        ds = xr.open_dataset(filepath)
        
        # 获取数据变量
        if var in ds:
            data = ds[var]
        elif '__xarray_dataarray_variable__' in ds:
            data = ds['__xarray_dataarray_variable__']
        else:
            data_vars = [v for v in ds.data_vars]
            if len(data_vars) > 0:
                data = ds[data_vars[0]]
            else:
                print("  ❌ No data variable found!")
                return False
        
        # 执行验证
        level_ok = verify_pressure_levels(data)
        stats_ok = verify_data_statistics(data, var)
        struct_ok = verify_vertical_structure(data, var)
        
        # 关闭数据集
        ds.close()
        
        # 总结
        if level_ok and stats_ok and struct_ok:
            print("\n  ✅ All checks passed!")
            return True
        else:
            print("\n  ⚠️  Some checks failed!")
            return False
            
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False

def main():
    """主函数"""
    print_header("Kelvin Wave Pressure Data Verification")
    
    print(f"\nData directory: {KELVIN_PRESSURE_DIR}")
    print(f"Experiments: {EXPERIMENTS}")
    print(f"Variables: {VARIABLES}")
    print(f"Expected pressure levels: {len(EXPECTED_LEVELS_PA)} levels")
    
    # 统计
    total_files = 0
    passed_files = 0
    failed_files = 0
    
    # 验证每个文件
    for exp in EXPERIMENTS:
        for var in VARIABLES:
            total_files += 1
            if verify_single_file(exp, var):
                passed_files += 1
            else:
                failed_files += 1
    
    # 最终总结
    print_header("Verification Summary")
    print(f"\nTotal files checked: {total_files}")
    print(f"Passed: {passed_files}")
    print(f"Failed: {failed_files}")
    
    if failed_files == 0:
        print("\n✅ All files verified successfully!")
        print("\nYou can now use the pressure coordinate data in your analysis.")
        return 0
    else:
        print(f"\n⚠️  {failed_files} file(s) failed verification!")
        print("\nPlease check the logs above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
