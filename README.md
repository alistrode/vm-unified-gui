# 多容器统一图形工作台

长期分支：`projects/vm-unified-gui`。不读取、使用或合并仓库主分支。

当前仍为开发中版本。`source/modes/` 是在真实 `Ubuntu-MultiContainer-GUI` 中部署的容器外标准桌面模式实现；完整功能和模式二逐像素验收尚未通过，不能作为已验收交付。

## 当前容器外桌面实现

`source/modes/` 使用现有 Ubuntu/Xfce/Xpra 和原有应用容器；容器外共享一套桌面依赖。模式一以多个完整桌面的实际功能验收；在容器外运行三个独立原生 Xfce 会话，各自拥有工作区、面板、窗口管理与配置，共用一套已安装依赖。模式二回到 1280×800 单桌面，参考仅为 `docs/original/final.png`。详细依赖、安装影响及未通过项见该目录 README。安装脚本仅面向既有项目，不是独立运行包。

## 历史增量实现

- `source/workbench.html`：统一窗口与分块监控的控制界面；`?design=1` 是明确标识的设计预览，不执行远端操作。
- `source/workbench_server.py`：Python 标准库实现的回环 API，采样 Ubuntu 宿主和应用容器状态，以固定白名单启动应用。
- `source/host/Start-Workbench.ps1`、`START.cmd`：Windows 一键启动入口草稿，复用既有 VirtualBox 与项目 VM，检查硬件余量并等待 HTTP 就绪。已通过 PowerShell 语法检查；尚未在 B 机运行验收。
- `source/display-bridge.js`：面向 Xpra HTML5 v21 的显示桥接，按容器主机元数据分组，切换布局并恢复原几何位置；尚未接入 B 机验证。
- `source/publish_python.py`：固定哈希依赖下载、离线 wheel 安装、受限容器导入验证和共享环境原子发布；导入失败保留原环境。
- `source/download_verified.py`：SHA-256 固定校验、已有文件复用、持续低于 800 KiB/s 的下载源切换。

设计稿与局部浏览器验证在 `docs/design/`，验收清单在 `docs/acceptance.json`。`tests/` 是验证代码，不属于应用实现；第三方运行环境不冒称自有源码。

## 开发模式

Python 3.10+：`python source/workbench_server.py --port 8090 --display-port 14500`。接口绑定 `127.0.0.1`；正式部署需要接入既有 Nginx/Xpra 显示服务并核对其实际端口。无需编译或安装 Python 第三方库。

在开发机运行 `python -m unittest discover -s tests -v`。这些检查覆盖接口边界、启动命令白名单、下载换源与缓存保护，不能替代真实虚拟机验收。

## 已核实的项目位置

- A 机 `LAPTOP-MCMQHDN4`：项目管理器保留 `E:\VM-Unified-GUI` 历史登记；实查目录不存在。
- B 机 `oKGTBFPZVQwi`：既有工程 `E:\VM-Unified-GUI`，原应用实现与维护资料在其 `source` 子目录；原 VM 名称 `Ubuntu-MultiContainer-GUI`。
- 既有部署文档登记 Ubuntu `/srv/unified` 和容器 `unified-a/b/c`。本轮最初实查 VM 为关机状态，CPU 1、内存 8192 MiB；本轮已启动，仅在此 VM 内修改和验证，保持运行。

Windows VM、Ubuntu、Docker、Xpra 及原应用镜像是外部运行依赖。完整交付前须从 B 机取回版本与校验信息，整合原工程、备份并现场验证；当前目录不包含这些运行时，也不声称可在干净系统离线运行。

## 验证范围

本地 12 项接口、下载及发布事务测试通过，另有窗口分组与布局检查通过；Windows PowerShell 启动脚本语法解析错误为 0；历史设计预览的重复截图差异曾为 0 像素；错误的两张设计参考图已删除。以上不代表真实应用窗口、容器、共享库或 B 机启动已经通过。

项目的原连接凭据、远端私钥、原始日志和真实会话资料不进入本分支。

## 2026-10-27 实机截图与源码下载

- [源码部署包](release/Ubuntu-MultiContainer-GUI-source-20261027.zip)：依赖现有 Ubuntu VM、容器镜像和外部运行环境，不是完整独立运行包。
- [模式一统一入口最近一次实测截图（未通过）](docs/runtime/mode1-browser-unverified.png)：三个独立原生桌面进程已启动并验证部分功能；浏览器实测仅 A 显示，B/C 连接失败，未完成统一入口验收。
- [模式二原生实机截图](docs/runtime/mode2-live.webp)：1280×800，三个容器应用窗口。与原参考图全像素比较有 25,831 个不同像素（2.5226%），未通过完全一致验收。

只修改指定的 Ubuntu-MultiContainer-GUI VM；保持运行。连接凭据、认证文件、运行日志和虚拟磁盘不包含在源码包中。
