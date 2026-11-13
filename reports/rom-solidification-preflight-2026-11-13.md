# TB375FC OxygenOS ROM 固化预审（2026-11-13）

本文件只整理输入与实施路线；本轮没有编译、改镜像或操作平板。`temp3/稳定安装/01-当前启用-Magisk` 是历史归档名称，**不是**当前真机模块清单。以 `reports/CURRENT_HANDOFF.md` 中较新的实测记录选版本，不把旧 ZIP 全部叠加。

## 已有阶段成果

- v3 工作树 `temp3/OxygenOS_16.0.5_TB373FU_TB375FC_v2/v3/` 已有 system/product/system_ext 文件树及部分重建的逻辑镜像，但尚未生成最终 super。它的静态配置和 AI 文件是阶段性成果，需按本表与最新模块校准。
- v4-cts 工作树同目录的 `v4-cts/` 已有 Circle to Search 的 product 与 system_ext 逻辑镜像；尚未组装 super、未修改线刷脚本。其 SystemUI v0.8 及 framework overlay v0.3 经早期扫描/实机圈搜测试；Eta 在该测试中停用。
- Gallery-only v1.1 在 `稳定安装/07-待固化/02-global-apps-gallery-v1.1-gallery-only.zip`，替代旧 02 v1.0 的双 APK 方案。只把 Gallery 纳入固化，不纳入 KeKeUserCenter。

## 直接放入 ROM 的静态内容

| 来源 | 固化落点或方法 | 注意 |
|---|---|---|
| 02 v1.1 Gallery-only | 原 `/my_stock/priv-app/OppoGallery2/OppoGallery2.apk` | 旧 v1.0 的 UserCenter 不带入；核对 APK 签名/版本与实际包扫描。 |
| 05 AI providers v2.9 | 官方 AIMemory/AIPaint/DMP APK 与所带 lib/权限 XML；`/my_stock/etc/config/app_v2.xml`、`/my_product/etc/extension/appfeature.ai_front_apps.xml` | 要把 AI、三指、自由浮窗、通信共享的 `com.oplus.oplus-feature.xml` 合成**一份**，不能按模块挂载顺序覆盖。05 的运行时 setting 同步另列。检查分区空间；v3 曾报告约 164 MB 容量压力。 |
| 06 OTA、07 Lenovo 隐私、24 通信前端 | 各 ZIP 的 `system/...` 原路径 APK/权限文件 | 按包逐个核验签名与 priv-app 权限，不把“看起来原厂”当作已验证。 |
| 08 相机优化、15 智能刷新 | 直接替换 XML | 不再保留 bind 脚本。 |
| 10 底角浮窗特性、23 通信特性 | 合并 `/my_product/etc/extension/com.oplus.oplus-feature.xml` 一次 | 10 的模式联动、23 的启动时序仍属运行时逻辑，静态特性表不能替代。 |
| 16 转场圆角、19 机型名、20/30 Settings 属性、12 扬声器属性、23 通信属性 | 合并到对应分区的 build.prop/default prop；按每项真实归属与启动时机核对 | 不能简单把 Magisk `system.prop` 原样拼到一个文件；重复键和持久属性需去重。 |
| 22 圈搜 | 采用较新的 `fixo_circle_to_search` v0.3：feature XML + `FixOCtsFramework.apk` RRO | 旧 v0.2 只有 feature XML，不能代替当前无 Eta 方案。 |
| 27 横屏 Homebar | RRO 放原 product overlay 路径 | 保留 overlay 的目标包、优先级与签名状态。 |
| 28 PiP 圆角 | 对应版本的 `system_ext/lib64/librenderengineextimpl.so` | 原库仅做过极小函数补丁；先核对源库哈希及依赖，不迁入 ColorOS 整套图形库。 |

## 修改过的 APK：包扫描与签名

- **Settings**：当前已验证的候选是 `reports/settings-rom-signature-audit-2026-11-12.md` 记录的 v5.3 APK + 原 ROM v3 签名块，早期挂载后保持 UID 1000/原 signer hash，设置能启动。固化应以该候选字节替换 `/system_ext/priv-app/Settings/Settings.apk`；旧 20 ZIP 的开机后 bind 脚本与 30 的属性/桥接功能分开。全页回归尚未完成。
- **SystemUI**：无 Eta 圈搜的 v0.8 早期扫描候选，已实测 Homebar 长按圈搜。构建脚本以已确认的 v0.6（26px 拖拽圆角）APK 为源，其 SHA-256 `d5ecf22aa1c6fc3945a508c008af06554e3a1e6bcda9380258a9b266f821bf26`；离线比较 v0.8 与该源的 8620 个 ZIP 条目，仅 `classes6.dex` CRC 改变。因此 v0.6 的其他修复字节已保留，不需要再并装旧 17 模块。仍需最终 ROM 回归三点/底角/圈搜。
- **ZuiCamera**：03 v2.0 也是改过的 APK，只有 `classes.dex` 与原 ROM 不同。原 ROM APK 的 v3 签名可验证，证书是 `CN=Codex Debug`（本移植包自身的证书，不能称为联想原厂）；v2.0 补丁 APK 缺少可用的 v2/v3 签名块。已准备保留 ROM 签名块的离线候选，详见 `reports/zui-camera-rom-signature-prep-2026-11-13.md`。不能直接复制后宣称可启动。
- APK 逐包验证：v1.1 Gallery 为有效 OnePlus v3 签名；05 AIMemory/AIPaint/DMP、06 OTA 为有效 Oplus 签名；07 ZuiLenovoPrivacy 为有效 Lenovo 签名；24 GoogleDialer/Messages 为有效 Google 签名。RRO APK 仍须在合并时检查目标包/overlayable 策略；“APK 签名有效”不单独证明系统集成可用。

