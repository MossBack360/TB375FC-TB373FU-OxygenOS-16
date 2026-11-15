#!/usr/bin/env python3
"""Repackage speaker rotation as a ROM-owned script with a Magisk test adapter."""

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_zip", type=Path)
    parser.add_argument("output_zip", type=Path)
    args = parser.parse_args()
    if args.output_zip.exists():
        raise FileExistsError(args.output_zip)

    with ZipFile(args.source_zip) as source:
        old = source.read("service.sh").decode("utf-8")
        prop = source.read("system.prop")
    marker = "LOG=/data/local/tmp/fixo_speaker_rotation.log"
    if old.count(marker) != 1 or prop != b"ro.audio.monitorRotation=true\n":
        raise ValueError("unexpected source module")
    script = old.replace(
        marker,
        "mkdir -p /data/vendor/fixo\nLOG=/data/vendor/fixo/speaker-rotation.log",
    )
    rc = """service fixo_speaker_rotation /system/bin/sh /system/etc/fixo/speaker-rotation.sh
    class late_start
    user root
    group root system log input
"""
    entries = {
        "module.prop": ("id=fixo_speaker_rotation_prop\n"
                        "name=Speaker rotation ROM-service trial\n"
                        "version=2.2-test\nversionCode=4\n"
                        "author=MossBack360\n"
                        "description=ROM-owned audio rotation script with Magisk test adapter.\n").encode(),
        "system.prop": prop,
        "service.sh": b'#!/system/bin/sh\nMODDIR=${0%/*}\nexec /system/bin/sh "$MODDIR/system/etc/fixo/speaker-rotation.sh"\n',
        "system/etc/fixo/speaker-rotation.sh": script.encode(),
        "rom/fixo-speaker-rotation.rc": rc.encode(),
        "README.txt": ("Magisk service.sh is a test adapter only. For the ROM, install the script at "
                       "/system/etc/fixo/speaker-rotation.sh, the RC at /system/etc/init/"
                       "fixo-speaker-rotation.rc, and keep ro.audio.monitorRotation=true. "
                       "Validate native init SELinux permissions separately.\n").encode(),
    }
    args.output_zip.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.output_zip, "w", ZIP_DEFLATED) as output:
        for name, data in entries.items():
            output.writestr(name, data)
    with ZipFile(args.output_zip) as output:
        if set(output.namelist()) != set(entries) or any("\\" in name for name in output.namelist()):
            raise ValueError("bad archive paths")
    print(args.output_zip)


if __name__ == "__main__":
    main()
