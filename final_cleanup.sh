#!/bin/bash

echo "=== 最终清理脚本 ==="
echo "当前目录: $(pwd)"
echo ""

# 切换到干净仓库目录
cd /home/administrator/ragflow-plus-clean

echo "1. 检查新仓库大小..."
du -sh .

echo ""
echo "2. 添加所有文件到 Git..."
git add .

echo ""
echo "3. 提交更改..."
git commit -m "初始提交：干净的源代码仓库"

echo ""
echo "4. 添加远程仓库..."
git remote add origin  https://github.com/yang123hao/Ragflow-plus.git

echo ""
echo "5. 推送到远程仓库..."
git push -u origin main --force

echo ""
echo "=== 清理完成！ ==="
echo "新仓库已创建并推送到远程！"
echo ""
echo "原仓库备份位置: /home/administrator/ragflow-plus-backup"
echo "新干净仓库位置: /home/administrator/ragflow-plus-clean"