## 运行时胶水：要保留行为，不必保留 Magisk

| 来源 | 运行时动作 | 固化方向 |
|---|---|---|
| 03 相机 SR | 设置 `debug.camera.morpho.sr.on=0` 并替换改过的 ZuiCamera | 属性入 ROM；APK 签名问题先解决。 |
| 05 AI providers | 启用 AI 包并持续维护 DMP setting | 若静态默认与开机数据迁移能替代轮询，优先简化；否则 init 管理的前台服务。 |
| 09 PQ、11 磁吸盖、12 扬声器旋转、13 注视屏幕、14 抬起亮屏、26 自动亮度 | 监听设置/输入/传感器并向 HAL 或系统服务发送动作 | 需要持续进程或系统组件；作为 init service 时保留原调用权限、重连与日志，不能只复制配置。 |
| 18 ZUI ZRAM writeback | 每次开机根据设置值生成 fstab backing size，随后进行有温控/限额的写回 | 静态 fstab 无法覆盖“关闭/2/4/6/8GB”等动态选择；需早期 init 阶段生成配置并保留周期任务，或改为等价的原生服务。 |
| 21/30 性能模式 | 监听 `high_performance_mode_on` 并以 shell 身份调用 PowerManager | 30 已含 20 的属性及桥接，不能与 21/旧 20 脚本重复启动；init 的 UID/SELinux 上下文需要单独验证。 |
| 23 通信共享 | 按 ColorOS 时序设置持久属性、拉起 modem/subsys/virtual RIL | 用 init 属性动作及受管理服务重现顺序；不能只放 feature XML 和前端 APK。 |
| 10 底角模式 | secure settings 与 panorama property 联动，按模式重启相关组件 | 若 ROM 只需默认底角行为可静态简化；如保留运行中切换，仍需服务/框架监听。 |

Android init 对**非 `oneshot`** 的 service 退出会重启，但它只监管该 service 的主进程：脚本若把 daemon 放后台并立即退出，会导致重复拉起。服务要以前台运行/`exec` 主程序，并明确 class、启动条件、user/group、SELinux、文件标签与重启策略。服务不会被 PackageManager 按 APK 签名当成应用卸载，但若权限、SELinux 或依赖初始化时机错误，仍会失败或重启循环。参考：https://android.googlesource.com/platform/system/core/+/main/init/README.md

## USB 网络共享：明确的一处差异

原始 v2 的 `/system/etc/init/hw/init.usb.configfs.rc` 缺少 `rndis,adb` 下的 `start adbd`；`25` 模块用轮询 `ctl.start adbd` 已实测 RNDIS tethering 成功。历史记录见 `temp3/USB网络共享正确修复方案.md`。ROM 固化优先加入：

```rc
on property:sys.usb.config=rndis,adb && property:sys.usb.configfs=1
    start adbd
```

但 v3 工作树当前文件**已经加入**这段，而且额外加入纯 `rndis` 与 `sys.usb.ffs.ready=1` 两段配置动作（与 v3 的 `originals-before-v3/init.usb.configfs.rc.original` 比较确认）。联想 vendor RC 已有 RNDIS gadget 动作；旧实测仅靠 `25` 模块启动 adbd 后就能完成 tethering。因此正式合并以原始 v2 为基线，只补上述 `start adbd` 动作；v3 多出的两段 gadget 配置不要照搬，以免同一配置事件同时创建函数/写 UDC。`25` 过渡轮询模块在 ROM 修复确认后移除。

已通过 `patch/prepare_usb_rndis_rc.py` 生成**尚未并入镜像**的最小版本：`out/rom-solidification-prep-2026-11-13/init.usb.configfs.rc`，SHA-256 `49835FC24C37F536AC3CE9428BB69CC94458ADAC7EDCDF078F3E1C7671C10EBE`。与原始文件的 diff 只有上面一个 init action（三行含空行）。

## 版本决策与未开始事项

1. 不把 `01-当前启用-Magisk` 里旧 17 v0.6、20 v5.3 后置挂载、22 v0.2 与较新早期扫描候选同时固化。Settings 采用已通过包扫描的候选；SystemUI 采用从 v0.6 继承全部其他条目的 v0.8 候选；圈搜采用 v0.3 RRO/feature 配套。
2. 先把关机充电动画问题诊断完，再合并镜像和线刷脚本。`charger` 二进制及资源见 `reports/offmode-charger-2026-11-13.md`，本轮不触碰。
3. 本清单是设计/审计，不等于所有模块已能无脚本固化，也不等于已完成分区容量、SELinux、VINTF、签名与全页回归。

## 2026-11-13 胶水与 USB 工作树更新
运行期代码已由 patch/prepare_rom_glue.py 暂存；服务仍 disabled，详情见 reports/rom-glue-stage-2026-11-13.md。最小 USB RC 已复制进入 v3 的 system_a 工作树，旧 v3 RC 保存在 out/rom-solidification-prep-2026-11-13/v3-usb-rc-before-minimal-fix.rc；未重建镜像。
