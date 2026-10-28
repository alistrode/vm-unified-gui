# B 机适配快照上传交接

2026-10-28：B 机 oKGTBFPZVQwi 已通过 5.6 连接并认证；仅只读访问 E:\VM-Unified-GUI 和既有 Ubuntu-MultiContainer-GUI。未更改远端代码、配置、服务、容器或 VM 电源状态。

从目标 VM 读取 14 项模式文件、实际网页、nginx 和 9 项服务/覆盖配置，25 项内容均与仓库部署快照一致。当前 source/modes 同步实际文件，包括快捷键配置。

删除旧 source/workbench_server.py、workbench.html、display-bridge.js、download_verified.py、publish_python.py、source/host；删除对应 tests、docs/design、旧 docs/source-manifest.json 和 docs/acceptance.json，以及旧源码 ZIP。它们属于未部署的网页工作台/模拟验证，历史提交仍保留。唯一模式二参考图 docs/original/final.png 保留；真实运行截图保留。

补齐原兼容 ZIP 内缺少的展开文件。当前 8 个项目服务、补丁、显示客户端资源、共享模块、宿主启动入口和维护索引保留。修正导出器的整机包清单和容器唯一标识采集，使其只输出项目依赖与配置。所有新增或调整的维护文件随完整包发布。

没有新增验收通过结论：模式一浏览器输入、剪贴板、完整模式切换待验收；模式二历史差异 25,831 像素；两种模式使用不同应用窗口。当前工程依赖既有 VM 和 Docker 镜像，不是独立一键运行发行包。

本轮范围澄清：不含 Ubuntu 系统和 Docker 镜像，其余已有项目文件需要补齐。已补入与 B 机留存 74 项清单逐项匹配的 Electron 43.1.1；运行时随完整 ZIP 分卷发布。B 机当前连接尚未恢复实时在线，其他现有文件仍待实时清点，不声明全部补传完成。
