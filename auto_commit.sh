#!/bin/bash
# 自动提交修改和新增脚本

# 完成 merge（如果 merge 正在进行）
if git status | grep -q "All conflicts fixed but you are still merging"; then
    git commit -m "Merge remote changes"
fi

# 添加修改和新增脚本
git add -u
git add *.py *.ipynb

# 检查是否有要提交的内容
if git diff --cached --quiet; then
    echo "No changes to commit."
else
    git commit -m "Auto update scripts"
    git push
fi
