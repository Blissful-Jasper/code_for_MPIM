# Code for MPIM - CCKW Analysis

> **对流耦合Kelvin波分析代码库**  
> **Author**: Jianpu | **Institution**: Hohai University  
> **Email**: xianpuji@hhu.edu.cn

---

## 📚 文档导航

本仓库包含完整的对流耦合Kelvin波（CCKW）分析代码和工具。

### 快速链接
- 📖 **[完整代码索引](README_CODE_INDEX.md)** - 所有脚本的详细说明和编号
- 📊 **[数据处理说明](README_data_processing.md)** - 数据预处理流程
- 🔧 **[配置文件](#配置文件)** - 处理参数配置

---

## 📂 代码组织

本代码库按功能分为15个系列，共80+个脚本：

| 系列 | 名称 | 脚本数 | 主要功能 |
|------|------|--------|----------|
| **00** | 数据预处理 | 7个 | 原始数据处理、格式转换、网格插值 |
| **01** | WK频谱分析 | 2个 | Wheeler-Kiladis频谱计算 |
| **02** | 波动滤波 | 5个 | Kelvin波提取、标准差分布 |
| **03** | 交叉谱分析 | 13个 | 变量间相干性和相位分析 |
| **04** | 合成分析 | 9个 | 相位合成、垂直剖面 |
| **05** | 散度分析 | 6个 | 风场散度、垂直运动 |
| **06** | 垂直结构 | 5个 | 温湿廓线、冷点层 |
| **07** | 热力学诊断 | 9个 | MSE、通量、辐射 |
| **08** | 密度质量 | 2个 | 空气密度、ω场 |
| **09** | 降水蒸发 | 2个 | 降水、E-P |
| **10** | 地表变量 | 3个 | 风速、湿度、SST |
| **11** | EOF分析 | 2个 | ω场EOF |
| **12** | 时空分析 | 2个 | Hovmöller图 |
| **13** | 其他分析 | 3个 | 分辨率对比、测试 |
| **14** | 工具脚本 | 4个 | 自动化、配置 |

**详细说明**：请查看 [README_CODE_INDEX.md](README_CODE_INDEX.md)

---

## 🚀 快速开始

### 1. 环境配置

```bash
# 创建环境
conda create -n cckw python=3.10
conda activate cckw

# 安装依赖
pip install xarray dask netCDF4 scipy numpy pandas matplotlib
pip install cartopy cmaps xeofs

# 安装wave_tools
cd ../wave_tools
pip install -e .
```

### 2. 数据处理

```bash
# 处理3D大气数据
python process_3d_data_optimized.py

# 处理海陆掩膜
python process_sea_land_mask.py
```

### 3. 运行分析

```bash
# WK频谱
jupyter notebook 01_Cal_wk_kelvin.ipynb

# Kelvin波提取
jupyter notebook Cal_cckw_filter_3d_fields.ipynb

# 交叉谱分析
jupyter notebook 05_cal_pr&olr_cross_spectrum.ipynb

# 合成分析
jupyter notebook Cal_composite_kelvin.ipynb
```

---

## 📊 核心工作流程

```
原始ICON数据
    ↓
[00] 数据预处理
    ↓
[01] WK频谱诊断 → 识别波动信号
    ↓
[02] Kelvin波滤波 → 提取波动分量
    ↓
    ├─→ [03] 交叉谱分析 → 变量关系
    ├─→ [04] 合成分析 → 相位演变
    ├─→ [05] 散度分析 → 动力特征
    └─→ [06] 垂直结构 → 三维特征
         ↓
    [07] 热力学诊断 → 能量收支
         ↓
    最终结果与图表
```

---

## 🔧 主要工具

### Python脚本

| 脚本 | 功能 | 特点 |
|------|------|------|
| `process_3d_data_optimized.py` | 3D数据处理 | 内存优化、分块处理 |
| `process_sea_land_mask.py` | 海陆掩膜 | 自动化批处理 |
| `wave_filter.py` | 波动滤波 | Dask并行、WK99方法 |

### 配置文件

| 文件 | 用途 |
|------|------|
| `process_config.yml` | 数据处理参数 |
| `kelvin.yaml` | Kelvin波滤波配置 |

### Shell脚本

| 脚本 | 功能 |
|------|------|
| `auto_commit.sh` | 自动Git提交 |
| `clean_cache.sh` | 清理缓存 |

---

## 📖 文档说明

### 主要文档

1. **[README_CODE_INDEX.md](README_CODE_INDEX.md)**
   - 完整的代码索引（80+个脚本）
   - 按功能系列分类
   - 详细的功能说明
   - 使用指南和示例

2. **[README_data_processing.md](README_data_processing.md)**
   - 数据预处理流程
   - 批处理方法
   - 配置参数说明

3. **README.md**（本文件）
   - 项目概述
   - 快速导航
   - 核心功能

---

## 📦 数据说明

### 模式信息
- **模式**：ICON (ICOsahedral Nonhydrostatic)
- **分辨率**：R2B05 (~50km)
- **时间**：1980-2014（35年）

### 实验设计
- **CNTL**：AMIP控制试验
- **P4K**：+4K SST增温试验
- **4CO2**：CO2翻倍试验

### 主要变量
- 降水（pr）、OLR（rlut）
- 温度（ta）、比湿（hus）
- 风场（ua, va, wa）
- 通量（hfls, hfss）

---

## 🎯 研究目标

1. **识别Kelvin波特征**
   - Wheeler-Kiladis频谱分析
   - 周期、波数、传播速度

2. **分析波动结构**
   - 垂直结构
   - 水平传播特征
   - 生命周期

3. **研究气候响应**
   - 对比CNTL、P4K、4CO2
   - 分析增温影响
   - 耦合机制变化

4. **诊断物理过程**
   - 能量收支
   - 对流-湿度-动力耦合
   - 反馈机制

---

## 📝 使用建议

### 新手入门
1. 阅读 [README_CODE_INDEX.md](README_CODE_INDEX.md) 了解代码结构
2. 从简单脚本开始：`01_Cal_wk_kelvin.ipynb`
3. 理解工作流程后再运行复杂分析

### 批量处理
- 使用 `process_*.py` 脚本进行批处理
- 配置 `process_config.yml` 文件
- 使用 `auto_commit.sh` 自动化提交

### 调试技巧
- 先在小数据集上测试
- 使用 `tes.ipynb` 进行原型开发
- 检查内存使用（`process_3d_data_optimized.py`有内存监控）

---

## 🔗 相关资源

### 工具包
- **wave_tools**: `../wave_tools/` - 波动分析工具包
- **NCL脚本**: `01_trop_wmo_ICON.ncl` - 对流层顶计算

### 外部依赖
- [Wheeler-Kiladis Diagnostics](https://www.ncl.ucar.edu/Applications/wheeler_kiladis.shtml)
- [xeofs Documentation](https://xeofs.readthedocs.io/)
- [ICON Model](https://www.icon-model.org/)

---

## 📧 联系方式

**作者**：Jianpu  
**邮箱**：xianpuji@hhu.edu.cn  
**机构**：Hohai University  
**GitHub**：https://github.com/Blissful-Jasper

---

## 📄 许可证

本项目遵循 MIT License - 详见 [LICENSE](LICENSE) 文件

---

**最后更新**：2026-02-16
