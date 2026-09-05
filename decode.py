#!/usr/bin/env python3
"""把 javascript_tool 溢出到磁盘的 base64 结果还原成 out/<name>.3mf"""
import base64, json, sys, os
src, dst = sys.argv[1], sys.argv[2]
raw = open(src, encoding='utf-8').read().strip()
try:
    j = json.loads(raw)
    txt = j[0]['text'] if isinstance(j, list) else j['text']
except Exception:
    txt = raw
txt = txt.strip()
if txt.startswith('"') and txt.endswith('"'):
    txt = json.loads(txt)
# 页面会在 base64 后追加 #PAD# 填充, 强制 javascript_tool 把结果落盘,
# 避免 base64 途经上下文被改动 (小文件曾因此出现 bad CRC)
if '#PAD#' in txt:
    txt = txt.split('#PAD#')[0]
txt = ''.join(txt.split())
data = base64.b64decode(txt)
os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
open(dst, 'wb').write(data)
print('%s  %d bytes' % (dst, len(data)))
