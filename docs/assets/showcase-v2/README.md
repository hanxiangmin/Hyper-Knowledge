# Workbench in motion / 工作台实录

Eight seconds, four chapters: overview → hyperedge → node → hover. The first six
scenes last one second each; the final hover plays at half speed for two seconds.
Both languages follow the same Su Shi example; the gallery
retains all ten captured states per language.

8 秒、四段逻辑：总览 → 超边 → 节点 → 悬停。前六个画面各 1 秒，最后的悬停半速播放 2 秒。中英文采用同一份苏轼生平示例；图集仍保留每种语言的完整十个状态。

## Watch / 观看

- [English looping GIF](tour-en.gif)
- [中文循环 GIF](tour-zh.gif)
- [English gallery](../../en/guide/workbench.md) · [中文图集](../../zh/guide/workbench.md)

## What was recorded / 录制内容

The browser loads the repository's self-contained
[workbench](../../../../examples/sushi-document-test/views/workbench.html)
in a fresh local Chromium context. It uses real pointer clicks, representation
buttons, and hover events. No signed-in profile or external model service is used.

| State | Object / 对象 |
| --- | --- |
| Overview / 总览 | Matrix, incidence, enclosure / 矩阵、关联、包络 |
| Hyperedge / 超边 | `assertion:family-san-su` · 三苏家族与文学群体 · 4 members |
| Node / 节点 | `person:su-shi` · 苏轼 · 10 memberships |
| Hover / 悬停 | The same family hyperedge; move in, move out, move in again |

PNG files are full-page browser screenshots. MP4 and GIF files use seven
excerpts from the actual WebM recordings: six at normal speed and the final
hover at half speed, with short bilingual captions and clean cuts.
A small pointer indicator follows real mouse events.
The short edit omits repeated views without removing their gallery screenshots.

PNG 为真实浏览器整页截图；MP4 和 GIF 从实际 WebM 录屏中截取七段，前六段保持正常速度，仅将最后的悬停放慢至半速，配合短字幕和直接切换，不再保留长时间等待、放大或淡入淡出。
鼠标指示点跟随真实鼠标事件。短片省略重复视图，但对应截图仍在图集中。英文版翻译界面与讲解，原文实体、关系名和角色仍保留中文。

| Chapter / 段落 | Short edit / 短片画面 | Duration / 时长 |
| --- | --- | --- |
| Overview / 总览 | Enclosure → matrix / 包络 → 矩阵 | 2 × 1 s |
| Hyperedge / 超边 | Enclosure → incidence / 包络 → 关联 | 2 × 1 s |
| Node / 节点 | Matrix → incidence / 矩阵 → 关联 | 2 × 1 s |
| Hover / 悬停 | Highlighted enclosure / 包络高亮 | 2 s · half speed / 半速 |

Selection in the matrix preserves the global table and highlights membership.
The incidence view expands one hyperedge's four members, or summarizes the
selected node's ten hyperedges. Enclosure hover highlights four members and
restores the overview when the pointer leaves. Recording does not modify nodes,
hyperedges, memberships, or evidence.

矩阵中的选择只高亮、不删行列；关联视图按所选对象展示成员或所属超边。悬停突出四个成员，移出后恢复总览。录制不改变节点、超边、成员关系和来源记录。

## Reproduce / 复现

GIFs are the public showcase format and loop without a player. The renderer also
keeps an MP4 intermediate for GIF generation and frame-by-frame validation.

GIF 是公开展示格式，无需播放器即可循环显示；渲染器保留 MP4 中间文件，用于生成 GIF 和逐帧验证。

Optional media tools are separate from the Skill runtime. From the repository root:

```sh
npm install --prefix temp/media-runtime playwright
npx --prefix temp/media-runtime playwright install chromium ffmpeg
python -m pip install Pillow
node tools/capture_showcase.mjs --out temp/live-capture --playwright ./temp/media-runtime/node_modules/playwright
python tools/render_live_showcase.py --capture temp/live-capture --out docs/assets/showcase-v2 --ffmpeg /path/to/ffmpeg
python tools/check_live_showcase.py --assets docs/assets/showcase-v2 --capture temp/live-capture --ffmpeg /path/to/ffmpeg
```

The renderer defaults to the eight-second edit. Add `--edit full` to render the
archival ten-scene version, preferably into a separate output directory.

渲染器默认生成 8 秒精简版。加上 `--edit full` 可重新生成十场景完整版，建议使用单独的输出目录。

To use an installed Chrome instead of downloading Chromium, pass
`--browser /path/to/chrome` to the capture command. If needed, also pass
`--ffmpeg /path/to/ffmpeg`; this prepares a private recording runtime under the
capture output directory. The default fonts are Microsoft YaHei on Windows;
use the renderer's font options for another CJK-capable font on other systems.

可通过 `--browser` 使用本机 Chrome，并通过 `--ffmpeg` 指定已有 FFmpeg；录制使用独立临时会话，不接管日常浏览器。其他系统请为视频渲染指定支持中文的字体。

## Checks / 检查

`live-manifest.json` records source hashes, scene timing, screenshot hashes,
video metadata, and per-scene browser-state checks. Raw `session.webm` and
`timeline.json` files remain in the capture output directory; rerunning the
commands regenerates them. Browser-state checks verify the 38 × 10 matrix with
49 memberships, four members in the selected hyperedge, ten hyperedges around
Su Shi, and reversible hover. Media checks decode the complete MP4s and verify
GIF timing and published-file hashes.

哈希、浏览器状态检查和视频解码检查可以确认素材对应正确数据与交互，但不等同于证明布局完全无碰撞。总览中的密集区域仍应结合矩阵、局部聚焦阅读。
