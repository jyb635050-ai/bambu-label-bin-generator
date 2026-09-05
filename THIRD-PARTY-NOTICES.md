# 第三方组件与许可

本项目把以下组件**内联进** `label-bin-generator.html`，并在 `vendor/` 保留原始文件。
全部为允许再分发的许可，下面是必须随附的版权声明。

## JavaScript 库
| 组件 | 版本 | 许可 | 版权 |
|---|---|---|---|
| [three.js](https://threejs.org/) | r147 | MIT | © 2010–2022 three.js authors |
| [JSZip](https://stuk.github.io/jszip/) | 3.10.1 | MIT（与 GPLv3 双许可，本项目按 MIT） | © 2009–2016 Stuart Knightley 等 |
| [opentype.js](https://opentype.js.org/) | 1.3.4 | MIT | © Frederik De Bleser |
| [earcut](https://github.com/mapbox/earcut) | 2.2.4 | ISC | © 2016 Mapbox |

## 内置字体
| 字体 | 许可 | 版权 |
|---|---|---|
| Roboto Black | Apache License 2.0 | © Google Inc. |
| Source Sans Pro Regular | SIL Open Font License 1.1 | © Adobe Systems Incorporated |
| Fira Sans Medium | SIL Open Font License 1.1 | © Mozilla Foundation, Carrois Apostrophe |

字体仅作为内置可选字形随程序分发；用户通过「上传 .ttf/.otf」使用的任何字库都只在本机解析，
不上传、不随程序分发。

## 说明
- Bambu Studio 与 Bambu Lab 是 Shenzhen Tuozhu Technology 的商标，本项目与其无从属关系。
- 生成的 3MF 内嵌一份 Bambu Studio 工程配置模板（打印参数），仅为让文件能被双击即切。
