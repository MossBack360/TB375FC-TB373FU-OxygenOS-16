# 已确认正常的 Settings：2026-09-06

用户在真机临时覆盖后明确确认：“你现在给我刷的这个已经修复问题了”。本目录保存的是当时设备实际挂载的同一份 APK，已通过 SHA-256 对照，不是相邻 fixOxygen 目录中的重新签名版本。

## 文件

- `Settings.apk`：真机确认修复问题的版本，仅用于当前移植 ROM 的系统覆盖，不是可直接点击安装的普通 APK。
- `fixo-settings-confirmed-magisk.zip`：包含完全相同 APK 的 Magisk 模块；已检查 ZIP 内容和校验值，尚未刷入、尚未进行重启验证。后续可在 Magisk 的“模块 → 从本地安装”中选择。模块只覆盖 Settings。
- `patch/`：代码补丁、构建后的离线校验脚本与归档脚本。
- `SHA256SUMS.txt`：本目录文件校验值。
- `current-vs-xiaoxin.patch`：当前原包与小新 ColorOS 参考包的代码差异。

APK SHA-256：`6d92c4dc3e3d7b169c57592e673eb4077a6f9fd503fe7fba7608ec771af8ebce`

## 设备与适用版本

- 小新 Pad Pro 2025，MT6897，实际设备代号 TB375FC。
- 当前 ROM 显示 OPD2203_16.0.5.1000(EX01)，Android 16，Magisk 30.7。
- 设备的 Settings 路径：`/system_ext/priv-app/Settings/Settings.apk`。
- 原 Settings SHA-256：`7520229a7f190d35d86a4b1945b03966a49df61aa90799f57904011fdba71c12`。
- 原 framework.jar SHA-256：`60ea788ac729e8f39c40c287ab91f65ce8575b2f4e560172d1d8de2add1cef37`。
- 原 oplus-framework.jar SHA-256：`d1e6ce599c0d154b784c968894eec7dea72b16d8349d9eb59d2e14b8987924da`。

## 修补与验证范围

当前底包缺少 `OplusMultiAppManager.getMultiAppUserInfoList()`，导致应用列表读取隐藏分身应用时崩溃。修补在 AppManagerUtils 中增加一个适配方法，用已有的 getMultiAppUserHandle 与 UserManager 获取真实分身用户，返回调用方所需的列表。全部 5 处调用统一使用这个方法。

涉及 AppManagerUtils、OAIDPreload、OplusNotificationAccessSettings、FoldDatabaseHelper、AppLandscapeManager。仅 classes2.dex 内容改变，其余 DEX、Manifest、资源、原生库、原有 META-INF 文件内容均保留；未重新签名、未修改 framework 或 SELinux 策略。保留原有签名元数据不代表修改后的 APK 拥有有效的原厂完整签名。

已通过 DEX 编译、重新反汇编、5 处调用检查、替代 API 检查、ZIP CRC、DEX SHA-1/Adler32 和未压缩文件对齐检查。设备临时覆盖后设置首页与应用管理 Activity 成功启动，Settings 进程保持运行；用户随后确认问题修复。未声称所有设置页面、分身状态或重启后模块均已完成回归。

## 保存时的设备状态

设备使用临时 bind mount，将 `/data/local/tmp/fixo-settings.apk` 覆盖至上述 Settings 路径。没有刷入永久模块，没有重启；重启会撤销临时覆盖并恢复原系统包。

如需当次运行中撤销临时覆盖，可在已授权 Root 的 ADB 下执行：

```sh
adb shell su -mm -c 'umount /system_ext/priv-app/Settings/Settings.apk'
adb shell am force-stop com.android.settings
```

若以后安装本归档模块，可在 Magisk 禁用该模块并重启恢复原包。不要与旧 oxygen_settings_fix 模块叠加使用，以免覆盖顺序导致加载另一份 APK。模块打包结构依据 [Magisk 官方说明](https://topjohnwu.github.io/Magisk/guides.html)。

## 反编译及复现资料

工作区 `work/current`、`work/xiaoxin-color`、`work/opd2403-color`、`work/opd2403-oxygen` 保留四份原始包的完整 smali 代码，资源以原始形式保留。`work/assemble` 是仅用于重建 classes2.dex 的修补工程。`work/framework` 与 `work/oplus-framework` 仅保存本次依赖的 API 代码摘录，来源为相邻工作区中与本次输入哈希一致的 framework 反编译结果。

当前原包与小新 ColorOS 包的所有 ZIP 条目中，只有 classes2.dex 不同；反汇编后唯一代码差异是 RamExpandSizePreference.onProgressChanged 对内存扩展属性的写入。因此小新参考包并未修复本次缺失接口问题。两个 OPD2403 参考包的 AppManagerUtils 没有当前版本的 getHideMultiApps 实现。

在工作区根目录重新构建现有修补工程：

```powershell
java -Xmx2g -jar tools/apktool_3.0.3.jar b -j 4 --no-apk work/assemble
python patch/package_apk.py --system-overlay
```

原始输入仍在工作区 `extract` 中，未修改。本归档请保留，不要作为后续试验输出目录。
