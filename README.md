<div align="center">

<img src="pi/icon.png" alt="M9A Pocket" width="180">

# M9A Pocket

_重返未来：1999 · 安卓端 MaaFramework 助手_

[![Release](https://img.shields.io/github/v/release/jkloning/M9A-Pocket?style=flat-square)](https://github.com/jkloning/M9A-Pocket/releases/latest)
[![License](https://img.shields.io/badge/license-AGPL--3.0-blue?style=flat-square)](#许可证)
[![MaaFramework](https://img.shields.io/badge/MaaFramework-5.12.3-green?style=flat-square)](https://github.com/MaaXYZ/MaaFramework)
[![Platform](https://img.shields.io/badge/platform-Android%20arm64--v8a%20%7C%20x86__64-orange?style=flat-square)](#下载)

[下载最新版](https://github.com/jkloning/M9A-Pocket/releases/latest) · [问题反馈](https://github.com/jkloning/M9A-Pocket/issues) · [上游 M9A](https://github.com/MAA1999/M9A)

</div>

基于图像识别的一键日常 · 手机原生运行 · 内置 Python Agent。本仓库是**自包含整仓**：
宿主 App 源码、M9A PI 资源、agent 运行时、打包脚本与 CI 全在这一个仓库里，架构对齐
[MAA-Meow](https://github.com/Aliothmoon/MAA-Meow)。

## 仓库结构

| 路径 | 内容 |
| --- | --- |
| `app/` `build-logic/` `semi-icons/` 等 | 宿主 App（MaaFwApp 内核 fork）：Compose 界面、Shizuku/Root 特权编排、虚拟屏后台运行、PI 加载与调度 |
| `pi/` | M9A PI 资源：`interface.json` + `resource/` + `tasks/` + `data/` + `agent/`（自定义识别/动作），迁移自上游 M9A v4.8.0 |
| `m9a-agent-dist/` | 内置 arm64 Python 运行时（CPython 3.13.15 + maafw 5.12.3 + numpy），`scripts/build_agent_bundle.py` 产出 |
| `pi-profile-m9a.yaml` | 打包配方：PI 白名单、agent 启动参数、应用身份（包名 `com.aliothmoon.maafw.m9a`） |
| `scripts/` | `setup_maa_framework.py`（拉取 MaaFramework .so）、`patch_kleidicv_sve.py`（模拟器兼容补丁）、`build_release_apks.py`（四变体一键构建） |
| `.github/workflows/` | 推 tag 自动构建真机包（arm64-v8a）并发布 Release |

## 下载

`M9APocket-<版本>-arm64-v8a.apk`：**ARM 64 位真机安装包**，应用内「检查更新」自动匹配它。

其他变体（universal / x64 模拟器 / arm64 模拟器兼容包）按需本地构建：
`python scripts/build_release_apks.py --only x64,zz-arm64-v8a-emu-compat`（兼容包关闭 OpenCV 的 SVE2
指令分派，供 Mac 上蓝叠 Air、MuMu Pro Mac 等谎报 HWCAP2_SVE2 的模拟器用）。

## 运行要求

| 项目 | 要求 |
| --- | --- |
| 系统 | Android 9.0（API 28）及以上 |
| 权限 | Shizuku 或 Root（二者其一） |
| 架构 | arm64-v8a（真机）/ x86_64（模拟器） |
| 运行条件 | **亮屏解锁状态**（游戏在锁屏下会被冻结导致任务超时） |
| 分辨率 | 识别发生在 1280×720 虚拟屏上，与手机物理分辨率无关 |

## 从源码构建

要求：JDK 17、Android SDK（NDK 27/28 + CMake 3.22.1）、Python 3.10+。

```bash
# 1. 本地 local.properties（CI 由 workflow 自动生成）
cat >> local.properties << 'EOF'
sdk.dir=<你的 Android SDK 路径>
pi.profile=pi-profile-m9a.yaml
build.versionName=4.7.2
build.versionCode=40702
EOF

# 2. 拉取 MaaFramework 的 Android .so（缓存到 .maa-cache/）
python scripts/setup_maa_framework.py

# 3. 一键出 4 个变体到 dist/（不带签名环境变量时产出未签名包）
python scripts/build_release_apks.py
# 可选：--only universal,zz-arm64-v8a-emu-compat / --fresh-libs 强制重下 .so
```

Debug 直接安装：`./gradlew installDebug`。

## 发版流程

1. 改动提交后推 `main`
2. 打 semver tag（`v4.7.3` 这类，必须大于已装机 versionName；正式版不带 `-beta` 后缀）
3. CI 自动构建真机包（arm64-v8a）并创建 Release（changelog 由 git-cliff 生成，`cliff.toml`）
4. **不要手动维护版本号文件**：`versionName`/`versionCode` 一律从 `pi/interface.json` 的 `version` 推导
   （`X.Y.Z` → `XYYZZ`，如 `4.7.2` → `40702`）；发新版只改 `pi/interface.json` 的 version
5. 设备端覆盖安装后按 versionCode 判断是否重新解包 `pi.zip`——漏抬版本会导致设备跑旧资源

## 与上游的差异

- 宿主：MaaFwApp fork，附带三处本地改动——release 支持 `-Pmaa.abi` 出单 ABI 包、
  `build.versionCode`/`build.versionName` 可从 local.properties 钉住、semi-icons 图标 tint 改用
  framework attr（修复 clean 构建资源链接失败）
- 兼容包：对 `libopencv_world4.so` 打 KleidiCV SVE2 分派补丁（锁 NEON），见
  [MAA-Meow issue #202](https://github.com/Aliothmoon/MAA-Meow/issues/202)
- 资源：任务与识别逻辑继承上游 M9A v4.8.0（本仓库不改动任务逻辑，仅打包与安全加固）

## 文档

| 文档 | 说明 |
| --- | --- |
| [上游 M9A](https://github.com/MAA1999/M9A) | Windows / PC 端原项目，`pi/` 资源迁移自 v4.8.0 |
| [MaaFramework](https://github.com/MaaXYZ/MaaFramework) | 自动化框架（v5.12.3，PI V2 清单） |
| [MaaFwApp](https://github.com/Aliothmoon/MaaFwApp) | 宿主内核上游（AGPL-3.0） |
| [MAA-Meow](https://github.com/Aliothmoon/MAA-Meow) | 本仓库整体架构的参照项目 |

## 许可证

- 宿主 App 源码来自 MaaFwApp，遵循 **AGPL-3.0**（见 `LICENSE`）
- `pi/` 资源迁移自 [MAA1999/M9A](https://github.com/MAA1999/M9A)，许可证继承上游（见 `pi/LICENSE`）
- MaaFramework 为 MaaXYZ 的开源项目；Shizuku 相关封装见宿主源码内署名

## 致谢

- [MAA1999/M9A](https://github.com/MAA1999/M9A) —— 重返未来：1999 助手，PI 资源来源
- [MaaXYZ/MaaFramework](https://github.com/MaaXYZ/MaaFramework) —— 自动化框架
- [Aliothmoon/MaaFwApp](https://github.com/Aliothmoon/MaaFwApp) 与 [Aliothmoon/MAA-Meow](https://github.com/Aliothmoon/MAA-Meow) —— 安卓宿主与整体架构参照
- [Shizuku](https://github.com/RikkaApps/Shizuku) —— 特权 API 方案
