"""Stage ROM-owned replacements for the stable modules' late-start glue.

This is a source preparation step. It does not alter a ROM tree or a device.
"""

from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT.parent / "temp3/稳定安装/01-当前启用-Magisk"
OUT = ROOT / "out/rom-glue-stage-2026-11-13"
BIN = OUT / "system/etc/fixo"
INIT = OUT / "system/etc/init/fixo-glue.rc"


def entry(prefix: str, name: str) -> bytes:
    matches = list(ARCHIVE.glob(prefix + "*.zip"))
    if len(matches) != 1:
        raise RuntimeError(f"expected one {prefix} archive, got {matches}")
    with ZipFile(matches[0]) as archive:
        return archive.read(name)


def script(prefix: str, name: str = "service.sh", changes=()) -> str:
    source = entry(prefix, name).decode("utf-8")
    for old, new in changes:
        if old not in source:
            raise RuntimeError(f"source changed: {prefix} {name}: {old!r}")
        source = source.replace(old, new)
    if "$MODDIR" in source or "resetprop" in source or "su -Z" in source:
        raise RuntimeError(f"Magisk dependency remains: {prefix} {name}")
    return source


def write(path: Path, data: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data.encode("utf-8") if isinstance(data, str) else data)


def main() -> None:
    work = "/data/vendor/fixo"
    root = "/system/etc/fixo"
    scripts = {
        "ai-providers.sh": script("05-", changes=(
            ('LOG="$MODDIR/runtime.log"', f'LOG="{work}/ai-providers.log"'),
            ('su -Z u:r:shell:s0 2000 -c "settings $*" 2>/dev/null',
             'settings "$@" 2>/dev/null'),
        )),
        "display-pq.sh": script("09-", changes=(
            ('CTL="$MODDIR/pqctl.jar"', f'CTL="{root}/pqctl.jar"'),
        )),
        "freeform-corner.sh": script("10-", changes=(
            ('resetprop persist.oplus.panorama.branch.enable',
             'setprop persist.oplus.panorama.branch.enable'),
        )),
        "hall-cover.sh": script("11-", changes=(
            ('MODDIR=${0%/*}', f'WORK={work}/hall'),
            ('$MODDIR/', '$WORK/'),
        )),
        "speaker-rotation.sh": script("12-", changes=(
            ('LOG=/data/local/tmp/fixo_speaker_rotation.log',
             f'LOG={work}/speaker-rotation.log'),
        )),
        "attention.sh": script("13-", changes=(
            ('HELPER="$MODDIR/attention-useractivity.apk"',
             f'HELPER="{root}/attention-useractivity.apk"'),
            ('LOG="$MODDIR/runtime.log"', f'LOG="{work}/attention.log"'),
            ('MODDIR=${0%/*}\n', ''),
        )),
        "wake-gesture.sh": script("14-", changes=(
            ('DEX="$MODDIR/wake-glue.dex"', f'DEX="{root}/wake-glue.dex"'),
            ('LOG="$MODDIR/runtime.log"', f'LOG="{work}/wake-gesture.log"'),
            ('MODDIR=${0%/*}\n', ''),
        )),
        "performance.sh": script("30-", "high_performance_bridge.sh", changes=(
            ('su -Z u:r:shell:s0 2000 -c "$1"', '/system/bin/sh -c "$1"'),
        )),
        "virtualcomm.sh": script("23-", changes=(
            ('LOG="$MODDIR/runtime.log"', f'LOG="{work}/virtualcomm.log"'),
            ('MODDIR=${0%/*}\n', ''),
            ('resetprop -n ', 'setprop '),
        )),
        "zram-writeback.sh": script("18-", changes=(
            ('logfile="$moddir/runtime.log"', f'logfile="{work}/zram-writeback.log"'),
            ('moddir=${0%/*}\n', ''),
        )),
    }
    # Init owns process lifecycle. Runtime data cannot live under read-only /system.
    scripts["hall-cover.sh"] = scripts["hall-cover.sh"].replace(
        'exec 9>"$WORK/daemon.lock"',
        'mkdir -p "$WORK"\nexec 9>"$WORK/daemon.lock"',
    )
    for name, body in scripts.items():
        write(BIN / name, body)
    for prefix, name in (
        ("09-", "pqctl.jar"),
        ("13-", "attention-useractivity.apk"),
        ("14-", "wake-glue.dex"),
    ):
        write(BIN / name, entry(prefix, name))

    brightness = entry("26-", "post-fs-data.sh").decode("utf-8")
    brightness = brightness.replace('MODDIR=${0%/*}', f'MODDIR={root}/autobrightness', 1)
    brightness = brightness.replace('WORK=/data/adb/tb375fc_autobrightness',
                                    f'WORK={work}/autobrightness')
    if '/data/adb/' in brightness:
        raise RuntimeError("brightness Magisk data path remains")
    write(BIN / "autobrightness-early.sh", brightness)
    with ZipFile(next(ARCHIVE.glob("26-*.zip"))) as archive:
        for name in archive.namelist():
            if name.startswith("files/tables/g") and name.endswith(".xml"):
                write(BIN / "autobrightness" / name, archive.read(name))

    # All services are disabled intentionally. Integration enables one at a time
    # after checking SELinux, package availability and early-boot ordering.
    lines = [
        "# ROM glue staging only: do not install this RC without per-service validation.",
        "on post-fs-data",
        f"    mkdir {work} 0770 root system",
        f"    mkdir {work}/hall 0700 root root",
        "",
    ]
    for name, command in (
        ("ai_providers", "ai-providers"),
        ("display_pq", "display-pq"),
        ("freeform_corner", "freeform-corner"),
        ("hall_cover", "hall-cover"),
        ("speaker_rotation", "speaker-rotation"),
        ("attention", "attention"),
        ("wake_gesture", "wake-gesture"),
        ("performance", "performance"),
        ("virtualcomm", "virtualcomm"),
    ):
        lines.extend((
            f"service fixo_{name} /system/bin/sh {root}/{command}.sh",
            "    class late_start",
            "    disabled",
            "    user shell" if name in {"performance", "ai_providers"} else "    user root",
            "    group shell system log input" if name in {"performance", "ai_providers"} else "    group root system log input",
            "    oneshot" if name == "virtualcomm" else "",
            "",
        ))
    write(INIT, "\n".join(line for line in lines if line is not None))
    manifest = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            manifest.append(f"{sha256(path.read_bytes()).hexdigest()}  {path.relative_to(OUT).as_posix()}")
    write(OUT / "SHA256SUMS.txt", "\n".join(manifest) + "\n")
    print(f"staged {len(manifest)} files in {OUT}")


if __name__ == "__main__":
    main()
