# 数据处理脚本使用说明

## 概述
本项目包含两个优化的数据处理脚本，用于处理ICON C5模型的气候模拟数据：

1. **process_sea_land_mask.py** - 处理2D海陆Mask静态场
2. **process_3d_data_optimized.py** - 处理3D大气变量（防崩溃版本）

---

## 1. 海陆Mask处理 (process_sea_land_mask.py)

### 功能特点
- 处理 `cell_sea_land_mask` 变量（无时间维度的2D静态场）
- 自动添加/移除临时时间维度以兼容转换函数
- 使用 `nearest` 插值方法（适合类别数据）

### 使用方法

#### 单个实验：
```python
from process_sea_land_mask import process_sea_land_mask

save_path = process_sea_land_mask(
    experiment_name="CNTL",
    dataset_key="AMIP_CNTL",
    save_dir="/path/to/save",
    grid_dict={"nside": 256, "nest": True, "minmax_lat": 36},
    target_lat=np.arange(-36, 36.1, 2.0),
    target_lon=np.arange(0, 360, 2.0),
    catalog=cat
)
```

#### 批量处理：
```python
from process_sea_land_mask import batch_process_sea_land_mask

experiments = {
    "cntl": ("CNTL", "AMIP_CNTL"),
    "4k": ("P4K", "AMIP_P4K"),
}

results = batch_process_sea_land_mask(
    experiments=experiments,
    save_dir=LAYER_DIR,
    grid_dict=grid_dict,
    target_lat=target_lat,
    target_lon=target_lon,
    catalog=cat
)
```

### 输出
- 文件格式: `cell_sea_land_mask_2deg.nc`
- 网格分辨率: 2° × 2°
- 维度: (lat: 37, lon: 180)

---

## 2. 3D变量处理 (process_3d_data_optimized.py)

### 核心优化特性

#### 🚀 防崩溃机制
1. **时间分批处理**
   - 默认每次处理2年数据 (730天)
   - 避免一次性加载14年全部数据
   - 可通过 `time_batch_size` 参数调整

2. **智能内存监控**
   - 实时监控系统内存使用率
   - 超过阈值（默认85%）自动跳过当前层
   - 避免系统内存耗尽导致崩溃

3. **自动重试机制**
   - 失败时自动重试（默认3次）
   - 区分内存错误和其他错误
   - 等待时间逐步增加

4. **增量保存**
   - 逐层计算并保存
   - 避免大量数据积压在内存
   - 支持断点续传

5. **进度记录**
   - 自动记录处理进度 (`_progress.txt`)
   - 记录失败的层级 (`_failed_levels.txt`)
   - 方便追踪和问题诊断

### 使用方法

#### 单个变量单个实验：
```python
from process_3d_data_optimized import process_3d_variable_optimized

result = process_3d_variable_optimized(
    var_name="wa",
    experiment_name="CNTL",
    dataset_key="AMIP_CNTL",
    save_dir=LAYER_DIR,
    grid_dict=grid_dict,
    target_lat=target_lat,
    target_lon=target_lon,
    catalog=cat,
    level_slice=(0, None),  # 处理所有层
    time_batch_size=730,  # 每次处理2年
    memory_threshold=85,  # 内存阈值85%
    max_retries=3,  # 最多重试3次
    skip_existing=True  # 跳过已存在的文件
)
```

#### 批量处理多个变量和实验：
```python
from process_3d_data_optimized import batch_process_3d_variables

variables_3d = ["wa", "ua", "va", "hus"]

experiments = {
    "cntl": ("CNTL", "AMIP_CNTL"),
    "4k": ("P4K", "AMIP_P4K"),
}

all_results = batch_process_3d_variables(
    var_names=variables_3d,
    experiments=experiments,
    save_dir=LAYER_DIR,
    grid_dict=grid_dict,
    target_lat=target_lat,
    target_lon=target_lon,
    catalog=cat,
    time_batch_size=730,
    memory_threshold=85,
    max_retries=3,
    skip_existing=True
)
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `var_name` | str | - | 变量名 (wa, ua, va, hus, etc.) |
| `experiment_name` | str | - | 实验名称 (CNTL, P4K, 4CO2) |
| `dataset_key` | str | - | Catalog中的数据集键名 |
| `level_slice` | tuple | (0, None) | 层级范围 (start, end) |
| `time_batch_size` | int | 730 | 时间批次大小（天）<br>- 730天 = 2年<br>- 365天 = 1年<br>- 根据内存调整 |
| `memory_threshold` | float | 85 | 内存阈值（%）<br>- 超过此值跳过当前层<br>- 建议: 80-90 |
| `max_retries` | int | 3 | 最大重试次数<br>- 建议: 2-5 |
| `skip_existing` | bool | True | 是否跳过已存在文件 |

### 输出文件

#### 文件结构
```
processed_data_lat_30/
├── 2d_layers/
│   └── mask_cntl/
│       └── cell_sea_land_mask_2deg.nc
└── 3d_layers/
    ├── wa_cntl_layers/
    │   ├── wa_lev_014.nc
    │   ├── wa_lev_015.nc
    │   ├── ...
    │   ├── wa_lev_090.nc
    │   ├── _progress.txt          # 进度记录
    │   └── _failed_levels.txt     # 失败层级（如有）
    └── wa_p4k_layers/
        └── ...
