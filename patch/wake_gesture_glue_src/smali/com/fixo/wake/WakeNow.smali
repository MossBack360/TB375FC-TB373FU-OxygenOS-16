.class public final Lcom/fixo/wake/WakeNow;
.super Ljava/lang/Object;
.source "WakeNow.java"

.method public static main([Ljava/lang/String;)V
    .locals 6

    :try_start
    invoke-static {}, Landroid/os/Looper;->prepare()V
    invoke-static {}, Landroid/app/ActivityThread;->systemMain()Landroid/app/ActivityThread;
    move-result-object v0
    invoke-virtual {v0}, Landroid/app/ActivityThread;->getSystemContext()Landroid/app/ContextImpl;
    move-result-object v0
    const-string v1, "power"
    invoke-virtual {v0, v1}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Landroid/os/PowerManager;
    invoke-static {}, Landroid/os/SystemClock;->uptimeMillis()J
    move-result-wide v1
    const/4 v3, 0x4
    const-string v4, "FixO:WakeNowTest"
    const/4 v5, 0x0
    invoke-virtual/range {v0 .. v5}, Landroid/os/PowerManager;->wakeUp(JILjava/lang/String;I)V
    const-string v0, "FixOWakeGesture"
    const-string v1, "direct wakeUp call succeeded"
    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    return-void
    :try_end
    .catch Ljava/lang/Throwable; {:try_start .. :try_end} :catch_all

    :catch_all
    move-exception v0
    const-string v1, "FixOWakeGesture"
    const-string v2, "direct wakeUp call failed"
    invoke-static {v1, v2, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    invoke-virtual {v0}, Ljava/lang/Throwable;->printStackTrace()V
    return-void
.end method
