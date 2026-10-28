# Ubuntu-MultiContainer-GUI：B 机适配完整部署快照

适配对象：B 机 Windows 10 Pro 22H2（19045.6456）上现有的 VirtualBox VM `Ubuntu-MultiContainer-GUI`；Ubuntu 24.04.3，用户 workspace/UID 1000，现有 Docker 容器 unified-a/b/c。仅管理这个项目，不包含创建、关机或修改其他虚拟机的操作。

本包收录实际部署文件、完整自有源码、实际配置、已安装补丁、共享 Python 模块、有效维护命令和依赖清单。它是当前真实部署的完整工程快照，不是已经通过独立运行验收的通用系统镜像或绿色包。

## 内容

- `deployment/current/rootfs/`：按真机绝对路径映射的文件。包括 /srv/unified、8 个 systemd 服务及 drop-in、nginx、Xorg、四个 Xfce 会话配置、启动项、共享模块，以及安装后的 Xpra Python/HTML5 补丁文件与许可证。
- `source/modes/`：当前桌面模式的完整自有源码；与真机采集的模式源码对应。
- `deployment/current/`：文件路径、SHA-256、权限、UID/GID；项目必需软件和应用镜像包版本；实际镜像内容 ID、应用主机名与项目挂载；有效服务内容；Windows 主机兼容资料；第三方运行时清单。
- `maintenance/`：已用维护操作的等效入口、截图和诊断脚本；`host/` 保存原 B 机启动、连接、构建和只读维护脚本。脚本用途和授权要求见本项目 skill 索引。
- `docs/runtime/`：已取得的实机截图，不代表新一轮验收通过。`docs/original/final.png` 仅是模式二参考图。

## 运行与维护入口

这是针对已有 B 机/VM 的适配快照，不能直接把 rootfs 复制到其他系统。保留原机私有认证和用户数据，按清单恢复到相同路径；已有项目中的源码安装入口为 `/srv/unified/modes/install.sh`，会重启项目桌面和应用，运行前应保存打开的内容。

在现有已部署 VM 上启动项目：`sudo bash maintenance/start-existing-project.sh`。Windows 原入口为 `maintenance/host/一键打开Linux工作台.vbs` 和 `start-workspace.ps1`，仍使用 E:\VM-Unified-GUI 与 http://127.0.0.1:48080/；启动器本身不启动或修改 VM。当前页面保留真实显示区域的 `id="display"`，兼容该原有入口。

所有额外测试、核对及手工验收脚本须依主分支 skill 先获批准；本次归档不把未完成的浏览器输入测试标为通过。原始构建和维护脚本不应越过当前补丁直接覆盖现有配置。

## 外部运行环境

需要现有 Ubuntu、VirtualBox、Docker Engine/Compose、Xfce、Xorg dummy、Python、nginx、Xpra 6.5.4-r0-1 和 HTML5 v21。本项目必需软件的实际版本和应用镜像包版本在 deployment/current/deployment-metadata.json 中；未包含整机软件清单。

`unified-real-apps:24.04` 镜像保留在原 VM；其实际镜像内容 ID、项目挂载和应用包版本已记录，构建来源脚本已收录。Ubuntu 虚拟磁盘、Docker 镜像、缓存、用户文档及私有认证材料不嵌入本工程包。

原目录另有 Electron 43.1.1 第三方运行时，当前 8 个项目服务不调用它；本次补入其 74 项实际运行时文件，内容逐项匹配此前 B 机采集清单。官方固定版本下载地址、74 个实际运行时文件的路径/大小/SHA-256 和许可证已收录。Xpra 上游：https://github.com/Xpra-org/xpra （GPL-2.0 系列）；HTML5 上游：https://github.com/Xpra-org/xpra-html5 （MPL-2.0）；Electron 上游：https://github.com/electron/electron （MIT 及其第三方许可）。不把第三方软件冒称为自有源码。

认证文件 guest-password.txt、SSH 私钥和 /srv/unified/state/auth 中的 Xauthority cookie 不上传。现有认证保留在原机；prepare-auth.sh 和 prepare-desktop-auth.sh 的生成逻辑已包含。

## 架构与实际状态

模式一在容器外运行 :101/:102/:103 三个独立原生 Xfce 桌面，在同一浏览器界面同屏显示。模式二使用 :100 统一桌面，显示同一批容器中的另一批应用窗口。四个会话共用一套已安装桌面依赖；应用自身 GTK/X11 客户端库仍在容器镜像内。

已取得三个完整桌面同屏、三路响应正常的截图，并确认点击桌面后的浏览器键盘焦点切换。浏览器输入、剪贴板和模式切换的完整链路尚未通过最终验收。模式二原生截图与参考图仍有 25,831 个不同像素（2.5226%）；未冻结时钟、替换截图或宣称像素一致。

## 本次上传整理（2026-10-28）

已连接 B 机并直接读取指定 VM 内当前源码、网页、nginx、8 个服务与显示服务覆盖配置，25 个文件与当前部署快照内容一致。补齐此前仅在 ZIP 内、尚未展开入库的 133 个文件。移除未部署旧网页工作台、旧启动器、对应模拟测试和设计验证图、旧源码 ZIP。B 机文件、容器和服务未修改，本次没有重跑功能验收。

采集与交付范围为本项目；导出脚本仅采集项目必需的宿主依赖，不采集整机软件清单、机器唯一标识或凭据。完整 ZIP 与本分支展开目录同步；仍依赖现有 VM 和镜像，验收限制如上。

## 已有运行时补传

Ubuntu 系统和 Docker 镜像按用户要求排除。Electron 43.1.1 的 74 个文件已从官方固定发行包补齐，全部逐项匹配 B 机留存文件清单的大小和摘要。运行时位于完整归档的 deployment/current/rootfs/srv/unified/console/electron/，保持上游许可与执行权限。

GitHub 单文件大小限制要求完整归档分卷保存为 release/Ubuntu-MultiContainer-GUI-B-existing-files.zip.part001 等文件；运行 `python3 maintenance/reassemble-package.py` 合并后解压。不是 Ubuntu 或 Docker 镜像。现有部署快照仍依赖原 VM，不新增功能验收通过结论。

本轮 B 机连接尚未恢复在线，项目其余目录尚待实时清点；本次运行时补传不表示全部现有文件已收齐。
