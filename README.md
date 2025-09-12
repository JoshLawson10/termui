# TermUI

> A modern, opinionated Terminal UI library for Python.

TermUI makes it fast and simple to build good-looking terminal applications.
It combines a **declarative widget API**, **centralized theming with variants**, and an
**async diff-based renderer** — so your apps look consistent and run efficiently.

---

## ✨ Features

- 🎨 **Centralized theming** — consistent look via theme tokens (`primary`, `secondary`,
  `accent`, etc.)
- 🧩 **Composable widgets** — Button, Container, Checkbox, RadioBox, Input, ProgressBar
- ⚡ **Diff-based rendering** — minimal redraws for performance
- ⌨️🖱️ **Keyboard & mouse input** — interactive UIs with hover + click support
- 📐 **Layout system** — vertical, horizontal, and grid layouts
- 🔌 **Variants API** — shadcn-style `variant="primary"` customization

---

## 📦 Installation

```bash
pip install termui
```

---

## 🚀 Quick Start

```python
from termui import App, Button, Container, VerticalLayout


def on_click():
    print("Button clicked!")


app = App(
    VerticalLayout(
        Container(
            Button("Click Me", on_click=on_click, variant="primary")
        )
    )
)

app.run()
```

Run this, and you’ll get a themed button in the terminal that reacts to clicks.

---

## 🎨 Theming

TermUI uses a centralized theme system with a familiar set of tokens:

```python
theme = {
    "primary": "#1d4ed8",
    "primary_content": "#ffffff",
    "secondary": "#9333ea",
    "secondary_content": "#ffffff",
    "accent": "#f59e0b",
    "accent_content": "#000000",
    "neutral": "#374151",
    "neutral_content": "#f3f4f6",
    "base_100": "#111827",
    "base_200": "#1f2937",
    "base_300": "#4b5563",
    "base_content": "#f9fafb",
    "info": "#0ea5e9",
    "info_content": "#ffffff",
    "success": "#22c55e",
    "success_content": "#ffffff",
    "warning": "#facc15",
    "warning_content": "#000000",
    "error": "#ef4444",
    "error_content": "#ffffff",
}
```

Widgets can use **variants** to map directly to theme tokens:

```python
Button("Save", variant="primary")
Button("Cancel", variant="secondary")
Button("Delete", variant="error")
```

---

## 📚 Documentation

See the full docs **[here](https://joshlawson10.github.io/termui)**.

---

## 🛠️ Roadmap

- [x] Core widgets (Button, Container, Checkbox, RadioBox, Input, ProgressBar)
- [x] Diff-based async rendering engine
- [x] Keyboard + mouse input
- [ ] Advanced layouts
- [ ] More widgets (Table, Modal, Dropdown, TextArea)
- [ ] Animations + transitions
- [ ] Plugin system for custom widgets

---
