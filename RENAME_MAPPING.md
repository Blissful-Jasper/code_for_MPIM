# 脚本重命名对照表

> **重命名日期**: 2026-02-16  
> **重命名目的**: 系统化代码组织，使编号清晰、功能明确

---

## 📋 重命名规则

### 编号体系
- **00系列**: 数据预处理 (Data Preprocessing)
- **10系列**: WK频谱分析 (Spectrum Analysis)
- **20系列**: Kelvin波滤波 (Wave Filtering)
- **30系列**: 交叉谱分析 (Cross-Spectrum Analysis)
- **50系列**: 合成分析 (Composite Analysis)
- **60系列**: 散度分析 (Divergence Analysis)
- **70系列**: 垂直结构 (Vertical Structure)
- **80系列**: 热力学诊断 (Thermodynamic Diagnostics)
- **90系列**: 密度质量 (Density & Mass)
- **95系列**: 降水蒸发 (Precipitation & Evaporation)
- **97系列**: 地表变量 (Surface Variables)
- **A0系列**: EOF分析 (EOF Analysis)
- **B0系列**: 时空分析 (Spatiotemporal Analysis)
- **Z0系列**: 其他分析 (Miscellaneous)

### 命名格式
```
[编号]_[功能类别]_[具体描述].ipynb
```
- **编号**: 两位数字或字母+数字（如 00, 10, A0）
- **功能类别**: 使用统一的英文简写（如 filter, composite, thermo）
- **具体描述**: 简洁的功能说明（使用下划线连接）

---

## 🔄 完整对照表

### 00系列 - 数据预处理

| 旧文件名 | 新文件名 | 功能说明 |
|---------|---------|---------|
| `Python_Only_data_preprocess.ipynb` | `00_preprocess_python_only.ipynb` | 纯Python数据预处理 |
| `Python_merge_3D.ipynb` | `00_preprocess_merge_3d.ipynb` | 3D数据合并 |
| `Data_preprocess_for_uw_wind.ipynb` | `00_preprocess_wind_field.ipynb` | 风场数据预处理 |
| `Data_preprocess_for_30_lattitude.ipynb` | `00_preprocess_lat30_region.ipynb` | 30°纬度区域预处理 |
| `01_trop_wmo_ICON.ncl` | `00_preprocess_tropopause_wmo.ncl` | WMO对流层顶计算（NCL） |

**工具脚本**（保持原名）:
- `process_3d_data_optimized.py` - 3D数据处理工具
- `process_sea_land_mask.py` - 海陆掩膜处理
- `wave_filter.py` - 波动滤波工具

---

### 10系列 - WK频谱分析

| 旧文件名 | 新文件名 | 功能说明 |
|---------|---------|---------|
| `01_Cal_wk_kelvin.ipynb` | `10_spectrum_wk_analysis.ipynb` | Wheeler-Kiladis频谱分析 |
| `Cal_spectrum_year_by_year.ipynb` | `11_spectrum_yearly_analysis.ipynb` | 逐年频谱分析 |

---

### 20系列 - Kelvin波滤波

| 旧文件名 | 新文件名 | 功能说明 |
|---------|---------|---------|
| `Cal_cckw_filter_3d_fields.ipynb` | `20_filter_kelvin_3d_fields.ipynb` | 3D场Kelvin波滤波 |
| `Cal_cckw_filter_for_hus.ipynb` | `21_filter_kelvin_humidity.ipynb` | 比湿场Kelvin波滤波 |
| `Cal_cckw_std_distribution.ipynb` | `22_filter_kelvin_std_dist.ipynb` | Kelvin波标准差分布 |
| `Cal_+4K_data_kelvin.ipynb` | `23_filter_kelvin_p4k_scenario.ipynb` | +4K情景Kelvin波分析 |

---

### 30系列 - 交叉谱分析

| 旧文件名 | 新文件名 | 功能说明 |
|---------|---------|---------|
| `Cal_cross_specturm.ipynb` | `30_cross_spectrum_basic.ipynb` | 基础交叉谱分析 |
| `Cal_cross_specturm_with_51.ipynb` | `31_cross_spectrum_level51.ipynb` | Level-51层交叉谱 |
| `Cal_cross_specturm_with_pywk99.ipynb` | `32_cross_spectrum_pywk99.ipynb` | 使用pywk99库的交叉谱 |
| `02_1_Cal_cross_specturm_specific_layter.ipynb` | `33_cross_spectrum_specific_layer.ipynb` | 特定层交叉谱分析 |
| `02_1.1_test_level-55_cross_specturm.ipynb` | `34_cross_spectrum_level55_test.ipynb` | Level-55层测试 |
| `02_1.2_cal_cs_wdhdz.ipynb` | `35_cross_spectrum_omega_dhdz.ipynb` | ω·dh/dz交叉谱 |
| `02_1.2_cal_cs_wdhdz_normalized.ipynb` | `36_cross_spectrum_omega_dhdz_normalized.ipynb` | 归一化ω·dh/dz交叉谱 |
| `05_cal_pr&olr_cross_spectrum.ipynb` | `37_cross_spectrum_pr_olr.ipynb` | 降水-OLR交叉谱 |
| `05_cal_pr_lhf_cross_spectrum.ipynb` | `38_cross_spectrum_pr_lhf.ipynb` | 降水-潜热通量交叉谱 |
| `05_cal_divergence&LHF_cross_spectrum.ipynb` | `39_cross_spectrum_div_lhf.ipynb` | 散度-LHF交叉谱 |
| `05_cal_mseverticalconvection_pr_lhf_cross_spectrum.ipynb` | `40_cross_spectrum_mse_pr_lhf.ipynb` | MSE垂直对流交叉谱 |
| `fig11_calculate_crossspectrum.ipynb` | `41_cross_spectrum_fig11_calculate.ipynb` | 图11交叉谱计算 |
| `fig11_plot_crossspectrum_clean.ipynb` | `42_cross_spectrum_fig11_plot.ipynb` | 图11交叉谱绘图 |

