# Quick Start

The smallest possible TermUI app:

```python
from termui import App, Button

def on_click():
    print("Hello, TermUI!")

app = App(Button("Click Me", on_click=on_click, variant="primary"))
app.run()
```

Output: a clickable button themed using your default theme.

- [Concepts](concepts.md) explains the building blocks.
- [Guides](../guides/layouts.md) shows how to build real UIs.
