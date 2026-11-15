#!/usr/bin/env python3
"""Stage the confirmed event-driven rotation helper in an unpacked ROM tree."""

import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile


JAR_SHA256 = "97a873132db89c6ec6a3f784c2e3760a807b6bed23671be443b72ad962773004"
RC = """on property:sys.boot_completed=1
    start fixo_speaker_rotation

service fixo_speaker_rotation /system/bin/app_process /system/bin com.fixo.rotation.RotationBridge
    class late_start
    disabled
    user root
    group root system log input
    seclabel u:r:shell:s0
    setenv CLASSPATH /system/etc/fixo/speaker-rotation.jar
"""


def ensure_line(path: Path, line: str) -> None:
    data = path.read_text(encoding="utf-8")
    if line not in data.splitlines():
        with path.open("a", encoding="utf-8", newline="\n") as output:
            output.write(line + "\n")


def stage(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != data:
        raise ValueError(f"refusing to overwrite differing {path}")
    path.write_bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("zip", type=Path)
    parser.add_argument("worktree", type=Path)
    args = parser.parse_args()
    with ZipFile(args.zip) as archive:
        jar = archive.read("system/etc/fixo/speaker-rotation.jar")
    if hashlib.sha256(jar).hexdigest() != JAR_SHA256:
        raise ValueError("speaker rotation jar hash changed")
    root = args.worktree / "filesystems/system_a/system_a/system"
    stage(root / "etc/fixo/speaker-rotation.jar", jar)
    stage(root / "etc/init/fixo-speaker-rotation.rc", RC.encode())
    cfg = args.worktree / "filesystems/system_a/config"
    for name, mode in (("etc/fixo/speaker-rotation.jar", "0644"),
                       ("etc/init/fixo-speaker-rotation.rc", "0644")):
        ensure_line(cfg / "system_a_fs_config", f"system_a/system/{name} 0 0 {mode}")
        escaped = name.replace(".", r"\.")
        line = f"/system_a/system/{escaped} u:object_r:system_file:s0"
        ensure_line(cfg / "system_a_file_contexts", line)
        ensure_line(cfg / "system_a_file_contexts.build-ascii", line)
    print("staged speaker rotation JAR and init RC")


if __name__ == "__main__":
    main()
