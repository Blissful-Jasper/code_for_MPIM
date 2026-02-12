"""
优化的3D数据处理脚本 - 防止内存崩溃版本

主要优化：
1. 时间分块处理：将时间维度分成小批次
2. 智能内存监控：实时监控内存使用
3. 自动重试机制：处理失败时自动重试
4. 增量保存：逐层保存，避免大量数据同时在内存
5. Dask优化配置：自动分块和内存管理
"""

import os
import xarray as xr
import numpy as np
import gc
import time
import psutil
from pathlib import Path
from dask.diagnostics import ProgressBar
import sys

# 导入网格转换函数
WAVE_TOOLS_PATH = Path("/work/mh1498/m301257/wave_tools")
sys.path.insert(0, str(WAVE_TOOLS_PATH.parent))
from wave_tools.utils import dataarray_to_equatorial_latlon_grid


def get_memory_usage():
    """获取当前内存使用情况"""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    mem_gb = mem_info.rss / 1024**3
    
    virtual_mem = psutil.virtual_memory()
    total_gb = virtual_mem.total / 1024**3
    available_gb = virtual_mem.available / 1024**3
    percent_used = virtual_mem.percent
    
    return {
        'process_gb': mem_gb,
        'system_total_gb': total_gb,
        'system_available_gb': available_gb,
        'system_percent': percent_used
    }


def print_memory_status(label=""):
    """打印内存状态"""
    mem = get_memory_usage()
    print(f"💾 内存 {label}: 进程 {mem['process_gb']:.2f}GB | "
          f"系统 {mem['system_available_gb']:.1f}/{mem['system_total_gb']:.1f}GB "
          f"({mem['system_percent']:.1f}%)")
    
    if mem['system_percent'] > 85:
        print(f"   ⚠️ 警告: 内存使用率过高!")
        return False
    return True


