#!/bin/bash
# 脚本文件系统化重命名方案
# 作者: Jianpu
# 日期: 2026-02-16

# ============================================
# 重命名方案说明
# ============================================
# 格式: XX_功能简称_具体描述.ipynb
# XX: 两位数字编号，表示分析流程顺序
# 功能简称: 使用统一的简写
# 具体描述: 详细功能说明（使用小写+下划线）
# ============================================

echo "开始重命名脚本文件..."
echo "================================================"

# 创建备份目录
BACKUP_DIR="./backup_before_rename_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "✓ 创建备份目录: $BACKUP_DIR"

# ============================================
# 00系列: 数据预处理 (Data Preprocessing)
# ============================================
echo ""
echo "【00系列】数据预处理..."

# Python脚本保持原名（这些是工具脚本）
# process_3d_data_optimized.py
# process_sea_land_mask.py
# wave_filter.py

mv "Python_Only_data_preprocess.ipynb" "00_preprocess_python_only.ipynb" 2>/dev/null && echo "✓ 00_preprocess_python_only.ipynb"
mv "Python_merge_3D.ipynb" "00_preprocess_merge_3d.ipynb" 2>/dev/null && echo "✓ 00_preprocess_merge_3d.ipynb"
mv "Data_preprocess_for_uw_wind.ipynb" "00_preprocess_wind_field.ipynb" 2>/dev/null && echo "✓ 00_preprocess_wind_field.ipynb"
mv "Data_preprocess_for_30_lattitude.ipynb" "00_preprocess_lat30_region.ipynb" 2>/dev/null && echo "✓ 00_preprocess_lat30_region.ipynb"
# NCL脚本
mv "01_trop_wmo_ICON.ncl" "00_preprocess_tropopause_wmo.ncl" 2>/dev/null && echo "✓ 00_preprocess_tropopause_wmo.ncl"

# ============================================
# 10系列: Wheeler-Kiladis频谱分析
# ============================================
echo ""
echo "【10系列】WK频谱分析..."

mv "01_Cal_wk_kelvin.ipynb" "10_spectrum_wk_analysis.ipynb" 2>/dev/null && echo "✓ 10_spectrum_wk_analysis.ipynb"
mv "Cal_spectrum_year_by_year.ipynb" "11_spectrum_yearly_analysis.ipynb" 2>/dev/null && echo "✓ 11_spectrum_yearly_analysis.ipynb"

# ============================================
# 20系列: Kelvin波提取与滤波
# ============================================
echo ""
echo "【20系列】Kelvin波滤波..."

mv "Cal_cckw_filter_3d_fields.ipynb" "20_filter_kelvin_3d_fields.ipynb" 2>/dev/null && echo "✓ 20_filter_kelvin_3d_fields.ipynb"
mv "Cal_cckw_filter_for_hus.ipynb" "21_filter_kelvin_humidity.ipynb" 2>/dev/null && echo "✓ 21_filter_kelvin_humidity.ipynb"
mv "Cal_cckw_std_distribution.ipynb" "22_filter_kelvin_std_dist.ipynb" 2>/dev/null && echo "✓ 22_filter_kelvin_std_dist.ipynb"
mv "Cal_+4K_data_kelvin.ipynb" "23_filter_kelvin_p4k_scenario.ipynb" 2>/dev/null && echo "✓ 23_filter_kelvin_p4k_scenario.ipynb"

# ============================================
# 30系列: 交叉谱分析
# ============================================
echo ""
echo "【30系列】交叉谱分析..."

