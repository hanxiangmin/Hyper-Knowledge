# Python 快速入门

使用 Python 在 5 分钟内完成首次知识提取。

---

## 前置要求

- [Hyper-Knowledge 已安装](installation.md)

---

## 第 1 步：搭建项目

创建新目录并设置环境：

```bash
mkdir my_extraction_project
cd my_extraction_project

# 创建虚拟环境（可选但推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装 hyperknowledge
pip install "hyper-knowledge @ git+https://github.com/hanxiangmin/Hyper-Knowledge.git"
```

---

## 第 2 步：配置模型

**方式 A — OpenAI（默认）**

创建 `.env` 文件：

```bash
echo "OPENAI_API_KEY=your-api-key" > .env
```

**方式 B — 其他 Provider（Anthropic、DeepSeek、百炼、vLLM）**

在 `.env` 中设置相应的环境变量：

```bash
# Anthropic
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx          # 用于 embeddings

# DeepSeek
DEEPSEEK_API_KEY=sk-xxx
OPENAI_API_KEY=sk-xxx          # 用于 embeddings

# 百炼（阿里云）
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

然后在脚本中配置客户端：

```python
from hyperknowledge import create_client, Template

# 示例：DeepSeek LLM + OpenAI embedder
llm, emb = create_client(llm="deepseek", embedder="openai:text-embedding-3-small")
ka = Template.create("general/biography_graph", language="zh", llm_client=llm, embedder=emb)
```

详见 [Provider 配置指南](../python/guides/provider-configuration.md)。

---

## 第 3 步：创建首个提取脚本

创建文件 `extract.py`：

```python
from dotenv import load_dotenv

# 从 .env 文件加载 API 密钥
load_dotenv()

from hyperknowledge import Template

# 创建模板实例
ka = Template.create("general/biography_graph", language="zh")

# 示例文本
text = """
苏轼，字子瞻，号东坡居士，是北宋时期最杰出的文学家、书画家、政治家。
他与父亲苏洵、弟弟苏辙并称"三苏"，同列唐宋八大家。

苏轼于1037年出生于眉州眉山。1057年科举中举，受欧阳修赏识。
后因乌台诗案被贬黄州，创作了大量千古传诵的名篇。

代表作：《念奴娇·赤壁怀古》《水调歌头·明月几时有》《赤壁赋》

苏轼一生宦海浮沉，历任杭州、密州、徐州、湖州等地知州。
在杭州任上，他疏浚西湖，修筑苏堤，留下"欲把西湖比西子"的千古名句。
晚年因新党执政被贬至惠州、儋州，仍心系百姓，兴办学堂，传播中原文化。

其文学成就横跨诗、词、文、赋，书法位列"宋四家"之首，
绘画开文人画先河，是中国历史上罕见的全才式人物。
"""

# 提取知识
result = ka.parse(text)

# 访问提取的数据
print(f"节点: {len(result.nodes)}")
print(f"边: {len(result.edges)}")

# 打印第一个节点
if result.nodes:
    node = result.nodes[0]
    print(f"\n第一个节点: {node.name} ({node.type})")

# 构建索引以支持搜索/对话功能
result.build_index()

# 可视化
result.show()
```

---

## 第 4 步：运行脚本

```bash
python extract.py
```

你应该看到：

```
节点: 5
边: 4

第一个节点: 苏轼 (人物)
```

同时会打开浏览器窗口显示交互式知识图谱。

![知识图谱可视化](../../assets/zh_show.jpg)

---

## 第 5 步：处理结果

访问提取结果的不同部分：

```python
# 遍历所有节点
for node in result.nodes:
    print(f"- {node.name}: {node.description}")

# 遍历所有边
for edge in result.edges:
    print(f"- {edge.source} --{edge.type}--> {edge.target}")

# 在知识库中搜索
result.build_index()
nodes, edges = result.search("代表作", top_k=3)
for node in nodes:
    print(f"节点: {node.name}")
for edge in edges:
    print(f"边: {edge.source} -> {edge.target}")
```

---

## 第 6 步：保存和加载

保存知识库以便后续使用：

```python
# 保存到磁盘
result.dump("./my_ka/")

# 稍后加载回来
new_ka = Template.create("general/biography_graph", language="zh")
new_ka.load("./my_ka/")
```

---

## 第 7 步：增量更新

添加更多文本而不会丢失现有知识：

```python
additional_text = """
1071年，苏轼主动请求外放，任杭州通判。在杭州期间他常常泛舟西湖，
写下了著名的《饮湖上初晴后雨》："欲把西湖比西子，淡妆浓抹总相宜。"
"""

# feed 添加到现有知识
result.feed_text(additional_text)

# 重新构建索引
result.build_index()

# 可视化更新后的图谱
result.show()
```

![更新后的知识图谱可视化](../../assets/zh_show.jpg)

---

## 完整示例

以下是完整的、可用于生产的脚本：

```python
"""从文档中提取知识并与之交互。"""

import os
from pathlib import Path
from dotenv import load_dotenv
from hyperknowledge import Template

# 配置
load_dotenv()

INPUT_FILE = "document.txt"
OUTPUT_DIR = "./output/"
TEMPLATE = "general/biography_graph"
LANGUAGE = "zh"


def main():
    # 创建模板
    print(f"创建模板: {TEMPLATE}")
    ka = Template.create(TEMPLATE, language=LANGUAGE)
    
    # 读取文档
    print(f"读取: {INPUT_FILE}")
    text = Path(INPUT_FILE).read_text(encoding="utf-8")
    
    # 提取知识
    print("提取知识...")
    result = ka.parse(text)
    
    # 打印摘要
    print(f"\n提取完成:")
    print(f"  - 节点: {len(result.nodes)}")
    print(f"  - 边: {len(result.edges)}")
    
    # 构建搜索索引
    print("构建搜索索引...")
    result.build_index()
    
    # 保存到磁盘
    print(f"保存到: {OUTPUT_DIR}")
    result.dump(OUTPUT_DIR)
    
    # 交互式可视化
    print("打开可视化...")
    result.show()
    
    print("\n完成!")


if __name__ == "__main__":
    main()
```

![交互式知识图谱可视化](../../assets/zh_show.jpg)

---

## 下一步

- [Python SDK 概览](../python/index.md) — 完整 API 参考
- [使用模板](../python/guides/using-templates.md) — 模板使用指南
- [自动类型指南](../concepts/autotypes.md) — 选择合适的数据结构

---

## 故障排除

**"No module named 'hyperknowledge'"**
→ 运行 `pip install "hyper-knowledge @ git+https://github.com/hanxiangmin/Hyper-Knowledge.git"`

**"API key not found"**
→ 检查 `.env` 文件或设置 `OPENAI_API_KEY` 环境变量

**"Template not found"**
→ 使用 `Template.list()` 查看可用模板
