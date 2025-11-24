Below is a **complete demo Python project** using the **src layout**, including `pytest`, plus the **common developer operations** (install, run, test, formatting, linting).
Everything is shown as a minimal but realistic structure.
 

# ✅ 1. Project Structure (src layout)

```
demo-app/
│
├── pyproject.toml
├── README.md
├── src/
│   └── demo_app/
│       ├── __init__.py
│       └── calculator.py
│
└── tests/
    └── test_calculator.py
```

---

# ✅ 2. `pyproject.toml`

This configuration uses:

* **uv** as the installer
* **setuptools** as build backend
* **pytest** as test framework
* **ruff** for lint + formatting
* **mypy** for type checking (optional but common)

```toml
[project]
name = "demo-app"
version = "0.1.0"
description = "A demo Python project using src layout"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-cov",
    "ruff",
    "mypy",
]

[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"
```

---

# ✅ 3. Example Source Code

### `src/demo_app/calculator.py`

```python
def add(a: int, b: int) -> int:
    return a + b


def subtract(a: int, b: int) -> int:
    return a - b
```

---

# ✅ 4. Tests

### `tests/test_calculator.py`

```python
from demo_app.calculator import add, subtract


def test_add():
    assert add(2, 3) == 5


def test_subtract():
    assert subtract(5, 3) == 2
```

---

# ✅ 5. Install the Project in Editable Mode (using uv)

```bash
uv pip install -e .[dev]
```

This installs:

* the **package** (demo_app)
* **pytest**
* **ruff**
* **mypy**
* any dev tools

---

# ✅ 6. Run the Tests

### Basic:

```bash
pytest
```

### With coverage:

```bash
pytest --cov=demo_app
```

### With verbose output:

```bash
pytest -v
```

---

# ✅ 7. Popular Developer Operations

These are common in nearly every modern Python project.

---

## ✔ Lint + Format (Ruff)

### Check style:

```bash
ruff check .
```

### Auto-fix:

```bash
ruff check . --fix
```

### Format like Black:

```bash
ruff format .
```

---

## ✔ Type Checking (Mypy)

```bash
mypy src
```

---

## ✔ Running the App

If you had an entry script (optional):

```
demo-app/
└── src/demo_app/__main__.py
```

You could run it like:

```bash
python -m demo_app
```

Or using uv:

```bash
uv run demo_app
```

---

# ✅ 8. Add a Simple CLI (optional but common)

### Add `__main__.py`

`src/demo_app/__main__.py`

```python
from .calculator import add

def main():
    print("2 + 3 =", add(2, 3))

if __name__ == "__main__":
    main()
```

Run it:

```bash
python -m demo_app
```
 