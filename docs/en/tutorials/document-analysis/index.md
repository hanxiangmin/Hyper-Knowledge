# Document Analysis Tutorial

Process large collections of documents efficiently.

---

## What You'll Learn

This tutorial covers strategies for processing large document collections:
- Batch processing techniques
- Parallelization strategies
- Error handling and recovery
- Performance optimization
- Memory management

---

## Use Cases

### Use Case 1: Document Archive Processing

Process thousands of historical documents:
- Legal document archives
- Medical records
- Research paper collections

### Use Case 2: Real-time Document Pipeline

Continuous processing of incoming documents:
- News feed analysis
- Social media monitoring
- Email processing

### Use Case 3: Large-scale Analysis

One-time processing of massive datasets:
- Corporate document repositories
- Government archives
- Academic databases

---

## Architecture

```
document-analysis/
├── input/              # Input documents
│   ├── pending/       # Documents to process
│   ├── processing/    # Currently processing
│   └── completed/     # Successfully processed
├── output/            # Extracted knowledge abstracts
│   ├── batch_001/
│   ├── batch_002/
│   └── combined/
├── logs/              # Processing logs
├── batch_processor.py # Main processor
└── config.yaml        # Configuration
```

---

## Strategies

### Strategy 1: Simple Batching

Process documents in fixed-size batches.

### Strategy 2: Parallel Processing

Use multiple workers to process documents concurrently.

### Strategy 3: Streaming

Process documents as they arrive without waiting for batches.

---

## Complete Example

```python
"""Batch Document Processor."""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Optional

from hyperknowledge import Template

# Setup logging
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
    """Process large collections of documents."""
    
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
        
        # Ensure directories exist
        for dir_name in ['input/pending', 'input/processing', 'input/completed', 
                        'output', 'logs']:
            Path(dir_name).mkdir(parents=True, exist_ok=True)
    
    def get_pending_documents(self) -> List[Path]:
        """Get list of pending documents."""
        pending_dir = Path("input/pending")
        docs = []
        docs.extend(pending_dir.glob("**/*.md"))
        docs.extend(pending_dir.glob("**/*.txt"))
        return sorted(docs)
    
    def process_single_document(self, doc_path: Path) -> ProcessingResult:
        """Process a single document."""
        import time
        start_time = time.time()
        
        try:
            # Move to processing
            processing_path = Path("input/processing") / doc_path.name
            doc_path.rename(processing_path)
            
            # Read document
            logger.info(f"Processing: {doc_path.name}")
            text = processing_path.read_text(encoding="utf-8")
            
            # Extract knowledge
            ka = Template.create(self.template, self.language)
            result = ka.parse(text)
            
            # Build index
            result.build_index()
            
            # Save output
            output_name = doc_path.stem
            output_path = Path("output") / output_name
            result.dump(str(output_path))
            
            # Move to completed
            completed_path = Path("input/completed") / doc_path.name
            processing_path.rename(completed_path)
            
            processing_time = time.time() - start_time
            logger.info(f"✓ Completed: {doc_path.name} ({processing_time:.2f}s)")
            
            return ProcessingResult(
                document=str(doc_path),
                success=True,
                output_path=str(output_path),
                error=None,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"✗ Failed: {doc_path.name} - {str(e)}")
            
            # Move back to pending for retry
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
        """Process a batch of documents."""
        results = []
        
        # Sequential processing (for memory efficiency)
        for doc in documents:
            result = self.process_single_document(doc)
            results.append(result)
        
        return results
    
    def process_parallel(self, documents: List[Path]) -> List[ProcessingResult]:
        """Process documents in parallel."""
        results = []
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_doc = {
                executor.submit(self.process_single_document, doc): doc 
                for doc in documents
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_doc):
                result = future.result()
                results.append(result)
        
        return results
    
    def run(self, parallel: bool = False):
        """Run the batch processor."""
        # Get pending documents
        documents = self.get_pending_documents()
        
        if not documents:
            logger.info("No pending documents to process")
            return []
        
        logger.info(f"Found {len(documents)} documents to process")
        
        # Process in batches
        all_results = []
        
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]
            logger.info(f"Processing batch {i//self.batch_size + 1}: {len(batch)} documents")
            
            if parallel:
                results = self.process_parallel(batch)
            else:
                results = self.process_batch(batch)
            
            all_results.extend(results)
            
            # Log batch summary
            successes = sum(1 for r in results if r.success)
            logger.info(f"Batch complete: {successes}/{len(batch)} successful")
        
        # Final summary
        total_success = sum(1 for r in all_results if r.success)
        logger.info(f"Processing complete: {total_success}/{len(documents)} successful")
        
        # Save results log
        self._save_results_log(all_results)
        
        return all_results
    
    def _save_results_log(self, results: List[ProcessingResult]):
        """Save processing results to log file."""
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
        
        logger.info(f"Results log saved: {log_file}")
    
    def combine_results(self, output_name: str = "combined"):
        """Combine all individual results into one knowledge abstract."""
        logger.info("Combining results...")
        
        output_dirs = [d for d in Path("output").iterdir() if d.is_dir()]
        
        if not output_dirs:
            logger.warning("No output directories found")
            return
        
        # Load first result
        ka = Template.create(self.template, self.language)
        combined = ka.load(str(output_dirs[0]))
        
        # Merge remaining
        for output_dir in output_dirs[1:]:
            ka = Template.create(self.template, self.language)
            ka.load(str(output_dir))
            
            # Merge entities and relations
            for entity in ka.data.entities:
                if entity not in combined.data.entities:
                    combined.data.entities.append(entity)
            
            for relation in ka.data.relations:
                if relation not in combined.data.relations:
                    combined.data.relations.append(relation)
        
        # Rebuild index and save
        combined.build_index()
        combined_path = Path("output") / output_name
        combined.dump(str(combined_path))
        
        logger.info(f"Combined knowledge abstract saved: {combined_path}")
        return combined


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch Document Processor")
    parser.add_argument("--template", default="general/graph", help="Template to use")
    parser.add_argument("--language", default="en", help="Document language")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size")
    parser.add_argument("--parallel", action="store_true", help="Enable parallel processing")
    parser.add_argument("--combine", action="store_true", help="Combine results after processing")
    
    args = parser.parse_args()
    
    processor = BatchDocumentProcessor(
        template=args.template,
        language=args.language,
        batch_size=args.batch_size
    )
    
    # Process documents
    results = processor.run(parallel=args.parallel)
    
    # Combine if requested
    if args.combine:
        processor.combine_results()
```

