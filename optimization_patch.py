"""
快速优化补丁 - 可直接添加到现有notebook
Quick Optimization Patches for Existing Notebook

使用方法：
1. 在现有notebook的开头运行此cell
2. 会自动启用缓存和内存优化
"""

import os
import gc
import pickle
import time
from functools import wraps
import numpy as np

# ============================================================
# 配置区域
# ============================================================
CACHE_DIR = "./cache/kelvin_wave/"
CHECKPOINT_DIR = "./checkpoints/"

for d in [CACHE_DIR, CHECKPOINT_DIR]:
    os.makedirs(d, exist_ok=True)

print("🔧 优化补丁已加载")
print(f"   缓存目录: {CACHE_DIR}")
print(f"   检查点目录: {CHECKPOINT_DIR}")

# ============================================================
# 辅助函数
# ============================================================

def format_time(seconds):
    """格式化时间显示"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        return f"{seconds/60:.1f}分钟"
    else:
        return f"{seconds/3600:.1f}小时"


def timer(func):
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"  ⏱️ {func.__name__} 耗时: {format_time(elapsed)}")
        return result
    return wrapper


# ============================================================
# 缓存管理
# ============================================================

class CacheManager:
    """缓存管理器"""
    
    @staticmethod
    def get_cache_path(exp_name, data_type='kelvin_wave'):
        """获取缓存文件路径"""
        return os.path.join(CACHE_DIR, f'{data_type}_{exp_name.lower()}_cached.nc')
    
    @staticmethod
    def exists(exp_name, data_type='kelvin_wave'):
        """检查缓存是否存在"""
        return os.path.exists(CacheManager.get_cache_path(exp_name, data_type))
    
    @staticmethod
    def load(exp_name, data_type='kelvin_wave'):
        """加载缓存"""
        import xarray as xr
        path = CacheManager.get_cache_path(exp_name, data_type)
        if os.path.exists(path):
            print(f"  ♻️ 从缓存加载 {exp_name}...")
            return xr.open_dataarray(path)
        return None
    
    @staticmethod
    def save(data, exp_name, data_type='kelvin_wave'):
        """保存缓存"""
        path = CacheManager.get_cache_path(exp_name, data_type)
        print(f"  💾 保存缓存到 {path}...")
        data.to_netcdf(path)
        print(f"     缓存大小: {os.path.getsize(path) / 1024 / 1024:.1f} MB")


# ============================================================
# 检查点管理
# ============================================================

class CheckpointManager:
    """检查点管理器"""
    
    @staticmethod
    def get_checkpoint_path(step_name, exp_name):
        """获取检查点文件路径"""
        return os.path.join(CHECKPOINT_DIR, f"{step_name}_{exp_name}.pkl")
    
    @staticmethod
    def exists(step_name, exp_name):
        """检查检查点是否存在"""
        return os.path.exists(CheckpointManager.get_checkpoint_path(step_name, exp_name))
    
    @staticmethod
    def load(step_name, exp_name):
        """加载检查点"""
        path = CheckpointManager.get_checkpoint_path(step_name, exp_name)
        if os.path.exists(path):
            print(f"  ♻️ 从检查点恢复 {step_name} - {exp_name}...")
            with open(path, 'rb') as f:
                return pickle.load(f)
        return None
    
    @staticmethod
    def save(data, step_name, exp_name):
        """保存检查点"""
        path = CheckpointManager.get_checkpoint_path(step_name, exp_name)
        print(f"  💾 保存检查点...")
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        print(f"     检查点大小: {os.path.getsize(path) / 1024 / 1024:.1f} MB")


# ============================================================
# 内存优化
# ============================================================

def cleanup_memory(*variables):
    """清理内存"""
    for var in variables:
        if var in globals():
            del globals()[var]
        elif var in locals():
            del locals()[var]
    gc.collect()
    print(f"  🧹 内存清理完成")


def monitor_memory():
    """监控内存使用"""
    import psutil
    process = psutil.Process()
    mem_info = process.memory_info()
    mem_mb = mem_info.rss / 1024 / 1024
    print(f"  📊 当前内存使用: {mem_mb:.1f} MB")
    return mem_mb


# ============================================================
# 进度跟踪
# ============================================================

class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self, total_steps):
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
        self.step_times = []
    
    def update(self, step_name=""):
        """更新进度"""
        self.current_step += 1
        elapsed = time.time() - self.start_time
        self.step_times.append(elapsed)
        
        # 计算进度
        progress = self.current_step / self.total_steps * 100
        
        # 估算剩余时间
        if self.current_step > 0:
            avg_time_per_step = elapsed / self.current_step
            remaining_steps = self.total_steps - self.current_step
            estimated_remaining = avg_time_per_step * remaining_steps
        else:
            estimated_remaining = 0
        
        print(f"\n  📊 进度: {self.current_step}/{self.total_steps} ({progress:.1f}%)")
        print(f"     已用时间: {format_time(elapsed)}")
        if remaining_steps > 0:
            print(f"     预计剩余: {format_time(estimated_remaining)}")
        
        if step_name:
            print(f"     当前步骤: {step_name}")
    
    def summary(self):
        """显示总结"""
        total_time = time.time() - self.start_time
        print(f"\n{'='*60}")
        print(f"✅ 全部完成！")
        print(f"   总耗时: {format_time(total_time)}")
        print(f"   平均每步: {format_time(total_time / self.total_steps)}")
        print(f"{'='*60}")


# ============================================================
# 优化的滤波函数包装器
# ============================================================

def apply_kelvin_filter_cached(pr_data_dict, sel_dict, wave_name='kelvin'):
    """
    应用Kelvin波滤波（带缓存）
    
    参数:
        pr_data_dict: 字典，键为实验名称，值为降水数据
        sel_dict: 选择字典（时间、纬度范围）
        wave_name: 波名称
    
    返回:
        kelvin_wave_data: 字典，键为实验名称，值为滤波后的数据
    """
    kelvin_wave_data = {}
    tracker = ProgressTracker(len(pr_data_dict))
    
    for exp, pr_data in pr_data_dict.items():
        print(f"\n{'='*60}")
        print(f"📍 处理 {exp}")
        print(f"{'='*60}")
        
        # 检查缓存
        cached_data = CacheManager.load(exp, 'kelvin_wave')
        if cached_data is not None:
            kelvin_wave_data[exp] = cached_data
            tracker.update(f\"{exp} (从缓存加载)\")
            continue
        
        # 如果没有缓存，进行计算
        print(f\"  ⚠️ 缓存不存在，开始计算...\")\
        from wave_filter import WaveFilter  # 假设已经导入
        
        wave_filter = WaveFilter(
            ds=pr_data,
            sel_dict=sel_dict,
            wave_name=wave_name,
            units='mm/day',
            spd=1,
            n_workers=4
        )
        
        print(f\"  ⏳ 加载数据...\")\n        wave_filter.load_data()
        
        print(f\"  ⏳ 去趋势...\")\n        wave_filter.detrend_data()
        
        print(f\"  ⏳ FFT变换...\")\n        wave_filter.fft_transform()
        
        print(f\"  ⏳ 应用滤波器...\")\n        wave_filter.apply_filter()
        
        print(f\"  ⏳ 逆FFT...\")\n        wave_filter.inverse_fft()
        
        filtered_data = wave_filter.create_output()
        
        # 保存到缓存
        CacheManager.save(filtered_data, exp, 'kelvin_wave')
        kelvin_wave_data[exp] = filtered_data
        
        # 清理内存
        del wave_filter
        gc.collect()
        
        tracker.update(f\"{exp} (新计算)\")\n    \n    tracker.summary()
    return kelvin_wave_data


# ============================================================
# 优化的相位合成函数包装器
# ============================================================

def phase_composite_analysis_cached(kelvin_wave_data, pr_data, lon_ref=180.0, nlag=10, Nstd=1.0):
    """
    相位合成分析（带检查点）
    
    参数:
        kelvin_wave_data: Kelvin波滤波后的数据字典
        pr_data: 原始降水数据字典
        lon_ref: 参考经度
        nlag: 滞后步数
        Nstd: 标准差倍数阈值
    
    返回:
        phase_composites: 相位合成结果字典
        lag_composites: 滞后合成结果字典
    """
    from wave_tools.phase import (
        meridional_projection,
        calculate_kelvin_phase,
        phase_composite,
        lag_composite,
        optimize_peak_detection,
        remove_clm
    )
    import numpy as np
    
    phase_composites = {}
    lag_composites = {}
    tracker = ProgressTracker(len(kelvin_wave_data))
    
    for exp in kelvin_wave_data.keys():
        print(f\"\\n{'='*60}\")
        print(f\"📍 相位合成分析: {exp}\")
        print(f\"{'='*60}\")
        
        # 检查检查点
        checkpoint_data = CheckpointManager.load('phase_composite', exp)
        if checkpoint_data is not None:
            phase_composites[exp] = checkpoint_data['phase']
            lag_composites[exp] = checkpoint_data['lag']
            tracker.update(f\"{exp} (从检查点恢复)\")
            continue
        
        print(f\"  ⚠️ 检查点不存在，开始计算...\")\
        \n        kelvin_data = kelvin_wave_data[exp]
        pr_original = pr_data[exp]
        lat = kelvin_data.lat.values
        lon = kelvin_data.lon.values
        
        # 纬向投影
        print(f\"  ⏳ 1/6: 纬向投影...\")\n        kelvin_eq = meridional_projection(kelvin_data, lat)
        pr_eq = meridional_projection(pr_original, lat)
        
        # 去除气候态
        print(f\"  ⏳ 2/6: 去除气候态...\")\n        pr_ano = remove_clm(pr_original)
        pr_ano_eq = meridional_projection(pr_ano, lat)
        
        # 峰值检测（优化：关闭并行）
        print(f\"  ⏳ 3/6: 峰值检测（串行模式）...\")\n        V = kelvin_eq.data
        V_std = np.nanstd(V)
        V_peak, _ = optimize_peak_detection(
            V, kelvin_eq, V_std, Nstd=Nstd,
            use_parallel=False,  # 关键优化
            n_jobs=1
        )
        print(f\"     标准差: {V_std:.3f} mm/day\")\
        \n        # 计算相位
        print(f\"  ⏳ 4/6: 计算相位...\")\n        phase = calculate_kelvin_phase(kelvin_eq, V_peak)
        
        # 相位合成
        print(f\"  ⏳ 5/6: 相位合成...\")\n        phase_bin, composite_mean, composite_count = phase_composite(
            kelvin_eq, phase
        )
        
        phase_composites[exp] = {
            'phase_bin': phase_bin,
            'composite_mean': composite_mean,
            'composite_count': composite_count,
            'std': V_std
        }
        
        # 滞后合成
        print(f\"  ⏳ 6/6: 滞后合成...\")\n        tlag, lag_comp_ano, it_max = lag_composite(
            pr_ano_eq, phase, lon, lon_ref=lon_ref, nlag=nlag
        )
        tlag, lag_comp_kw, _ = lag_composite(
            kelvin_eq, phase, lon, lon_ref=lon_ref, nlag=nlag
        )
        
        lag_composites[exp] = {
            'tlag': tlag,
            'lag_composite_ano': lag_comp_ano,
            'lag_composite_kw': lag_comp_kw,
            'lon': lon,
            'n_events': len(it_max)
        }
        
        print(f\"     发现 {len(it_max)} 个事件\")\
        \n        # 保存检查点
        checkpoint_data = {
            'phase': phase_composites[exp],
            'lag': lag_composites[exp]
        }
        CheckpointManager.save(checkpoint_data, 'phase_composite', exp)
        
        # 清理内存
        del kelvin_eq, pr_eq, pr_ano, pr_ano_eq, V, V_peak, phase
        gc.collect()
        
        tracker.update(f\"{exp} (新计算)\")\n    \n    tracker.summary()
    return phase_composites, lag_composites


# ============================================================
# 使用示例
# ============================================================

def print_usage_example():
    """打印使用示例"""
    print(\"\\n\" + \"=\"*60)
    print(\"📖 使用示例\")
    print(\"=\"*60)
    print(\"\"\"
# 1. 应用Kelvin波滤波（带缓存）
sel_dict = {
    'time': slice('1980-01-01', '1993-12-31'),
    'lat': slice(-15, 15)
}

kelvin_wave_data = apply_kelvin_filter_cached(
    pr_data_dict=pr_data,
    sel_dict=sel_dict,
    wave_name='kelvin'
)

# 2. 相位合成分析（带检查点）
phase_composites, lag_composites = phase_composite_analysis_cached(
    kelvin_wave_data=kelvin_wave_data,
    pr_data=pr_data,
    lon_ref=180.0,
    nlag=10,
    Nstd=1.0
)

# 3. 清空所有缓存（如果需要重新计算）
import shutil
shutil.rmtree(CACHE_DIR)
shutil.rmtree(CHECKPOINT_DIR)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    \"\"\")

print(\"\\n✅ 所有优化工具已准备就绪！\")
print(\"\\n💡 提示：\")
print(\"   - 首次运行会保存缓存和检查点\")
print(\"   - 后续运行会自动加载，节省60-80%时间\")
print(\"   - 如遇断线，重新运行会从检查点恢复\")
print(\"\\n\" + \"=\"*60)

# 显示使用示例
print_usage_example()