mv "Cal_cross_specturm.ipynb" "30_cross_spectrum_basic.ipynb" 2>/dev/null && echo "✓ 30_cross_spectrum_basic.ipynb"
mv "Cal_cross_specturm_with_51.ipynb" "31_cross_spectrum_level51.ipynb" 2>/dev/null && echo "✓ 31_cross_spectrum_level51.ipynb"
mv "Cal_cross_specturm_with_pywk99.ipynb" "32_cross_spectrum_pywk99.ipynb" 2>/dev/null && echo "✓ 32_cross_spectrum_pywk99.ipynb"
mv "02_1_Cal_cross_specturm_specific_layter.ipynb" "33_cross_spectrum_specific_layer.ipynb" 2>/dev/null && echo "✓ 33_cross_spectrum_specific_layer.ipynb"
mv "02_1.1_test_level-55_cross_specturm.ipynb" "34_cross_spectrum_level55_test.ipynb" 2>/dev/null && echo "✓ 34_cross_spectrum_level55_test.ipynb"
mv "02_1.2_cal_cs_wdhdz.ipynb" "35_cross_spectrum_omega_dhdz.ipynb" 2>/dev/null && echo "✓ 35_cross_spectrum_omega_dhdz.ipynb"
mv "02_1.2_cal_cs_wdhdz_normalized.ipynb" "36_cross_spectrum_omega_dhdz_normalized.ipynb" 2>/dev/null && echo "✓ 36_cross_spectrum_omega_dhdz_normalized.ipynb"
mv "05_cal_pr&olr_cross_spectrum.ipynb" "37_cross_spectrum_pr_olr.ipynb" 2>/dev/null && echo "✓ 37_cross_spectrum_pr_olr.ipynb"
mv "05_cal_pr_lhf_cross_spectrum.ipynb" "38_cross_spectrum_pr_lhf.ipynb" 2>/dev/null && echo "✓ 38_cross_spectrum_pr_lhf.ipynb"
mv "05_cal_divergence&LHF_cross_spectrum.ipynb" "39_cross_spectrum_div_lhf.ipynb" 2>/dev/null && echo "✓ 39_cross_spectrum_div_lhf.ipynb"
mv "05_cal_mseverticalconvection_pr_lhf_cross_spectrum.ipynb" "40_cross_spectrum_mse_pr_lhf.ipynb" 2>/dev/null && echo "✓ 40_cross_spectrum_mse_pr_lhf.ipynb"
mv "fig11_calculate_crossspectrum.ipynb" "41_cross_spectrum_fig11_calculate.ipynb" 2>/dev/null && echo "✓ 41_cross_spectrum_fig11_calculate.ipynb"
mv "fig11_plot_crossspectrum_clean.ipynb" "42_cross_spectrum_fig11_plot.ipynb" 2>/dev/null && echo "✓ 42_cross_spectrum_fig11_plot.ipynb"

# ============================================
# 50系列: 合成分析
# ============================================
echo ""
echo "【50系列】合成分析..."

mv "Cal_composite_kelvin.ipynb" "50_composite_kelvin_phase.ipynb" 2>/dev/null && echo "✓ 50_composite_kelvin_phase.ipynb"
mv "Cal_composite_kelvin_hus.ipynb" "51_composite_kelvin_humidity.ipynb" 2>/dev/null && echo "✓ 51_composite_kelvin_humidity.ipynb"
mv "Cal_composite_kelvin_vertical_profile.ipynb" "52_composite_kelvin_vertical.ipynb" 2>/dev/null && echo "✓ 52_composite_kelvin_vertical.ipynb"
mv "Cal_composite_pre_with_long.ipynb" "53_composite_pr_longitude.ipynb" 2>/dev/null && echo "✓ 53_composite_pr_longitude.ipynb"
mv "Cal_pr_regression_composite.ipynb" "54_composite_pr_regression.ipynb" 2>/dev/null && echo "✓ 54_composite_pr_regression.ipynb"
mv "09_Cal_LHF_composite_with_time.ipynb" "55_composite_lhf_time.ipynb" 2>/dev/null && echo "✓ 55_composite_lhf_time.ipynb"
mv "09_cal_LHF_composite_with_time.ipynb" "55_composite_lhf_time_v2.ipynb" 2>/dev/null && echo "✓ 55_composite_lhf_time_v2.ipynb"
mv "09_cal_LHF_composite_with_lon.ipynb" "56_composite_lhf_longitude.ipynb" 2>/dev/null && echo "✓ 56_composite_lhf_longitude.ipynb"
mv "Cal_LHF_composite_with_time.ipynb" "57_composite_lhf_time_backup.ipynb" 2>/dev/null && echo "✓ 57_composite_lhf_time_backup.ipynb"
mv "Cal_LHF_composite_with_lon.ipynb" "58_composite_lhf_lon_backup.ipynb" 2>/dev/null && echo "✓ 58_composite_lhf_lon_backup.ipynb"

