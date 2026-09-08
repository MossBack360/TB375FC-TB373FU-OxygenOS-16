.class public final Lcom/fixo/displaypq/PqCtl;
.super Ljava/lang/Object;
.source "PqCtl.java"

.method public static main([Ljava/lang/String;)V
    .locals 7

    :try_start
    array-length v0, p0
    const/4 v1, 0x2
    if-lt v0, v1, :usage

    const/4 v0, 0x0
    aget-object v0, p0, v0
    const/4 v1, 0x1
    aget-object v2, p0, v1

    const-string v3, "chameleon"
    invoke-virtual {v3, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v3
    if-eqz v3, :check_picture

    invoke-static {v2}, Ljava/lang/Integer;->parseInt(Ljava/lang/String;)I
    move-result v0
    if-eqz v0, :chameleon_off
    move v0, v1
    goto :call_chameleon
    :chameleon_off
    const/4 v0, 0x0
    :call_chameleon
    invoke-static {v0}, Lcom/mediatek/pq/PictureQuality;->enableChameleon(Z)Z
    move-result v0
    sget-object v1, Ljava/lang/System;->out:Ljava/io/PrintStream;
    invoke-virtual {v1, v0}, Ljava/io/PrintStream;->println(Z)V
    return-void

    :check_picture
    const-string v3, "oplus"
    invoke-virtual {v3, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v3
    if-eqz v3, :check_picture_mode
    invoke-static {v2}, Ljava/lang/Integer;->parseInt(Ljava/lang/String;)I
    move-result v0
    invoke-static {v0}, Lcom/mediatek/pq/PictureQuality;->oplusSetMode(I)Ljava/lang/String;
    move-result-object v0
    sget-object v1, Ljava/lang/System;->out:Ljava/io/PrintStream;
    const-string v2, "ok"
    invoke-virtual {v1, v2}, Ljava/io/PrintStream;->println(Ljava/lang/String;)V
    return-void

    :check_picture_mode
    const-string v3, "picture"
    invoke-virtual {v3, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v3
    if-eqz v3, :check_preset
    invoke-static {v2}, Ljava/lang/Integer;->parseInt(Ljava/lang/String;)I
    move-result v0
    invoke-static {v0}, Lcom/mediatek/pq/PictureQuality;->setPictureMode(I)Z
    move-result v0
    sget-object v1, Ljava/lang/System;->out:Ljava/io/PrintStream;
    invoke-virtual {v1, v0}, Ljava/io/PrintStream;->println(Z)V
    return-void

    :check_preset
    const-string v3, "preset"
    invoke-virtual {v3, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v3
    if-eqz v3, :usage
    invoke-static {v2}, Ljava/lang/Integer;->parseInt(Ljava/lang/String;)I
    move-result v0

    const/16 v2, 0x9
    new-array v3, v2, [D
    if-ne v0, v1, :preset_standard_or_nature

    fill-array-data v3, :matrix_vivid
    goto :apply_matrix

    :preset_standard_or_nature
    const/4 v2, 0x2
    if-ne v0, v2, :preset_standard
    fill-array-data v3, :matrix_nature
    goto :apply_matrix

    :preset_standard
    fill-array-data v3, :matrix_standard_peridot

    :apply_matrix
    invoke-static {v3, v1}, Lcom/mediatek/pq/PictureQuality;->setCcorrMatrix([DI)Z
    move-result v0
    sget-object v1, Ljava/lang/System;->out:Ljava/io/PrintStream;
    invoke-virtual {v1, v0}, Ljava/io/PrintStream;->println(Z)V
    return-void

    :usage
    sget-object v0, Ljava/lang/System;->err:Ljava/io/PrintStream;
    const-string v1, "usage: PqCtl chameleon 0|1 | oplus N | picture N | preset 0|1|2"
    invoke-virtual {v0, v1}, Ljava/io/PrintStream;->println(Ljava/lang/String;)V
    return-void
    :try_end
    .catch Ljava/lang/Throwable; {:try_start .. :try_end} :catch_all

    :catch_all
    move-exception v0
    invoke-virtual {v0}, Ljava/lang/Throwable;->printStackTrace()V
    return-void

    :matrix_vivid
    .array-data 8
        0x3ff0000000000000L
        0x0
        0x0
        0x0
        0x3ff0000000000000L
        0x0
        0x0
        0x0
        0x3ff0000000000000L
    .end array-data

    :matrix_standard_peridot
    .array-data 8
        0x3feae7ff583a53b9L
        0x3fc6dff822bbecabL
        0x3f98feef5ec80c74L
        0x3f9cffeb074a771dL
        0x3ff0000000000000L
        0x0
        0x3f8ffd60e94ee393L
        0x3fb21ff2e48e8a72L
        0x3fee5feda6612839L
    .end array-data

    :matrix_nature
    .array-data 8
        0x3febf7f8ca8198f2L
        0x3fb4ffeb074a771dL
        0x3fa43fe5c91d14e4L
        0x3f81fb3fa6defc7aL
        0x3feef7f8ca8198f2L
        0x3f98feef5ec80c74L
        0x0
        0x3f907f23cc8de2acL
        0x3fef87fcb923a29cL
    .end array-data
.end method
