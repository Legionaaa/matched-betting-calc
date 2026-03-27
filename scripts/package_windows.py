from __future__ import annotations

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import nicegui


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    main_script = repo_root / "matched_betting_calc.py"
    icon_path = repo_root / "images" / "logo.ico"
    images_dir = repo_root / "images"
    nicegui_dir = Path(nicegui.__file__).resolve().parent
    build_stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dist_root = repo_root / "dist"
    dist_path = dist_root / build_stamp
    work_path = repo_root / "build" / f"pyinstaller-{build_stamp}"
    spec_path = repo_root / "build" / "spec"
    latest_build_file = dist_root / "latest_build.txt"
    stable_exe = dist_root / "MatchedBettingCalc.exe"

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "MatchedBettingCalc",
        "--windowed",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--distpath",
        str(dist_path),
        "--workpath",
        str(work_path),
        "--specpath",
        str(spec_path),
        "--icon",
        str(icon_path),
        "--add-data",
        f"{nicegui_dir}{os.pathsep}nicegui",
        "--add-data",
        f"{images_dir}{os.pathsep}images",
        str(main_script),
    ]

    print("Running PyInstaller:")
    print(" ".join(f'"{part}"' if " " in part else part for part in command))
    subprocess.run(command, check=True)

    built_exe = dist_path / "MatchedBettingCalc.exe"
    latest_build_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(built_exe, stable_exe)
    latest_build_file.write_text(str(built_exe), encoding="utf-8")
    print()
    print(f"Built EXE: {built_exe}")
    print(f"Copied latest EXE to: {stable_exe}")
    print(f"Latest build path saved to: {latest_build_file}")


if __name__ == "__main__":
    main()
