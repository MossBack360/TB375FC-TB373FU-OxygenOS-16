package dev.mossback360.fixo.pipradius;

import android.util.Log;
import io.github.libxposed.api.XposedModule;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.concurrent.atomic.AtomicInteger;

public final class ModuleMain extends XposedModule {
    private static final String TAG = "FixOPipNativeRadius";
    private final ThreadLocal<Integer> pipRoundDepth = ThreadLocal.withInitial(() -> 0);
    private final AtomicInteger hitCount = new AtomicInteger();

    @Override
    public void onPackageLoaded(PackageLoadedParam param) {
        if (!"com.android.systemui".equals(param.getPackageName()) || !param.isFirstPackage()) return;
        try {
            Class<?> helper = Class.forName("com.android.wm.shell.pip.PipSurfaceTransactionHelper", false,
                    param.getDefaultClassLoader());
            Class<?> surface = Class.forName("android.view.SurfaceControl");
            Class<?> transaction = Class.forName("android.view.SurfaceControl$Transaction");
            Field transactionNative = transaction.getDeclaredField("mNativeObject");
            Field surfaceNative = surface.getDeclaredField("mNativeObject");
            Method nativeCorner = surface.getDeclaredMethod("nativeSetCornerRadius",
                    long.class, long.class, float.class);
            transactionNative.setAccessible(true);
            surfaceNative.setAccessible(true);
            nativeCorner.setAccessible(true);

            int roundHooks = 0;
            for (Method method : helper.getDeclaredMethods()) {
                Class<?>[] types = method.getParameterTypes();
                if (!"round".equals(method.getName()) || types.length < 3 ||
                        types[0] != transaction || types[1] != surface) continue;
                hook(method).intercept(chain -> {
                    int depth = pipRoundDepth.get();
                    pipRoundDepth.set(depth + 1);
                    try { return chain.proceed(); }
                    finally {
                        if (depth == 0) pipRoundDepth.remove();
                        else pipRoundDepth.set(depth);
                    }
                });
                roundHooks++;
            }
            if (roundHooks == 0) {
                Log.e(TAG, "No PiP round method found; hook inactive");
                return;
            }

            Method setCorner = transaction.getDeclaredMethod("setCornerRadius", surface, float.class);
            hook(setCorner).intercept(chain -> {
                if (pipRoundDepth.get() == 0) return chain.proceed();
                try {
                    Object tx = chain.getThisObject();
                    Object sc = chain.getArg(0);
                    float radius = (Float) chain.getArg(1);
                    nativeCorner.invoke(null, transactionNative.getLong(tx), surfaceNative.getLong(sc), radius);
                    int count = hitCount.incrementAndGet();
                    if (count <= 5) Log.i(TAG, "PiP nativeSetCornerRadius hit=" + count + " radius=" + radius);
                    return tx;
                } catch (Throwable error) {
                    Log.e(TAG, "Native call failed; falling back to original", error);
                    return chain.proceed();
                }
            });
            Log.i(TAG, "Installed: PiP round hooks=" + roundHooks);
        } catch (Throwable error) {
            Log.e(TAG, "Hook setup failed; SystemUI left unchanged", error);
        }
    }
}
