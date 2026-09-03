# 文档分析教程

高效处理大量文档集合。

---

## 你将学到什么

本教程涵盖处理大型文档集合的策略：
- 批处理技术
- 并行化策略
- 错误处理和恢复
- 性能优化
- 内存管理

---

## 用例

### 用例 1：文档档案处理

处理数千份历史文档：
- 法律文档档案
- 医疗记录
- 研究论文集合

### 用例 2：实时文档管道

持续处理传入文档：
- 新闻源分析
- 社交媒体监控
- 邮件处理

### 用例 3：大规模分析

一次性处理海量数据集：
- 企业文档仓库
- 政府档案
- 学术数据库

---

## 架构

```
document-analysis/
├── input/              # 输入文档
│   ├── pending/       # 待处理文档
│   ├── processing/    # 正在处理
│   └── completed/     # 成功处理
├── output/            # 提取的知识库
│   ├── batch_001/
│   ├── batch_002/
│   └── combined/
├── logs/              # 处理日志
├── batch_processor.py # 主处理器
└── config.yaml        # 配置
```

---

## 策略

### 策略 1：简单批处理

处理固定大小的批次文档。

### 策略 2：并行处理

使用多个工作线程并发处理文档。

### 策略 3：流式处理

文档到达时立即处理，无需等待批次。

---

## 完整示例

