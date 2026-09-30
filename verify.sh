#!/bin/bash
# 验收: 对 out/ 里每个 3mf 跑两条 CLI 命令 (bash 3.2 兼容, 不用关联数组)
BS=/Applications/BambuStudio.app/Contents/MacOS/BambuStudio
PASS=1
check() {
  f=$1; ex=$2; ey=$3; ez=$4; ec=$5
  echo "═══════════════════ $f.3mf ═══════════════════"
  # --info 偶发空输出(连续调用时), 重试两次
  INFO=""
  for try in 1 2 3; do
    INFO=$("$BS" --info out/$f.3mf 2>&1 | grep -Ev 'trace|Initializing')
    echo "$INFO" | grep -q '^manifold' && break
  done
  sx=$(echo "$INFO"|awk -F' = ' '/^size_x/{printf "%g",$2}')
  sy=$(echo "$INFO"|awk -F' = ' '/^size_y/{printf "%g",$2}')
  sz=$(echo "$INFO"|awk -F' = ' '/^size_z/{printf "%g",$2}')
  mf=$(echo "$INFO"|awk -F' = ' '/^manifold/{print $2}')
  nf=$(echo "$INFO"|awk -F' = ' '/^number_of_facets/{print $2}')
  echo "  --info    : ${sx}×${sy}×${sz} mm | manifold=$mf | facets=$nf"
  if [ "$mf" = "yes" ]; then echo "  ✓ manifold = yes"; else echo "  ✗ manifold=$mf"; PASS=0; fi
  if [ "$sx" = "$ex" ] && [ "$sy" = "$ey" ] && [ "$sz" = "$ez" ]; then
    echo "  ✓ 尺寸与参数一致 (期望 ${ex}×${ey}×${ez})"
  else echo "  ✗ 尺寸不符, 期望 ${ex}×${ey}×${ez}"; PASS=0; fi
  rm -rf /tmp/v && mkdir -p /tmp/v
  "$BS" --slice 0 --outputdir /tmp/v out/$f.3mf >/dev/null 2>&1
  ES=$(python3 -c "import json;d=json.load(open('/tmp/v/result.json'));print(d['error_string'],'| return_code =',d['return_code'])" 2>/dev/null)
  echo "  --slice 0 : error: $ES"
  case "$ES" in Success.*) echo "  ✓ error: Success";; *) echo "  ✗ 切片未成功"; PASS=0;; esac
  if [ -f /tmp/v/plate_1.gcode ]; then
    gc=$(grep -m1 '^; filament_colour' /tmp/v/plate_1.gcode | sed 's/.*= //')
    gt=$(grep -m1 '^; filament_type'   /tmp/v/plate_1.gcode | sed 's/.*= //')
    echo "  gcode     : filament_colour = $gc | filament_type = $gt"
    if [ "$gc" = "$ec" ]; then echo "  ✓ 颜色与所选一致 (期望 $ec)"; else echo "  ✗ 颜色不符, 期望 $ec"; PASS=0; fi
    if echo "$gt" | grep -qE '^PLA(;PLA)+$'; then echo "  ✓ filament_type = PLA;PLA"; else echo "  ✗ filament_type=$gt"; PASS=0; fi
  else echo "  ✗ 没生成 plate_1.gcode"; PASS=0; fi
}
check A 200 100 1.5 '#FFFFFF;#000000'
check B 120 60  2.5 '#D42B2B;#FFFFFF'
check C 150 100 40  '#3C7DD9;#F0F0F0'
check F_keychain 68.388 28.97 4.2 '#1A6BD4;#FFD400'
check H_stencil 200 100 2 '#F2F2F0;#000000'
check G_keychain_lego 84.172 26.328 3.6 '#D7261E;#FFC800;#141414;#FFFFFF'
echo "═════════════════════════════════════════════"
if [ $PASS = 1 ]; then echo "✅ A/B/C 全部通过两道验收命令"; else echo "❌ 存在未通过项"; fi
