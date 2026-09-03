# 增量更新

!!! tip "进阶 - 提取后操作"
    本指南涵盖初始提取后添加更多文档。您应该先熟悉 [Level 1: 使用模板](using-templates.md)。

在不重新处理的情况下向现有知识库添加新信息。

---

## 概述

`feed_text()` 方法允许您增量地向现有知识库添加文档：

1. **保留现有数据** — 不会覆盖已有内容
2. **智能合并** — 处理重复和冲突
3. **更新元数据** — 跟踪更新发生的时间

---

## 基本用法

```python
from hyperknowledge import Template

ka = Template.create("general/biography_graph", "zh")

# 初始提取
result = ka.parse(initial_text)
print(f"初始: {len(result.nodes)} 个节点")

# 添加更多内容
result.feed_text(additional_text)
print(f"Feed 后: {len(result.nodes)} 个节点")
```

---

## 用例

### 随着时间构建知识

```python
ka = Template.create("general/biography_graph", "zh")
ka = ka.parse(early_life_text)

# 添加职业信息
ka.feed_text(career_text)

# 添加晚年
ka.feed_text(later_years_text)

# 在 feed 新数据后重建索引
ka.build_index()

# 最终结果组合所有时期（支持交互式搜索/对话）
ka.show()
```

![交互式可视化](../../../assets/zh_show.jpg)

### 处理多个文档

```python
ka = Template.create("general/concept_graph", "zh")
ka = ka.parse(documents[0])

for doc in documents[1:]:
    ka.feed_text(doc)
    print(f"已添加文档，现在有 {len(ka.nodes)} 个节点")
```

### 使用新信息更新

```python
# 原始提取
ka = ka.parse(original_paper)

# 添加更正/更新
ka.feed_text(corrections)

# 保存更新版本
ka.dump("./updated_ka/")
```

---

## 合并如何工作

### 实体合并

```python
# 如果相同实体出现在两个文本中
# 结果：合并描述，字段组合
```

### 关系合并

```python
# 如果相同关系存在
# 结果：使用最新信息更新
```

### 重复处理

```python
# 检测并合并完全重复的
# 相似的重复（相似名称）可能创建单独条目
```

---

## 最佳实践

### 1. 相同的模板类型

确保使用兼容的自动类型：

```python
# 好：相同模板类型
ka = ka.parse(text1)  # biography_graph
ka.feed_text(text2)   # 相同类型

# 注意：混合类型可能导致问题
```

### 2. Feed 后重建索引

```python
ka.feed_text(new_text)
ka.build_index()  # 搜索/聊天需要
```

### 3. 保存中间状态

```python
# 重大更新后保存
ka.feed_text(chapter1)
ka.dump("./kb_v1/")

ka.feed_text(chapter2)
ka.dump("./kb_v2/")
```

### 4. 监控增长

```python
initial_count = len(ka.nodes)
ka.feed_text(new_text)
new_count = len(ka.nodes)

print(f"添加了 {new_count - initial_count} 个新节点")
```

---

## 完整示例

```python
"""从多个来源增量构建知识库。"""

from hyperknowledge import Template
from pathlib import Path

def build_ka(source_dir, output_dir):
    ka = Template.create("general/biography_graph", "zh")
    
    # 获取所有文本文件
    files = sorted(Path(source_dir).glob("*.md"))
    
    if not files:
        print("未找到文件")
        return
    
    # 从第一个文件初始提取
    print(f"处理 {files[0].name}...")
    ka = ka.parse(files[0].read_text())
    
    # Feed 剩余文件
    for file in files[1:]:
        print(f"添加 {file.name}...")
        ka.feed_text(file.read_text())
        print(f"  现在有 {len(ka.nodes)} 个节点")
    
    # 为搜索/聊天构建索引
    print("构建搜索索引...")
    ka.build_index()
    
    # 保存
    print(f"保存到 {output_dir}...")
    ka.dump(output_dir)
    
    print("完成！")
    return ka

# 用法
ka = build_ka("./sources/", "./combined_ka/")
```

---

## 比较：Parse vs Feed

| 操作 | 使用时机 | 结果 |
|-----------|----------|--------|
| `parse()` | 从头开始 | 新知识库 |
| `feed_text()` | 添加到现有 | 更新的知识库 |

### 链式操作

```python
# Parse 返回新实例
result1 = ka.parse(text1)
result2 = ka.parse(text2)  # 独立于 result1

# Feed 修改现有
result1.feed_text(text2)   # result1 被更新
```

---

## 限制

### 1. 内存使用

大型知识库消耗内存：

```python
# 监控大小
import sys
size = sys.getsizeof(ka.data)
print(f"知识库大小: {size} 字节")
```

### 2. 合并质量

合并并不完美：
- 相似但不完全相同的实体可能不会合并
- 非常大的知识库可能会变慢

### 3. 索引过期

Feed 后始终重建：

```python
ka.feed_text(text)
ka.build_index()  # 不要忘记！
```

---

## 故障排除

### "内存错误"

分批处理：

```python
for batch in chunks(documents, batch_size=5):
    for doc in batch:
        ka.feed_text(doc)
    ka.dump(f"./kb_checkpoint/")  # 定期保存
```

### "重复实体"

规范化实体名称：

```python
# 不要"苏轼"和"苏东坡"混用
# 使用一致的命名
```

### "索引过期"

```python
# 忘记重建了？
ka.build_index()
```

---

## 另请参见

**相关工作流：**
- [搜索和聊天](search-and-chat.md) — 查询更新后的知识
- [保存和加载](saving-loading.md) — 持久化合并结果

**基础知识：**
- [使用模板](using-templates.md) — Level 1 基础
- [使用自动类型](working-with-autotypes.md) — Level 2 自定义
