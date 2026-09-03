# 安装

Hyper-Knowledge 需要 **Python 3.11+**。

---

## 安装为 CLI 工具

如果您想在任何地方使用 `hk` 命令：

=== "uv (推荐)"

    首先安装 [uv](https://docs.astral.sh/uv/)（如果尚未安装）：

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

    然后安装 Hyper-Knowledge：

    ```bash
    uv tool install hyperknowledge
    ```

=== "pipx"

    ```bash
    pipx install hyperknowledge
    ```

    > 没有安装 pipx？运行 `pip install pipx` 安装。

---

## 安装为 Python 库

如果您想在 Python 代码中使用 Hyper-Knowledge：

=== "uv (推荐)"

    ```bash
    uv pip install hyperknowledge
    ```

=== "pip"

    ```bash
    pip install hyperknowledge
    ```

---

## 验证安装

=== "CLI"

    ```bash
    hk --version
    ```

    您应该看到类似输出：

    ```
    Hyper-Knowledge CLI version 0.4.0
    ```

=== "Python"

    ```python
    import hyperknowledge
    print(hyperknowledge.__version__)
    ```

---

## 开发安装

如果您想贡献或修改源代码：

```bash
git clone https://github.com/hanxiangmin/Hyper-Knowledge.git
cd hyper-knowledge

# 使用 uv 安装（推荐）
uv sync --extra dev

# 或使用 pip
pip install -e ".[dev]"
```

---

## 接下来做什么？

- [:octicons-arrow-right-24: CLI 快速入门](cli-quickstart.md) — 从终端进行首次提取
- [:octicons-arrow-right-24: Python 快速入门](python-quickstart.md) — 使用 Python 进行首次提取
