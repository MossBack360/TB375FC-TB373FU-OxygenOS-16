# PiP rounded-corner RenderEngine fix v1.0

## Result

The previously verified four-byte `forceNoClipSmooth()` early-return experiment is packaged as Magisk module `fixo_pip_renderengine_no_clip` v1.0. The exact test binary previously removed the persistent Chrome PiP inner/outer corner mismatch and its transition jump. This module uses the same binary SHA-256, `7c5c7c37234886135482c69fc0bbc50b3b2b9ca8f38544d12ccc7df0336de895`.

On 2026-11-11, the module installed and survived reboot. `sys.boot_completed=1`; the live `/system_ext/lib64/librenderengineextimpl.so` hash matches the payload; SurfaceFlinger PID 1129 and SystemUI PID 2268 remained stable across two checks. The standalone LSPosed PiP-radius test APK is absent. The older ColorOS SurfaceFlinger and SkiaGL experiment modules have `disable` markers. A fresh post-install visual PiP test has not yet been recorded; the behavioral evidence comes from the earlier identical bind-mounted binary.

## Exact change

| Item | Value |
| --- | --- |
| Target in ROM | `/system_ext/lib64/librenderengineextimpl.so` |
| Original file SHA-256 | `dc12fd204d76591d231ae3f62034779112c25b664593f2aa110ce2ac460acd35` |
| Function | `android::renderengine::skia::SkiaRenderEngineExtImpl::forceNoClipSmooth` |
| File offset | `0x1a3a80` |
| Original 4 bytes | `c8 23 00 b0` |
| Replacement 4 bytes | `c0 03 5f d6` (AArch64 `ret`) |
| Patched file SHA-256 | `7c5c7c37234886135482c69fc0bbc50b3b2b9ca8f38544d12ccc7df0336de895` |

The binary differs from the ROM original at exactly those four bytes. It leaves `setCornerRadiusExt`, its weight, all other RenderEngine code, SystemUI, Launcher, and SurfaceFlinger untouched. The OPlus smooth/no-clip radius rewrite is skipped for every layer that reaches this function; this is a global RenderEngine change, not a Chrome-only condition.

## Build and archive

Builder: `patch/pip-renderengine-no-clip/build.py`. It verifies the source hash, original bytes, resulting hash, and ZIP entry separators. The installation script rejects a ROM whose live library hash differs from the expected original.

Magisk payload path: `system/system_ext/lib64/librenderengineextimpl.so`.

Archive: `E:\工程\github\xiaoxin Oxygen\temp3\稳定安装\01-当前启用-Magisk\28-pip-rounded-corner-renderengine-fix-v1.0.zip` (SHA-256 `7e1addb53c1e69b3bb46b38ac58ff9c7c72be9547416b6f8ee01fe96c0142e53`). A build copy is preserved under `fixO/out/pip-renderengine-no-clip-v1.0-2026-11-11/`.

## ROM integration later

When building the matching OxygenOS 16 `system_ext` image, patch the original library at the listed offset and place the resulting file at `/system_ext/lib64/librenderengineextimpl.so` before repacking `super.img`. Check both hashes before packaging. If the base library hash differs, find the function in that build and re-evaluate the patch; do not reuse this four-byte offset blindly. Once the ROM carries the patched library, omit the Magisk module to avoid an unnecessary duplicate mount.

Rollback on the current ROM: disable module ID `fixo_pip_renderengine_no_clip` and reboot. The original image library will be visible again.
