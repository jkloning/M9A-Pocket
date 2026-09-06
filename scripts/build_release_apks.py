#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M9A-Pocket 发版构建：一键产出 4 个 APK 变体。

    M9APocket-<version>-universal.apk            双 ABI，通用兜底
    M9APocket-<version>-arm64-v8a.apk            ARM 64 位真机
    M9APocket-<version>-x64.apk                  x86_64 模拟器（Windows 蓝叠 / MuMu / 雷电等）
    M9APocket-<version>-zz-arm64-v8a-emu-compat.apk
                                                  arm64 模拟器兼容包：KleidiCV 的 SVE2
                                                  分派锁死为 NEON，谎报 HWCAP2_SVE2 的
                                                  模拟器（Mac 蓝叠 Air / MuMu Pro Mac）
                                                  装别的包一启动任务就 SIGILL 时用这个

每个变体 = 铺对应 ABI 的 jniLibs ->（兼容包先打 SVE2 补丁）-> gradle 指定同一 ABI
出 release 包 -> 改名收进 dist/，逐包复核 ABI 集合，兼容包出包后再从 APK 里
抽出 .so 复核一遍。

MaaFramework 的 .so 走 scripts/setup_maa_framework.py 的本地缓存（--skip-download），
没有缓存时传 --fresh-libs 让它重新下载。

签名沿用宿主约定：KEYSTORE_PATH / KEYSTORE_PASSWORD / KEY_ALIAS / KEY_PASSWORD
走环境变量或 local.properties，脚本原样透传，不碰签名材料。

Usage:
    python scripts/build_release_apks.py                    # 全部 4 个
    python scripts/build_release_apks.py --only universal,zz-arm64-v8a-emu-compat
    python scripts/build_release_apks.py --fresh-libs       # 强制重新下载 MaaFramework
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PI_DIR = REPO_ROOT / "pi"                   # interface.json 在这层，version 取自它
DIST_DIR = REPO_ROOT / "dist"
JNILIBS = REPO_ROOT / "app/src/main/jniLibs"
OPENCV_SO = "libopencv_world4.so"

GRADLEW = REPO_ROOT / ("gradlew.bat" if sys.platform == "win32" else "gradlew")


@dataclass(frozen=True)
class Variant:
    label: str            # 文件名里的变体名
    abis: tuple           # 该包允许包含的 ABI 集合（用于 jniLibs 裁剪与成包复核）
    setup_args: tuple     # setup_maa_framework.py 的固定参数（字面量）
    gradle_args: tuple    # gradlew 的固定参数（字面量）
    compat: bool          # 是否打 KleidiCV SVE2 补丁


# 每个变体的全部命令参数都是字面量，运行期不做任何拼接
VARIANTS = (
    Variant("universal",
            ("arm64-v8a", "x86_64"),
            ("--abi", "all"),
            ("clean", "-Pmaa.abi=all", "assembleRelease"),
            False),
    Variant("arm64-v8a",
            ("arm64-v8a",),
            ("--abi", "arm64-v8a"),
            ("clean", "-Pmaa.abi=arm64-v8a", "assembleRelease"),
            False),
    Variant("x64",
            ("x86_64",),
            ("--abi", "x86_64"),
            ("clean", "-Pmaa.abi=x86_64", "assembleRelease"),
            False),
    Variant("zz-arm64-v8a-emu-compat",
            ("arm64-v8a",),
            ("--abi", "arm64-v8a"),
            ("clean", "-Pmaa.abi=arm64-v8a", "assembleRelease"),
            True),
)


def show(argv: list[str]) -> None:
    print("[CMD]", *argv)


def die(msg: str) -> None:
    raise SystemExit("[ERROR] " + msg)


def deploy_libs(variant: Variant, fresh: bool) -> None:
    """铺 jniLibs；所有 subprocess.run 都接收字面量参数列表 + shell=False"""
    if fresh:
        show([sys.executable, "scripts/setup_maa_framework.py", *variant.setup_args])
        subprocess.run(
            [sys.executable, "scripts/setup_maa_framework.py", *variant.setup_args],
            check=True, cwd=str(REPO_ROOT), shell=False)
    else:
        show([sys.executable, "scripts/setup_maa_framework.py",
              *variant.setup_args, "--skip-download"])
        try:
            subprocess.run(
                [sys.executable, "scripts/setup_maa_framework.py", *variant.setup_args,
                 "--skip-download"],
                check=True, cwd=str(REPO_ROOT), shell=False)
        except subprocess.CalledProcessError:
            print("[INFO] 本地缓存不可用，回退为重新下载")
            show([sys.executable, "scripts/setup_maa_framework.py", *variant.setup_args])
            subprocess.run(
                [sys.executable, "scripts/setup_maa_framework.py", *variant.setup_args],
                check=True, cwd=str(REPO_ROOT), shell=False)

    # setup 脚本只清自己要写的 ABI 目录，把不该带的 ABI 删掉，防止单 ABI 包混入另一边
    want = set(variant.abis)
    if JNILIBS.is_dir():
        for entry in JNILIBS.iterdir():
            if entry.is_dir() and entry.name not in want:
                print("[CLEAN] 移除不需要的 jniLibs:", entry.name)
                shutil.rmtree(entry)


