"""
处理 cell_sea_land_mask 静态变量
将 HEALPix 网格转换为经纬度网格并插值到目标分辨率

特点:
- 无时间维度
- 无高度维度  
- 纯2D静态场
"""

import os
import xarray as xr
import numpy as np
from dask.diagnostics import ProgressBar
import gc


def process_sea_land_mask(experiment_name, dataset_key, save_dir, grid_dict, 
                          target_lat, target_lon, catalog):
    """
    处理 cell_sea_land_mask 静态变量（无时间、无高度维度）
    
    Parameters:
    -----------
    experiment_name : str
        实验名称 (CNTL, P4K, 4CO2)
    dataset_key : str
        在catalog中的数据集键名
    save_dir : str
        保存目录
    grid_dict : dict
        网格转换参数 {'nside': 256, 'nest': True, 'minmax_lat': 36}
    target_lat : array
        目标纬度数组 (例如: np.arange(-36, 36.1, 2.0))
    target_lon : array
        目标经度数组 (例如: np.arange(0, 360, 2.0))
    catalog : intake.Catalog
        数据目录对象
    
    Returns:
    --------
    str : 保存的文件路径
    """
    import time
    from pathlib import Path
    import sys
    
    # 导入网格转换函数
    WAVE_TOOLS_PATH = Path("/work/mh1498/m301257/wave_tools")
    sys.path.insert(0, str(WAVE_TOOLS_PATH.parent))
    from wave_tools.utils import dataarray_to_equatorial_latlon_grid
    
    var_name = 'cell_sea_land_mask'
    
    print("="*70)
    print(f"🌊 处理海陆Mask变量: {var_name.upper()} - {experiment_name}")
    print("="*70)
    
    # 创建保存目录
    exp_save_dir = os.path.join(save_dir, f"mask_{experiment_name.lower()}")
    os.makedirs(exp_save_dir, exist_ok=True)
    print(f"📁 保存路径: {exp_save_dir}")
    
    # 构建保存文件路径
    save_path = os.path.join(exp_save_dir, f"{var_name}_2deg.nc")
    
    # 检查文件是否已存在
    if os.path.exists(save_path):
        print(f"✅ 文件已存在，跳过处理")
        print(f"   文件: {save_path}")
        return save_path
    
    # 加载数据
    print(f"📖 读取海陆Mask数据...")
    
    try:
        start_time = time.time()
        
        # cell_sea_land_mask 是静态场，无时间维度
        mask_data = catalog.ICON.C5[dataset_key].to_dask()[var_name]
        
        # 检查维度
        print(f"✅ 数据信息:")
        print(f"   变量: {var_name}")
        print(f"   维度: {list(mask_data.dims)}")
        print(f"   形状: {mask_data.shape}")
        print(f"   数据类型: {mask_data.dtype}")
        
        # 检查是否有意外的维度
        if 'time' in mask_data.dims:
            print(f"⚠️  检测到时间维度，将选择第一个时间点")
            mask_data = mask_data.isel(time=0)
        
        if 'level' in mask_data.dims or 'level_full' in mask_data.dims or 'level_half' in mask_data.dims:
            print(f"⚠️  检测到高度维度，将选择第一层")
            for dim in ['level', 'level_full', 'level_half']:
                if dim in mask_data.dims:
                    mask_data = mask_data.isel({dim: 0})
                    break
        
        print(f"   处理后维度: {list(mask_data.dims)}")
        print(f"   处理后形状: {mask_data.shape}")
        print("="*70)
        
        # 步骤1: 转换到经纬度网格
        print(f"🔄 步骤1/3: 转换HEALPix网格到经纬度网格...")
        
        # 临时添加时间维度（转换函数需要）
        mask_data_with_time = mask_data.expand_dims({"time": [0]})
        print(f"   临时添加时间维度: {list(mask_data_with_time.dims)}")
        
        mask_lonlat_with_time = dataarray_to_equatorial_latlon_grid(
            mask_data_with_time, 
            grid_type='healpix', 
            grid_dict=grid_dict
        )
        
        # 移除临时时间维度
        mask_lonlat = mask_lonlat_with_time.isel(time=0)
        
        print(f"   ✅ 网格转换完成")
        print(f"      转换后形状: {mask_lonlat.shape}")
        print(f"      转换后维度: {list(mask_lonlat.dims)}")
        
        # 步骤2: 插值到目标分辨率 (2°x2°)
        print(f"🔄 步骤2/3: 插值到 {len(target_lat)}°x{len(target_lon)}° 网格...")
        mask_2deg = mask_lonlat.interp(
            lat=target_lat, 
            lon=target_lon, 
            method='nearest'  # 对于mask使用nearest而非linear
        )
        print(f"   ✅ 插值完成")
        print(f"      插值后形状: {mask_2deg.shape}")
        print(f"      纬度范围: [{target_lat[0]:.1f}, {target_lat[-1]:.1f}]")
        print(f"      经度范围: [{target_lon[0]:.1f}, {target_lon[-1]:.1f}]")
        
        # 步骤3: 计算并保存
        print(f"🔄 步骤3/3: 计算并保存到NetCDF...")
        
        # 触发计算
        with ProgressBar():
            mask_computed = mask_2deg.compute()
        
        # 添加属性信息
        mask_computed.attrs['long_name'] = 'Sea-Land Mask'
        mask_computed.attrs['description'] = 'Static sea-land mask: 0=land, 1=sea'
        mask_computed.attrs['source'] = f'ICON {experiment_name} experiment'
        mask_computed.attrs['grid_resolution'] = '2 degrees'
        mask_computed.attrs['original_grid'] = 'HEALPix'
        mask_computed.attrs['interpolation_method'] = 'nearest neighbor'
        
        # 转换为Dataset并保存
        ds_to_save = mask_computed.to_dataset(name=var_name)
        ds_to_save.to_netcdf(save_path)
        
        elapsed_time = time.time() - start_time
        
        print(f"   ✅ 保存完成!")
        print(f"      文件路径: {save_path}")
        print(f"      文件大小: {os.path.getsize(save_path) / 1024**2:.2f} MB")
        print(f"      总耗时: {elapsed_time:.1f} 秒")
        
        # 打印数据统计
        print(f"\n📊 数据统计:")
        print(f"   最小值: {float(mask_computed.min())}")
        print(f"   最大值: {float(mask_computed.max())}")
        print(f"   唯一值: {np.unique(mask_computed.values)}")
        
        # 计算海洋和陆地比例
        if mask_computed.dtype in [np.float32, np.float64]:
            sea_fraction = float((mask_computed > 0.5).sum() / mask_computed.size)
            land_fraction = 1 - sea_fraction
            print(f"   海洋占比: {sea_fraction*100:.1f}%")
            print(f"   陆地占比: {land_fraction*100:.1f}%")
        
        print("="*70)
        
        # 清理内存
        del mask_data, mask_lonlat, mask_2deg, mask_computed, ds_to_save
        gc.collect()
        
        return save_path
        
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")
        import traceback
        traceback.print_exc()
        gc.collect()
        raise


