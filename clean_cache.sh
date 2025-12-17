#!/bin/bash
# 清理缓存脚本 - 释放磁盘空间和内存

echo "========================================================================"
echo "缓存清理脚本"
echo "========================================================================"

# 检查当前缓存大小
echo ""
echo "当前缓存大小："
du -sh cache/ dask-worker-space/ dask-scratch-space/ 2>/dev/null

echo ""
echo "清理选项："
echo "1. 清理 Dask 临时文件（推荐，安全）"
echo "2. 清理所有缓存（谨慎！会删除计算结果）"
echo "3. 仅显示大小，不清理"
echo ""
read -p "请选择 (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "清理 Dask 临时文件..."
        rm -rf dask-worker-space/* dask-scratch-space/*
        echo "✓ 完成"
        ;;
    2)
        echo ""
        read -p "⚠️  确定要删除所有缓存吗？(yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo "清理所有缓存..."
            rm -rf cache/* dask-worker-space/* dask-scratch-space/*
            echo "✓ 完成"
        else
            echo "✗ 已取消"
        fi
        ;;
    3)
        echo "✓ 不执行清理操作"
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "清理后缓存大小："
du -sh cache/ dask-worker-space/ dask-scratch-space/ 2>/dev/null

echo ""
echo "========================================================================"
echo "建议：重启 Jupyter kernel 以释放内存"
echo "========================================================================"
