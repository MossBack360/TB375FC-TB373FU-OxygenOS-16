"""Add the TB375FC processor mapping to the stock OPlus XML, without editing Settings.apk."""

from pathlib import Path
import sys
import xml.etree.ElementTree as ET


source, target = map(Path, sys.argv[1:3])
data = source.read_bytes()
marker = b"</settings_device_processor_config>"
assert data.rstrip().endswith(marker)
assert b'model_name="MT6897-TB375FC"' not in data
entry = ('    <processor model_name="MT6897-TB375FC" '
         'name_cn="MediaTek 天玑 8300" name_en="MediaTek Dimensity 8300"/>\n').encode()
offset = data.rfind(marker)
patched = data[:offset] + entry + data[offset:]
ET.fromstring(patched)
target.parent.mkdir(parents=True, exist_ok=True)
target.write_bytes(patched)
print("Set ro.product.cpuinfo=MT6897-TB375FC in an early build.prop as well.")
