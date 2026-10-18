# 多容器统一图形工作台

长期分支：`projects/vm-unified-gui`。不读取、使用或合并仓库主分支。

当前为开发中的增量实现，尚未完成旧工程源码整合和 B 机部署，不是已验收的完整交付版本。

## 已保存的实现

- `source/workbench.html`：统一窗口与分块监控的控制界面；`?design=1` 是明确标识的设计预览，不执行远端操作。
- `source/workbench_server.py`：Python 标准库实现的回环 API，采样 Ubuntu 宿主和应用容器状态，以固定白名单启动应用。
- `source/host/Start-Workbench.ps1`、`START.cmd`：Windows 一键启动入口草稿，复用既有 VirtualBox 与项目 VM，检查硬件余量并等待 HTTP 就绪。已通过 PowerShell 语法检查；尚未在 B 机运行验收。
- `source/download_verified.py`：SHA-256 固定校验、已有文件复用、持续低于 800 KiB/s 的下载源切换。

设计稿与局部浏览器验证在 `docs/design/`，验收清单在 `docs/acceptance.json`。`tests/` 是验证代码，不属于应用实现；第三方运行环境不冒称自有源码。

## 开发模式

Python 3.10+：`python source/workbench_server.py --port 8090 --display-port 14500`。接口绑定 `127.0.0.1`；正式部署需要接入既有 Nginx/Xpra 显示服务并核对其实际端口。无需编译或安装 Python 第三方库。

在开发机运行 `python -m unittest discover -s tests -v`。这些检查覆盖接口边界、启动命令白名单、下载换源与缓存保护，不能替代真实虚拟机验收。

## 已核实的项目位置

- A 机 `LAPTOP-MCMQHDN4`：项目管理器保留 `E:\VM-Unified-GUI` 历史登记；实查目录不存在。
- B 机 `oKGTBFPZVQwi`：既有工程 `E:\VM-Unified-GUI`，原应用实现与维护资料在其 `source` 子目录；原 VM 名称 `Ubuntu-MultiContainer-GUI`。
- 既有部署文档登记 Ubuntu `/srv/unified` 和容器 `unified-a/b/c`。本轮最初实查 VM 为关机状态，CPU 1、内存 8192 MiB；当前尚未重新启动验收。

Windows VM、Ubuntu、Docker、Xpra 及原应用镜像是外部运行依赖。完整交付前须从 B 机取回版本与校验信息，整合原工程、备份并现场验证；当前目录不包含这些运行时，也不声称可在干净系统离线运行。

## 验证范围

本地 9 项接口及下载测试通过；Windows PowerShell 启动脚本语法解析错误为 0；设计预览两种布局与各自参考图的重复截图差异为 0 像素。以上不代表真实应用窗口、容器、共享库或 B 机启动已经通过。

项目的原连接凭据、远端私钥、原始日志和真实会话资料不进入本分支。
