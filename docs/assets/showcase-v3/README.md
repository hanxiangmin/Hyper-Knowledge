# Workbench in motion / 工作台实录

Eight seconds, four reading moves: structure overview → matrix → selected
hyperedge → selected node → enclosure hover. The first six scenes last one
second each; the final hover plays at half speed for two seconds. Both
languages use the same role-aware Su Shi showcase, and the gallery keeps all ten
captured states per language.

8 秒、四段阅读逻辑：结构总览 → 关联矩阵 → 选中超边 → 选中节点 → 包络悬停。前六个画面各 1 秒，最后的悬停半速播放 2 秒。中英文采用同一份苏轼高阶关联示例；图集保留每种语言的完整十个状态。

## Watch / 观看

- [English looping GIF](tour-en.gif)
- [中文循环 GIF](tour-zh.gif)
- [English gallery](../../en/guide/workbench.md) · [中文图集](../../zh/guide/workbench.md)

## What was recorded / 录制内容

The browser loads the repository's self-contained
[capsule workbench](../../../../examples/sushi-local-preview/views/capsule-trial/workbench.html)
in a fresh local Chromium context. It uses real pointer clicks, representation
buttons, and hover events. No signed-in browser profile, external model service,
or online parser is used.

| State | Object / 对象 |
| --- | --- |
| Overview / 总览 | Matrix, incidence, and capsule/enclosure overview / 矩阵、关联、胶囊包络总览 |
| Hyperedge / 超边 | `assertion:family-san-su` · 三苏 · 4 members |
| Node / 节点 | `person:su-shi` · 苏轼 · 18 incident hyperedges |
| Hover / 悬停 | The same San Su enclosure; move in, move out, move in again |

PNG files are full-page browser screenshots. MP4 and GIF files use seven
excerpts from the actual WebM recordings: six at normal speed and the final
hover at half speed, with short bilingual captions and clean cuts. A small
pointer indicator follows real mouse events. The short edit omits repeated
views without removing their gallery screenshots.

PNG 为真实浏览器整页截图；MP4 和 GIF 从实际 WebM 录屏中截取七段，前六段保持正常速度，仅将最后的悬停放慢至半速，配合短字幕和直接切换。鼠标指示点跟随真实鼠标事件。短片省略重复视图，但对应截图仍在图集中。

| Chapter / 段落 | Short edit / 短片画面 | Duration / 时长 |
| --- | --- | --- |
| Overview / 总览 | Capsule overview → matrix / 胶囊总览 → 矩阵 | 2 × 1 s |
| Hyperedge / 超边 | Highlighted enclosure → incidence / 包络高亮 → 关联 | 2 × 1 s |
| Node / 节点 | Matrix → incidence / 矩阵 → 关联 | 2 × 1 s |
| Hover / 悬停 | Light-filled enclosure / 浅色填充包络 | 2 s · half speed / 半速 |

The captured bundle contains 39 nodes, 18 native hyperedges, and 65 membership
links. Matrix selection preserves the global table and highlights membership.
Incidence expands one selected hyperedge or summarizes one node's incident
hyperedges. Enclosure hover fills the current relationship lightly and fades
unrelated content. Recording does not modify nodes, hyperedges, memberships, or
evidence.

该数据包包含 39 个节点、18 条原生超边、65 条成员归属。矩阵中的选择只高亮、不删行列；关联视图按所选对象展示成员或所属超边；包络悬停为当前关系填入浅色并淡化无关内容。录制不改变节点、超边、成员关系和来源记录。

## Reproduce / 复现

GIFs are the public showcase format and loop without a player. The renderer also
keeps MP4 files for browser previews and frame validation.

GIF 是公开展示格式，无需播放器即可循环显示；渲染器也保留 MP4，便于浏览器预览和逐帧验证。

Optional media tools are separate from the Skill runtime. From the repository
root:

```sh
node tools/capture_showcase.mjs \
  --source examples/sushi-local-preview/views/capsule-trial/workbench.html \
  --bundle examples/sushi-local-preview/bundle \
  --out temp/live-capture \
  --playwright ./temp/media-runtime/node_modules/playwright

python tools/render_live_showcase.py \
  --capture temp/live-capture \
  --out docs/assets/showcase-v3 \
  --ffmpeg /path/to/ffmpeg

python tools/check_live_showcase.py \
  --assets docs/assets/showcase-v3 \
  --capture temp/live-capture \
  --ffmpeg /path/to/ffmpeg
```

To use an installed Chrome instead of downloading Chromium, pass
`--browser /path/to/chrome` to the capture command. If needed, also pass
`--ffmpeg /path/to/ffmpeg`. The capture uses an isolated temporary profile and
does not take over a daily browser session.

可通过 `--browser` 使用本机 Chrome，并通过 `--ffmpeg` 指定已有 FFmpeg。录制使用独立临时会话，不接管日常浏览器。

## Checks / 检查

`live-manifest.json` records source hashes, scene timing, screenshot hashes,
video metadata, and per-scene browser-state checks. `live-qa.json` confirms 20
published screenshots, ten gallery states per language, two eight-second GIFs,
two MP4 previews, decode checks, and source-hash checks.

这些检查确认素材来自正确的数据和交互，但不等同于证明每个画面在所有窗口尺寸下都完全无碰撞。密集结构仍应结合矩阵、局部聚焦和来源详情一起阅读。
