#!/usr/bin/env python3
"""
诊断P4K交叉谱异常的脚本
检查降水和散度数据的符号、相关性等
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
print("="*60)
print("加载数据...")
print("="*60)

# 降水数据
pr_cntl = xr.open_dataarray('./processed_data/pr_cntl_2deg_interp.nc')
pr_p4k = xr.open_dataarray('./processed_data/pr_p4k_2deg_interp.nc')
pr_4co2 = xr.open_dataarray('./processed_data/pr_4co2_2deg_interp.nc')

# 散度数据
div_cntl = xr.open_dataset('./processed_data/divergence_lev55_cntl.nc')['divergence']
div_p4k = xr.open_dataset('./processed_data/divergence_lev55_p4k.nc')['divergence']
div_4co2 = xr.open_dataset('./processed_data/divergence_lev55_4co2.nc')['divergence']

print("\n数据加载完成！")

# 1. 检查数据的基本统计信息
print("\n" + "="*60)
print("1. 基本统计信息")
print("="*60)

for name, pr, div in [('CNTL', pr_cntl, div_cntl), 
                       ('P4K', pr_p4k, div_p4k), 
                       ('4CO2', pr_4co2, div_4co2)]:
    print(f"\n{name}:")
    print(f"  降水 - 均值: {pr.mean().values:.6e}, 标准差: {pr.std().values:.6e}")
    print(f"  散度 - 均值: {div.mean().values:.6e}, 标准差: {div.std().values:.6e}")
    print(f"  降水范围: [{pr.min().values:.6e}, {pr.max().values:.6e}]")
    print(f"  散度范围: [{div.min().values:.6e}, {div.max().values:.6e}]")

# 2. 检查时间序列相关性
print("\n" + "="*60)
print("2. 降水与散度的时间序列相关性（热带平均）")
print("="*60)

# 计算热带平均 (15S-15N)
for name, pr, div in [('CNTL', pr_cntl, div_cntl), 
                       ('P4K', pr_p4k, div_p4k), 
                       ('4CO2', pr_4co2, div_4co2)]:
    pr_tropical = pr.mean(dim=['lat', 'lon'])
    div_tropical = div.mean(dim=['lat', 'lon'])
    
    # 计算相关系数
    corr = np.corrcoef(pr_tropical.values, div_tropical.values)[0, 1]
    print(f"{name}: 相关系数 = {corr:.4f}")

# 3. 检查去年循环后的相关性
print("\n" + "="*60)
print("3. 去年循环后的降水与散度相关性")
print("="*60)

for name, pr, div in [('CNTL', pr_cntl, div_cntl), 
                       ('P4K', pr_p4k, div_p4k), 
                       ('4CO2', pr_4co2, div_4co2)]:
    # 去年循环
    pr_ano = pr.groupby('time.dayofyear') - pr.groupby('time.dayofyear').mean()
    div_ano = div.groupby('time.dayofyear') - div.groupby('time.dayofyear').mean()
    
    # 热带平均
    pr_tropical = pr_ano.mean(dim=['lat', 'lon'])
    div_tropical = div_ano.mean(dim=['lat', 'lon'])
    
    # 相关系数
    corr = np.corrcoef(pr_tropical.values, div_tropical.values)[0, 1]
    print(f"{name}: 相关系数 = {corr:.4f}")
    
    # 检查符号
    print(f"  降水异常均值: {pr_ano.mean().values:.6e}")
    print(f"  散度异常均值: {div_ano.mean().values:.6e}")

# 4. 检查散度数据的符号定义
print("\n" + "="*60)
print("4. 检查散度数据的符号定义")
print("="*60)

print("\n理论上，在对流区域：")
print("  - 降水应该 > 0（下雨）")
print("  - 散度应该 < 0（辐合，低层）")
print("  或")
print("  - 散度应该 > 0（辐散，高层）")
print("\n实际检查（选取降水最大的时刻）：")

for name, pr, div in [('CNTL', pr_cntl, div_cntl), 
                       ('P4K', pr_p4k, div_p4k), 
                       ('4CO2', pr_4co2, div_4co2)]:
    # 找到降水最大的时间和位置
    pr_max_time = pr.mean(dim=['lat', 'lon']).argmax().values
    
    pr_at_max = pr.isel(time=pr_max_time).mean().values
    div_at_max = div.isel(time=pr_max_time).mean().values
    
    print(f"\n{name}:")
    print(f"  最大降水时刻的平均降水: {pr_at_max:.6e}")
    print(f"  最大降水时刻的平均散度: {div_at_max:.6e}")
    print(f"  符号是否一致: {'✓' if (pr_at_max > 0 and div_at_max > 0) or (pr_at_max < 0 and div_at_max < 0) else '✗'}")

# 5. 可视化检查
print("\n" + "="*60)
print("5. 生成诊断图...")
print("="*60)

fig, axes = plt.subplots(3, 2, figsize=(14, 12))

for idx, (name, pr, div) in enumerate([('CNTL', pr_cntl, div_cntl), 
                                        ('P4K', pr_p4k, div_p4k), 
                                        ('4CO2', pr_4co2, div_4co2)]):
    # 去年循环
    pr_ano = pr.groupby('time.dayofyear') - pr.groupby('time.dayofyear').mean()
    div_ano = div.groupby('time.dayofyear') - div.groupby('time.dayofyear').mean()
    
    # 热带平均时间序列
    pr_ts = pr_ano.mean(dim=['lat', 'lon'])
    div_ts = div_ano.mean(dim=['lat', 'lon'])
    
    # 左图：时间序列对比（前100天）
    ax1 = axes[idx, 0]
    ax1_twin = ax1.twinx()
    
    ax1.plot(pr_ts[:100], 'b-', label='Precipitation', linewidth=1)
    ax1_twin.plot(div_ts[:100], 'r-', label='Divergence', linewidth=1)
    
    ax1.set_xlabel('Time (days)')
    ax1.set_ylabel('Precipitation anomaly', color='b')
    ax1_twin.set_ylabel('Divergence anomaly', color='r')
    ax1.set_title(f'{name} - Time series (first 100 days)')
    ax1.grid(True, alpha=0.3)
    
    # 右图：散点图
    ax2 = axes[idx, 1]
    ax2.scatter(pr_ts.values, div_ts.values, s=1, alpha=0.3)
    
    # 计算相关系数
    corr = np.corrcoef(pr_ts.values, div_ts.values)[0, 1]
    
    ax2.set_xlabel('Precipitation anomaly')
    ax2.set_ylabel('Divergence anomaly')
    ax2.set_title(f'{name} - Correlation: {corr:.4f}')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
    ax2.axvline(x=0, color='k', linestyle='--', linewidth=0.5)

plt.tight_layout()
plt.savefig('./figures/cross_spectrum_with_51/diagnostic_pr_div_relationship.png', dpi=150, bbox_inches='tight')
print("✅ 诊断图已保存: ./figures/cross_spectrum_with_51/diagnostic_pr_div_relationship.png")

print("\n" + "="*60)
print("诊断完成！")
print("="*60)
