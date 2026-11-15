package com.fixo.rotation;

import android.util.Log;
import android.view.IRotationWatcher;
import android.view.IWindowManager;
import android.view.WindowManagerGlobal;

public final class RotationBridge {
    private static final String TAG = "FixOSpeakerRotation";
    private static int last = -1;

    private RotationBridge() {}

    private static synchronized void apply(int rotation) {
        final int degrees;
        switch (rotation) {
            case 0: degrees = 270; break;
            case 1: degrees = 0; break;
            case 2: degrees = 90; break;
            case 3: degrees = 180; break;
            default: return;
        }
        if (rotation == last) return;
        try {
            int exit = new ProcessBuilder("/system_ext/bin/AudioSetParam", "-s",
                    "gsensor_rotation=" + degrees).start().waitFor();
            if (exit != 0) throw new IllegalStateException("AudioSetParam exit=" + exit);
            last = rotation;
            Log.i(TAG, "rotation=" + rotation + " gsensor_rotation=" + degrees);
        } catch (Exception e) {
            Log.e(TAG, "rotation update failed", e);
        }
    }

    public static void main(String[] args) throws Exception {
        IWindowManager wm = WindowManagerGlobal.getWindowManagerService();
        if (wm == null) throw new IllegalStateException("window service missing");
        wm.asBinder().linkToDeath(() -> System.exit(1), 0);
        IRotationWatcher watcher = new IRotationWatcher.Stub() {
            @Override public void onRotationChanged(int rotation) { apply(rotation); }
        };
        apply(wm.watchRotation(watcher, 0));
        synchronized (RotationBridge.class) {
            while (true) RotationBridge.class.wait();
        }
    }
}
