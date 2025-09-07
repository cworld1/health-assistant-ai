@echo off
chcp 65001 >nul

echo 🛑 停止 NVIDIA NeMo Agent Toolkit AI对话机器人
echo ==============================================

REM 停止相关进程
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul

echo ✅ 所有服务已停止
pause
