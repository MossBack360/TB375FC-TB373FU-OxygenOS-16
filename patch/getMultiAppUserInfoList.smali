# Compatibility with the supplied ColorOS framework: one clone profile.
# Keep real UserInfo data and return an empty list when no clone exists.
.method public static getMultiAppUserInfoList(Lcom/oplus/multiapp/OplusMultiAppManager;)Ljava/util/List;
    .locals 3

    new-instance v0, Ljava/util/ArrayList;
    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V

    if-eqz p0, :done
    invoke-virtual {p0}, Lcom/oplus/multiapp/OplusMultiAppManager;->getMultiAppUserHandle()Landroid/os/UserHandle;
    move-result-object p0
    if-eqz p0, :done

    invoke-static {}, Landroid/app/AppGlobals;->getInitialApplication()Landroid/app/Application;
    move-result-object v1
    if-eqz v1, :done

    const-class v2, Landroid/os/UserManager;
    invoke-virtual {v1, v2}, Landroid/content/Context;->getSystemService(Ljava/lang/Class;)Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Landroid/os/UserManager;
    if-eqz v1, :done

    invoke-virtual {p0}, Landroid/os/UserHandle;->getIdentifier()I
    move-result p0
    invoke-virtual {v1, p0}, Landroid/os/UserManager;->getUserInfo(I)Landroid/content/pm/UserInfo;
    move-result-object v1
    if-eqz v1, :done

    new-instance v2, Lcom/oplus/wrapper/content/pm/UserInfo;
    invoke-direct {v2, v1}, Lcom/oplus/wrapper/content/pm/UserInfo;-><init>(Landroid/content/pm/UserInfo;)V
    invoke-virtual {v0, v2}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    :done
    return-object v0
.end method
