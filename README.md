# Xiaoxin Pad Pro 2025 OxygenOS 移植修复

这个仓库保存 TB375FC（MT6897，OPD2203）移植 OxygenOS 的分析记录、反编译补丁和 Magisk 模块构建脚本。

## 目录

- `patch/`：Settings、系统更新、翻盖、ZUI 相机隐私入口和 Dolby 试验模块的构建脚本。
- `hall/`、`hall-v2/`：翻盖传感器常驻模块源码。
- `build/`：可复用的模块文件树（原始 ROM APK 不提交）。
- `reports/`：对照测试和问题记录。
- `fixOxygen/`：原来独立目录中保留下来的兼容补丁源码；原始 ROM、解包缓存、工具和密钥已忽略。

ROM 解包目录、设备拉取文件和生成的刷入包体积很大，且包含厂商专有文件，因此只在本地保存，不进入 Git 历史。重新构建脚本需要把对应官方 ROM 提取结果放在被脚本引用的本地 `out/` 或 `work/` 目录。

## 已确认的模块

- `fixo_settings_confirmed`：Settings 主界面、国际版图标/文案、关于本机红蓝卡片和彩蛋素材。
- `fixo_ota_system`：系统升级入口及权限白名单。
- `xiaoxin_hall_cover`：翻盖状态与息屏/亮屏联动。
- `fixo_zui_lenovo_privacy`：ZUI 相机的用户协议和隐私政策 Activity。
- `fixo_dolby_dap`：在 OxygenOS vendor 已有 Dolby 库上补注册 DAP，并恢复 DaxService；仍属于试验模块。

设备实测问题和后续计划见 `KNOWN_ISSUES.md`。
