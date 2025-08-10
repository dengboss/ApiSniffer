API接口抓包工具 说明文档
==========================

【简介】
本工具基于 mitmdump 和 PyQt5，支持移动应用/网页应用接口数据抓取、过滤、导出等功能，适用于 Windows 平台，无需安装 Python 和 mitmproxy。

【环境要求】
- Windows 10/11
- 无需安装 Python（如果使用 main.exe）
- 无需安装 mitmproxy（使用独立版本）

【快速开始】
方式一：使用独立可执行文件（推荐）
1. 下载完整的发布包
2. 双击 main.exe 启动程序

方式二：从源码运行
1. 确保已安装 Python 3.8+
2. 运行自动配置脚本：python setup_mitmproxy.py
3. 启动程序：python main.py

【文件说明】
- main.exe           —— 主程序，双击运行
- mitmdump.exe       —— 抓包核心引擎，必须与 main.exe 同目录
- mitm_writer.py     —— 抓包数据处理脚本，必须与 main.exe 同目录
- captured_data.json —— 抓包数据文件，自动生成
- setup_mitmproxy.py —— 自动配置脚本（仅源码运行时需要）

【使用步骤】
1. 解压所有文件到同一文件夹。
2. 双击 main.exe 启动程序。
3. 点击"开始监听"，根据提示设置手机/被抓包设备的代理：
   - 代理服务器IP：本机局域网IP（如 192.168.1.100）
   - 端口：8080
4. 在被抓包设备浏览器访问 http://mitm.it，选择对应平台下载并安装证书，并信任该证书。
5. 在被抓包设备上操作应用程序，数据会自动显示在主界面。
6. 可通过"只监听域名"输入框过滤指定域名流量。
7. 支持右键复制表格内容、导出Excel、清除数据等功能。

【常见问题】
1. 启动后抓不到数据？
   - 检查代理设置是否正确，手机和电脑需在同一局域网。
   - 检查 Windows 防火墙是否放行 8080 端口。
   - 确认 mitmdump.exe 与 main.exe 在同一目录。
2. HTTPS 抓包失败？
   - 必须在被抓包设备安装并信任 mitmproxy 证书（http://mitm.it）。
3. 导出Excel失败？
   - 请确保 main.exe 目录下有写入权限。
4. 清除数据后历史数据又出现？
   - 请升级到最新版本，已修复此问题。
5. 运行报错"缺少 mitmdump.exe"？
   - 请将 mitmdump.exe 放在 main.exe 同一目录。
   - 或运行 python setup_mitmproxy.py 自动下载配置。
6. 点击"开始监听"没有反应？
   - 检查 mitmdump.exe 是否为独立版本（不依赖系统Python）
   - 运行 mitmdump.exe --version 测试是否正常
   - 如有问题，请重新下载独立版本的 mitmproxy

【技术说明】
- 本工具使用独立版本的 mitmproxy，不依赖系统 Python 环境
- mitmdump.exe 包含完整的 Python 运行时和所有依赖
- 首次启动可能较慢，因为需要解压临时文件

【联系方式】
如有问题或建议，请联系开发者。