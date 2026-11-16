# Attention ROM stage and SystemUI open issue — 2026-11-16

## 13 Screen attention

The previously tested ASI attention module is archived at `temp3/稳定安装/01-当前启用-Magisk/13-screen-attention-asi-glue-v0.2-trial.zip` (SHA-256 `9f698dc411a1eaf600b58e425ab20e037f7a4ab4bee1182ea1df5200d8069374`). Earlier v0.1 testing with a 10-second timeout kept the display awake for 25 seconds while watched; v0.2 was later owner-confirmed working. The current tablet has no `fixo_attention_asi` Magisk module, and `Settings.Secure.adaptive_sleep` is unset, so this feature is not active now.

`patch/stage_attention_rom.py` staged the archived helper and listener into v5 `system_a` as `system/etc/fixo/attention-useractivity.apk`, `system/etc/fixo/attention.sh`, and `system/etc/init/fixo-attention.rc`. Exact fs_config and file-context entries were added. The init service starts after `sys.boot_completed=1`, runs in shell SELinux context, follows the adaptive-sleep switch, registers Google ASI, and refreshes PowerManager user activity when attention is detected. The staged script passed `sh -n`; a short shell-domain probe successfully selected ASI and invoked the helper. The testable Attention service was restored to its original SystemUI AON component afterward. A live ROM boot, first-run ASI permissions, and gaze behavior remain unverified. No v5 `super.img` was built or flashed.

## SystemUI corner fallback

The owner reported that multi-finger scaling in an app that does not support freeform windows (for example Settings) takes a fallback path and leaves an abnormal corner transition. This is distinct from the confirmed Chrome PiP corner fix and from the ordinary bottom-corner freeform gesture. No paired layer trace or call-path evidence yet identifies its cause. The existing SystemUI and corner modules are not changed for this issue.

## Remaining checks

- Build and boot the v5 ROM, then verify native init launches the attention service and the attention toggle controls it.
- Reproduce the SystemUI fallback with a supported versus unsupported freeform app, capture the transition logs/layer state, and locate the specific fallback transaction before patching.
