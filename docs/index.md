# TermUI

> A modern, declarative, and efficient Terminal UI library for Python.

---

## 🎯 Why TermUI?

Most terminal UI libraries fall into one of two extremes:

- **Low-level** (like `curses`) — powerful but verbose, every detail must be handled manually.
- **High-level frameworks** (like `textual`) — full-featured but heavy, with steep learning curves.

**TermUI** takes a different path:

- **Declarative, React-like API** — build UIs by composing widgets, not redrawing text.
- **Consistent by default** — centralized theming + variants mean your UI looks good with minimal effort.
- **Efficient and async** — a diff-based renderer ensures only what changes is updated.
- **Simple but powerful** — easy to start, flexible enough for full-screen apps.

The goal is to make terminal apps feel as natural to build as modern web apps, while staying fast, lean, and Pythonic.

---

## ✨ Core Principles

- **Declarative** – UIs are defined as nested components, not imperative drawing calls.
- **Themed** – colors and styles are centralized, ensuring consistency across widgets.
- **Composable** – small widgets combine to build complex layouts.
- **Efficient** – diff-based rendering avoids costly full-screen redraws.
- **Accessible** – easy to get started, but extensible for advanced users.

---

## 🚀 Example

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

---

## 🎨 Theming & Variants

TermUI ships with a familiar set of theme tokens:

```
primary, primary_content
secondary, secondary_content
accent, accent_content
neutral, neutral_content
base_100, base_200, base_300, base_content
info, info_content
success, success_content
warning, warning_content
error, error_content
```

Widgets map directly to these through **variants**:

```python
Button("Save", variant="primary")
Button("Cancel", variant="secondary")
Button("Delete", variant="error")
```

---

## 📚 Learn More

- [Getting Started →](getting-started/installation.md)
- [Quick Start →](getting-started/quickstart.md)
- [Guides →](guides/layouts.md)
- [API Reference →](api/app.md)

---

## 🛠️ Roadmap

- Core widgets (Button, Input, ProgressBar, Checkbox, RadioBox, Container)
- Layout system (vertical, horizontal, grid)
- Centralized theming + variants
- Diff-based async rendering
- Mouse & keyboard input

Future goals: animations, advanced widgets (Table, Modal, Dropdown), and plugin support.

---

## ❤️ Philosophy

We believe terminal apps should be:

- **Fast to build** — no boilerplate, no fuss.
- **Consistent by design** — theming and variants give a polished look out of the box.
- **Efficient under the hood** — diff rendering ensures smooth performance.
- **Familiar to modern developers** — inspired by the best ideas from web UI libraries.

If building terminal apps feels like building for the web — **but simpler** — we’ve done our job.

---
