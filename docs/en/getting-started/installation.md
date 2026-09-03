# Installation

Hyper-Knowledge requires **Python 3.11+**.

---

## Install as CLI Tool

If you want to use the `hk` command from anywhere:

=== "uv (recommended)"

    Install [uv](https://docs.astral.sh/uv/) first (if you haven't):

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

    Then install Hyper-Knowledge:

    ```bash
    uv tool install hyperknowledge
    ```

=== "pipx"

    ```bash
    pipx install hyperknowledge
    ```

    > Don't have pipx? Install it with `pip install pipx`.

---

## Install as Python Library

If you want to use Hyper-Knowledge in your Python code:

=== "uv (recommended)"

    ```bash
    uv pip install hyperknowledge
    ```

=== "pip"

    ```bash
    pip install hyperknowledge
    ```

---

## Verify Installation

=== "CLI"

    ```bash
    hk --version
    ```

    You should see something like:

    ```
    Hyper-Knowledge CLI version 0.4.0
    ```

=== "Python"

    ```python
    import hyperknowledge
    print(hyperknowledge.__version__)
    ```

---

## Development Installation

If you want to contribute or modify the source code:

```bash
git clone https://github.com/hanxiangmin/Hyper-Knowledge.git
cd hyper-knowledge

# Install with uv (recommended)
uv sync --extra dev

# Or with pip
pip install -e ".[dev]"
```

---

## What's Next?

- [:octicons-arrow-right-24: CLI Quickstart](cli-quickstart.md) — Your first extraction from the terminal
- [:octicons-arrow-right-24: Python Quickstart](python-quickstart.md) — Your first extraction with Python
