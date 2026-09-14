# Attention user-activity helper

This minimal app-process entry point calls `PowerManager.userActivity()` without generating an Android key or touch event.

Build with the repository's apktool and copy the result into the module tree before packaging:

```powershell
java -jar tools/apktool_3.0.3.jar b patch/attention-useractivity-helper -o patch/modules/fixo_attention_asi/attention-useractivity.apk
```

Confirmed helper APK SHA-256: `755a62d642204de06737a28325825634b25f4eb66f55f83b418d5bd9f32217fa`.
