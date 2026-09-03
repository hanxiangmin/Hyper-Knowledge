# Python 快速入门

在 5 分钟内开始使用 Hyper-Knowledge Python SDK。

---

## 前置要求

- Python 3.11+
- OpenAI API 密钥

## 安装

```bash
pip install "hyper-knowledge @ git+https://github.com/hanxiangmin/Hyper-Knowledge.git"
```

## 基本用法

### 1. 配置 API 密钥

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key"
```

或使用 `.env` 文件：

```python
from dotenv import load_dotenv
load_dotenv()
```

### 2. 提取知识

```python
from hyperknowledge import Template

# 创建模板
ka = Template.create("general/biography_graph", language="zh")

# 您的文本
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

# 提取
result = ka.parse(text)

# 访问结果
print(f"节点数: {len(result.nodes)}")
print(f"边数: {len(result.edges)}")

# 打印第一个节点
if result.nodes:
    node = result.nodes[0]
    print(f"\n第一个: {node.name} ({node.type})")
    print(f"描述: {node.description}")
```

**输出：**
```
节点数: 5
边数: 4

第一个: 苏轼 (人物)
描述: 北宋文学家、书画家、政治家
```

### 3. 可视化

```python
# 构建索引以支持搜索/对话功能
result.build_index()

# 打开交互式可视化
result.show()
```

![交互式可视化](../../assets/zh_show.jpg)

### 4. 搜索

```python
# 构建搜索索引
result.build_index()

# 搜索
nodes, edges = result.search("代表作", top_k=3)
for node in nodes:
    print(f"节点: {node.name}")
for edge in edges:
    print(f"边: {edge.source} -> {edge.target}")
```

### 5. 聊天

```python
# 提问
response = result.chat("苏轼写过哪些著名的诗词？")
print(response.content)
```

### 6. 保存和加载

```python
# 保存到磁盘
result.dump("./sushi_kb/")

# 之后加载
new_ka = Template.create("general/biography_graph", language="zh")
new_ka.load("./sushi_kb/")
```

---

## 完整示例

```python
"""完整示例：提取、探索和保存知识。"""

from dotenv import load_dotenv
load_dotenv()

from hyperknowledge import Template

def main():
    # 创建模板
    print("Creating template...")
    ka = Template.create("general/biography_graph", language="zh")
    
    # 示例文本
    text = """
    苏轼，字子瞻，号东坡居士，是北宋时期最杰出的文学家、书画家、政治家。
    他与父亲苏洵、弟弟苏辙并称"三苏"，同列唐宋八大家。
    
    苏轼于1037年出生于眉州眉山。1057年科举中举，受欧阳修赏识。
    后因乌台诗案被贬黄州，创作了大量千古传诵的名篇。
    
    代表作：《念奴娇·赤壁怀古》《水调歌头·明月几时有》《赤壁赋》
    
    苏轼一生宦海浮沉，历任杭州、密州、徐州、湖州等地知州。
    在杭州任上，他疏浚西湖，修筑苏堤。
    晚年因新党执政被贬至惠州、儋州，仍心系百姓，兴办学堂，传播中原文化。
    """
    
    # 提取知识
    print("Extracting knowledge...")
    result = ka.parse(text)
    
    # 显示结果
    print(f"\n提取结果：")
    print(f"  节点数: {len(result.nodes)}")
    print(f"  边数: {len(result.edges)}")

    # 列出节点
    print("\n发现的节点：")
    for node in result.nodes:
        print(f"  - {node.name} ({node.type})")
    
    # 构建索引和搜索
    print("\nBuilding search index...")
    result.build_index()
    
    search_nodes, search_edges = result.search("西湖", top_k=2)
    print(f"\n搜索结果: {len(search_nodes)} 个节点, {len(search_edges)} 条边")
    
    # 保存
    print("\nSaving knowledge abstract...")
    result.dump("./sushi_kb/")
    
    print("\nDone! Try: hk show ./sushi_kb/")

if __name__ == "__main__":
    main()
```

---

## 下一步

- 学习[核心概念](core-concepts.md)
- 阅读[使用模板指南](guides/using-templates.md)
- 探索 [API 参考](api-reference/template.md)
