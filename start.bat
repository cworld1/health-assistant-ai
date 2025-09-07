@echo off
chcp 65001 >nul

echo 🚀 启动 NVIDIA NeMo Agent Toolkit AI对话机器人
echo ==============================================

REM 设置环境变量
set TAVILY_API_KEY=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

REM 激活Python虚拟环境
call .venv\Scripts\activate.bat

REM 启动后端服务
echo 📡 启动后端服务...
start /b aiq serve --config_file configs\hackathon_config.yml --host 0.0.0.0 --port 8001

REM 等待后端启动
echo ⏳ 等待后端服务启动...
timeout /t 10 /nobreak >nul

REM 启动前端服务
echo 🎨 启动前端服务...
cd external\aiqtoolkit-opensource-ui
start /b npm run dev
cd ..\..

echo.
echo ✅ 系统启动完成！
echo.
echo 🌐 访问地址:
echo    前端界面: http://localhost:3000
echo    API文档:  http://localhost:8001/docs
echo.
echo 📝 测试建议:
echo    1. 天气查询: '北京今天的天气怎么样，气温是多少？'
echo    2. 公司信息: '帮我介绍一下NVIDIA Agent Intelligence Toolkit'
echo    3. 时间查询: '现在几点了？'
echo.
echo 🛑 停止服务: 按 Ctrl+C 或运行 stop.bat
echo.
pause
