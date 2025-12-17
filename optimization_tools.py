#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kelvin波相位合成代码优化工具
Optimization Tools for Kelvin Wave Phase Composite Analysis

主要功能：
1. 缓存管理 - 避免重复计算滤波
2. 检查点保存 - 断点续传
3. 内存优化 - 及时清理
4. 进度显示 - 时间估算
"""

import os
import gc
import time
import pickle
import xarray as xr
import numpy as np

# 配置
CACHE_DIR = "./cache/kelvin_wave/"
CHECKPOINT_DIR = "./checkpoints/"

for d in [CACHE_DIR, CHECKPOINT_DIR]:
    os.makedirs(d, exist_ok=True)

print("=" * 70)
print("✅ Kelvin波分析优化工具已加载")
print(f"   缓存目录: {CACHE_DIR}")
print(f"   检查点目录: {CHECKPOINT_DIR}")
print("=" * 70)


def format_time(seconds):
    """格式化时间显示"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        return f"{seconds/60:.1f}分钟"
    else:
        return f"{seconds/3600:.1f}小时"


def get_cache_file(exp_name, data_type='kelvin_wave'):
    """获取缓存文件路径"""
    return os.path.join(CACHE_DIR, f'{data_type}_{exp_name.lower()}.nc')


def load_from_cache(exp_name, data_type='kelvin_wave'):
    """从缓存加载数据"""
    cache_file = get_cache_file(exp_name, data_type)
    if os.path.exists(cache_file):
        print(f"  ♻️ 从缓存加载 {exp_name}...")
        return xr.open_dataarray(cache_file)
    return None


def save_to_cache(data, exp_name, data_type='kelvin_wave'):
    """保存数据到缓存"""
    cache_file = get_cache_file(exp_name, data_type)
    print(f"  💾 保存到缓存...")
    data.to_netcdf(cache_file)
    size_mb = os.path.getsize(cache_file) / 1024 / 1024
    print(f"     文件大小: {size_mb:.1f} MB")


def get_checkpoint_file(step_name, exp_name):
    """获取检查点文件路径"""
    return os.path.join(CHECKPOINT_DIR, f"{step_name}_{exp_name}.pkl")


def load_checkpoint(step_name, exp_name):
    """加载检查点"""
    checkpoint_file = get_checkpoint_file(step_name, exp_name)
    if os.path.exists(checkpoint_file):
        print(f"  ♻️ 从检查点恢复 {exp_name}...")
        with open(checkpoint_file, 'rb') as f:
            return pickle.load(f)
    return None


def save_checkpoint(data, step_name, exp_name):
    """保存检查点"""
    checkpoint_file = get_checkpoint_file(step_name, exp_name)
    print(f"  💾 保存检查点...")
    with open(checkpoint_file, 'wb') as f:
        pickle.dump(data, f)


def cleanup_memory():
    """清理内存"""
    gc.collect()
    print(f"  🧹 内存已清理")


def apply_kelvin_filter_with_cache(pr_data, exp_name, sel_dict, WaveFilter):
    """
    应用Kelvin波滤波（带缓存）
    
    参数:
        pr_data: 降水数据
        exp_name: 实验名称（CNTL, P4K, 4CO2）
        sel_dict: 时间和纬度选择字典
        WaveFilter: 波滤波器类
    
    返回:
        filtered_data: 滤波后的数据
    """
    # 检查缓存
    cached_data = load_from_cache(exp_name, 'kelvin_wave')
    if cached_data is not None:
        return cached_data
    
    # 缓存不存在，进行计算
    print(f"  ⚠️ 缓存不存在，开始计算...")
    start_time = time.time()
    
    wave_filter = WaveFilter(
        ds=pr_data,
        sel_dict=sel_dict,
        wave_name='kelvin',
        units='mm/day',
        spd=1,
        n_workers=4
    )
    
    print(f"  ⏳ Step 1/5: Loading data...")
    wave_filter.load_data()
    
    print(f"  ⏳ Step 2/5: Detrending...")
    wave_filter.detrend_data()
    
    print(f"  ⏳ Step 3/5: FFT transform...")
    wave_filter.fft_transform()
    
    print(f"  ⏳ Step 4/5: Applying filter...")
    wave_filter.apply_filter()
    
    print(f"  ⏳ Step 5/5: Inverse FFT...")
    wave_filter.inverse_fft()
    
    filtered_data = wave_filter.create_output()
    
    # 保存到缓存
    save_to_cache(filtered_data, exp_name, 'kelvin_wave')
    
    elapsed = time.time() - start_time
    print(f"  ✅ 完成！耗时: {format_time(elapsed)}")
    
    # 清理
    del wave_filter
    cleanup_memory()
    
    return filtered_data


