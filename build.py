#!/usr/bin/env python3
# 把 src/app.html + vendor/* 组装成单个自包含 html (双击 file:// 直接跑)
import base64, json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, 'src', 'app.html')
VEN  = os.path.join(ROOT, 'vendor')
OUT  = os.path.join(ROOT, 'label-bin-generator.html')

FONTS = [
    ('Roboto-Black.ttf',          'Roboto Black · 粗黑无衬线'),
    ('SourceSansPro-Regular.otf', 'Source Sans Pro · 常规无衬线'),
    ('FiraSansOT-Medium.otf',     'Fira Sans Medium · 中粗无衬线'),
]

def read(p):
    with open(p, 'r', encoding='utf-8') as f: return f.read()

def js_lib(name):
    s = read(os.path.join(VEN, name))
    # 防止库里出现 </script> 提前闭合
    return s.replace('</script>', '<\\/script>')

html = read(SRC)

html = html.replace('/*@@VENDOR_JSZIP@@*/',    js_lib('jszip.min.js'))
html = html.replace('/*@@VENDOR_THREE@@*/',    js_lib('three.min.js'))
html = html.replace('/*@@VENDOR_OPENTYPE@@*/', js_lib('opentype.min.js'))
html = html.replace('/*@@VENDOR_EARCUT@@*/',   js_lib('earcut.min.js'))

font_entries = []
for fn, label in FONTS:
    with open(os.path.join(VEN, 'fonts', fn), 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    font_entries.append('{label:%s,file:%s,data:"%s"}' % (json.dumps(label, ensure_ascii=False),
                                                          json.dumps(fn), b64))
html = html.replace('/*@@BUILTIN_FONTS@@*/',
                    'var BUILTIN_FONTS=[' + ','.join(font_entries) + '];')

cfg = json.load(open(os.path.join(ROOT, 'reference', 'project_settings_2PLA.config')))
assert len(cfg) == 569, 'project_settings 条目数变了: %d' % len(cfg)
html = html.replace('/*@@PROJECT_SETTINGS@@*/',
                    'var PROJECT_SETTINGS_TEMPLATE=' + json.dumps(cfg, ensure_ascii=False, separators=(',', ':')) + ';')

for marker in ['@@VENDOR_', '@@BUILTIN_FONTS@@', '@@PROJECT_SETTINGS@@']:
    if marker in html:
        sys.exit('未替换的占位符: ' + marker)

with open(OUT, 'w', encoding='utf-8') as f: f.write(html)
print('built %s  %.2f MB' % (OUT, os.path.getsize(OUT)/1048576))
