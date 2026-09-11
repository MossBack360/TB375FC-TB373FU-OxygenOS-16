# OxygenOS 平板移植：全屏三点菜单与底角浮窗手势

本文记录 TB375FC/TB373FU OxygenOS 16 移植中两个独立功能的恢复方法。

## 1. 全屏应用顶部的三点菜单

这个功能本身没有被删除，SystemUI 里仍然有完整的菜单和处理逻辑。真正阻止它显示的是 SystemUI 内部的机型限制名单：

`NOT_SUPPORT_FULLSCREEN_WINDOW_DECOR_PRODUCTS`

移植包把当前机型识别成 `OPD2203`，而这个名单包含 `OPD2203`，所以全屏应用顶部不会显示窗口装饰菜单。

修复时只修改了 SystemUI `classes2.dex` 的字符串表，把名单中的 `OPD2203` 替换成名单里已经存在的另一个机型字符串 `OPD2408`。这样保留了原有判断逻辑和其他机型限制，只让当前机型不再命中这一条限制。

补丁通过 Magisk 在启动后绑定挂载修改后的 SystemUI，并检查原始 APK SHA-256；如果基底版本不匹配，就跳过修改，避免错误覆盖其他 ROM。

## 2. 从屏幕底角拖拽全屏应用切换为浮窗

这个功能的设置教程、动画资源和 `sScaleOpenFreeform` 条目原本都在 `OplusFlexibleWindowUI.apk` 中，国际版并没有完全删除它。

最初缺少的是系统特性配置。当前移植系统的：

`/my_product/etc/extension/com.oplus.oplus-feature.xml`

只有：

`oplus.software.pocketstudio.support`

而 ColorOS 平板配置还包含：

`oplus.software.wms.panorama_work_station`

FlexibleWindowUI 的设置界面只根据平板类型和属性显示教程，所以教程可以出现；底层窗口管理服务还会检查 `panorama_work_station` 特性，缺少它时不会注册实际的底角拖拽处理，因此手势无效。

独立的 `fixo_freeform_corner_gesture` 模块做了两件事：

1. 设置 `persist.oplus.panorama.branch.enable=true`，打开 FlexibleWindowUI 的分支条件。
2. 在 `post-fs-data` 阶段把带有 `oplus.software.wms.panorama_work_station` 的特性文件绑定挂载到原路径，确保 system_server 初始化时就能读到它。

同时把 `panoramic_forced_disable_state` 保持为 `0`。补丁没有修改 SystemUI、Launcher 或 Settings APK，因此和三点菜单补丁保持解耦。

修复后的系统日志会出现：

`FLAG_FULL_SCREEN_DRAG`、`finishDragAnimationAndStartFlexible`、`toggleToFlexibleTask`

这些日志表示底角拖拽已经进入窗口管理服务并完成全屏到浮窗的切换。

## 关键经验

- 先确认功能资源和代码是否仍在，再判断是 APK 缺失还是 feature gate 被关闭。
- UI 能显示不代表底层服务已经启用，设置页面和 WindowManager 可能使用不同的条件。
- 三点菜单是 SystemUI 的机型 denylist 问题；底角拖拽是 Oplus feature 配置与属性 gate 问题，两者应保持独立补丁。
