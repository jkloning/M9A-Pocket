<div align="center">

<img src="icon.png" alt="M9A Pocket" width="180">

# M9A Pocket

_重返未来：1999 · 安卓端 MaaFramework 助手_

基于图像识别的一键日常 · 手机原生运行 · 内置 Python Agent

[![Release](https://img.shields.io/github/v/release/jkloning/M9A-Pocket?style=flat-square)](https://github.com/jkloning/M9A-Pocket/releases/latest)
[![License](https://img.shields.io/badge/license-继承上游-blue?style=flat-square)](#许可证)
[![MaaFramework](https://img.shields.io/badge/MaaFramework-5.12.3-green?style=flat-square)](https://github.com/MaaXYZ/MaaFramework)
[![Platform](https://img.shields.io/badge/platform-Android%20arm64--v8a-orange?style=flat-square)](#运行要求)

[下载最新版](https://github.com/jkloning/M9A-Pocket/releases/latest) · [问题反馈](https://github.com/jkloning/M9A-Pocket/issues) · [上游 M9A](https://github.com/MAA1999/M9A)

</div>

> [!WARNING]
> 项目处于活跃开发与实测阶段，接口与任务行为可能随版本更新变动。游戏更新导致界面变化时，任务可能需要等待适配。

## 特性

| | 特性 | 说明 |
| --- | --- | --- |
| 📱 | 安卓原生 | 基于 MaaFwApp 宿主 + ADB 控制器，无需连接电脑 |
| 🔑 | 权限方案 | Shizuku / Root 均可，无需解锁 Bootloader |
| 🐍 | Python Agent | 内置 arm64 Python 运行时，支持上游全部自定义识别 / 动作 |
| 🔄 | 应用内自更新 | 更新源即本仓库 Releases，发现新版直接下载安装 |
| 🧭 | 自适应启动 | 兼容任意初始状态（登录页 / 公告 / 主界面）进入日常流程 |
| ⏱️ | 定时执行 | 由 MaaFwApp 宿主提供定时计划任务能力 |

## 任务列表

任务与选项完整继承上游 M9A v4.7.1，本仓库不改动任务逻辑，仅做打包与安全加固（见[与上游的差异](#与上游的差异)）。

| 任务 | 说明 |
| --- | --- |
| 启动游戏 / 关闭游戏 | 冷启动 / 热启动均可，含公告关闭 |
| 领取奖励 | 邮件、任务、综合体、活动盒子、迷思海周扫荡、拉普拉斯论坛等 |
| 常规作战 | 刷体力关卡，支持吃糖（体力溢出可控） |
| 智能均衡刷材料 | 按掉落与需求智能规划刷材料 |
| 每日心相（意志解析） | — |
| 收取荒原 | — |
| 银行购物 | — |
| 自动深眠 / 自动醒梦 | 周本类玩法 |
| 活动类 | 活动推图、复刻推图、活动代币刷取、局外演绎（黄昏的音序 / 无声综合征）、警铃鸣响时（需高练度）、匣中交流赛、UTTU 闪烁集会、翻斗棋速刷、缪斯碰碰盒速刷、雨前漫游指南、完全归纳法、8-bit 街机秀等 |
| 工具类 | 使用兑换码、仓库材料识别、角色升级（beta）、切换账号 |

## 运行要求

| 项目 | 要求 |
| --- | --- |
| 系统 | Android 9.0（API 28）及以上 |
| 权限 | Shizuku 或 Root（二者其一） |
| 架构 | arm64-v8a |
| 运行条件 | **亮屏解锁状态**（游戏在锁屏下会被冻结导致任务超时） |
| 分辨率 | 资源按 1280×720 设计，20:9 全面屏若游戏不 letterbox 则可能错位 |

## 安装

1. 从 [Releases](https://github.com/jkloning/M9A-Pocket/releases/latest) 下载 APK 并安装
2. 打开 App，按提示启动 Shizuku 并授权（Root 设备可选 Root 模式）
3. 更新源选择 **GitHub**（本仓库即更新源；Mirror 酱上游仅分发桌面版，选它会报"没有匹配的安装包"）
4. 选择服务器（官服 / B 服 / OPPO 服 / 各国际服），勾选任务，开始

> [!TIP]
> 建议插电运行并开启系统的"屏幕常亮"，或通过 `adb shell svc power stayon true` 设置充电时常亮。

## 文档

| 文档 | 说明 |
| --- | --- |
| [上游 M9A](https://github.com/MAA1999/M9A) | Windows / PC 端原项目，本仓库资源迁移自 v4.7.1 |
| [MaaFramework](https://github.com/MaaXYZ/MaaFramework) | 自动化框架（v5.12.3，PI V2 清单） |
| [MaaFwApp](https://github.com/Aliothmoon/MaaFwApp) | 安卓打包宿主（AGPL-3.0） |

## 与上游的差异

任务与识别逻辑与上游 v4.7.1 完全一致，差异仅有：

- `interface.json` 的 `github` 字段指向本仓库——应用内「检查更新」走 M9A-Pocket Releases（上游仓库无安卓包，指过去只会报"没有匹配的安装包"）
- Agent 安全加固（打包时审查发现，均不改变功能）：
  - `agent/utils/version_checker.py`：MirrorChyan API 主机写死 + 参数编码，防 SSRF
  - `agent/custom/reco/general.py`：逻辑表达式改 AST 白名单求值，替换 `eval`，防代码注入
  - `agent/utils/account_store.py`：JSON 保存增加项目目录容器校验，防路径穿越
  - `agent/custom/action/eight_bit.py`：随机数改用 `secrets`

## 发版流程（维护者）

1. 修改本仓库资源 → commit + push（约定：每次更新必 push）
2. 打 semver tag（`v4.7.3` 这类，必须大于已装机 versionName；正式版不要带 `-beta` 后缀）
3. 创建 Release 并上传 APK（单一 universal 包命名不带 ABI 标记，任意设备都能匹配）
4. 构建宿主 versionCode 需同步抬高（`build.versionCode=XYYZZ`，如 4.7.2 → 40702），否则 MaaFwApp 按 versionCode 判断资源缓存，覆盖安装后不会重新解压

## 参与贡献

1. Fork 本仓库并创建分支
2. 修改 `resource/` 下的流水线与模板（模板请从实机截图裁剪）
3. 提交遵循 Conventional Commits（如 `fix: ...`、`feat: ...`）
4. 发起 Pull Request

## 致谢

- [MAA1999/M9A](https://github.com/MAA1999/M9A) —— 重返未来：1999 助手，本仓库的资源来源
- [MaaXYZ/MaaFramework](https://github.com/MaaXYZ/MaaFramework) —— 自动化框架
- [Aliothmoon/MaaFwApp](https://github.com/Aliothmoon/MaaFwApp) —— 安卓打包宿主
- [Shizuku](https://github.com/RikkaApps/Shizuku) —— 特权 API 方案

## 许可证

本仓库资源迁移自 M9A，许可证继承上游；MaaFwApp 宿主为 AGPL-3.0。第三方代码保留其原始许可证。