def process_3d_variable_optimized(
    var_name, 
    experiment_name, 
    dataset_key, 
    save_dir, 
    grid_dict, 
    target_lat, 
    target_lon,
    catalog,
    level_slice=(0, None),
    time_batch_size=730,  # 每次处理2年数据
    memory_threshold=85,
    max_retries=3,
    skip_existing=True
):
    """
    优化的3D变量处理函数
    
    Parameters:
    -----------
    var_name : str
        变量名 (例如 'wa', 'ua', 'va', 'hus')
    experiment_name : str
        实验名称 (CNTL, P4K, 4CO2)
    dataset_key : str
        在catalog中的数据集键名
    save_dir : str
        保存目录
    grid_dict : dict
        网格转换参数 {'nside': 256, 'nest': True, 'minmax_lat': 36}
    target_lat : array
        目标纬度数组
    target_lon : array
        目标经度数组
    catalog : intake.Catalog
        数据目录对象
    level_slice : tuple
        层级切片范围 (start, end)
    time_batch_size : int
        时间批次大小（天数）。默认730天（2年）
    memory_threshold : float
        内存使用率阈值（%）
    max_retries : int
        最大重试次数
    skip_existing : bool
        是否跳过已存在的文件
    
    Returns:
    --------
    dict : 处理结果统计
    """
    
    print("="*70)
    print(f"🔄 处理3D变量: {var_name.upper()} - {experiment_name}")
    print("="*70)
    print_memory_status("(开始)")
    
    # 创建保存目录
    exp_save_dir = os.path.join(save_dir, f"{var_name}_{experiment_name.lower()}_layers")
    os.makedirs(exp_save_dir, exist_ok=True)
    print(f"📁 保存路径: {exp_save_dir}")
    
    # 进度记录文件
    progress_file = os.path.join(exp_save_dir, "_progress.txt")
    failed_levels_file = os.path.join(exp_save_dir, "_failed_levels.txt")
    
    total_start_time = time.time()
    
    try:
        # 1. 加载数据元信息
        print(f"📖 读取数据元信息...")
        var_full = catalog.ICON.C5[dataset_key].to_dask()[var_name].sel(
            time=slice("1980", "1993")
        )
        
        # 检测level维度
        level_dim_name = None
        for dim in ['level_full', 'level_half', 'level']:
            if dim in var_full.dims:
                level_dim_name = dim
                break
        
        if level_dim_name is None:
            raise ValueError(f"无法找到level维度。{var_name}的维度: {list(var_full.dims)}")
        
        print(f"✅ 检测到level维度: {level_dim_name}")
        
        # 选择层级范围
        var_selected = var_full.sel({level_dim_name: slice(*level_slice)})
        levels = var_selected[level_dim_name].values
        n_levels = len(levels)
        n_times = len(var_selected.time)
        
        print(f"✅ 数据信息:")
        print(f"   变量: {var_name}")
        print(f"   时间范围: 1980-1993")
        print(f"   时间步数: {n_times} 天")
        print(f"   总层数: {n_levels}")
        print(f"   层级范围: {levels[0]:.1f} - {levels[-1]:.1f}")
        print(f"   时间批次大小: {time_batch_size} 天")
        
        # 计算时间批次
        n_time_batches = int(np.ceil(n_times / time_batch_size))
        print(f"   时间批次数: {n_time_batches}")
        print("="*70)
        
        # 统计变量
        failed_levels = []
        skipped_levels = 0
        processed_levels = 0
        
        # 2. 逐层处理
        for level_idx, level in enumerate(levels, 1):
            level_start_time = time.time()
            
            # 构建保存路径
            save_path = os.path.join(exp_save_dir, f"{var_name}_lev_{int(level):03d}.nc")
            
            # 检查是否已存在
            if skip_existing and os.path.exists(save_path):
                print(f"✅ [{level_idx}/{n_levels}] Level {int(level):3d} - 已存在，跳过")
                skipped_levels += 1
                continue
            
            # 检查内存
            mem_status = get_memory_usage()
            if mem_status['system_percent'] > memory_threshold:
                print(f"⚠️ [{level_idx}/{n_levels}] Level {int(level):3d} - 内存不足，跳过")
                print(f"   内存使用率: {mem_status['system_percent']:.1f}% > {memory_threshold}%")
                failed_levels.append(int(level))
                gc.collect()
                time.sleep(3)
                continue
            
            print(f"🔄 [{level_idx}/{n_levels}] 处理 Level {int(level):3d}...")
            
            # 重试机制
            success = False
            for attempt in range(max_retries):
                try:
                    # 步骤1: 选择单层数据
                    layer_data = var_selected.sel({level_dim_name: level})
                    print(f"   ├─ 选择层级完成 (形状: {layer_data.shape})")
                    
                    # 步骤2: 分批处理时间维度
                    processed_batches = []
                    
                    for batch_idx in range(n_time_batches):
                        start_idx = batch_idx * time_batch_size
                        end_idx = min((batch_idx + 1) * time_batch_size, n_times)
                        
                        if n_time_batches > 1:
                            print(f"   ├─ 时间批次 {batch_idx+1}/{n_time_batches} "
                                  f"(时间步 {start_idx}-{end_idx})...")
                        
                        # 选择时间批次
                        batch_data = layer_data.isel(time=slice(start_idx, end_idx))
                        
                        # 转换到经纬度网格
                        batch_lonlat = dataarray_to_equatorial_latlon_grid(
                            batch_data, 'healpix', grid_dict
                        )
                        
                        # 插值到2°x2°
                        batch_2deg = batch_lonlat.interp(
                            lat=target_lat, lon=target_lon, method='linear'
                        )
                        
                        # 立即计算并释放中间变量
                        with ProgressBar():
                            batch_computed = batch_2deg.compute()
                        
                        processed_batches.append(batch_computed)
                        
                        # 清理批次内存
                        del batch_data, batch_lonlat, batch_2deg
                        gc.collect()
                    
                    # 步骤3: 合并所有时间批次
                    if len(processed_batches) > 1:
                        print(f"   ├─ 合并 {len(processed_batches)} 个时间批次...")
                        layer_final = xr.concat(processed_batches, dim='time')
                    else:
                        layer_final = processed_batches[0]
                    
                    # 步骤4: 保存
                    print(f"   ├─ 保存到文件...")
                    ds_to_save = layer_final.to_dataset(name=var_name)
                    ds_to_save.to_netcdf(save_path)
                    
                    # 获取文件大小
                    file_size_mb = os.path.getsize(save_path) / 1024**2
                    layer_time = time.time() - level_start_time
                    
                    print(f"   ✅ Level {int(level):3d} 完成 "
                          f"(耗时: {layer_time:.1f}s, 文件: {file_size_mb:.2f}MB)")
                    
                    processed_levels += 1
                    
                    # 清理内存
                    del layer_data, processed_batches, layer_final, ds_to_save
                    gc.collect()
                    
                    success = True
                    break  # 成功则跳出重试循环
                    
                except MemoryError as e:
                    print(f"   ⚠️ [尝试 {attempt+1}/{max_retries}] 内存错误: {str(e)}")
                    gc.collect()
                    time.sleep(5)
                    if attempt == max_retries - 1:
                        print(f"   ❌ Level {int(level):3d} 处理失败（内存不足）")
                        failed_levels.append(int(level))
                
                except Exception as e:
                    print(f"   ⚠️ [尝试 {attempt+1}/{max_retries}] 错误: {str(e)}")
                    gc.collect()
                    time.sleep(2)
                    if attempt == max_retries - 1:
                        print(f"   ❌ Level {int(level):3d} 处理失败: {str(e)}")
                        failed_levels.append(int(level))
            
            # 更新进度
            with open(progress_file, 'w') as f:
                f.write(f"Last processed: Level {int(level):03d} ({level_idx}/{n_levels})\n")
                f.write(f"Time: {time.ctime()}\n")
                f.write(f"Processed: {processed_levels}, Skipped: {skipped_levels}, Failed: {len(failed_levels)}\n")
        
        # 3. 保存失败的层级列表
        if failed_levels:
            with open(failed_levels_file, 'w') as f:
                f.write(f"Failed levels for {var_name} - {experiment_name}:\n")
                for lev in failed_levels:
                    f.write(f"{lev}\n")
            print(f"\n⚠️ 有 {len(failed_levels)} 层处理失败，已记录到: {failed_levels_file}")
        
        total_time = time.time() - total_start_time
        
        # 4. 打印总结
        print("\n" + "="*70)
        print(f"📊 处理总结: {var_name.upper()} - {experiment_name}")
        print("="*70)
        print(f"✅ 成功处理: {processed_levels} 层")
        print(f"⏭️  跳过（已存在）: {skipped_levels} 层")
        print(f"❌ 处理失败: {len(failed_levels)} 层")
        print(f"⏱️  总耗时: {total_time/60:.1f} 分钟")
        print(f"📁 保存目录: {exp_save_dir}")
        print("="*70)
        print_memory_status("(结束)")
        
        return {
            'success': processed_levels,
            'skipped': skipped_levels,
            'failed': len(failed_levels),
            'failed_levels': failed_levels,
            'total_time': total_time
        }
        
    except Exception as e:
        print(f"\n❌ 数据处理失败: {str(e)}")
        import traceback
        traceback.print_exc()
        gc.collect()
        raise
    
    finally:
        # 最终清理
        gc.collect()


