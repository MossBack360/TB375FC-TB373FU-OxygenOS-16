# Mobile network / Communication Sharing framework split — 2026-11-20

## Result

After a clean OxygenOS boot, `Mobile network` was hidden when only `virtualmodem_wifinetwork_support` was present. Restoring `virtualmodem_support` exposed the entry but historically made `com.android.phone` block while requesting Lenovo-missing `vircommslot1`.

The working trial separates the UI capability gate from the unavailable radio HAL:

- `fixo_freeform_corner_gesture` v1.6 is the single owner of `com.oplus.oplus-feature.xml` and retains Panorama, three-finger Mind Space, and the three VirtualComm feature declarations.
- `fixo_virtualcomm_backend` v1.3 overlays `/system_ext/framework/oplus-telephony-common.jar`.
- Only `OplusRilImpl.setVirtualRadio()` and `setVirtualServiceProxy()` return before querying `vircommslot*` / `vircomm*`.
- `mIsVirtualcommDevice` and the upper UI/service capability checks remain enabled.

Verified on the current tablet:

- The three VirtualComm features are present in the live table.
- Patched framework JAR SHA-256: `853d5741aff3b73579728e730dd205fe5923c9c58e3598adc3cb12da5c1f8f70`.
- `com.android.phone` PID `2422` remained stable across two checks.
- Settings launched `com.android.phone/com.android.simsettings.activity.OplusSimSettingsActivity`.
- Its window owns a shown Surface with `mDrawState=HAS_DRAWN`.
- The page visibly contains Mobile data, Data usage, Communication sharing, More connection settings, and Call settings.

This proves the page/Phone-process regression is fixed. It does not prove cross-device calls and SMS without a paired compatible OPlus phone.

## Artifacts

- `C:/Users/GY/Documents/GitHub/temp/out/virtualcomm-backend-v1.3-ril-bypass-20261120/fixo-virtualcomm-backend-v1.3-ril-bypass.zip`
  - SHA-256 `1556b883d74b3c1bd6fa60e7e27615c8352813f5b4c1c9975fb0a5ad053e8b3a`
- `C:/Users/GY/Documents/GitHub/temp/out/freeform-feature-v1.6-virtualcomm-merged-20261120/fixo-freeform-feature-v1.6-virtualcomm-merged.zip`
  - SHA-256 `2497eb6d427c5b295dd4f259cd58b98164126ea1172d9866254df50cad88e959`

## Device Connect visibility audit

The current `OPSynergy.apk` is the international tablet build (`entrance_oneplusTabletExportAallRelease`). No `Build.MODEL`, `Build.PRODUCT`, OPD model, or TB375 model gate was found in its entrance scanner.

- Remote Control support exists in the international code, but `RemoteControlHelper` requires the official activity `com.oplus.remotecontrol/.feature.settings.activity.RemoteControlActivity`. The package is omitted on the current ROM, so it is hidden. This is a missing optional package, not a TB375FC blacklist and not a normal top-level Settings card.
- Link to Windows exists as a helper but `isSupport()` returns `false` in this build.
- iPhone/communication-sharing search entries depend on the HFP communication-sharing capability and system user.
- Android Auto depends on a resolvable Gearhead settings Intent.
- NFC and Touch Pay depend on NFC hardware/runtime support.
- OWork and Touch Interactions depend on exported activities carrying the expected Linker metadata.
- Other Device Connect cards are discovered from `com.oplus.linker.mix.entrance` metadata and then filtered by static visibility, API level, URI visibility, and component availability.

Therefore Remote Control is the only currently identified feature missing solely because its optional official APK is absent. Other conditional entries are capability/package/region filters, not model-name hides.