```python
"""批处理文档处理器。"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Optional

from hyperknowledge import Template

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    document: str
    success: bool
    output_path: Optional[str]
    error: Optional[str]
    processing_time: float


class BatchDocumentProcessor:
    """处理大量文档集合。"""
    
    def __init__(
        self,
        template: str = "general/graph",
        language: str = "en",
        batch_size: int = 10,
        max_workers: int = 4
    ):
        self.template = template
        self.language = language
        self.batch_size = batch_size
        self.max_workers = max_workers
        
        # 确保目录存在
        for dir_name in ['input/pending', 'input/processing', 'input/completed', 
                        'output', 'logs']:
            Path(dir_name).mkdir(parents=True, exist_ok=True)
    
    def get_pending_documents(self) -> List[Path]:
        """获取待处理文档列表。"""
        pending_dir = Path("input/pending")
        docs = []
        docs.extend(pending_dir.glob("**/*.md"))
        docs.extend(pending_dir.glob("**/*.txt"))
        return sorted(docs)
    
    def process_single_document(self, doc_path: Path) -> ProcessingResult:
        """处理单个文档。"""
        import time
        start_time = time.time()
        
        try:
            # 移至处理中
            processing_path = Path("input/processing") / doc_path.name
            doc_path.rename(processing_path)
            
            # 读取文档
            logger.info(f"处理: {doc_path.name}")
            text = processing_path.read_text(encoding="utf-8")
            
            # 提取知识
            ka = Template.create(self.template, self.language)
            result = ka.parse(text)
            
            # 构建索引
            result.build_index()
            
            # 保存输出
            output_name = doc_path.stem
            output_path = Path("output") / output_name
            result.dump(str(output_path))
            
            # 移至已完成
            completed_path = Path("input/completed") / doc_path.name
            processing_path.rename(completed_path)
            
            processing_time = time.time() - start_time
            logger.info(f"✓ 完成: {doc_path.name} ({processing_time:.2f}s)")
            
            return ProcessingResult(
                document=str(doc_path),
                success=True,
                output_path=str(output_path),
                error=None,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"✗ 失败: {doc_path.name} - {str(e)}")
            
            # 移回待处理以便重试
            if processing_path.exists():
                processing_path.rename(doc_path)
            
            return ProcessingResult(
                document=str(doc_path),
                success=False,
                output_path=None,
                error=str(e),
                processing_time=processing_time
            )
    
    def process_batch(self, documents: List[Path]) -> List[ProcessingResult]:
        """处理一批文档。"""
        results = []
        
        # 顺序处理（内存效率）
        for doc in documents:
            result = self.process_single_document(doc)
            results.append(result)
        
        return results
    
    def process_parallel(self, documents: List[Path]) -> List[ProcessingResult]:
        """并行处理文档。"""
        results = []
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_doc = {
                executor.submit(self.process_single_document, doc): doc 
                for doc in documents
            }
            
            # 收集完成的结果
            for future in as_completed(future_to_doc):
                result = future.result()
                results.append(result)
        
        return results
    
    def run(self, parallel: bool = False):
        """运行批处理器。"""
        # 获取待处理文档
        documents = self.get_pending_documents()
        
        if not documents:
            logger.info("没有待处理文档")
            return []
        
        logger.info(f"发现 {len(documents)} 个文档待处理")
        
        # 分批处理
        all_results = []
        
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]
            logger.info(f"处理批次 {i//self.batch_size + 1}: {len(batch)} 个文档")
            
            if parallel:
                results = self.process_parallel(batch)
            else:
                results = self.process_batch(batch)
            
            all_results.extend(results)
            
            # 记录批次摘要
            successes = sum(1 for r in results if r.success)
            logger.info(f"批次完成: {successes}/{len(batch)} 成功")
        
        # 最终摘要
        total_success = sum(1 for r in all_results if r.success)
        logger.info(f"处理完成: {total_success}/{len(documents)} 成功")
        
        # 保存结果日志
        self._save_results_log(all_results)
        
        return all_results
    
    def _save_results_log(self, results: List[ProcessingResult]):
        """保存处理结果到日志文件。"""
        log_data = [
            {
                "document": r.document,
                "success": r.success,
                "output_path": r.output_path,
                "error": r.error,
                "processing_time": r.processing_time,
                "timestamp": datetime.now().isoformat()
            }
            for r in results
        ]
        
        log_file = f"logs/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, "w") as f:
            json.dump(log_data, f, indent=2)
        
        logger.info(f"结果日志已保存: {log_file}")
    
    def combine_results(self, output_name: str = "combined"):
        """将所有单独结果合并为一个知识库。"""
        logger.info("合并结果...")
        
        output_dirs = [d for d in Path("output").iterdir() if d.is_dir()]
        
        if not output_dirs:
            logger.warning("未找到输出目录")
            return
        
        # 加载第一个结果
        ka = Template.create(self.template, self.language)
        combined = ka.load(str(output_dirs[0]))
        
        # 合并剩余结果
        for output_dir in output_dirs[1:]:
            ka = Template.create(self.template, self.language)
            ka.load(str(output_dir))
            
            # 合并实体和关系
            for entity in ka.data.entities:
                if entity not in combined.data.entities:
                    combined.data.entities.append(entity)
            
            for relation in ka.data.relations:
                if relation not in combined.data.relations:
                    combined.data.relations.append(relation)
        
        # 重建索引并保存
        combined.build_index()
        combined_path = Path("output") / output_name
        combined.dump(str(combined_path))
        
        logger.info(f"合并知识库已保存: {combined_path}")
        return combined


# CLI 接口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="批处理文档处理器")
    parser.add_argument("--template", default="general/graph", help="使用的模板")
    parser.add_argument("--language", default="en", help="文档语言")
    parser.add_argument("--batch-size", type=int, default=10, help="批次大小")
    parser.add_argument("--parallel", action="store_true", help="启用并行处理")
    parser.add_argument("--combine", action="store_true", help="处理后合并结果")
    
    args = parser.parse_args()
    
    processor = BatchDocumentProcessor(
        template=args.template,
        language=args.language,
        batch_size=args.batch_size
    )
    
    # 处理文档
    results = processor.run(parallel=args.parallel)
    
    # 如需要则合并
    if args.combine:
        processor.combine_results()
```

---

## 使用说明

### 设置

```bash
# 创建目录结构
mkdir -p input/pending input/processing input/completed output logs

# 添加待处理文档
cp /path/to/documents/*.md input/pending/
```

### 运行

```bash
# 顺序处理
python batch_processor.py

# 并行处理
python batch_processor.py --parallel --max-workers 4

# 使用自定义模板
python batch_processor.py --template finance/earnings_summary

# 处理并合并结果
python batch_processor.py --combine
```

