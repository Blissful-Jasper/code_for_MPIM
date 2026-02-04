# 热带区域对比分析使用指南

## 📋 概述

本指南说明如何使用更新后的 `06_Cal_difference_qs_qa_allregion.ipynb` 进行热带区域（陆地、海洋、全球）的比湿和风速对潜热通量贡献的对比分析。

---

## 🎯 主要功能

### 1. 区域定义

代码自动计算三种区域类型的统计数据：

| 区域类型 | 代码标识 | 说明 |
|---------|---------|------|
| 🌏 全球 | `'all'` | 30°S-30°N 所有格点（陆地+海洋） |
| 🌊 海洋 | `'ocean'` | 30°S-30°N 仅海洋格点 |
| 🏔️ 陆地 | `'land'` | 30°S-30°N 仅陆地格点 |

### 2. 计算变量

对每个区域分别计算：

- **qs**: 海表/地表饱和比湿 (kg/kg)
- **qa**: 近地表空气比湿 (kg/kg)
- **dq**: 湿度差 = qs - qa (kg/kg)
- **风速**: 10m表面风速 (m/s)

### 3. 实验对比

- **CNTL**: 控制实验
- **P4K**: 海温+4K实验
- **4CO2**: CO₂浓度翻4倍实验

---

## 📂 输出文件结构

```
./figures/Cal_qs_qa_tropical/
├── regional_comparison_all_vars.png       # 区域对比柱状图（绝对值）
├── regional_relative_changes.png          # 相对变化对比图（百分比）
├── comprehensive_regional_comparison.png  # 综合对比图（风速+湿度）
├── humidity_qs_qa_dq_climatology.png     # 空间分布图
└── latent_heat_factors_summary.png       # 因子总结图

./processed_data/tropical_qs_qa_results/
└── tropical_regional_means.nc             # 区域平均数据（NetCDF格式）
```

---

## 🚀 快速开始

### 步骤1: 运行数据加载单元格

运行前几个单元格加载必要的模块和数据：

```python
# Cell 1: 导入包
# Cell 2: 定义区域函数
# Cell 3-7: 加载温度、气压、比湿数据
```

### 步骤2: 计算区域统计

运行关键计算单元格：

```python
# Cell: "计算热带区域平均值"
# 这将自动计算所有三个区域的统计数据
```

输出示例：
```
🌍 处理区域: 全球（陆地+海洋）
全球（陆地+海洋） - Control:
  qs = 0.018234 kg/kg
  qa = 0.012456 kg/kg
  dq = 0.005778 kg/kg
```

### 步骤3: 生成可视化

运行绘图单元格生成对比图：

```python
# Cell: 绘制区域对比柱状图
# Cell: 绘制相对变化对比图
# Cell: 打印区域统计表
```

### 步骤4: 风速分析

```python
# Cell: 加载和处理风速数据
# Cell: 创建综合对比图
```

---

## 📊 主要输出解读

### 1. 区域对比柱状图

**文件**: `regional_comparison_all_vars.png`

- **行**: 不同实验（CNTL, P4K, 4CO2）
- **列**: 不同变量（qs, qa, dq）
- **柱子颜色**:
  - 🔵 蓝色 = 全球
  - 🟢 绿色 = 海洋
  - 🔴 红色 = 陆地

**用途**: 直观比较陆地、海洋、全球的绝对值差异

---

### 2. 相对变化对比图

**文件**: `regional_relative_changes.png`

- **行**: P4K-CNTL 和 4CO2-CNTL
- **柱子高度**: 相对变化百分比

**用途**: 量化气候变化下各区域的响应幅度

---

### 3. 综合对比图

**文件**: `comprehensive_regional_comparison.png`

- **同时展示**: 风速、qs、qa、dq 的相对变化
- **分区域**: 全球、海洋、陆地各有独立子图

**用途**: 识别主导因子（风速 vs 湿度梯度）

---

## 🔬 科学分析建议

### 关键问题

1. **海洋 vs 陆地**
   - 哪个区域的湿度梯度变化更大？
   - 风速变化在陆地和海洋有何不同？

2. **主导机制**
   - 在海洋上，风速还是湿度梯度主导LHF变化？
   - 在陆地上，哪个因子更重要？

3. **气候响应差异**
   - P4K vs 4CO2：哪个实验显示更强的陆地-海洋对比？
   - 为什么会有这些差异？

### 分析流程建议

```python
# 1. 计算海洋/陆地的响应比
ocean_dq_change = (dq_4co2_ocean - dq_cntl_ocean) / dq_cntl_ocean * 100
land_dq_change = (dq_4co2_land - dq_cntl_land) / dq_cntl_land * 100
response_ratio = ocean_dq_change / land_dq_change

# 2. 识别主导因子
if abs(dq_change) > abs(wind_change):
    print("湿度梯度主导")
else:
    print("风速主导")

# 3. 区域加权平均
global_mean = (ocean_area * ocean_value + land_area * land_value) / total_area
```

---

## 🛠️ 自定义修改

### 修改纬度范围

```python
TROPICAL_LAT_MIN = -20  # 改为 20°S
TROPICAL_LAT_MAX = 20   # 改为 20°N
```

### 添加新区域

```python
def _subtropical_ocean(ds):
    """亚热带海洋 (20-40°N/S)"""
    lat = ds.lat
    subtropical_mask = ((lat >= 20) & (lat <= 40)) | ((lat >= -40) & (lat <= -20))
    return subtropical_mask & _ocean(ds)
```

### 修改颜色方案

```python
colors_regional = {
    'all': '#YOUR_COLOR',
    'ocean': '#YOUR_COLOR', 
    'land': '#YOUR_COLOR'
}
```

---

## ❓ 常见问题

### Q1: 如何只分析海洋？

**答**: 在计算平均值时，只使用 `region_key='ocean'`：

```python
ocean_only = regional_means['ocean']
```

### Q2: 陆地数据为什么看起来有噪声？

**答**: 陆地地形复杂，局地变化大。可以考虑：
- 增加平滑处理
- 按植被类型进一步细分
- 使用中位数代替平均值

### Q3: 如何导出数据到Excel？

```python
import pandas as pd

# 创建DataFrame
df = pd.DataFrame({
    'Region': list(REGIONS.values()),
    'CNTL_qs': [regional_means[r]['qs_cntl']*1000 for r in REGIONS.keys()],
    'P4K_qs': [regional_means[r]['qs_p4k']*1000 for r in REGIONS.keys()],
    # ... 添加更多列
})

df.to_excel('regional_statistics.xlsx', index=False)
```

---

## 📚 相关文档

- **主notebook**: `06_Cal_difference_qs_qa_allregion.ipynb`
- **数据说明**: `readme_about_data_folder.md`
- **原始数据**: `/work/mh1498/m301257/data_origin/`

---

## 📧 联系支持

如有问题或建议，请联系课题组或查看项目README。

**最后更新**: 2026-01-24
