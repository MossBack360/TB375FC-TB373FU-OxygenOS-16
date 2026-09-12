.class public final Lcom/fixo/wake/WakeGestureDaemon;
.super Ljava/lang/Object;
.source "WakeGestureDaemon.java"

# A boot-safe app_process daemon. It bypasses the blocked SettingsProvider key and
# listens to the tablet's standard TYPE_WAKE_GESTURE (23) sensor directly.

.field public static manager:Landroid/hardware/SensorManager;
.field public static sensor:Landroid/hardware/Sensor;
.field public static listener:Landroid/hardware/TriggerEventListener;
.field public static power:Landroid/os/PowerManager;

.method public static arm()Z
    .locals 3

    sget-object v0, Lcom/fixo/wake/WakeGestureDaemon;->manager:Landroid/hardware/SensorManager;
    sget-object v1, Lcom/fixo/wake/WakeGestureDaemon;->listener:Landroid/hardware/TriggerEventListener;
    sget-object v2, Lcom/fixo/wake/WakeGestureDaemon;->sensor:Landroid/hardware/Sensor;
    invoke-virtual {v0, v1, v2}, Landroid/hardware/SensorManager;->requestTriggerSensor(Landroid/hardware/TriggerEventListener;Landroid/hardware/Sensor;)Z
    move-result v0
    return v0
.end method

.method public static main([Ljava/lang/String;)V
    .locals 7

    :try_start
    invoke-static {}, Landroid/os/Looper;->prepare()V

    invoke-static {}, Landroid/app/ActivityThread;->systemMain()Landroid/app/ActivityThread;
    move-result-object v0
    invoke-virtual {v0}, Landroid/app/ActivityThread;->getSystemContext()Landroid/app/ContextImpl;
    move-result-object v0

    const-string v1, "sensor"
    invoke-virtual {v0, v1}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Landroid/hardware/SensorManager;
    sput-object v1, Lcom/fixo/wake/WakeGestureDaemon;->manager:Landroid/hardware/SensorManager;

    const-string v2, "power"
    invoke-virtual {v0, v2}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Landroid/os/PowerManager;
    sput-object v0, Lcom/fixo/wake/WakeGestureDaemon;->power:Landroid/os/PowerManager;

    const/16 v2, 0x17
    const/4 v3, 0x1
    invoke-virtual {v1, v2, v3}, Landroid/hardware/SensorManager;->getDefaultSensor(IZ)Landroid/hardware/Sensor;
    move-result-object v2
    sput-object v2, Lcom/fixo/wake/WakeGestureDaemon;->sensor:Landroid/hardware/Sensor;

    if-eqz v2, :missing

    new-instance v3, Lcom/fixo/wake/WakeGestureDaemon$Listener;
    invoke-direct {v3}, Lcom/fixo/wake/WakeGestureDaemon$Listener;-><init>()V
    sput-object v3, Lcom/fixo/wake/WakeGestureDaemon;->listener:Landroid/hardware/TriggerEventListener;

    invoke-static {}, Lcom/fixo/wake/WakeGestureDaemon;->arm()Z
    move-result v3

    const-string v4, "FixOWakeGesture"
    new-instance v5, Ljava/lang/StringBuilder;
    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V
    const-string v6, "sensor="
    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {v5, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v2, " armed="
    invoke-virtual {v5, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {v5, v3}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v2
    invoke-static {v4, v2}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    if-eqz v3, :arm_failed
    invoke-static {}, Landroid/os/Looper;->loop()V
    return-void

    :missing
    new-instance v0, Ljava/lang/IllegalStateException;
    const-string v1, "TYPE_WAKE_GESTURE sensor 23 missing"
    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V
    throw v0

    :arm_failed
    new-instance v0, Ljava/lang/IllegalStateException;
    const-string v1, "requestTriggerSensor returned false"
    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V
    throw v0
    :try_end
    .catch Ljava/lang/Throwable; {:try_start .. :try_end} :catch_all

    :catch_all
    move-exception v0
    const-string v1, "FixOWakeGesture"
    const-string v2, "daemon failed"
    invoke-static {v1, v2, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    invoke-virtual {v0}, Ljava/lang/Throwable;->printStackTrace()V
    return-void
.end method
