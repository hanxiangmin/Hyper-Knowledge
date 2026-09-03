# Hyper-Knowledge Dataset Benchmark

- Status: `passed`
- Mode: `offline_preflight`
- Datasets: 2
- Passed: 2
- Failed: 0
- Warnings: 2
- Manifest SHA-256: `8c9f6da95c12c8e5c6ec93063fa4a40caf6ba8c06ad3302b3b9eb826813dcf43`

> Offline preflight validates files and dataset contracts only; it does not measure extraction accuracy or model quality.

| Dataset | Language | Domain | Bytes | Status |
|---|---:|---:|---:|---:|
| examples/en/tesla_question.md | - | - | 191 | passed |
| examples/zh/sushi_question.md | - | - | 162 | passed |

## Diagnostics

| Severity | Dataset | Check | Evidence | Supported fix |
|---|---|---|---|---|
| warning | examples/en/tesla_question.md | dataset.markdown_heading | no Markdown heading found | Add a descriptive Markdown heading or document the exception |
| warning | examples/zh/sushi_question.md | dataset.markdown_heading | no Markdown heading found | Add a descriptive Markdown heading or document the exception |
