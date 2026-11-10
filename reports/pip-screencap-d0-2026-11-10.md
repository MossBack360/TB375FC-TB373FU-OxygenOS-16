# Chrome PiP screenshot versus screen recording: DisplaySettings `+0xd0`

Device: TB375FC, OxygenOS 16. The live `librenderengineextimpl.so` SHA-256 was `dc12fd204d76591d231ae3f62034779112c25b664593f2aa110ce2ac460acd35` (stock). The test LSPosed PiP radius APK was uninstalled. OPlus Launcher was foreground, and Chrome PiP had two `ChromeChildSurface` layers.

A temporary entry uprobe on `SkiaRenderEngineExtImpl::forceNoClipSmooth` at file offset `0x1a3a80` recorded the layer name, `SkRRect` type, weight, and proprietary `DisplaySettings` bytes. The trace is in `out/pip-screencap-d0-2026-11-10/trace2.txt`; the event definition is in the same directory. The probe was disabled and removed (`tracing_on=0`, `uprobe_events` empty).

| Capture | Same Chrome child | `type` | `weight` | `d0` | Time from trace |
| --- | --- | ---: | ---: | ---: | ---: |
| `screencap -p` | `ChromeChildSurface#166` | 3 | 1.7 | 0 | 259.796493 |
| `screenrecord --time-limit 3` | `ChromeChildSurface#166` | 3 | 1.7 | 1 | 262.082362 onward |

The first screenshot sample also recorded this child with `d0=0` during screenshot work, followed by `d0=1` in a later physical-display redraw before the command returned. The repeated capture shows `d0=0` for the screenshot and `d0=1` for every recorded video frame. `d5=d6=0` in both.

This confirms different runtime input values for screenshot and video/physical rendering while the PiP child, shape type, and weight remain the same. In the previously disassembled OPlus function, the measured Chrome case with `d0=0,d5=0` returns before its radius rewrite; `d0=1` passes this display-state gate, subject to later conditions. This explains why a still screenshot can miss the visually observed defect. The semantic field name at `+0xd0` and the caller that assigns it remain unknown. This entry probe does not by itself show the final rendered pixels or prove that the `+0xd0` gate is the only cause.