def phase_composite_with_checkpoint(kelvin_data, pr_data, exp_name, 
                                   lon_ref=180.0, nlag=10, Nstd=1.0,
                                   lat_range=(-10, 10)):
    """
    相位合成分析（带检查点）
    
    参数:
        kelvin_data: Kelvin波滤波后的数据
        pr_data: 原始降水数据
        exp_name: 实验名称
        lon_ref: 参考经度
        nlag: 滞后步数
        Nstd: 标准差倍数阈值
        lat_range: 纬度平均范围，默认 (-10, 10)
    
    返回:
        phase_result: 相位合成结果字典
        lag_result: 滞后合成结果字典
    """
    # 检查检查点
    checkpoint_data = load_checkpoint('phase_composite', exp_name)
    if checkpoint_data is not None:
        return checkpoint_data['phase'], checkpoint_data['lag']
    
    # 检查点不存在，进行计算
    print(f"  ⚠️ 检查点不存在，开始计算...")
    start_time = time.time()
    
    from wave_tools.phase import (
        calculate_kelvin_phase,
        phase_composite,
        lag_composite,
        optimize_peak_detection,
        remove_clm
    )
    
    # 定义简化的纬度平均函数
    def latitude_average(data, lat_range):
        """简单的纬度平均"""
        data_selected = data.sel(lat=slice(lat_range[0], lat_range[1]))
        return data_selected.mean(dim='lat')
    
    lat = kelvin_data.lat.values
    lon = kelvin_data.lon.values
    
    # Step 1: 纬度平均（替代经向投影）
    print(f"  ⏳ Step 1/6: Latitude averaging ({lat_range[0]}° to {lat_range[1]}°)...")
    kelvin_eq = latitude_average(kelvin_data, lat_range)
    pr_eq = latitude_average(pr_data, lat_range)
    
    # Step 2: 去除气候态
    print(f"  ⏳ Step 2/6: Removing climatology...")
    pr_ano = remove_clm(pr_data)
    pr_ano_eq = latitude_average(pr_ano, lat_range)
    
    # Step 3: 峰值检测（关闭并行以提高性能）
    print(f"  ⏳ Step 3/6: Peak detection (serial mode)...")
    V = kelvin_eq.data
    V_std = np.nanstd(V)
    V_peak, _ = optimize_peak_detection(
        V, kelvin_eq, V_std, Nstd=Nstd,
        use_parallel=False,  # 关键优化：关闭并行
        n_jobs=1
    )
    print(f"     Std: {V_std:.3f} mm/day")
    
    # Step 4: 计算相位
    print(f"  ⏳ Step 4/6: Calculating phase...")
    phase = calculate_kelvin_phase(kelvin_eq, V_peak)
    print(f"     Phase range: [{np.nanmin(phase.data):.3f}, {np.nanmax(phase.data):.3f}]")
    
    # Step 5: 相位合成
    print(f"  ⏳ Step 5/6: Phase composite...")
    phase_bin, composite_mean, composite_count = phase_composite(kelvin_eq, phase)
    
    phase_result = {
        'phase_bin': phase_bin,
        'composite_mean': composite_mean,
        'composite_count': composite_count,
        'std': V_std
    }
    
    # Step 6: 滞后合成
    print(f"  ⏳ Step 6/6: Lag composite...")
    tlag, lag_comp_ano, it_max = lag_composite(
        pr_ano_eq, phase, lon, lon_ref=lon_ref, nlag=nlag
    )
    tlag, lag_comp_kw, _ = lag_composite(
        kelvin_eq, phase, lon, lon_ref=lon_ref, nlag=nlag
    )
    
    lag_result = {
        'tlag': tlag,
        'lag_composite_ano': lag_comp_ano,
        'lag_composite_kw': lag_comp_kw,
        'lon': lon,
        'n_events': len(it_max)
    }
    
    print(f"     Found {len(it_max)} events")
    
    # 保存检查点
    checkpoint_data = {
        'phase': phase_result,
        'lag': lag_result
    }
    save_checkpoint(checkpoint_data, 'phase_composite', exp_name)
    
    elapsed = time.time() - start_time
    print(f"  ✅ 完成！耗时: {format_time(elapsed)}")
    
    # 清理内存
    del kelvin_eq, pr_eq, pr_ano, pr_ano_eq, V, V_peak, phase
    cleanup_memory()
    
    return phase_result, lag_result


def clear_cache():
    """清空所有缓存"""
    import shutil
    for d in [CACHE_DIR, CHECKPOINT_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)
    print("✅ 缓存已清空")


def print_usage():
    """打印使用说明"""
    print("\n" + "=" * 70)
    print("📖 使用说明")
    print("=" * 70)
    print("""
1. 应用Kelvin波滤波（带缓存）:

   from optimization_patch import apply_kelvin_filter_with_cache
   
   filtered_data = apply_kelvin_filter_with_cache(
       pr_data=pr_data['CNTL'],
       exp_name='CNTL',
       sel_dict={'time': slice('1980-01-01', '1993-12-31'), 
                 'lat': slice(-15, 15)},
       WaveFilter=WaveFilter  # 传入WaveFilter类
   )

2. 相位合成分析（带检查点）:

   from optimization_patch import phase_composite_with_checkpoint
   
   phase_result, lag_result = phase_composite_with_checkpoint(
       kelvin_data=kelvin_wave_data['CNTL'],
       pr_data=pr_data['CNTL'],
       exp_name='CNTL',
       lon_ref=180.0,
       nlag=10,
       Nstd=1.0
   )

3. 清空缓存（如需重新计算）:

   from optimization_patch import clear_cache
   clear_cache()

4. 完整示例:

   # 导入必要的模块
   from optimization_patch import (
       apply_kelvin_filter_with_cache,
       phase_composite_with_checkpoint,
       format_time
   )
   import time
   
   # 处理所有实验
   total_start = time.time()
   kelvin_wave_data = {}
   phase_composites = {}
   lag_composites = {}
   
   for exp in ['CNTL', 'P4K', '4CO2']:
       print(f"\\n处理 {exp}...")
       
       # 滤波（自动使用缓存）
       kelvin_wave_data[exp] = apply_kelvin_filter_with_cache(
           pr_data=pr_data[exp],
           exp_name=exp,
           sel_dict=sel_dict,
           WaveFilter=WaveFilter
       )
       
       # 相位合成（自动使用检查点）
       phase_composites[exp], lag_composites[exp] = \\
           phase_composite_with_checkpoint(
               kelvin_data=kelvin_wave_data[exp],
               pr_data=pr_data[exp],
               exp_name=exp
           )
   
   total_time = time.time() - total_start
   print(f"\\n✅ 全部完成！总耗时: {format_time(total_time)}")
    """)
    print("=" * 70)


if __name__ == "__main__":
    print_usage()