def batch_process_3d_variables(
    var_names,
    experiments,
    save_dir,
    grid_dict,
    target_lat,
    target_lon,
    catalog,
    **kwargs
):
    """
    批量处理多个3D变量和实验
    
    Parameters:
    -----------
    var_names : list
        变量名列表
    experiments : dict
        实验配置字典 {"exp_key": ("EXP_NAME", "DATASET_KEY")}
    其他参数同 process_3d_variable_optimized
    
    Returns:
    --------
    dict : 所有处理结果
    """
    
    print("\n" + "🌍"*35)
    print("📊 批量处理3D变量")
    print("🌍"*35 + "\n")
    
    all_results = {}
    overall_failed = []
    
    for var_name in var_names:
        var_results = {}
        
        print(f"\n{'='*70}")
        print(f"📊 开始处理变量: {var_name.upper()}")
        print(f"{'='*70}\n")
        
        for exp_key, (exp_name, dataset_key) in experiments.items():
            try:
                result = process_3d_variable_optimized(
                    var_name=var_name,
                    experiment_name=exp_name,
                    dataset_key=dataset_key,
                    save_dir=save_dir,
                    grid_dict=grid_dict,
                    target_lat=target_lat,
                    target_lon=target_lon,
                    catalog=catalog,
                    **kwargs
                )
                var_results[exp_name] = result
                print(f"✅ {var_name.upper()} - {exp_name} 处理成功\n")
                
            except Exception as e:
                error_msg = f"{var_name.upper()} - {exp_name}: {str(e)}"
                print(f"❌ {error_msg}\n")
                overall_failed.append(error_msg)
                var_results[exp_name] = {'error': str(e)}
                gc.collect()
                continue
        
        all_results[var_name] = var_results
    
    # 打印总体统计
    print("\n" + "="*70)
    print("📊 总体处理总结")
    print("="*70)
    
    for var_name, var_results in all_results.items():
        print(f"\n{var_name.upper()}:")
        for exp_name, result in var_results.items():
            if 'error' in result:
                print(f"  ❌ {exp_name}: 失败")
            else:
                print(f"  ✅ {exp_name}: 成功 {result['success']} 层, "
                      f"跳过 {result['skipped']} 层, "
                      f"失败 {result['failed']} 层 "
                      f"(耗时 {result['total_time']/60:.1f}分钟)")
    
    if overall_failed:
        print(f"\n⚠️ 总体失败任务: {len(overall_failed)}")
        for error in overall_failed:
            print(f"  - {error}")
    
    return all_results


# ============================================================================
# 使用示例
# ============================================================================

if __name__ == "__main__":
    import intake
    
    # 加载catalog
    cat = intake.open_catalog("https://data.nextgems-h2020.eu/catalog.yaml")
    
    # 设置参数
    DATA_DIR = "/work/mh1498/m301257/processed_data_lat_30"
    LAYER_DIR = os.path.join(DATA_DIR, "3d_layers")
    os.makedirs(LAYER_DIR, exist_ok=True)
    
    # 网格参数
    grid_dict = {"nside": 256, "nest": True, "minmax_lat": 36}
    target_lat = np.arange(-36, 36.1, 2.0)
    target_lon = np.arange(0, 360, 2.0)
    
    # 定义实验
    experiments = {
        "cntl":  ("CNTL",   "AMIP_CNTL"),
        "4k":    ("P4K",    "AMIP_P4K"),
        # "4co2":  ("4CO2",   "AMIP_4CO2"),
    }
    
    # 定义要处理的3D变量
    variables_3d = ["wa"]  # 垂直速度
    
    # 批量处理
    results = batch_process_3d_variables(
        var_names=variables_3d,
        experiments=experiments,
        save_dir=LAYER_DIR,
        grid_dict=grid_dict,
        target_lat=target_lat,
        target_lon=target_lon,
        catalog=cat,
        time_batch_size=730,  # 每次处理2年
        memory_threshold=85,
        max_retries=3,
        skip_existing=True
    )
    
    print("\n🎉 所有处理完成!")