# ============================================
# 60系列: 散度与垂直运动
# ============================================
echo ""
echo "【60系列】散度分析..."

mv "02_0_Cal_divergence_of_wind_speed.ipynb" "60_divergence_wind_calc.ipynb" 2>/dev/null && echo "✓ 60_divergence_wind_calc.ipynb"
mv "02_0.0_Cal_divergence_of_wind_speed.ipynb" "61_divergence_wind_calc_v2.ipynb" 2>/dev/null && echo "✓ 61_divergence_wind_calc_v2.ipynb"
mv "03_Cal_wadhdz.ipynb" "62_divergence_omega_dhdz.ipynb" 2>/dev/null && echo "✓ 62_divergence_omega_dhdz.ipynb"
mv "05_Cal_div_interp_pressure_level.ipynb" "63_divergence_interp_pressure.ipynb" 2>/dev/null && echo "✓ 63_divergence_interp_pressure.ipynb"
mv "05_Cal_div_into_specific_pre.ipynb" "64_divergence_specific_pressure.ipynb" 2>/dev/null && echo "✓ 64_divergence_specific_pressure.ipynb"
mv "05_Plot_cross_spe_div_pre_level.ipynb" "65_divergence_plot_cross_spectrum.ipynb" 2>/dev/null && echo "✓ 65_divergence_plot_cross_spectrum.ipynb"

# ============================================
# 70系列: 垂直结构分析
# ============================================
echo ""
echo "【70系列】垂直结构..."

mv "07_plot_hus_vertical_composite.ipynb" "70_vertical_humidity_composite.ipynb" 2>/dev/null && echo "✓ 70_vertical_humidity_composite.ipynb"
mv "07_plot_space_vertical_composite.ipynb" "71_vertical_spatial_composite.ipynb" 2>/dev/null && echo "✓ 71_vertical_spatial_composite.ipynb"
mv "Cal_temperature_profile.ipynb" "72_vertical_temperature_profile.ipynb" 2>/dev/null && echo "✓ 72_vertical_temperature_profile.ipynb"
mv "Cal_temperature_height_only_cold_point.ipynb" "73_vertical_cold_point_height.ipynb" 2>/dev/null && echo "✓ 73_vertical_cold_point_height.ipynb"

# ============================================
# 80系列: 热力学诊断
# ============================================
echo ""
echo "【80系列】热力学诊断..."

mv "Cal_MSE.ipynb" "80_thermo_mse_budget.ipynb" 2>/dev/null && echo "✓ 80_thermo_mse_budget.ipynb"
mv "Cal_dhdt.ipynb" "81_thermo_dhdt_term.ipynb" 2>/dev/null && echo "✓ 81_thermo_dhdt_term.ipynb"
mv "Cal_flux.ipynb" "82_thermo_flux_calc.ipynb" 2>/dev/null && echo "✓ 82_thermo_flux_calc.ipynb"
mv "Cal_Radiation.ipynb" "83_thermo_radiation.ipynb" 2>/dev/null && echo "✓ 83_thermo_radiation.ipynb"
mv "06_Cal_difference_qs_qa_allregion.ipynb" "84_thermo_qs_qa_diff_regional.ipynb" 2>/dev/null && echo "✓ 84_thermo_qs_qa_diff_regional.ipynb"
mv "Cal_difference_qs_qa.ipynb" "85_thermo_qs_qa_diff.ipynb" 2>/dev/null && echo "✓ 85_thermo_qs_qa_diff.ipynb"
mv "Cal_effective_potential_temperature.ipynb" "86_thermo_effective_pot_temp.ipynb" 2>/dev/null && echo "✓ 86_thermo_effective_pot_temp.ipynb"
mv "12_1_calculate_dqdz.ipynb" "87_thermo_dqdz_calc.ipynb" 2>/dev/null && echo "✓ 87_thermo_dqdz_calc.ipynb"
mv "12_1_calculate_dry_static_stability.ipynb" "88_thermo_dry_static_stability.ipynb" 2>/dev/null && echo "✓ 88_thermo_dry_static_stability.ipynb"