---

### 50系列 - 合成分析

| 旧文件名 | 新文件名 | 功能说明 |
|---------|---------|---------|
| `Cal_composite_kelvin.ipynb` | `50_composite_kelvin_phase.ipynb` | Kelvin波相位合成 |
| `Cal_composite_kelvin_hus.ipynb` | `51_composite_kelvin_humidity.ipynb` | Kelvin波比湿合成 |
| `Cal_composite_kelvin_vertical_profile.ipynb` | `52_composite_kelvin_vertical.ipynb` | Kelvin波垂直剖面合成 |
| `Cal_composite_pre_with_long.ipynb` | `53_composite_pr_longitude.ipynb` | 降水经度合成 |
| `Cal_pr_regression_composite.ipynb` | `54_composite_pr_regression.ipynb` | 降水回归合成 |
| `09_Cal_LHF_composite_with_time.ipynb` | `55_composite_lhf_time.ipynb` | LHF时间合成 |
| `09_cal_LHF_composite_with_time.ipynb` | `55_composite_lhf_time_v2.ipynb` | LHF时间合成v2 |
| `09_cal_LHF_composite_with_lon.ipynb` | `56_composite_lhf_longitude.ipynb` | LHF经度合成 |
| `Cal_LHF_composite_with_time.ipynb` | `57_composite_lhf_time_backup.ipynb` | LHF时间合成（备份） |
| `Cal_LHF_composite_with_lon.ipynb` | `58_composite_lhf_lon_backup.ipynb` | LHF经度合成（备份） |

---

### 60系列 - 散度分析

| 旧文件名 | 新文件名 | 功能说明 |
|---------|---------|---------|
| `02_0_Cal_divergence_of_wind_speed.ipynb` | `60_divergence_wind_calc.ipynb` | 风速散度计算 |
| `02_0.0_Cal_divergence_of_wind_speed.ipynb` | `61_divergence_wind_calc_v2.ipynb` | 风速散度计算v2 |
| `03_Cal_wadhdz.ipynb` | `62_divergence_omega_dhdz.ipynb` | ω·dh/dz项计算 |
| `05_Cal_div_interp_pressure_level.ipynb` | `63_divergence_interp_pressure.ipynb` | 散度插值到气压层 |
| `05_Cal_div_into_specific_pre.ipynb` | `64_divergence_specific_pressure.ipynb` | 散度插值到特定气压层 |
| `05_Plot_cross_spe_div_pre_level.ipynb` | `65_divergence_plot_cross_spectrum.ipynb` | 散度交叉谱绘图 |

---

### 70系列 - 垂直结构

| 旧文件名 | 新文件名 | 功能说明 |
|---------|---------|---------|
| `07_plot_hus_vertical_composite.ipynb` | `70_vertical_humidity_composite.ipynb` | 比湿垂直合成 |
| `07_plot_space_vertical_composite.ipynb` | `71_vertical_spatial_composite.ipynb` | 空间垂直合成 |
| `Cal_temperature_profile.ipynb` | `72_vertical_temperature_profile.ipynb` | 温度垂直剖面 |
| `Cal_temperature_height_only_cold_point.ipynb` | `73_vertical_cold_point_height.ipynb` | 冷点层高度 |

---

### 80系列 - 热力学诊断

| 旧文件名 | 新文件名 | 功能说明 |
|---------|---------|---------|
| `Cal_MSE.ipynb` | `80_thermo_mse_budget.ipynb` | 湿静力能收支 |
| `Cal_dhdt.ipynb` | `81_thermo_dhdt_term.ipynb` | dh/dt项计算 |
| `Cal_flux.ipynb` | `82_thermo_flux_calc.ipynb` | 能量通量计算 |
| `Cal_Radiation.ipynb` | `83_thermo_radiation.ipynb` | 辐射项计算 |
| `06_Cal_difference_qs_qa_allregion.ipynb` | `84_thermo_qs_qa_diff_regional.ipynb` | 饱和比湿差异（区域） |
| `Cal_difference_qs_qa.ipynb` | `85_thermo_qs_qa_diff.ipynb` | 饱和比湿差异 |
| `Cal_effective_potential_temperature.ipynb` | `86_thermo_effective_pot_temp.ipynb` | 有效位温 |
| `12_1_calculate_dqdz.ipynb` | `87_thermo_dqdz_calc.ipynb` | dq/dz计算 |
| `12_1_calculate_dry_static_stability.ipynb` | `88_thermo_dry_static_stability.ipynb` | 干静力稳定度 |

