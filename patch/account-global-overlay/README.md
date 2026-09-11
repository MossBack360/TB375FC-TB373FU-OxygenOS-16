# OnePlus international account overlay

This module loads the archived international `com.oneplus.account` APK over
`/my_stock/priv-app/KeKeUserCenter/KeKeUserCenter.apk` after PackageManager
finishes boot scanning. It preserves the original APK and account data.

Reference APK:

- version: `EXP_9.16.102_1640995` (`916102`)
- SHA-256: `8A667D7EA830319735BEB43878F93B76604BB7A776EC3F6A033D2414281D9D4D`
- signing certificate SHA-256: `4681AD50CAFC580EDFE027BD3FE593254E72CD2DEF1B351FEA306CCF6220CF07`

The target ROM APK is `EXP_9.16.104_f75a519` and uses the same signing
certificate. Disable the module and reboot to restore it.