---

## 性能提示

### 1. 批次大小

```python
# 内存受限环境使用小批次
processor = BatchDocumentProcessor(batch_size=5)

# I/O 密集型处理使用大批次
processor = BatchDocumentProcessor(batch_size=50)
```

### 2. 并行工作线程

```python
# CPU 密集型: 匹配 CPU 核心数
processor = BatchDocumentProcessor(max_workers=os.cpu_count())

# API 密集型: 限制以避免速率限制
processor = BatchDocumentProcessor(max_workers=5)
```

### 3. 内存管理

```python
# 分小块处理
def process_large_dataset(documents, chunk_size=100):
    for i in range(0, len(documents), chunk_size):
        chunk = documents[i:i + chunk_size]
        results = processor.process_batch(chunk)
        
        # 保存中间结果
        save_checkpoint(results, i)
        
        # 清理内存
        gc.collect()
```

---

## 错误处理

### 重试逻辑

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def process_with_retry(doc_path):
    return processor.process_single_document(doc_path)
```

### 失败文档队列

```python
def process_with_fallback(documents):
    failed = []
    
    for doc in documents:
        result = processor.process_single_document(doc)
        if not result.success:
            failed.append(doc)
    
    # 使用不同设置重试失败文档
    for doc in failed:
        # 尝试使用更小的分块
        result = processor.process_single_document(
            doc, 
            chunk_size=1024  # 更小的分块
        )
```

---

## 监控

### 进度跟踪

```python
from tqdm import tqdm

def process_with_progress(documents):
    results = []
    
    with tqdm(total=len(documents), desc="处理中") as pbar:
        for doc in documents:
            result = processor.process_single_document(doc)
            results.append(result)
            pbar.update(1)
            
            # 更新描述
            success_rate = sum(1 for r in results if r.success) / len(results)
            pbar.set_postfix({"成功率": f"{success_rate:.1%}"})
    
    return results
```

### 指标收集

```python
import time
from dataclasses import asdict

def collect_metrics(results: List[ProcessingResult]):
    metrics = {
        "总文档数": len(results),
        "成功": sum(1 for r in results if r.success),
        "失败": sum(1 for r in results if not r.success),
        "平均处理时间": sum(r.processing_time for r in results) / len(results),
        "总时间": sum(r.processing_time for r in results),
        "错误": [r.error for r in results if r.error]
    }
    
    with open("logs/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    
    return metrics
```

---

## 高级：流式处理器

用于实时文档处理：

```python
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class StreamingProcessor(FileSystemEventHandler):
    """文档到达时立即处理。"""
    
    def __init__(self):
        self.processor = BatchDocumentProcessor()
        self.queue = asyncio.Queue()
    
    def on_created(self, event):
        if not event.is_directory:
            self.queue.put_nowait(event.src_path)
    
    async def process_queue(self):
        while True:
            file_path = await self.queue.get()
            result = self.processor.process_single_document(Path(file_path))
            
            if result.success:
                logger.info(f"已处理: {file_path}")
            else:
                logger.error(f"失败: {file_path} - {result.error}")
            
            self.queue.task_done()
    
    def start(self, watch_dir: str = "input/pending"):
        # 启动文件监视器
        observer = Observer()
        observer.schedule(self, watch_dir, recursive=True)
        observer.start()
        
        # 启动处理循环
        asyncio.run(self.process_queue())
```

---

## 总结

您现在拥有一个完整的批处理系统，可以：

✓ 处理大型文档集合  
✓ 处理错误和重试  
✓ 并行运行以提高速度  
✓ 监控进度和收集指标  
✓ 将结果合并为统一的知识库  

### 下一步

- 部署为服务
- 添加 REST API 接口
- 实现实时流式处理
- 使用分布式处理扩展

---

## 参见

- [研究助手教程](../research-assistant/index.md)
- [知识库教程](../knowledge-base/index.md)
