# OPD2514 AI 与质感轮廓光移植记录

目标设备是 TB375FC/TB373FU（MT6897），当前移植系统为 OPD2203 来源的国际版 OxygenOS。对比包为 `OPD2514_11.A.28_0280_202605151142`，来自用户提供的 `ecb32008434b420c98515e3c41d5c4f1.zip`。

## AI 组件结论

当前系统已经有以下核心组件：

| 组件 | 当前系统 | OPD2514 | 结论 |
| --- | --- | --- | --- |
| AIUnit (`com.oplus.aiunit`) | 已有 | 已有 | 不替换 |
| AIWriter | 已有 | 已有对应能力 | 不替换 |
| Metis (`com.oplus.metis`) | 已有 | 已有 | 不替换 |
| DeepThinker (`com.oplus.deepthinker`) | 已有，版本号同为 16.0.160 | 有，文件哈希不同 | 暂不替换，避免覆盖已验证环境 |
| AONService (`com.aiunit.aon`) | 15.0.73 | 16.0.09 | 暂不升级，避免影响现有传感器/系统行为 |
| AIPaint (`com.oplus.aipaint`) | 缺失 | 16.0.38 | 可单独加入 |
| Google Gemini (`com.google.android.apps.bard`) | 缺失 | 1.0.795460806 | 可单独加入 |

OPD2514 的 `appfeature.ai_front_apps.xml` 与当前系统字节一致，不是缺失总开关。AIPaint 的清单明确依赖 `AIUnit`、`Metis` 和 AssistantScreen；当前核心依赖已经存在。Settings 中 AI 页面主要由外部组件的入口元数据动态发现，不适合直接替换整包 Settings。

已生成独立模块：

`out/opd2514-ai-addons-2026-09-10-v1.1/fixo-opd2514-ai-addons-v1.1-magisk.zip`

模块只加入 AIPaint 和 Gemini，不覆盖 AIUnit、AIWriter、Metis、DeepThinker、AONService、Settings 或 SystemUI；同时保留 `/my_product` 目标存在时的挂载回退日志。

## 质感轮廓光结论

OPD2514 的 SystemUI/Launcher 没有 ColorOS 的完整轮廓光消费链，只有较早的 AGSL 描边基础类。ColorOS 基线额外包含 `NotificationEffectRepository`、`CalculateGradientStrokeTools`、`BlurStroke`，以及 `BlurConfig` 到 `PlatformBlurDrawable` 的参数传递。当前 Oxygen 的 `BlurConfig` 没有这些参数，`PlatformBlurDrawable` 也没有把参数送入 `BaseDrawable`，所以只改 Settings 开关不会产生桌面或控制中心效果。

已生成独立试验模块：

`out/material-stroke-render-trial-2026-09-10/fixo-material-stroke-render-trial-v1.0-magisk.zip`

该模块仅向当前 Oxygen SystemUI 的平台模糊绘制步骤注入一组渐变描边参数，保留原 APK 的全部资源和其他 dex。它带原始 SystemUI SHA-256 校验；版本不匹配时跳过，重启 SystemUI 后 30 秒内不稳定则自动卸载挂载并禁用模块。它是渲染链路诊断包，不是完整 ColorOS SystemUI 替换。

主机验证已通过：模块 ZIP 无损、嵌入 APK 条目完整，除 `classes5.dex` 外其余 dex 与资源字节保持一致；当前解包源已恢复为未修改状态。
