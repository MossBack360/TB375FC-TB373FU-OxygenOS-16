#!/usr/bin/env python3
"""Stage selected static ROM payloads in an extracted v5 worktree."""

import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unique_zip(folder: Path, prefix: str) -> Path:
    found = list(folder.glob(prefix + "*.zip"))
    if len(found) != 1:
        raise ValueError(f"Expected one {prefix} ZIP in {folder}, got {found}")
    return found[0]


class Stage:
    def __init__(self, work: Path):
        self.work = work
        self.records = []

    def put(self, part: str, rel: str, data: bytes, source: str) -> None:
        if rel.startswith("/") or ".." in Path(rel).parts or "\\" in rel:
            raise ValueError(rel)
        root = self.work / "filesystems" / part / part
        target = root / rel
        config = self.work / "filesystems" / part / "config"
        fs = config / f"{part}_fs_config"
        known = {line.split(" ", 1)[0] for line in fs.read_text(encoding="utf-8").splitlines()}
        new_file = not target.exists()
        before = digest(target.read_bytes()) if target.is_file() else "new"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        additions = []
        parent = target.parent
        while parent != root:
            key = f"{part}/{parent.relative_to(root).as_posix()}"
            if key not in known:
                additions.append(f"{key} 0 0 0755")
                known.add(key)
            parent = parent.parent
        key = f"{part}/{rel}"
        if key not in known:
            additions.append(f"{key} 0 0 0644")
        if additions:
            with fs.open("a", encoding="utf-8", newline="\n") as out:
                out.write("\n".join(reversed(additions)) + "\n")
        if new_file:
            escaped = rel.replace(".", r"\.")
            context = f"/{part}/{escaped} u:object_r:system_file:s0\n"
            with (config / f"{part}_file_contexts").open("a", encoding="utf-8", newline="\n") as out:
                out.write(context)
            if part == "system_a":
                with (config / "system_a_file_contexts.build-ascii").open("a", encoding="utf-8", newline="\n") as out:
                    out.write(context)
        self.records.append(f"{source} -> {part}/{rel} {before} -> {digest(data)}")

    def module(self, archive: Path) -> None:
        with ZipFile(archive) as bundle:
            for name in bundle.namelist():
                if "\\" in name:
                    raise ValueError(f"Bad ZIP separator: {archive}:{name}")
                if not name.startswith("system/") or name.endswith("/"):
                    continue
                parts = name.split("/")
                if parts[1] == "system_ext":
                    part, rel = "system_ext_a", "/".join(parts[2:])
                elif parts[1] == "product":
                    part, rel = "product_a", "/".join(parts[2:])
                elif parts[1] == "vendor":
                    raise ValueError(f"Vendor file needs early-init review: {name}")
                else:
                    part, rel = "system_a", "/".join(parts[1:])
                    if not rel.startswith("my_"):
                        rel = "system/" + rel
                self.put(part, rel, bundle.read(name), f"{archive.name}:{name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("work", type=Path)
    parser.add_argument("stable", type=Path)
    parser.add_argument("fixo_out", type=Path)
    args = parser.parse_args()
    stage = Stage(args.work)
    active = args.stable / "01-当前启用-Magisk"
    for prefix in ("05-", "06-", "07-", "23-", "24-", "27-", "28-"):
        stage.module(unique_zip(active, prefix))
    with ZipFile(unique_zip(args.stable / "07-待固化", "02-")) as bundle:
        stage.put("system_a", "my_stock/priv-app/OppoGallery2/OppoGallery2.apk",
                  bundle.read("payload/OppoGallery2.apk"), "02-gallery-only")
    with ZipFile(unique_zip(active, "05-")) as bundle:
        for entry, rel in (
            ("payload/app_v2.xml", "my_stock/etc/config/app_v2.xml"),
            ("payload/appfeature.ai_front_apps.xml", "my_product/etc/extension/appfeature.ai_front_apps.xml"),
            ("payload/com.oplus.oplus-feature.xml", "my_product/etc/extension/com.oplus.oplus-feature.xml"),
        ):
            stage.put("system_a", rel, bundle.read(entry), f"05:{entry}")
    settings = args.fixo_out / "settings-signature-audit-2026-11-12" / "Settings-v5.3-rom-signing-block-candidate.apk"
    data = settings.read_bytes()
    if digest(data) != "4d763c6c3a3fa15e7561d48434fce8b7373470ac5e0eec6adbbcc4cb11c1b098":
        raise ValueError("Unverified Settings candidate")
    stage.put("system_ext_a", "priv-app/Settings/Settings.apk", data, "Settings v5.3 early-scan candidate")
    output = args.work / "staged-static-files.txt"
    output.write_text("\n".join(stage.records) + "\n", encoding="utf-8")
    print(f"Staged {len(stage.records)} static files: {output}")


if __name__ == "__main__":
    main()
