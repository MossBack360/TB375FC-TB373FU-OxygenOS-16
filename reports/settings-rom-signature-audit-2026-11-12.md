# Settings ROM signature audit (2026-11-12)

## Question

Can the modified `Settings.apk` be placed directly in this third-party ROM, without replacing PackageManager or the post-boot Magisk bind mount?

## Observed on the current device

- The live ROM has no `fixo_settings_confirmed` module. Its `/system_ext/priv-app/Settings/Settings.apk` SHA-256 is `7520229a7f190d35d86a4b1945b03966a49df61aa90799f57904011fdba71c12`.
- `dumpsys package com.android.settings` reports `sharedUser=android.uid.system/1000`, `apkSigningVersion=3`, and `versionCode=16000000`.
- Android build-tools 36 `apksigner verify` rejects the ROM APK: its v3 content digest does not match. A v1-only verification also reports changed `classes.dex`/`classes2.dex` and a new `classes12.dex` without a manifest digest. Thus the ROM's own APK contents were modified after its retained signature metadata was created. Its working state does **not** prove it is an untouched official APK.
- The currently archived v5.3 payload SHA-256 is `fe8b6161f642fbbacc5eb54646f5b5040afbfa93ca999de967f7013041369bcb`. It has no usable original signing block; `apksigner` rejects it with missing `META-INF/MANIFEST.MF`.
- Both manifests declare package `com.android.settings` and `android.uid.system` shared UID.

## Relevant AOSP behavior

`InstallPackageHelper` passes `skipVerify=scanSystemPartition` when collecting certificates for a system-partition package. The v3 `unsafeGetCertsWithoutVerification` path verifies the signature block itself but does not verify the APK contents. This explains how a system APK can retain its signer identity while failing standalone `apksigner` content verification. It does **not** prove this port's exact PackageManager implementation, or that a newly supplied APK will boot without testing.

- https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/services/core/java/com/android/server/pm/InstallPackageHelper.java
- https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/java/android/util/apk/ApkSignatureSchemeV3Verifier.java

## Offline candidate, not installed

`patch/reuse_settings_signing_block.py` copied the ROM APK's exact 4096-byte signing block onto the v5.3 payload and adjusted only the ZIP central-directory offset. Candidate SHA-256: `4d763c6c3a3fa15e7561d48434fce8b7373470ac5e0eec6adbbcc4cb11c1b098`. ZIP entries and their CRCs match the v5.3 payload. `apksigner verify` now detects the preserved v3 signer and reports only the expected content-digest mismatch, matching the ROM APK's failure category. The candidate is under ignored `out/settings-signature-audit-2026-11-12/` and has not been installed, mounted, or inserted into a ROM image.

## Practical implication

Replacing PackageManager or signing Settings with the owner's new key may be unnecessary. A system-image copy retaining the ROM APK's signer metadata is a narrower path. At the initial offline audit stage, the post-boot module was the only confirmed v5.3 runtime path; the subsequent early-boot scan result is recorded below. Do not treat the offline candidate as a stable all-pages fix without regression checks.

## Early-boot scan test completed

The owner authorized a reversible test. `patch/package_settings_rom_scan_trial.py` packages the candidate under Magisk's `system/system_ext/priv-app/Settings/Settings.apk` path so Magisk mounts it before the package scan. Test ZIP SHA-256 `43f8174db8d01c367edfd0810a9a1820c92ea5061cc1116354afbf13f220d086`, module ID `fixo_settings_rom_scan_trial`. No partition was written.

After reboot, `sys.boot_completed=1`; the live Settings APK hash was the candidate `4d763c6c3a3fa15e7561d48434fce8b7373470ac5e0eec6adbbcc4cb11c1b098`. `pm path com.android.settings` resolved to `/system_ext/priv-app/Settings/Settings.apk`; `dumpsys package` retained `sharedUser=android.uid.system/1000`, `apkSigningVersion=3`, and signer hash `17e1e36b` (the same signer hash recorded before the test). The Settings launcher event reached a `com.android.settings` activity; process PID 2820 remained stable over seven seconds, and no Settings fatal exception or parse failure appeared in a focused recent logcat query.

This establishes that the current ROM's PackageManager accepts the modified Settings payload at boot when its original v3 signing block is retained. It does not yet establish that every Settings page works, nor that the original v5.3 module's `system.prop` and high-performance bridge are included: the trial contains only the APK. The trial remains installed for owner UI checks. To roll back: `su -c 'touch /data/adb/modules/fixo_settings_rom_scan_trial/disable'` followed by reboot; the ROM's base APK remains intact.
