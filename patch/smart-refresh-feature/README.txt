FixO Smart Refresh Feature Glue v0.3

Purpose:
- Restore the native Settings option: 智能切换
- Let the existing OPlus display stack select a high refresh rate during use
  and reduce it when appropriate.

This module does not replace Settings.apk, SystemUI.apk, or framework files.
It preserves the live multimedia feature list and adds only the three display
feature declarations present in the prepared ColorOS port tree. A reversible
early bind mount is used because Magisk magic mount does not cover this
device's standalone my_product partition.