---

### 90系列 - 密度与质量

| 旧文件名 | 新文件名 | 功能说明 |
|---------|---------|---------|
| `04_Cal_full_level_of_rho.ipynb` | `90_density_full_level_rho.ipynb` | 完整层空气密度 |
| `Cal_omega_region_mean.ipynb` | `91_density_omega_regional.ipynb` | ω场区域平均 |

---

### 95系列 - 降水与蒸发

| 旧文件名 | 新文件名 | 功能说明 |
|---------|---------|---------|
| `Cal_precipitation.ipynb` | `95_precip_analysis.ipynb` | 降水分析 |
| `Cal_evaporation_minus_precipitation.ipynb` | `96_precip_evap_minus_pr.ipynb` | E-P计算 |

---

### 97系列 - 地表变量

| 旧文件名 | 新文件名 | 功能说明 |
|---------|---------|---------|
| `Cal_surface_wind_speed.ipynb` | `97_surface_wind_speed.ipynb` | 地表风速 |
| `Cal_relative_humidity_t2m.ipynb` | `98_surface_rh_t2m.ipynb` | 2米相对湿度 |
| `Cal_SST_clean.ipynb` | `99_surface_sst_clean.ipynb` | 海表温度（清洗版） |

---

### A0系列 - EOF分析

| 旧文件名 | 新文件名 | 功能说明 |
|---------|---------|---------|
| `Cal_wa_xeof.ipynb` | `A0_eof_omega_analysis.ipynb` | ω场EOF分析 |
| `wa_xeof.ipynb` | `A1_eof_omega_backup.ipynb` | ω场EOF分析（备份） |

---

### B0系列 - 时空分析

| 旧文件名 | 新文件名 | 功能说明 |
|---------|---------|---------|
| `Cal_homoller.ipynb` | `B0_spatiotemporal_hovmoller.ipynb` | Hovmöller图 |
| `Cal_with_trop_wmo_from_NCL.ipynb` | `B1_spatiotemporal_with_tropopause.ipynb` | 结合对流层顶分析 |

---

### Z0系列 - 其他分析

| 旧文件名 | 新文件名 | 功能说明 |
|---------|---------|---------|
| `Cal_different_resolution.ipynb` | `Z0_misc_resolution_comparison.ipynb` | 分辨率对比 |
| `Tas_vs_Snowcover_Albedo_NA_DJF_modify.ipynb` | `Z1_misc_tas_snow_albedo.ipynb` | 温度vs积雪反照率 |
| `tes.ipynb` | `Z9_test_playground.ipynb` | 测试脚本 |

---

## 📊 重命名统计

| 系列 | 脚本数量 | 说明 |
|------|---------|------|
| 00系列 | 5个 | 数据预处理 |
| 10系列 | 2个 | WK频谱分析 |
| 20系列 | 4个 | Kelvin波滤波 |
| 30系列 | 13个 | 交叉谱分析 |
| 50系列 | 10个 | 合成分析 |
| 60系列 | 6个 | 散度分析 |
| 70系列 | 4个 | 垂直结构 |
| 80系列 | 9个 | 热力学诊断 |
| 90系列 | 2个 | 密度质量 |
| 95系列 | 2个 | 降水蒸发 |
| 97系列 | 3个 | 地表变量 |
| A0系列 | 2个 | EOF分析 |
| B0系列 | 2个 | 时空分析 |
| Z0系列 | 3个 | 其他分析 |
| **总计** | **67个** | 重命名的notebook文件 |

**工具脚本**（未重命名）: 3个 Python 脚本

---

## 🔙 恢复方法

如需恢复到重命名前的状态：

```bash
# 查找备份目录
ls -d backup_before_rename_*

# 从备份恢复（示例）
cd backup_before_rename_20260216_104058
# 查看备份内容并手动恢复需要的文件
```

---

## ✅ 重命名优势

### 1. **系统化组织**
- 清晰的功能分类
- 连续的编号系统
- 易于查找和管理

### 2. **可读性提升**
- 文件名即说明功能
- 统一的命名规范
- 减少混淆

### 3. **维护便利**
- 便于添加新脚本
- 易于识别重复功能
- 方便版本管理

### 4. **学习友好**
- 按编号顺序学习
- 功能分类明确
- 快速定位需要的脚本

---

**重命名执行**: 2026-02-16 10:40:58  
**备份位置**: `./backup_before_rename_20260216_104058/`  
**执行脚本**: `rename_scripts.sh`