---

## Usage

### Setup

```bash
# Create directory structure
mkdir -p input/pending input/processing input/completed output logs

# Add documents to process
cp /path/to/documents/*.md input/pending/
```

### Run

```bash
# Sequential processing
python batch_processor.py

# Parallel processing
python batch_processor.py --parallel --max-workers 4

# With custom template
python batch_processor.py --template finance/earnings_summary

# Process and combine results
python batch_processor.py --combine
```

---

## Performance Tips

### 1. Batch Size

```python
# Small batches for memory-constrained environments
processor = BatchDocumentProcessor(batch_size=5)

# Larger batches for I/O bound processing
processor = BatchDocumentProcessor(batch_size=50)
```

### 2. Parallel Workers

```python
# CPU-bound: Match CPU cores
processor = BatchDocumentProcessor(max_workers=os.cpu_count())

# API-bound: Limit to avoid rate limits
processor = BatchDocumentProcessor(max_workers=5)
```

### 3. Memory Management

```python
# Process in smaller chunks
def process_large_dataset(documents, chunk_size=100):
    for i in range(0, len(documents), chunk_size):
        chunk = documents[i:i + chunk_size]
        results = processor.process_batch(chunk)
        
        # Save intermediate results
        save_checkpoint(results, i)
        
        # Clear memory
        gc.collect()
```

---

## Error Handling

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def process_with_retry(doc_path):
    return processor.process_single_document(doc_path)
```

### Failed Document Queue

```python
def process_with_fallback(documents):
    failed = []
    
    for doc in documents:
        result = processor.process_single_document(doc)
        if not result.success:
            failed.append(doc)
    
    # Retry failed documents with different settings
    for doc in failed:
        # Try with smaller chunks
        result = processor.process_single_document(
            doc, 
            chunk_size=1024  # Smaller chunks
        )
```

---

## Monitoring

### Progress Tracking

```python
from tqdm import tqdm

def process_with_progress(documents):
    results = []
    
    with tqdm(total=len(documents), desc="Processing") as pbar:
        for doc in documents:
            result = processor.process_single_document(doc)
            results.append(result)
            pbar.update(1)
            
            # Update description
            success_rate = sum(1 for r in results if r.success) / len(results)
            pbar.set_postfix({"success_rate": f"{success_rate:.1%}"})
    
    return results
```

### Metrics Collection

```python
import time
from dataclasses import asdict

def collect_metrics(results: List[ProcessingResult]):
    metrics = {
        "total_documents": len(results),
        "successful": sum(1 for r in results if r.success),
        "failed": sum(1 for r in results if not r.success),
        "avg_processing_time": sum(r.processing_time for r in results) / len(results),
        "total_time": sum(r.processing_time for r in results),
        "errors": [r.error for r in results if r.error]
    }
    
    with open("logs/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    
    return metrics
```

---

## Advanced: Streaming Processor

For real-time document processing:

```python
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class StreamingProcessor(FileSystemEventHandler):
    """Process documents as they arrive."""
    
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
                logger.info(f"Processed: {file_path}")
            else:
                logger.error(f"Failed: {file_path} - {result.error}")
            
            self.queue.task_done()
    
    def start(self, watch_dir: str = "input/pending"):
        # Start file watcher
        observer = Observer()
        observer.schedule(self, watch_dir, recursive=True)
        observer.start()
        
        # Start processing loop
        asyncio.run(self.process_queue())
```

---

## Summary

You now have a complete batch processing system that can:

✓ Process large document collections  
✓ Handle errors and retries  
✓ Run in parallel for speed  
✓ Monitor progress and collect metrics  
✓ Combine results into unified knowledge abstracts  

### Next Steps

- Deploy as a service
- Add REST API interface
- Implement real-time streaming
- Scale with distributed processing

---

## See Also

- [Research Assistant Tutorial](../research-assistant/index.md)
- [Knowledge Abstract Tutorial](../knowledge-base/index.md)
