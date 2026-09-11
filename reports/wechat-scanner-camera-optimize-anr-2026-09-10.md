# OxygenOS 移植版微信扫一扫延迟与 ANR：`sys_camera_optimize_config.xml`

## 环境

- 设备：Lenovo TB375FC（小新 Pad Pro 12.7 2025，MT6897）
- ROM：基于 OPD2203 的 OxygenOS 16 移植版
- 微信：8.0.78，`com.tencent.mm`
- 故障页面：`com.tencent.mm.plugin.scanner.ui.BaseScanUI`

## 表现

- 从微信内部打开“扫一扫”，经常等待数秒后退回微信地球启动页，再返回主页。
- 进程没有直接闪退到桌面，容易误判为相机 HAL 打开慢或微信自身重载。
- 从桌面扫一扫小组件进入有时正常。
- 在任意比例的分屏模式下，扫一扫基本稳定，但进入页面仍可能等待几秒。

## 最初的误导线索

- 相机预览页是触发点，因此首先怀疑 CameraService、相机 HAL、SELinux 和 ZUI 相机组件。
- 分屏稳定、全屏失败，又使问题看起来像全屏标题栏、三个点菜单、平行视窗或焦点切换冲突。
- 针对微信平行视窗和全屏标题栏所做的 XML 兼容修改没有解决根因，最终全部撤销。

## ANR 证据

`dumpsys activity exit-info com.tencent.mm` 显示失败实际是微信主进程 ANR：

```text
Input dispatching timed out
com.tencent.mm.ui.LauncherUI is not responding
Waited 5000ms for FocusEvent(hasFocus=true)
```

主线程在 `BaseScanUI.onCreate()` 中同步调用以下路径并卡住：

```text
BinderProxy.transactNative
IActivityTaskManager.getTasks
ActivityTaskManager.getTasks
ActivityManager.getRunningTasks
com.tencent.mm.plugin.scanner.ui.BaseScanUI.onCreate
```

同一时间 CameraManager 线程处于空闲状态，也没有 SELinux `avc: denied`，因此“相机硬件打开太慢”不是直接根因。

## 最终根因

系统存在以下配置：

```text
/system_ext/etc/sys_camera_optimize_config.xml
```

原始内容只把两个扫码 Activity 加入优化名单：

```xml
<optimize_camera_cls_list>
    <cls>com.tencent.mm.plugin.scanner.ui.BaseScanUI</cls>
    <cls>com.alipay.mobile.scan.as.main.MainCaptureActivity</cls>
</optimize_camera_cls_list>
```

同时启用了全部四项策略：

```xml
<only_support_cls_list_switch>true</only_support_cls_list_switch>
<optimize_camera_cls_function_mask>1111</optimize_camera_cls_function_mask>
```

XML 注释和 `oplus-services.jar` 反编译结果表明，四项策略包括：

1. 内存释放（memory release）
2. 延迟组件启动（delay component）
3. 进程冻结（freeze）
4. 抑制 GC（GC suppression）

读取与执行代码位于：

```text
com.android.server.oplus.cameraoptimize.OplusOptimizeRUSHelper
com.android.server.oplus.cameraoptimize.OplusCameraStartupOptimization
```

`OplusCameraStartupOptimization` 监听 Activity/Usage 事件；类名命中名单且 `mEnable=true` 时，对对应应用进程执行启动优化。该策略原本用于减少大型应用进入扫码页时的内存和启动抖动，但在此移植系统上与微信启动、任务查询及焦点分发产生冲突，最终让主线程超过 5 秒没有处理焦点事件并触发 ANR。

分屏稳定很可能是因为分屏下任务和焦点路径不同，使这组启动优化没有形成同样的阻塞时序。它是定位线索，但不是最终修复点。

## 修复

原系统分区只读，因此没有直接修改或删除文件。独立 Magisk 模块在 `post-fs-data` 阶段 bind mount 一份有效但已关闭功能的 XML：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<filter-conf>
    <version>20260910</version>
    <only_support_cls_list_switch>false</only_support_cls_list_switch>
    <optimize_camera_cls_function_mask>0000</optimize_camera_cls_function_mask>
    <memory_release_value></memory_release_value>
    <optimize_camera_cls_list>
    </optimize_camera_cls_list>
</filter-conf>
```

模块：`fixo_camera_optimize_disable` v1.1
成品：`out/camera-optimize-disable-2026-09-10/fixo-camera-optimize-disable-v1.1-magisk.zip`

本 ROM 的 Magisk 不会自动挂载模块根目录中的 `system_ext`，因此必须在 `post-fs-data.sh` 中显式执行：

```sh
mount --bind "$MODDIR/system_ext/etc/sys_camera_optimize_config.xml" \
    /system_ext/etc/sys_camera_optimize_config.xml
```

重启后已通过文件内容和 `/proc/1/mountinfo` 确认覆盖生效。用户随后确认微信扫一扫恢复正常。

## 与其他相机修复的关系

ZUI 相机使用缩放倍率拍照时的崩溃来自 `libmorpho_HDSR.so`，由独立模块关闭 Morpho 超分处理。`sys_camera_optimize_config.xml` 的名单不包含 ZUI 相机，因此两项修复应继续解耦。

## 这类问题通常怎样被发现

最直接的方法不是从相机 HAL 开始追，而是搜索发生问题的完整 Activity 类名。这里对整个 ROM 执行：

```text
com.tencent.mm.plugin.scanner.ui.BaseScanUI
```

很快就会在 `sys_camera_optimize_config.xml` 中得到唯一且高度可疑的命中。再用 ANR 栈确认卡住的是 Activity/任务管理而非 CameraService，最后反编译引用该 XML 的 `oplus-services.jar`，就能建立完整证据链。

发现它的人也可能来自其他 ColorOS/OxygenOS 移植项目的经验：这类按应用设置的 OPlus 优化名单在原机上用于提速，换到不同 framework、vendor 或内存调度组合后，反而很容易成为兼容性问题。

## 可用博客标题

**微信扫一扫只在分屏里正常：一次由 ColorOS 相机“优化”引发的 5 秒 ANR**