# ============================================
# 90系列: 大气密度与质量
# ============================================
echo ""
echo "【90系列】密度与质量..."

mv "04_Cal_full_level_of_rho.ipynb" "90_density_full_level_rho.ipynb" 2>/dev/null && echo "✓ 90_density_full_level_rho.ipynb"
mv "Cal_omega_region_mean.ipynb" "91_density_omega_regional.ipynb" 2>/dev/null && echo "✓ 91_density_omega_regional.ipynb"

# ============================================
# 95系列: 降水与蒸发
# ============================================
echo ""
echo "【95系列】降水与蒸发..."

mv "Cal_precipitation.ipynb" "95_precip_analysis.ipynb" 2>/dev/null && echo "✓ 95_precip_analysis.ipynb"
mv "Cal_evaporation_minus_precipitation.ipynb" "96_precip_evap_minus_pr.ipynb" 2>/dev/null && echo "✓ 96_precip_evap_minus_pr.ipynb"

# ============================================
# 97系列: 地表变量
# ============================================
echo ""
echo "【97系列】地表变量..."

mv "Cal_surface_wind_speed.ipynb" "97_surface_wind_speed.ipynb" 2>/dev/null && echo "✓ 97_surface_wind_speed.ipynb"
mv "Cal_relative_humidity_t2m.ipynb" "98_surface_rh_t2m.ipynb" 2>/dev/null && echo "✓ 98_surface_rh_t2m.ipynb"
mv "Cal_SST_clean.ipynb" "99_surface_sst_clean.ipynb" 2>/dev/null && echo "✓ 99_surface_sst_clean.ipynb"

# ============================================
# A0系列: EOF分析
# ============================================
echo ""
echo "【A0系列】EOF分析..."

mv "Cal_wa_xeof.ipynb" "A0_eof_omega_analysis.ipynb" 2>/dev/null && echo "✓ A0_eof_omega_analysis.ipynb"
mv "wa_xeof.ipynb" "A1_eof_omega_backup.ipynb" 2>/dev/null && echo "✓ A1_eof_omega_backup.ipynb"

# ============================================
# B0系列: 时空分析
# ============================================
echo ""
echo "【B0系列】时空分析..."

mv "Cal_homoller.ipynb" "B0_spatiotemporal_hovmoller.ipynb" 2>/dev/null && echo "✓ B0_spatiotemporal_hovmoller.ipynb"
mv "Cal_with_trop_wmo_from_NCL.ipynb" "B1_spatiotemporal_with_tropopause.ipynb" 2>/dev/null && echo "✓ B1_spatiotemporal_with_tropopause.ipynb"

# ============================================
# Z0系列: 其他分析
# ============================================
echo ""
echo "【Z0系列】其他分析..."

mv "Cal_different_resolution.ipynb" "Z0_misc_resolution_comparison.ipynb" 2>/dev/null && echo "✓ Z0_misc_resolution_comparison.ipynb"
mv "Tas_vs_Snowcover_Albedo_NA_DJF_modify.ipynb" "Z1_misc_tas_snow_albedo.ipynb" 2>/dev/null && echo "✓ Z1_misc_tas_snow_albedo.ipynb"
mv "tes.ipynb" "Z9_test_playground.ipynb" 2>/dev/null && echo "✓ Z9_test_playground.ipynb"

# ============================================
# 完成
# ============================================
echo ""
echo "================================================"
echo "✓ 重命名完成！"
echo ""
echo "重命名规则:"
echo "  00系列 - 数据预处理"
echo "  10系列 - WK频谱分析"
echo "  20系列 - Kelvin波滤波"
echo "  30系列 - 交叉谱分析"
echo "  50系列 - 合成分析"
echo "  60系列 - 散度分析"
echo "  70系列 - 垂直结构"
echo "  80系列 - 热力学诊断"
echo "  90系列 - 密度质量"
echo "  95系列 - 降水蒸发"
echo "  97系列 - 地表变量"
echo "  A0系列 - EOF分析"
echo "  B0系列 - 时空分析"
echo "  Z0系列 - 其他分析"
echo ""
echo "如需恢复，请使用备份目录中的文件"
