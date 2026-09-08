# fixOxygen 兼容补丁归档

这里是原先独立的 `fixOxygen` 工作目录在本工程中的源码归档入口。可提交内容只保留补丁脚本和说明；原始 Settings APK、framework 镜像、签名密钥、ROM 解包目录、`platform-tools` 和生成的刷入包均由上层 `.gitignore` 排除。

新的脚本统一放在工程根目录的 `patch/`，避免两套同名构建脚本继续分叉。该目录中的历史脚本仅用于追溯早期修复过程。
