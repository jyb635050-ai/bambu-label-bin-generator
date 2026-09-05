# PROGRESS — 名牌 & 收纳盒 参数化 3MF 生成器

状态: **已完成**。A/B/C 三个验收文件全部通过两道 CLI 命令 (2026-08-28)。
接手先读本文件, 再读 README.md。

## 交付物
| 路径 | 说明 |
|---|---|
| `label-bin-generator.html` | **成品**。1.44MB 单文件, 双击即用, 零网络。 |
| `src/app.html` | 源码模板 (含占位符, 不含大 blob)。改这个。 |
| `build.py` | 把 src + vendor 组装成成品 html。`python3 build.py` |
| `verify.sh` | 一键跑验收两道命令。`./verify.sh` |
| `decode.py` | 把浏览器导出的 base64 还原成 .3mf (自动化验收用) |
| `vendor/` | three.js r147 / JSZip 3.10.1 / opentype.js 1.3.4 / earcut 2.2.4 + 3 款字体 |
| `out/` | A.3mf B.3mf C.3mf (验收件) + D_merged / E_uploaded (附加验证) |

## 验收结果 (`./verify.sh`)
| | --info 尺寸 | manifold | --slice 0 | filament_colour | filament_type |
|---|---|---|---|---|---|
| A 名牌 200×100×1 凸0.5 白底黑字 2行 | 200×100×1.5 ✓ | yes | Success rc=0 | `#FFFFFF;#000000` ✓ | PLA;PLA ✓ |
| B 名牌 120×60×2 红底白字 3行 | 120×60×2.5 ✓ | yes | Success rc=0 | `#D42B2B;#FFFFFF` ✓ | PLA;PLA ✓ |
| C 收纳盒 150×100×40 3×2 壁厚2 | 150×100×40 ✓ | yes | Success rc=0 | `#3C7DD9;#F0F0F0` ✓ | PLA;PLA ✓ |
附加: D_merged(合并格 180×120×40) / E_uploaded(上传字体+圆角 150×80×2.3) 同样双命令通过。
注: 本机 CLI 不往 stdout 打 "error: Success", 成功信号在 `outputdir/result.json`
的 `error_string="Success."` + `return_code=0`; verify.sh 读的就是它。

## 一个必须说明的偏离
`reference/project_settings_2PLA.config` 里 `printable_area = 180×180`,
**与验收A(200×100名牌)直接冲突** —— 实测用它必失败:
`rc=-50 "One of the plate is empty or has no object fully inside it."`
另一个参照资产 `golden_label.3mf` 自身就是 200×100 名牌、能切、其 `printable_area = 256×256`,
printer_model 同为 Bambu Lab A1 (A1 真实幅面 256, 180 是模板里的错值)。
→ **生成时除 filament_colour 外, 额外把 printable_area 覆写成 256×256。**
reference/ 三个文件一字未改。实测边界: 200×100 ✓ / 240×200 ✓ / 250×250 ✓。
页面校验按此: >190mm 黄色警示(引用你测过的数), >250mm 硬拦截。

## 踩过的三个坑 (改代码前务必读)
1. **earcut 会悄悄吞边界边** → 破面。它遇到零面积"耳朵"(共线点、孔与外轮廓顶点共线)
   时直接删点不吐三角形, 那条边界边就没人用了, 侧壁找不到配对 → 非流形。
   - 表现1: 收纳盒顶面(外框+N个格腔洞), 栅格对齐的孔必触发, badEdges 上百。
   - 表现2: 字符 `#` 在三款字体上全炸 (孔的角点恰好与外轮廓顶点共线)。
   - 解法: 盒子改成**完全不碰 earcut** 的构造(见下); 文字加 `safeTriangulate`——
     先 earcut, 再审计"每条边界边恰好用一次", 不过就回退到自写的打孔+剪耳
     (剪耳逢摘必吐三角形, 边界边一定用满, 水密由构造保证)。
2. **字体是非零绕向(nonzero), 不是奇偶(even-odd)**。按包含深度分组会把重叠轮廓
   误判成挖孔。改按绕向: 取面积最大环的朝向为实体朝向, 同号实体异号挖孔。
   (TTF 与 OTF 朝向约定相反, 取相对号两边通吃。)
3. **JSZip 默认会写目录条目** → 变成 8 个 zip 条目。必须 `{createFolders:false}`, 才是规定的 5 条目。

## 几何构造 (水密的根据)
不变量: **每条边恰好被两个三角形以相反方向使用**。页面每次重建都跑 `checkMesh` 验这条,
不过就红色 `不可导出` 并禁用按钮 —— 非水密根本导不出去。
- 名牌底板 / 文字: `prismFromRing` / `extrudeGroup` = 顶面 + 底面(翻转) + 侧壁,
  侧壁按环自身绕向走, 外环 CCW / 孔 CW 时法线自动朝外。
- 收纳盒(单壳, 一体式底部封实):
  ① 底面 z=0 形心扇形(翻转, -Z) ② 外壁 0→H ③a 外轮廓↔内框用**极角归并环带**(ribbon)
  ③b 内框以里走**栅格单元**, 落在格腔里的跳过 → 自然形成腔口 ④ 每腔内壁 bt→H
  ⑤ 腔底 z=bt 形心扇形(+Z)。同一高度的顶点按坐标复用(makePool), 杜绝 T 型接缝。
  合并格 = 栅格线取并集后, 大矩形跨多个单元, 中间隔断自然消失。

## 已覆盖的测试
- 106 个字符 × 3 款内置字体逐字挤出: 全部水密 (含 `#$%&@` 等易炸字符)。
- 收纳盒 9 种构型: 3×2 / 合并列 / 双合并 / 圆角0 / 1×1 / 8×6密排 / 全合并 / 大圆角 / 20×20。
- 名牌: 多行/空行/单字/负字距/正字距/超小板/圆角/厚凸起/左对齐/纯空格。
- 上传 .otf 走真实 handler; 合并/拆开/全部还原走真实按钮; 导出按钮走真实 blob 下载链路。

## 未能亲手验的一项 (如实记录)
"双击 .html" 这个动作本身没能在本环境跑通取证:
连着的 Chrome 是远端 Windows 机(开不了本机文件), 预览面板对 1.4MB 本地文件只做 data: 快照(超限打不开),
`screencapture` 抓到的桌面里没有任何应用窗口(抓不到真实会话)。
已做的等价验证: 成品文件在真实浏览器引擎里跑通全部功能(经 http://localhost);
静态审计确认零外部依赖 —— 无 ES module / 无 fetch/XHR(我的代码路径) / 无 Worker /
无 localStorage / 无外链 src|href, 全部 UMD 内联, 字体走 base64→atob→opentype.parse。
这几项正是 file:// 会卡的全部环节。
