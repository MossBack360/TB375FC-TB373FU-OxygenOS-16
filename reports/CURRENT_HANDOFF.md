# TB375FC OxygenOS port handoff

Updated: 2026-09-11

Use the installed `$tb375fc-oxygenos-port` skill in a new Codex window. Its current-state and patch-catalog references are the primary handoff record.

The device currently runs OxygenOS 16 as `OPD2203` on TB375FC. The confirmed active SystemUI module is `fixo_fullscreen_caption` v0.5. It combines:

- restored fullscreen three-dot window controls;
- the accepted v0.2 drag-phase corner-radius fallback;
- follow-finger back gesture animation using `RubberBandBezierCalculator`.

The attempted v0.4 formal freeform 30↔50 px corner-radius interpolation was rejected for visual quality and remains archived. Do not reinstall it unless explicitly comparing behavior.

The third-party `TB375FC_ColosOS` module was found to force `persist.sys.oplus.anim_level=3`. A 2026-09-09 baseline had value 2. The installed module now uses value 1, and its original value-3 file is backed up on-device.

Open work remains Dolby DSP routing, incomplete international AI, material contour-glow rendering, and unconfirmed GPS status. Existing Dolby, OPD2514 AI, material-stroke, and smooth-corner trials are not confirmed fixes.
