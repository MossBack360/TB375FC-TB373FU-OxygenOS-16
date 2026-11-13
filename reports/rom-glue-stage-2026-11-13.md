# ROM 胶水代码预备（2026-11-13）

运行 `python patch/prepare_rom_glue.py`，从 `temp3/稳定安装/01-当前启用-Magisk` 的历史 ZIP 提取已用过的脚本和依赖，输出到 `out/rom-glue-stage-2026-11-13/`。这一步没有编译镜像或操作平板；ZIP 目录名不代表当前设备启用状态。

## 已准备

- `system/etc/init/fixo-glue.rc`：为 AI providers、画质、底角模式、磁吸盖、扬声器旋转、注视屏幕、抬起亮屏、性能模式、通信共享准备独立 init 服务。**全部 `disabled`**，等待逐项审查后再启用。通信共享是 `oneshot`，其余保持前台主进程以供 init 监督。
- `system/etc/fixo/*.sh` 与 `pqctl.jar`、注视辅助 APK、抬起亮屏 DEX：保留原有行为；把日志、FIFO、锁文件从只读模块目录迁往 `/data/vendor/fixo`。性能模式直接以 shell UID 执行，不再调用 Magisk `su -Z`。原脚本的 `resetprop` 改为系统 `setprop`，实际属性权限须在目标 ROM 检验。
- `autobrightness-early.sh` 和四档曲线表：保留开机前选择曲线的代码，工作目录改为 `/data/vendor/fixo/autobrightness`。尚未编写 init 启动动作，因为必须先证实它在 framework 读取曲线前执行，且旧 `/data/adb/tb375fc_autobrightness/preset` 需要迁移。
- `zram-writeback.sh`：只保留运行期、温控和限额写回逻辑。未纳入 init RC，因为其动态 fstab/backing 配置需要在 Lenovo `swapon_all` 前完成；直接启动写回循环不能代替这一步。
- `SHA256SUMS.txt`：记录生成文件哈希。所有 11 个 `.sh` 已通过 WSL `sh -n`。

## USB 与相机

USB 固化直接用 `patch/prepare_usb_rndis_rc.py` 生成的原始 RC 加一条 `rndis,adb` 下 `start adbd` action。历史 25 号模块靠开机后轮询补拉 adbd，因此曾成功；把修复放进原始 RC 可在属性变化时立即触发。v3 工作树里另外两段 gadget 配置与 Lenovo vendor RC 重叠，正式合并时不应带入。生成文件为 `out/rom-solidification-prep-2026-11-13/init.usb.configfs.rc`。

现已把该最小 RC 放入 v3 工作树的 `system_a/system/etc/init/hw/init.usb.configfs.rc`，目标 SHA-256 `49835fc24c37f536ac3ce9428bb69cc94458adac7edcdf078f3e1c7671c10ebe`；被替换的旧 v3 文件备份为 `out/rom-solidification-prep-2026-11-13/v3-usb-rc-before-minimal-fix.rc`，SHA-256 `770e135e5b6a3d10a4ef0386999580b2d75fbb9046c6eba2ecc12d79367d8bb0`。未重建对应镜像。

相机 03 v2.0 主要是替换 `ZuiCamera.apk` 并设置 `debug.camera.morpho.sr.on=0`。原 ROM APK 有有效 v3 签名，证书是 `CN=Codex Debug`；修改版只改 DEX，却已没有有效签名块。直接放进 ROM 能否通过 PackageManager **尚未实测**。已准备保留旧签名块的早期扫描候选，详情见 `reports/zui-camera-rom-signature-prep-2026-11-13.md`；待用户测试相机后再定最终文件。不要把“系统应用路径”当成签名免检。

## 合并前检查

1. 先确定 v3/v4 最终基线及所有静态 APK/XML/属性的版本，避免把历史 17/20/22 号旧版与较新 SystemUI、Settings、CTS 一起放入。
2. 为每个 init 服务实测启动身份、SELinux、目录标签和依赖就绪时机，再逐一移除 `disabled` 并加启动动作。尤其测试性能模式 shell 域、通信共享 `ctl.*`、底角 `persist.*`、磁吸盖 input 节点。
3. 亮度及 ZRAM 写回要单独处理早期启动时序；未完成前继续使用各自已验证的模块，不在 ROM 中启动半套逻辑。
4. 充电关机动画待诊断；本次没有编译 super 或线刷包。
