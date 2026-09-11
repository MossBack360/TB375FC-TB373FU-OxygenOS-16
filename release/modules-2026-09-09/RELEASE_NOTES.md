# TB375FC / TB373FU OxygenOS 16 修复模块 2026-09-09

本 release 面向 TB375FC / TB373FU 的 OxygenOS 16 移植系统，集中整理目前已经确认可用的 Magisk 模块。

## 模块说明

- `fixo-settings-easter-logo-only-magisk.zip`
  - 系统设置综合修复模块。
  - 包含设置首页图标与国际版头像素材、OnePlus AI 名称修正、关于本机顶部系统版本展示修复、OxygenOS 彩蛋动画素材修复，以及此前设置相关的累计修复。

- `fixo-global-apps-v1.0-magisk.zip`
  - 国际版 OnePlus 账号与国际版 OnePlus 相册组件。
  - 用于替换移植包里偏国内版的账号/相册体验。

- `fixo-ota-system-magisk.zip`
  - 恢复系统更新相关 APK、权限和入口。
  - 主要用于让设置里的系统更新入口正常跳转与展示。

- `fixo-zui-camera-privacy-v1.2-magisk.zip`
  - 修复 ZUI 相机中“用户协议”和“隐私政策”入口异常跳转/崩溃问题。

- `fixo-display-pq-v1.0-magisk.zip`
  - 修复显示与亮度里的环境色自适应、屏幕色彩模式入口。
  - 色彩模式切换存在明显延迟，这是目前已知表现。

- `xiaoxin-hall-confirmed-magisk.zip`
  - 盒盖/开盖常驻脚本版。
  - 不依赖系统设置开关，适合多数 TB375FC/TB373FU 相关 ROM 尝试。

- `xiaoxin-hall-settings-linked-v2-magisk.zip`
  - 盒盖/开盖系统开关联动版。
  - 根据系统“智能保护盖”开关决定是否启用合盖息屏、开盖亮屏。

## 安装建议

通过 Magisk 安装需要的模块后重启。两个盒盖模块二选一即可；如果你希望跟随系统开关，优先使用 `xiaoxin-hall-settings-linked-v2-magisk.zip`。

Settings 模块只需要安装本 release 中的最终版，旧的 Settings 测试包不需要再装。

## 未包含

Dolby 模块暂未发布。当前测试中设置界面、服务和参数路径可以触发，但实际音频处理没有可听效果，先保留为待研究问题。
