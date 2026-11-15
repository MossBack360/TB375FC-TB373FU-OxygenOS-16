#!/usr/bin/env python3
"""Build a static hall key-layout experiment with no runtime service."""

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


LAYOUT = b"# TB375FC hall: 252=cover closed, 253=cover opened.\nkey 252 SLEEP\nkey 253 WAKEUP WAKE\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    entries = {
        "module.prop": ("id=fixo_hall_keylayout_trial\n"
                        "name=TB375FC hall static keylayout trial\n"
                        "version=0.1-test\nversionCode=1\n"
                        "author=MossBack360\n"
                        "description=Map hall close/open keys to Android sleep/wake without a daemon.\n").encode(),
        "system/usr/keylayout/hall.kl": LAYOUT,
        "README.txt": ("Static experiment. Check cover close/open and the Settings smart-cover "
                       "switch. If the switch no longer controls behavior, disable this module "
                       "and reboot. Do not enable the old hall daemon simultaneously.\n").encode(),
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
