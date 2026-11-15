# Magisk 31.1 升级与充电采样，2026-11-15

设备：Lenovo TB375FC，当前 slot `_a`，原运行核心 Magisk 30.7 (30700)，电池测试时约 94–95%。用户授权升级 Magisk 并采集充电状态。

## 充电

只读脚本 `patch/charge_probe_readonly.sh` 每 10 秒读取电量计、电池电流、电压、charge counter、主充电器在线/限流/状态，最多运行 30 分钟；输出 `/sdcard/Download/tb375fc-charge-probe.csv`。首次采集从 94%/9,588,000 µAh 上升到 95%/9,690,000 µAh，系统及原厂电量计都报 `Charging`，USB 在线，主充电器输入限流节点报 `500`。因此“完全没有充进电”与当前实测不符；接近满电时的瞬时电流和百分比变化不宜单独解释为故障。升级尝试导致的正常重启后，探针已续接同一 CSV。

## 升级尝试

官方 `Magisk-v31.1.apk` 从 GitHub v31.1 release 下载，SHA-256 `89cefac0a318afa39fb3880c45c87b036c05bc1ebf02a7a715b7f8d7c26ac6e7`，与 GitHub release asset digest 相同。安装 App 后通过“直接安装（推荐）”升级；UI 明示目标 `/dev/block/by-name/init_boot_a`、`Installing 31.1`、`Flashing new boot image`、`All done!`。但正常重启后 daemon 仍是 30.7，`init_boot_a` SHA-256 与升级前完全相同，证明这次直接安装没有让核心升级生效。App 与 `/data/adb/magisk` 中的工具已是 31.1。

升级前备份并拉回电脑：`init_boot_a` SHA-256 `301b05071bde4a4ad8a214818b2df1d0d088909832cc80d3c4504e11f3ec6fea`，`boot_a` `eaa05f16578fb9c70a7931b87577096509ee4423d11db43b41abfb044e97e2bf`，`vendor_boot_a` `6b9756006e529db948ce17411cfb0bc9ad375196fcfffdc2a2f24fb2350ce1c7`。电脑目录 `temp3/magisk-upgrade-2026-11-14/`，不入 Git。

在平板隔离目录使用 Magisk 31.1 官方 `boot_patch.sh` 对**本机备份**的 `init_boot_a` 离线修补，生成 8 MiB 镜像 SHA-256 `f796abb6cdc36175236debf338c14c6e8d4df4efb613220f67935e4f2814ab6f`；新镜像内 `/init` 与 31.1 `magiskinit` SHA-256 均为 `c0c7cc1c8e1afb92bff602164f6aa1bb4103f5028d076216d8bef48496e2f4dc`。这证明可构建不同于旧镜像的 31.1 补丁。

设备进入 bootloader fastboot 后，serial `HA2FNXNQ`、product `P98300DA1`、current-slot `a`，但 `unlocked: no`、`secure: yes`，故**没有执行 fastboot flash 或解锁**。已 fastboot reboot 返回 Android；`sys.boot_completed=1`、Magisk 30.7 root 与原模块仍正常，充电状态为 Charging。新镜像只保留在电脑作为研究产物，未写入分区。

官方文档明确提醒某些 MTK 设备会在开机后锁定 boot 分区，需要在设备上修补镜像并通过 recovery/fastboot 写入；该机制与直接安装未生效吻合，但本机锁定原因仍未被日志完全证明。Magisk 31.0 起的 `magiskinit` 调整 charger/`force_normal_boot` 判断顺序，是本次考虑升级的原因。核心仍为 30.7，故 Magisk 安全模式问题未解决。
## 同日后续：从原版镜像完成 Magisk 31.1

用户提供 `C:/Users/GY/Documents/MEGA下载/initboot oxy/init_boot.img`，8 MiB，SHA-256 `7138f0e13e396c57e6860b24c1f9ddb9fec77a7400347f6231ac36aab533602b`，与真机 `init_boot_b` 完全一致。将当前 A 槽 Magisk 30.7 镜像的 ramdisk 恢复到 stock 后，与该原版 B 槽 ramdisk 对照，文件列表及逐文件内容均一致；CPIO 整体哈希不同是打包/元数据差异。用真机上的官方 Magisk 31.1 `boot_patch.sh` 修补用户原版，输出 SHA-256 `f796abb6cdc36175236debf338c14c6e8d4df4efb613220f67935e4f2814ab6f`，与早先从 A 槽旧补丁镜像恢复后修补的输出**完全相同**。

Android 报 `ro.boot.verifiedbootstate=orange`、`ro.boot.flash.locked=0`，与 fastboot 的 `unlocked: no`、`secure: yes` 相矛盾。用户明确要求刷入，经当前 slot `a`、镜像哈希、电量和回退文件复核后，执行 `fastboot flash init_boot_a`；设备返回 `Sending OKAY`、`Writing OKAY`。重启后 `sys.boot_completed=1`、Magisk daemon `31.1:MAGISK:R` / `31100`、`init_boot_a` 读取哈希与补丁一致，root 与 charger v0.4 模块挂载正常。先前“未刷入”的结论仅适用于第一次直接安装尝试，现已被后续成功刷入取代。原始 A 槽镜像及成功补丁均保存在 `temp3/magisk-upgrade-2026-11-14/`，不入 Git。

已存在的其他模块 `disable` 标记时间为前一日 15:24，早于本次刷入；本次没有因此新增 charger 模块停用标记。Magisk 31.1 是否避免关机充电后的安全模式，仍需实际关机充电循环验证。
