#!/usr/bin/env python3
"""Package the Settings-linked hall event service for Magisk testing."""

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


RC = """on property:sys.boot_completed=1
    start fixo_hall_cover

service fixo_hall_cover /system/bin/sh /system/etc/fixo/hall-cover.sh
    class late_start
    disabled
    user system
    group system input log
    seclabel u:r:shell:s0
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    source = Path(__file__).resolve().parent / "hall_cover_event/hall-cover.sh"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    entries = {
        "module.prop": ("id=xiaoxin_hall_cover\nname=Xiaoxin Hall Cover ROM-service trial\n"
                        "version=2.1-test\nversionCode=3\nauthor=MossBack360\n"
                        "description=Event-driven cover sleep/wake following the Settings switch.\n").encode(),
        "service.sh": ("#!/system/bin/sh\n"
                       "exec su -Z u:r:shell:s0 1000 -c '/system/bin/sh /system/etc/fixo/hall-cover.sh'\n").encode(),
        "system/etc/fixo/hall-cover.sh": source.read_bytes(),
        "rom/fixo-hall-cover.rc": RC.encode(),
        "README.txt": ("Magisk service.sh is a test adapter. The ROM uses the same hall-cover.sh "
                       "with rom/fixo-hall-cover.rc installed under /system/etc/init. "
                       "No sysfs hall read or extra SELinux allow rule is needed.\n").encode(),
    }
    with ZipFile(args.output, "w", ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    with ZipFile(args.output) as archive:
        if set(archive.namelist()) != set(entries) or any("\\" in n for n in archive.namelist()):
            raise ValueError("bad module archive")
    print(args.output)


if __name__ == "__main__":
    main()
