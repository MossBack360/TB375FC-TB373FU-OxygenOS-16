# FixO ASI screen attention glue v0.2-trial

- Same module ID as v0.1, so installation upgrades it in place.
- Does not replace or patch Settings, SystemUI, framework, or AI addon files.
- Retries ASI registration after boot instead of accepting the early `false` result.
- Near the actual display timeout, asks ASI for one attention sample.
- Treats simultaneous face and gaze detection as presence, working around the incorrect landscape `gaze on screen` result.
- Calls Android `PowerManager.userActivity()` only when presence is detected.
- Follows OxygenOS/ZUI's existing `adaptive_sleep` secure setting; initializes an unset value to enabled once.

Accepted limitations after owner testing:

- Sampling close to timeout can cause a brief dim-then-bright transition.
- Because landscape ASI reports valid face and gaze frames but zero "gaze on screen" frames, a nearby person can occasionally be accepted even when not looking directly at the display.

`attention-useractivity.apk` is generated from `patch/attention-useractivity-helper` and is intentionally ignored by Git.
