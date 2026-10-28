---
name: workspace-backup-dev
description: 当前真机部署、补丁与有效维护命令索引；先遵守主分支规范。
---

如果你看到这段话，你必须立刻去看仓库主分支的 workspace-backup-dev 这个 skill，禁止查看主分支的其他 skill。连接工具根据实际使用的 5.6 分支选择，不打包连接凭据。

仅操作 Ubuntu-MultiContainer-GUI。测试、核对和手工验收须先按主分支 skill 获得批准。上传文件或保留历史截图不代表验收通过。

## 当前入口与配置

- 完整适配快照：release/Ubuntu-MultiContainer-GUI-B-existing-files.zip.part*。
- 当前源码：source/modes/；真机文件及版本清单：deployment/current/。
- 当前 8 个服务、nginx、Xorg、桌面配置及已安装补丁均在 deployment/current/rootfs/ 中按绝对路径映射保存。
- 安装源文件和维护脚本可能重启项目桌面/应用，运行前保存文档；不执行 VM 关机或其他 VM 管理操作。

## 有效命令与等效代码索引

以下将有用的临时操作归并到有效源文件，避免遗失修补步骤。原始主机安装资料不能绕过当前源码和补丁覆盖现有运行配置。

| 文件 | 用途 |
| --- | --- |
| [maintenance/read-current-project.py](../../../maintenance/read-current-project.py) | 在指定 VM 内只读导出当前模式源码、网页、nginx 和项目服务，不读取凭据 |
| [source/modes/controller.py](../../../source/modes/controller.py) | 选择模式与管理统一桌面窗口 |
| [source/modes/desktops.py](../../../source/modes/desktops.py) | 三个独立原生 Xfce 会话与容器应用启动 |
| [source/modes/index.html](../../../source/modes/index.html) | 三桌面同屏、失败重连、点击后的键盘焦点切换、原启动器兼容 |
| [source/modes/install-desktops.py](../../../source/modes/install-desktops.py) | 独立会话配置、nginx 路径隔离与公共资源缓存 |
| [source/modes/install.sh](../../../source/modes/install.sh) | 当前模式源码、补丁和服务部署入口 |
| [source/modes/native-integration.py](../../../source/modes/native-integration.py) | 原生应用菜单与空闲快捷键 |
| [source/modes/native_core.py](../../../source/modes/native_core.py) | 原生窗口、会话总线及状态操作 |
| [source/modes/patch_html5.py](../../../source/modes/patch_html5.py) | 客户端连接等待参数、就绪句柄与更新后的脚本引用 |
| [source/modes/patch_html5_ping.py](../../../source/modes/patch_html5_ping.py) | 让心跳检查遵守 PING_GRACE |
| [source/modes/patch_xpra.py](../../../source/modes/patch_xpra.py) | 使 display-resize 禁用设置真正生效 |
| [source/modes/prepare-desktop-auth.sh](../../../source/modes/prepare-desktop-auth.sh) | 生成三个桌面的容器侧认证文件；不上传认证值 |
| [source/modes/status_server.py](../../../source/modes/status_server.py) | 本机模式和显示尺寸接口 |
| [maintenance/apply-installed-display-patches.sh](../../../maintenance/apply-installed-display-patches.sh) | 已安装显示修补的等效执行入口 |
| [maintenance/capture-independent-desktops.sh](../../../maintenance/capture-independent-desktops.sh) | 分别截取三个原生桌面；不能代替同屏验收 |
| [maintenance/capture-unified-desktop.sh](../../../maintenance/capture-unified-desktop.sh) | 原生 X11 统一桌面截图；须批准 |
| [maintenance/export-actual-snapshot.sh](../../../maintenance/export-actual-snapshot.sh) | 导出非敏感部署文件、权限、包版本和运行时清单 |
| [maintenance/host/build-real-apps.sh](../../../maintenance/host/build-real-apps.sh) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/check-auth-code.sh](../../../maintenance/host/check-auth-code.sh) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/check-auth.sh](../../../maintenance/host/check-auth.sh) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/check-display.sh](../../../maintenance/host/check-display.sh) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/check-web.sh](../../../maintenance/host/check-web.sh) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/connect-project.ps1](../../../maintenance/host/connect-project.ps1) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/download-packages.py](../../../maintenance/host/download-packages.py) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/final-verify.sh](../../../maintenance/host/final-verify.sh) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/guest-exec.py](../../../maintenance/host/guest-exec.py) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/inspect-full.sh](../../../maintenance/host/inspect-full.sh) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/inspect-guest.sh](../../../maintenance/host/inspect-guest.sh) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/install-current-xpra.sh](../../../maintenance/host/install-current-xpra.sh) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/network-fix.sh](../../../maintenance/host/network-fix.sh) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/start-workspace.ps1](../../../maintenance/host/start-workspace.ps1) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/transfer-guest.py](../../../maintenance/host/transfer-guest.py) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/upgrade-offline-repo.sh](../../../maintenance/host/upgrade-offline-repo.sh) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/verify.sh](../../../maintenance/host/verify.sh) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/host/一键打开Linux工作台.vbs](../../../maintenance/host/一键打开Linux工作台.vbs) | 原 B 机维护/构建/连接来源；诊断执行须批准 |
| [maintenance/manual-native-desktop-acceptance.sh](../../../maintenance/manual-native-desktop-acceptance.sh) | 原生会话的手工功能验收；须先获批准 |
| [maintenance/native-focus-observer.py](../../../maintenance/native-focus-observer.py) | 记录真实显示服务器的鼠标与焦点状态 |
| [maintenance/native-input-observer.py](../../../maintenance/native-input-observer.py) | 记录真实容器输入、剪贴板和导航观察结果，不伪造通过 |
| [maintenance/restore-standard-native-panels.sh](../../../maintenance/restore-standard-native-panels.sh) | 保留备份后恢复原生面板；重启三个项目桌面 |
| [maintenance/start-existing-project.sh](../../../maintenance/start-existing-project.sh) | 启动现有项目服务，不关机、不操作其他 VM |
| [maintenance/stop-owned-diagnostics.sh](../../../maintenance/stop-owned-diagnostics.sh) | 仅结束本项目临时诊断单元 |
| [deployment/current/rootfs/srv/unified/prepare-auth.sh](../../../deployment/current/rootfs/srv/unified/prepare-auth.sh) | 原机实际认证、共享依赖发布或窗口维护脚本 |
| [deployment/current/rootfs/srv/unified/publish-python.sh](../../../deployment/current/rootfs/srv/unified/publish-python.sh) | 原机实际认证、共享依赖发布或窗口维护脚本 |
| [deployment/current/rootfs/srv/unified/tile-monitor.sh](../../../deployment/current/rootfs/srv/unified/tile-monitor.sh) | 原机实际认证、共享依赖发布或窗口维护脚本 |
| [deployment/current/rootfs/srv/unified/verify.sh](../../../deployment/current/rootfs/srv/unified/verify.sh) | 原机实际系统脚本；诊断/验收须先获批准 |

临时的路径隔离、自动重连、焦点、心跳与窗口缩放修改，已分别归入上表当前源文件；未保留会覆盖新实现的过时编辑脚本。无效试验、缓存、口令、私钥和认证 cookie 不上传。

## 本次仓库清理

已移除未部署到 B 机的旧网页工作台、旧 /workbench/ 启动器及其测试、模拟验证图片和记录、旧源码 ZIP。当前入口保持 B 机原启动器与 source/modes。ZIP 与展开的源码、配置、显示资源和维护文件同步发布。采集脚本只记录项目所需依赖，不采集整机软件清单或机器唯一标识。

| [maintenance/package-existing-runtime.py](../../../maintenance/package-existing-runtime.py) | 将匹配 B 机已有清单的 Electron 运行时纳入完整快照并分卷，不含 Ubuntu/Docker 镜像 |
| [maintenance/reassemble-package.py](../../../maintenance/reassemble-package.py) | 合并 release 中完整归档分卷 |
