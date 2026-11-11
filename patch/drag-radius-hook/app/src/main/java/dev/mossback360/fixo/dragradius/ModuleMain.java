package dev.mossback360.fixo.dragradius;

import android.util.Log;
import android.view.Display;
import io.github.libxposed.api.XposedModule;
import java.lang.reflect.Method;
import java.util.concurrent.atomic.AtomicInteger;

public final class ModuleMain extends XposedModule {
    private static final String TAG = "FixODragRadius";
    private static final String PROPERTY = "debug.fixo.drag_radius_px";
    private static final String DRAG_CLASS =
            "com.android.wm.shell.windowdecor.FullscreenTaskIndicatorManager$SpringDragManager";
    private final AtomicInteger hitCount = new AtomicInteger();

    @Override
    public void onModuleLoaded(ModuleLoadedParam param) {
        Log.i(TAG, "module loaded in " + param.getProcessName());
        log(Log.INFO, TAG, "module loaded in " + param.getProcessName());
    }

    @Override
    public void onPackageLoaded(PackageLoadedParam param) {
        Log.i(TAG, "package callback " + param.getPackageName());
        log(Log.INFO, TAG, "package callback " + param.getPackageName());
        if (!"com.android.systemui".equals(param.getPackageName())) return;
        try {
            Class<?> utility = Class.forName(
                    "com.android.wm.shell.fullscreen.OplusFlexibleWindowAnimationUtils",
                    false, param.getDefaultClassLoader());
            Method getRadius = utility.getDeclaredMethod("getDisplayCornerRadius", Display.class);
            Method getProperty = Class.forName("android.os.SystemProperties")
                    .getDeclaredMethod("get", String.class, String.class);
            getProperty.setAccessible(true);
            hook(getRadius).intercept(chain -> {
                String value = (String) getProperty.invoke(null, PROPERTY, "-1");
                int radius;
                try { radius = Integer.parseInt(value); }
                catch (NumberFormatException ignored) { return chain.proceed(); }
                if (radius < 0 || radius > 200) return chain.proceed();
                boolean drag = false;
                for (StackTraceElement frame : Thread.currentThread().getStackTrace()) {
                    if (DRAG_CLASS.equals(frame.getClassName())) { drag = true; break; }
                }
                if (!drag) return chain.proceed();
                int count = hitCount.incrementAndGet();
                if (count <= 10) log(Log.INFO, TAG, "hit=" + count + " radiusPx=" + radius);
                return radius;
            });
            Log.i(TAG, "hook installed; set " + PROPERTY + "=0..200 for test, -1 to bypass");
        } catch (Throwable error) {
            Log.e(TAG, "hook setup failed", error);
        }
    }
}
