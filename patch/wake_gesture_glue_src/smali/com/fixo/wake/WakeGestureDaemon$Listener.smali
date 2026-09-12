.class public final Lcom/fixo/wake/WakeGestureDaemon$Listener;
.super Landroid/hardware/TriggerEventListener;
.source "WakeGestureDaemon.java"

.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lcom/fixo/wake/WakeGestureDaemon;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x19
    name = "Listener"
.end annotation

.method public constructor <init>()V
    .locals 0
    invoke-direct {p0}, Landroid/hardware/TriggerEventListener;-><init>()V
    return-void
.end method

.method public onTrigger(Landroid/hardware/TriggerEvent;)V
    .locals 8

    :try_start
    const-string v0, "FixOWakeGesture"
    const-string v1, "TYPE_WAKE_GESTURE triggered"
    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    invoke-static {}, Lcom/fixo/wake/WakeGestureDaemon;->arm()Z
    move-result v0
    if-eqz v0, :rearm_failed

    sget-object v0, Lcom/fixo/wake/WakeGestureDaemon;->power:Landroid/os/PowerManager;
    invoke-virtual {v0}, Landroid/os/PowerManager;->isInteractive()Z
    move-result v1
    if-nez v1, :done

    invoke-static {}, Landroid/os/SystemClock;->uptimeMillis()J
    move-result-wide v1
    const/4 v3, 0x4
    const-string v4, "FixO:TYPE_WAKE_GESTURE"
    const/4 v5, 0x0
    invoke-virtual/range {v0 .. v5}, Landroid/os/PowerManager;->wakeUp(JILjava/lang/String;I)V

    :done
    return-void

    :rearm_failed
    const-string v0, "FixOWakeGesture"
    const-string v1, "re-arm returned false"
    invoke-static {v0, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    return-void
    :try_end
    .catch Ljava/lang/Throwable; {:try_start .. :try_end} :catch_all

    :catch_all
    move-exception v0
    const-string v1, "FixOWakeGesture"
    const-string v2, "trigger callback failed"
    invoke-static {v1, v2, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    return-void
.end method
