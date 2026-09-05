# M9A-android

重返未来：1999（M9A）MaaFramework 安卓资源包。基于 M9A v4.7.1 Windows 发布包（interface_version=2），通过 [MaaFwApp](https://github.com/Aliothmoon/MaaFwApp) 打包为安卓 APK（`com.aliothmoon.maafw.m9a`）。

## 仓库内容

与上游 [MaaXYZ/M9A](https://github.com/MaaXYZ/M9A) 发布包的资源层一致：`interface.json`、`tasks/`、`resource/`、`data/`、`i18n/`、`agent/`（Python agent 源码）、`CONTACT`、`LICENSE`。

Agent 运行时（arm64-v8a Python bundle）不进本仓库，由打包配方从仓库外引用。

## 打包

```bash
# MaaFwApp local.properties:
#   pi.profile=<本仓库外>/pi-profile-m9a.yaml
#   build.versionName=4.7.1
cd MaaFwApp && gradlew assembleDebug
# 产物: app/build/outputs/apk/debug/app-debug.apk
```

打包配方要点（`pi-profile-m9a.yaml`，仓库外）：

```yaml
assets: <本仓库路径>
agent:
  sourceDir: <仓库外>/m9a-agent-dist   # MaaAgentCoreAndroid 3.13.15-maafw5.12.3
  runtimes:
    - location: bundle
      executable: bin/python3
      args: [-u, agent/main.py]
      env:
        PYTHONHOME: "{bundle}/prefix"
        PYTHONPATH: "{bundle}/site-packages/pure.zip:{bundle}/site-packages"
        LD_LIBRARY_PATH: "{bundle}/prefix/lib:{nativeLibs}"
        MAAFW_BINARY_PATH: "{nativeLibs}"
app: { id: m9a, label: M9A, icon: <本仓库路径>/icon.png }
```

## 踩坑记录

- Agent `env` 必须按上面写全：曾漏 `PYTHONPATH`/`MAAFW_BINARY_PATH`，设备上报 `ModuleNotFoundError: No module named 'maa'`（2026-09-05 已修正）。
- 亮屏解锁状态下运行（游戏锁屏会被冻结，任务将超时）；USB 供电建议配合 `adb shell svc power stayon true`。

## 许可

迁移自 [MaaXYZ/M9A](https://github.com/MaaXYZ/M9A)（其资源许可继承上游）；打包宿主 MaaFwApp 为 AGPL-3.0。
