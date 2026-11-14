# ZuiCamera v2.0 ROM 固化签名预审（未刷机）

- 原 ROM `/system/priv-app/ZuiCamera/ZuiCamera.apk` SHA-256：`6752402e1d1f2308941d50aaf056f9a69246337884f7cc1b9a7905b9f5f2c9ba`。`apksigner verify` 通过 v3 签名；证书 `CN=Codex Debug`，SHA-256 `27a4b619c35bc5d0d6d54071ad22a6f0f62e3d0b67bf52845861b2de3857cfec`。
- 03 v2.0 补丁 APK SHA-256：`42e55eb755521791ac757e6c8ca1d0b1c6b6fcdf02e7a29004a126fcface1676`。2798 个 ZIP 条目同名，仅 `classes.dex` 的 CRC 不同；补丁实现见 `out/zui-camera-sr-runtime-fix-v2.0-2026-09-14/README.md`。它独立执行 `apksigner verify` 失败，报告缺少 v2/v3 签名块。
- 原模块 `fixo_zui_camera_sr_disable` v2.0 在 `sys.boot_completed=1` 后以 bind mount 覆盖同一路径，另维持 `debug.camera.morpho.sr.on=0`。因此过去的可用性**不等于**修改版 APK 在包扫描阶段可用。
- `patch/prepare_zui_camera_rom_apk.py` 从哈希锁定的原 ROM APK 复制 4096 字节 v3 签名块到补丁 APK，只调整 ZIP central-directory offset；输出 `out/zui-camera-rom-scan-2026-11-13/ZuiCamera-v2-rom-signing-block-candidate.apk`，SHA-256 `7A21A0C3F28B1EB715DBBB9BD4A1BE5E3722EEF4F998DE100C68BD58A4BEB862`。候选 ZIP 条目和 CRC 与 v2.0 补丁完全一致。
- 候选的 `apksigner verify` 仍报告预期的 v3 内容摘要不匹配；这**不是**有效的独立安装 APK。Settings 曾用同类候选通过该移植 ROM 的早期系统包扫描，但相机本身尚未做早期扫描/实际启动测试。现在只保留离线候选，不写入 ROM。
- 固化时还需把 `debug.camera.morpho.sr.on=0` 放到有效的属性源，避免只复制 APK 丢失该功能门。

## 2026-11-14 实机结果

原始 v2.0 修改 APK 早期挂载后未被 PackageManager 注册；保留原 ROM v3 签名块的候选早期挂载后被注册，用户确认相机预览及拍照正常。确切 A/B 和回退记录见 `reports/zui-camera-early-scan-trial-2026-11-14.md`。相同候选与属性已放入 v3、v4-cts 解包工作树，尚未重建镜像。
