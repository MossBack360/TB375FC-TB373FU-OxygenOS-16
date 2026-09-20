# Circle to Search — confirmed 2026-09-20

- Device: Lenovo TB375FC, OxygenOS 16 port. User confirmed that long-pressing the navigation handle opens working Circle to Search.
- Root cause: `pm has-feature com.google.android.feature.CONTEXTUAL_SEARCH` returned `false`. The ROM Settings implementation gates its Circle to Search controls on this feature; the secure gesture switch defaults to `1`.
- Fix: Magisk module `fixo_circle_to_search` v0.2-test adds only `system/etc/permissions/fixo_circle_to_search.xml` declaring that feature. No Settings, SystemUI, or Google APK was changed.
- ZIP: `out/circle-to-search-v0.2-test-2026-09-20/fixo_circle_to_search_v0.2-test.zip`; SHA-256 `8921B2F9652FA539877928985C4CC2E6288ED6BFDBC2D0D28B3E18F487A2414B`.
- After reboot: `pm has-feature` returned `true`; XML SHA-256 `8c0853b74ba7dfa15f7d74767e6ca2a780a8b0ca41b889999da7e8d36efa85a2`. Settings and SystemUI APK hashes remained unchanged.
- ADB long-press first showed Google's Circle to Search setup screen. User then confirmed actual circle search works.
- Do not install v0.1-test ZIP: Windows `Compress-Archive` stored backslashes in entry names, so Magisk did not mount the XML. Its source is archived only as a rejected packaging attempt.
- Recovery: disable module ID `fixo_circle_to_search` and reboot.
