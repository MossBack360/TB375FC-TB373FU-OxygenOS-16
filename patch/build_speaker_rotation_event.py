#!/usr/bin/env python3
"""Build event-driven speaker rotation helper and reversible Magisk test ZIP."""

import argparse
from pathlib import Path
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sdk", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    root = Path(__file__).resolve().parent / "speaker_rotation_event"
    build = args.output.parent / "build-event"
    stubs = build / "stubs"
    classes = build / "classes"
    dex = build / "dex"
    for folder in (stubs, classes, dex):
        folder.mkdir(parents=True, exist_ok=True)
    android_jar = args.sdk / "platforms/android-30/android.jar"
    d8 = args.sdk / "build-tools/36.0.0/d8.bat"
    subprocess.run(["javac", "--release", "8", "-cp", str(android_jar),
                    "-d", str(stubs), *map(str, sorted((root / "stubs/android/view").glob("*.java")))],
                   check=True)
    subprocess.run(["javac", "--release", "8", "-cp", f"{android_jar};{stubs}",
                    "-d", str(classes),
                    str(root / "src/com/fixo/rotation/RotationBridge.java")], check=True)
    subprocess.run([str(d8), "--lib", str(android_jar), "--classpath", str(stubs),
                    "--output", str(dex),
                    *map(str, sorted((classes / "com/fixo/rotation").glob("RotationBridge*.class")))],
                   check=True)
    jar = build / "speaker-rotation.jar"
    with ZipFile(jar, "w", ZIP_DEFLATED) as archive:
        archive.write(dex / "classes.dex", "classes.dex")
    rc = """on property:sys.boot_completed=1
    start fixo_speaker_rotation

service fixo_speaker_rotation /system/bin/app_process /system/bin com.fixo.rotation.RotationBridge
    class late_start
    disabled
    user root
    group root system log input
    setenv CLASSPATH /system/etc/fixo/speaker-rotation.jar
"""
    entries = {
        "module.prop": ("id=fixo_speaker_rotation_prop\n"
                        "name=Speaker rotation event service trial\n"
                        "version=2.4-test\nversionCode=6\n"
                        "author=MossBack360\n"
                        "description=WindowManager rotation callback; no periodic dumpsys.\n").encode(),
        "system.prop": b"ro.audio.monitorRotation=true\n",
        "service.sh": ("#!/system/bin/sh\n"
                       "until [ \"$(getprop sys.boot_completed)\" = 1 ]; do sleep 1; done\n"
                       "export CLASSPATH=/system/etc/fixo/speaker-rotation.jar\n"
                       "while true; do\n"
                       "    /system/bin/app_process /system/bin com.fixo.rotation.RotationBridge\n"
                       "    sleep 2\n"
                       "done\n").encode(),
        "system/etc/fixo/speaker-rotation.jar": jar.read_bytes(),
        "rom/fixo-speaker-rotation.rc": rc.encode(),
        "README.txt": ("The Magisk service.sh is only the test launcher. In ROM, install the jar "
                       "at /system/etc/fixo/ and the RC at /system/etc/init/. "
                       "The helper subscribes to WindowManager.watchRotation and calls "
                       "AudioSetParam only when rotation changes. Verify init SELinux separately.\n").encode(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.output, "w", ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    with ZipFile(args.output) as archive:
        if set(archive.namelist()) != set(entries) or any("\\" in x for x in archive.namelist()):
            raise ValueError("bad module archive")
    print(args.output)


if __name__ == "__main__":
    main()