def batch_process_sea_land_mask(experiments, save_dir, grid_dict, target_lat, 
                                 target_lon, catalog):
    """
    批量处理多个实验的海陆mask
    
    Parameters:
    -----------
    experiments : dict
        实验配置字典，格式: {"exp_key": ("EXP_NAME", "DATASET_KEY")}
        例如: {"cntl": ("CNTL", "AMIP_CNTL"), "4k": ("P4K", "AMIP_P4K")}
    save_dir : str
        保存根目录
    grid_dict : dict
        网格转换参数
    target_lat : array
        目标纬度
    target_lon : array
        目标经度
    catalog : intake.Catalog
        数据目录对象
    
    Returns:
    --------
    dict : {实验名: 保存路径} 的字典
    """
    results = {}
    failed = []
    
    print("\n" + "🌍"*35)
    print("📊 批量处理海陆Mask变量")
    print("🌍"*35 + "\n")
    
    for exp_key, (exp_name, dataset_key) in experiments.items():
        try:
            save_path = process_sea_land_mask(
                experiment_name=exp_name,
                dataset_key=dataset_key,
                save_dir=save_dir,
                grid_dict=grid_dict,
                target_lat=target_lat,
                target_lon=target_lon,
                catalog=catalog
            )
            results[exp_name] = save_path
            print(f"✅ {exp_name} 处理成功\n")
            
        except Exception as e:
            error_msg = f"{exp_name}: {str(e)}"
            print(f"❌ {error_msg}\n")
            failed.append(error_msg)
            gc.collect()
            continue
    
    # 打印总结
    print("\n" + "="*70)
    print("📊 处理总结")
    print("="*70)
    print(f"✅ 成功: {len(results)} 个实验")
    for exp_name, path in results.items():
        print(f"   - {exp_name}: {path}")
    
    if failed:
        print(f"\n❌ 失败: {len(failed)} 个实验")
        for error in failed:
            print(f"   - {error}")
    
    return results


# ============================================================================
# 使用示例
# ============================================================================

if __name__ == "__main__":
    import intake
    
    # 加载catalog
    cat = intake.open_catalog("https://data.nextgems-h2020.eu/catalog.yaml")
    
    # 设置参数
    DATA_DIR = "/work/mh1498/m301257/processed_data_lat_30"
    LAYER_DIR = os.path.join(DATA_DIR, "2d_layers")
    os.makedirs(LAYER_DIR, exist_ok=True)
    
    # 网格参数
    grid_dict = {"nside": 256, "nest": True, "minmax_lat": 36}
    target_lat = np.arange(-36, 36.1, 2.0)
    target_lon = np.arange(0, 360, 2.0)
    
    # 定义实验
    experiments = {
        "cntl":  ("CNTL",   "AMIP_CNTL"),
        "4k":    ("P4K",    "AMIP_P4K"),
        "4co2":  ("4CO2",   "AMIP_4CO2"),
    }
    
    # 批量处理
    results = batch_process_sea_land_mask(
        experiments=experiments,
        save_dir=LAYER_DIR,
        grid_dict=grid_dict,
        target_lat=target_lat,
        target_lon=target_lon,
        catalog=cat
    )
    
    print("\n🎉 所有处理完成!")