```

#### 单个文件信息
- 文件名: `{var_name}_lev_{level:03d}.nc`
- 维度: (time: ~5114, lat: 37, lon: 180)
- 文件大小: ~260 MB/层
- 数据类型: float32

### 性能参考

基于实际测试（wa变量，CNTL实验）：
- **总层数**: 26层
- **总时间步**: 5114天（~14年）
- **单层处理时间**: ~5.4分钟/层
- **总处理时间**: ~141分钟（~2.4小时）
- **总数据量**: ~6.6 GB
- **内存使用**: 峰值 ~14 GB

### 故障排查

#### 1. 内存不足
**问题**: 提示内存使用率过高
**解决方案**:
- 减小 `time_batch_size`（如改为365天）
- 提高 `memory_threshold`（如改为90）
- 关闭其他占内存的程序
- 使用更少的并行worker

#### 2. 处理失败
**问题**: 某些层处理失败
**解决方案**:
- 检查 `_failed_levels.txt` 查看失败层级
- 增加 `max_retries` 次数
- 手动处理失败的层级
- 检查磁盘空间是否充足

#### 3. 网络超时
**问题**: 数据加载超时
**解决方案**:
- 检查网络连接
- 增加Dask超时设置
- 重新运行（会自动跳过已完成的层）

#### 4. 磁盘空间不足
**问题**: 写入文件失败
**解决方案**:
- 检查磁盘空间: `df -h`
- 清理不需要的中间文件
- 选择处理部分层级: `level_slice=(0, 10)`

---

## 3. 最佳实践

### 内存管理
```python
# 1. 配置Dask
import dask
dask.config.set({
    'array.slicing.split_large_chunks': True,
    'distributed.worker.memory.target': 0.95,
    'distributed.worker.memory.spill': 0.90,
    'array.chunk-size': '128MiB'
})

# 2. 定期检查内存
from process_3d_data_optimized import print_memory_status
print_memory_status("当前状态")

# 3. 手动触发垃圾回收
import gc
gc.collect()
```

### 批量处理建议
1. **先测试单个变量单个实验**，确保参数合适
2. **使用较小的时间批次**（365-730天）
3. **启用 `skip_existing=True`**，支持断点续传
4. **定期检查进度文件**，监控处理状态
5. **预留足够磁盘空间**（每个变量每个实验约7GB）

### 性能优化
- **time_batch_size**: 根据内存大小调整
  - 256GB内存: 730-1095天
  - 128GB内存: 365-730天
  - 64GB内存: 365天或更少
  
- **level_slice**: 分批处理层级
  - 高层大气: `(0, 30)`
  - 中层大气: `(30, 60)`
  - 低层大气: `(60, None)`

---

## 4. 示例工作流

### 完整处理流程

```python
import intake
import numpy as np
import os

# 1. 初始化
cat = intake.open_catalog("https://data.nextgems-h2020.eu/catalog.yaml")
DATA_DIR = "/work/mh1498/m301257/processed_data_lat_30"
LAYER_DIR = os.path.join(DATA_DIR, "3d_layers")
os.makedirs(LAYER_DIR, exist_ok=True)

# 2. 设置参数
grid_dict = {"nside": 256, "nest": True, "minmax_lat": 36}
target_lat = np.arange(-36, 36.1, 2.0)
target_lon = np.arange(0, 360, 2.0)

experiments = {
    "cntl": ("CNTL", "AMIP_CNTL"),
    "4k": ("P4K", "AMIP_P4K"),
}

# 3. 处理海陆Mask
from process_sea_land_mask import batch_process_sea_land_mask
mask_results = batch_process_sea_land_mask(
    experiments=experiments,
    save_dir=os.path.join(DATA_DIR, "2d_layers"),
    grid_dict=grid_dict,
    target_lat=target_lat,
    target_lon=target_lon,
    catalog=cat
)

# 4. 处理3D变量
from process_3d_data_optimized import batch_process_3d_variables
variables_3d = ["wa"]  # 可扩展: ["wa", "ua", "va", "hus"]

results_3d = batch_process_3d_variables(
    var_names=variables_3d,
    experiments=experiments,
    save_dir=LAYER_DIR,
    grid_dict=grid_dict,
    target_lat=target_lat,
    target_lon=target_lon,
    catalog=cat,
    time_batch_size=730,
    memory_threshold=85,
    max_retries=3,
    skip_existing=True
)

print("🎉 所有处理完成！")
```

---

## 5. 常见问题 (FAQ)

**Q: 为什么要分批处理时间维度？**
A: 14年数据（~5000天）一次性加载会占用大量内存，分批处理可以有效控制内存使用。

**Q: 处理中断了怎么办？**
A: 设置 `skip_existing=True`，重新运行脚本会自动跳过已完成的层，从中断处继续。

**Q: 如何知道哪些层处理失败了？**
A: 查看输出目录下的 `_failed_levels.txt` 文件。

**Q: 可以同时处理多个变量吗？**
A: 可以，但建议根据内存情况逐个或分批处理，避免内存不足。

**Q: 如何减少处理时间？**
A: 可以增大 `time_batch_size`（如果内存充足），或者并行运行多个脚本处理不同变量。

**Q: 数据质量如何验证？**
A: 脚本会自动打印每层的数据信息，也可以手动打开生成的NetCDF文件检查。

---

## 6. 联系与支持

如有问题或建议，请：
1. 检查 `_progress.txt` 和 `_failed_levels.txt`
2. 查看完整的错误堆栈信息
3. 调整参数后重试

---

**最后更新**: 2026-02-11
**版本**: 1.0
