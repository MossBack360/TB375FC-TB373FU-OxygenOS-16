#!/system/bin/sh
cmd attention clearTestableAttentionService >/dev/null 2>&1
pm revoke com.google.android.as android.permission.CAMERA >/dev/null 2>&1
