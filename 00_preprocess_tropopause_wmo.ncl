;================================================================
; compute_ptop_icon.ncl
; 计算 WMO thermal tropopause pressure (Pa) from ICON outputs
; 路径已设为 /work/mh1498/m301257/
; 假定变量名：ta, pfull
;================================================================

begin
  ; -------------------------
  ; 用户需要确认 / 可修改的地方
  ; -------------------------
  base_path = "/work/mh1498/m301257/"

  ; 文件路径（根据你的结构）
  ta_files = (/"ta_cntl_layers/ta_all_levels.nc", "ta_p4k_layers/ta_all_levels.nc", "ta_4co2_layers/ta_all_levels.nc"/)
  pfull_files = (/"pfull_cntl_layers/pfull_all_levels.nc", "pfull_p4k_layers/pfull_all_levels.nc", "pfull_4co2_layers/pfull_all_levels.nc"/)
  exp_names = (/"CNTL", "P4K", "4CO2"/)

  ; 假定变量名，若文件里变量名不同请改这里
  ta_varname = "ta"
  pfull_varname = "pfull"

  ; -------------------------
  ; 循环处理三个实验
  ; -------------------------
  ncase = dimsizes(ta_files)
  do i = 0, ncase-1
    ta_path = base_path + ta_files(i)
    pfull_path = base_path + pfull_files(i)
    print("===============================================")
    print("Processing experiment: " + exp_names(i))
    print("TA file: " + ta_path)
    print("PFULL file: " + pfull_path)
    print("===============================================")

    ; 打开文件
    f_ta = addfile(ta_path, "r")
    f_p  = addfile(pfull_path, "r")

    ta = f_ta->$ta_varname$   ; 变量可能的维度: (time, level, lat, lon) 或 (level, time, lat, lon)
    pfull = f_p->$pfull_varname$
    time = f_ta->time
    lat  = f_ta->lat
    lon  = f_ta->lon
    ntime = dimsizes(time)
    nlat  = dimsizes(lat)
    nlon  = dimsizes(lon)
    ; 打印变量摘要
    ; print("Before any transpose:")
    ; printVarSummary(ta)
    ; printVarSummary(pfull)

    ; -------------------------
    ; 确保两个数组的维度顺序一致并为 (time, level, lat, lon)
    ; -------------------------
    ; 先获取 dimsizes
    ; dims_ta = dimsizes(ta)
    ; dims_p  = dimsizes(pfull)
    ta_tran = ta(time|:, lat|:, lon|:,level|:) 
    pfull_tran = pfull(time|:, lat|:, lon|:,level|:)

    ; print("After transpose to (time, level, lat, lon):")

    ; printVarSummary(ta_tran)
    ; printVarSummary(pfull_tran)
    opt = True
    opt@lapsec = 1.0
    ptop = trop_wmo(pfull_tran, ta_tran, 1, opt)  ; 计算热层顶压强，维度: (time, lat, lon)
    printVarSummary(ptop)

    ; -------------------------
    ; 添加元数据并写入 NetCDF
    ; -------------------------
   
    print(ptop(0,0,0))  

    outname = "ptop_" + exp_names(i) + "_processed_opt_lapsec1.0.nc"
    fout = addfile(outname, "c")
    ptop_out = ptop
    ; ptop_out!0 = "time"
    ; ptop_out!1 = "lat"
    ; ptop_out!2 = "lon"
    printVarSummary(ptop_out)
    ; ptop_out&time = time
    ; ptop_out&lat  = (ta&lat)
    ; ptop_out&lon  = (ta&lon)

    ptop_out@units = "Pa"
    ptop_out@long_name = "Thermal tropopause pressure (WMO WMO lapse-rate definition)"

    ; 写入
    fout->ptop = ptop_out
    print("Saved tropopause to: " + outname)
;     ; 清理
    delete(ta)
    delete(pfull)
    delete(ptop)
    delete(f_ta)
    delete(f_p)
    delete(fout)
    
  
  end do


end
