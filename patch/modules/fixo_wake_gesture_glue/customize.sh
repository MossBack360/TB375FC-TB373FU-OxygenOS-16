set_perm "$MODPATH/service.sh" 0 0 0755
set_perm "$MODPATH/uninstall.sh" 0 0 0755
set_perm "$MODPATH/wake-glue.dex" 0 0 0644

# Prevent the temporary interactive test daemon from competing with the module.
old_pid="$(pidof fixo_wake_glue 2>/dev/null)"
[ -n "$old_pid" ] && kill $old_pid 2>/dev/null
