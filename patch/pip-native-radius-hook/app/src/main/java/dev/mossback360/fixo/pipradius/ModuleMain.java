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
    private String lastConfig = "";

    @Override
    public void onModuleLoaded(ModuleLoadedParam param) {
        log(Log.INFO, TAG, "onModuleLoaded process=" + param.getProcessName());
    }

    @Override
    public void onPackageLoaded(PackageLoadedParam param) {
        log(Log.INFO, TAG, "onPackageLoaded package=" + param.getPackageName()
                + " first=" + param.isFirstPackage());
        if (!"com.android.systemui".equals(param.getPackageName())) return;
        try {
            Class<?> helper = Class.forName("com.android.wm.shell.pip.PipSurfaceTransactionHelper", false,
                    param.getDefaultClassLoader());
            Class<?> surface = Class.forName("android.view.SurfaceControl");
            Class<?> transaction = Class.forName("android.view.SurfaceControl$Transaction");
            Field transactionNative = transaction.getDeclaredField("mNativeObject");
            Field surfaceNative = surface.getDeclaredField("mNativeObject");
            Method nativeCorner = surface.getDeclaredMethod("nativeSetCornerRadius",
                    long.class, long.class, float.class);
            Method nativeCornerExt = surface.getDeclaredMethod("nativeSetCornerRadiusExt",
                    long.class, long.class, float.class, float.class);
            Method getProperty = Class.forName("android.os.SystemProperties")
                    .getDeclaredMethod("get", String.class, String.class);
            transactionNative.setAccessible(true);
            surfaceNative.setAccessible(true);
            nativeCorner.setAccessible(true);
            nativeCornerExt.setAccessible(true);
            getProperty.setAccessible(true);

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
                log(Log.ERROR, TAG, "No PiP round method found; hook inactive");
                return;
            }

            Method setCorner = transaction.getDeclaredMethod("setCornerRadius", surface, float.class);
            hook(setCorner).intercept(chain -> {
                if (pipRoundDepth.get() == 0) return chain.proceed();
                try {
                    String mode = (String) getProperty.invoke(null, "debug.fixo.pip.corner_mode", "native");
                    String rawWeight = "ext".equals(mode)
                            ? (String) getProperty.invoke(null, "debug.fixo.pip.corner_weight", "1.7") : "";
                    String config = mode + ":" + rawWeight;
                    if (!config.equals(lastConfig)) {
                        lastConfig = config;
                        hitCount.set(0);
                        log(Log.INFO, TAG, "PiP config=" + config);
                    }
                    Object tx = chain.getThisObject();
                    Object sc = chain.getArg(0);
                    float radius = (Float) chain.getArg(1);
                    if ("stock".equals(mode)) return chain.proceed();
                    long txNative = transactionNative.getLong(tx);
                    long scNative = surfaceNative.getLong(sc);
                    float weight = Float.NaN;
                    if ("ext".equals(mode)) {
                        weight = Float.parseFloat(rawWeight);
                        if (!Float.isFinite(weight) || weight < 0.0f || weight > 2.5f)
                            throw new IllegalArgumentException("Invalid PiP weight: " + rawWeight);
                        nativeCornerExt.invoke(null, txNative, scNative, radius, weight);
                    } else {
                        nativeCorner.invoke(null, txNative, scNative, radius);
                    }
                    int count = hitCount.incrementAndGet();
                    if (count <= 8) log(Log.INFO, TAG, "PiP hit=" + count + " mode=" + mode
                            + " radius=" + radius + " weight=" + weight);
                    return tx;
                } catch (Throwable error) {
                    log(Log.ERROR, TAG, "Native call failed; falling back to original", error);
                    return chain.proceed();
                }
            });
            log(Log.INFO, TAG, "Installed: PiP round hooks=" + roundHooks);
        } catch (Throwable error) {
            log(Log.ERROR, TAG, "Hook setup failed; SystemUI left unchanged", error);
        }
    }
}
