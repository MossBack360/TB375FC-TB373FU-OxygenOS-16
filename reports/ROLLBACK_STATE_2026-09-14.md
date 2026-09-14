# 2026-09-14 夜间回滚状态

> Historical failure snapshot only. The owner subsequently clean-flashed the port and confirmed the staged 12-module restore documented in `confirmed-module-milestone-2026-09-14.md`. Do not treat the AI-enabled state below as current.

## 当前平板状态

- `fixo_freeform_corner_gesture` v1.2：启用。恢复确认版 Panorama/底角特性表。
- `fixo_opd2514_ai_addons` v2.5：启用。AIMemory、AIPaint、DMP 均存在。
- `fixo_ai_a30_restore` v1.0：停用，避免与 AI v2.5 重复。
- `fixo_fullscreen_caption` v0.5：已安装但自动停用。当前环境加载它后 SystemUI 不稳定，运行日志为 `SystemUI unstable; restored original and disabled trial`。
- `three_finger_flash_memory_enable=0`；当前生效特性表无 `finger_flashnotes_enable`，因此不启用三指上滑。
- 当前 `/system/framework/oplus-services.jar` 为原始 SHA-256：`54FDE217F7B0E3CDDEB0FF5A0AE9F6D13CE1314E502E7E6FB12ADBD660A91CD4`。
- 当前 `/system_ext/priv-app/SystemUI/SystemUI.apk` 为原始 SHA-256：`72CFA6810C72D7AEF8CFDFD8F57EE8F88117C2B5867F272D3700A08FE3C32DC7`。
- 当前特性表 SHA-256：`DBCE47F3238EBD2EAF23D8BE343BCC95CFA13060ECDC0F6A6CF91DE500250568`，包含 `oplus.software.wms.panorama_work_station`，不包含三指 feature。
- 回滚后 SystemUI PID `2275`、system_server PID `1297` 连续检查稳定。

## 包位置与版本

1. 底角拖拽确认版 v1.2
   `E:\工程\github\xiaoxin Oxygen\fixO\out\freeform-corner-gesture-confirmed-2026-09-10\fixo-freeform-corner-gesture-confirmed-v1.2-magisk.zip`
   SHA-256：`E14F8D9F3A787AD31725F4861848CAD9987B7128B7FAD750DAA62AD12935C7F4`

2. OnePlus AI / Mind Space v2.5
   `E:\工程\github\xiaoxin Oxygen\temp\opd2514-ai-addons-v2.5-2026-09-12\fixo-opd2514-oneplus-ai-v2.5-magisk.zip`
   SHA-256：`18BC794E4D23CBF528055B63BF9CB2D73857AA0A2B54A336D0163AC025521CAF`

3. 三点菜单/SystemUI v0.5（当前环境不兼容，勿直接启用）
   `E:\工程\github\xiaoxin Oxygen\fixO\out\systemui-gesture-polish-v0.5-2026-09-11\fixo-systemui-gesture-polish-v0.5-magisk.zip`
   SHA-256：`DAE75D0B2D274C1224714316434E4BB60CBC49F6E74D1E73EF45F07B931CF3E2`

4. A.30 AI v1.0 备份（当前停用）
   `E:\工程\github\xiaoxin Oxygen\fixO\out\ai-mindspace-working-20260914\fixo_ai_a30_restore-working.zip`
   SHA-256：`25436E191972CC8D4BC514687454A4FEC7ACB2C43B30019E923FFB69F07FA7E4`

## 今晚放弃的试验

`fixo_freeform_corner_gesture` v1.4 把 `OplusPanoramaWorkBranchUtil.hasTabletPanoramaWorkFeature()` 从 `false` 改为 `true`。它能让 `PanoramaWorkBranchBaseController` 实例化并输出 `hookStartActivity`，但用户测试仍报告底角注册失败，因此已用 v1.2 覆盖，不得当作确认修复。

归档目录：
`E:\工程\github\xiaoxin Oxygen\fixO\out\panorama-tablet-gate-v1.4-abandoned-2026-09-14\`

## 明日继续

- 三点菜单：不能直接复用 v0.5；当前 SystemUI 会在 `SeedlingCardProvider.attachInfo` 处因 `SeedlingPluginManager` 为 null 而反复重启。
- 底角：v1.2 已恢复；先由用户确认实际手势，再决定是否继续追输入监听注册链。
- AI：保持 v2.5，不再同时启用 `fixo_ai_a30_restore`。