def patch_opencv(mode_neon_write: bool) -> None:
    """打补丁后紧接一次 --verify；mode_neon_write=False 时只校验"""
    so = str(JNILIBS / "arm64-v8a" / OPENCV_SO)
    if mode_neon_write:
        show([sys.executable, "scripts/patch_kleidicv_sve.py", so, "--mode", "neon"])
        subprocess.run(
            [sys.executable, "scripts/patch_kleidicv_sve.py", so, "--mode", "neon"],
            check=True, cwd=str(REPO_ROOT), shell=False)
    show([sys.executable, "scripts/patch_kleidicv_sve.py", so,
          "--mode", "neon", "--verify"])
    subprocess.run(
        [sys.executable, "scripts/patch_kleidicv_sve.py", so,
         "--mode", "neon", "--verify"],
        check=True, cwd=str(REPO_ROOT), shell=False)


def verify_apk_opencv(apk: Path) -> None:
    """从成包里抽出 opencv .so 复核补丁仍在，防 gradle 缓存吃进旧库"""
    check_so = DIST_DIR / ".check-emu-compat.so"
    with zipfile.ZipFile(str(apk)) as zf:
        check_so.write_bytes(zf.read("lib/arm64-v8a/" + OPENCV_SO))
    show([sys.executable, "scripts/patch_kleidicv_sve.py", str(check_so),
          "--mode", "neon", "--verify"])
    try:
        subprocess.run(
            [sys.executable, "scripts/patch_kleidicv_sve.py", str(check_so),
             "--mode", "neon", "--verify"],
            check=True, cwd=str(REPO_ROOT), shell=False)
    finally:
        check_so.unlink(missing_ok=True)


def read_version() -> str:
    ifs = json.loads((PI_DIR / "interface.json").read_text(encoding="utf-8"))
    return str(ifs["version"]).lstrip("v")


def build_variant(variant: Variant, fresh: bool, version: str) -> Path:
    print("=" * 60)
    print("[BUILD]", variant.label)
    print("=" * 60)
    deploy_libs(variant, fresh)
    if variant.compat:
        patch_opencv(mode_neon_write=True)

    show([str(GRADLEW), *variant.gradle_args])
    subprocess.run(
        [str(GRADLEW), *variant.gradle_args],
        check=True, cwd=str(REPO_ROOT), shell=False)

    out_dir = REPO_ROOT / "app/build/outputs/apk/release"
    candidates = sorted(out_dir.glob("*.apk"))
    if not candidates:
        die("没找到产物: " + str(out_dir))
    unsigned = any("unsigned" in c.stem for c in candidates)
    if unsigned:
        print("[WARN] 产物是未签名包，确认 KEYSTORE_* 环境变量是否就位")

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    dest = DIST_DIR / ("M9APocket-v" + version + "-" + variant.label + ".apk")
    for c in candidates:
        shutil.copy2(c, dest)

    # 复核成包的 ABI 集合与变体定义一致
    with zipfile.ZipFile(str(dest)) as zf:
        got = {n.split("/")[1] for n in zf.namelist()
               if n.startswith("lib/") and n.endswith(".so")}
    expect = set(variant.abis)
    if got != expect:
        die(variant.label + " ABI 不符: 期望 " + str(sorted(expect))
            + "，实际 " + str(sorted(got)))
    print("[CHECK]", variant.label, "ABI =", ",".join(sorted(got)))

    if variant.compat:
        verify_apk_opencv(dest)

    size_mb = dest.stat().st_size / 1024 / 1024
    print("[DONE]", dest.name, "(%.1f MB)" % size_mb, "（未签名）" if unsigned else "")
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description="M9A-Pocket 四变体发版构建")
    ap.add_argument("--only", help="逗号分隔的 label 子集，如 universal,zz-arm64-v8a-emu-compat")
    ap.add_argument("--fresh-libs", action="store_true",
                    help="让 setup_maa_framework.py 重新下载 MaaFramework（默认用本地缓存）")
    args = ap.parse_args()

    wanted = {s.strip() for s in args.only.split(",")} if args.only else None
    version = read_version()
    print("[INFO] 版本 v" + version + "（取自 pi/interface.json）")
    if not GRADLEW.is_file():
        die("找不到 " + str(GRADLEW))

    outputs = []
    for variant in VARIANTS:
        if wanted and variant.label not in wanted:
            continue
        outputs.append(build_variant(variant, args.fresh_libs, version))

    print("=" * 60)
    print("[SUMMARY]", len(outputs), "个包 ->", DIST_DIR)
    for p in outputs:
        print("  %s  (%.1f MB)" % (p.name, p.stat().st_size / 1024 / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
