# 全屏窗口菜单模块

适用于本工程实测的 TB375FC OxygenOS OPD2203_16.0.5.1000(EX01) 移植包。用户已确认顶部三点菜单恢复，模块已通过开机自动挂载检查。

构建：`python patch/build_fullscreen_caption.py`。脚本要求原 SystemUI 的指定 SHA256，输出目录为 `out/fullscreen-caption-trial-2026-09-09/`。用户确认版本另存于 `out/fullscreen-caption-confirmed-2026-09-09/`。

安装模块后重启即可生效，开机阶段会短暂重启 SystemUI。无需修改整机型号，也不修改 Settings APK。模块 ID 为 `fixo_fullscreen_caption`。与其他替换 SystemUI 的模块可能覆盖同一路径，因此运行时核对原包哈希，版本不符则跳过。

回退：在 Magisk 停用此模块并重启。详细证据及验证范围见 `reports/oxygen-caption-and-stroke-2026-09-09.md`。
