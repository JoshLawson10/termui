# TermUI

A modern, asynchronous terminal user interface library for Python that makes building beautiful terminal applications simple and intuitive.

## Overview

TermUI is a Python library designed to create rich, interactive terminal applications with ease. Built on modern async/await patterns, it provides a widget-based architecture similar to modern GUI frameworks but optimized for terminal environments.

### Key Features

- **Asynchronous Architecture**: Built from the ground up with async/await for responsive, non-blocking applications
- **Widget-Based Design**: Compose complex UIs from simple, reusable widget components
- **Flexible Layout System**: Multiple layout options including vertical, horizontal, and grid layouts
- **Rich Styling**: Support for colors, borders, and visual effects using modern terminal capabilities
- **Event Handling**: Comprehensive keyboard and mouse input handling with customizable keybinds
- **Screen Management**: Multi-screen applications with easy navigation and state management
- **Efficient Rendering**: Differential rendering system that only updates changed content

### Quick Example

```python
from termui import App
from termui.widgets import Text, Button, Container
from termui.layouts import VerticalLayout
from termui.screen import Screen
from termui.color import Color

class MainScreen(Screen):
    def setup(self):
        self.screen_metadata(
            name="Main Screen",
            background_color=Color(20, 20, 30)
        )

    def build(self):
        return VerticalLayout(
            Container(
                title="Welcome to TermUI",
                title_color=Color(100, 200, 255)
            ),
            Text("Hello, Terminal World!",
                 fg_color=Color(255, 255, 255)),
            Button("Click Me!",
                   style="primary medium",
                   on_click=self.handle_click),
            spacing=1
        )

    def handle_click(self):
        print("Button clicked!")

    def update(self):
        pass

class MyApp(App):
    def build(self):
        main_screen = MainScreen()
        self.register_screen(main_screen)
        self.show_screen("Main Screen")

if __name__ == "__main__":
    app = MyApp()
    app.run()
```

## Architecture

TermUI follows a component-based architecture with several key concepts:

### Applications (`App`)

The main entry point for your terminal application. Apps manage screens, handle the main event loop, and coordinate rendering.

[Read More ->](api/index.md)

### Screens (`Screen`)

Individual views or pages in your application. Screens contain widgets and define the complete UI for a particular state or view.

[Read More ->](api/index.md)

### Widgets

The building blocks of your UI. TermUI includes several built-in widgets.

[Read More ->](api/widget.md)

### Layouts

Organize and position widgets automatically:

- `VerticalLayout` - Stack widgets vertically
- `HorizontalLayout` - Arrange widgets horizontally
- `GridLayout` - Position widgets in a flexible grid

[Read More ->](api/layout.md)

### Event System

Handle user input with:

- Keyboard events and customizable keybinds
- Mouse events (clicks, movement, hover)
- Custom event handlers for widgets

## Installation

```bash
pip install termui
```

## Core Concepts

### Asyncronous by Design

TermUI is built around Python's asyncio for handling input, updates, and rendering concurrently without blocking:

```python
# The main app loop runs three concurrent tasks:
# - Input processing
# - Screen updates
# - Rendering
await asyncio.gather(
    self._input_loop(),
    self._update_loop(),
    self._render_loop()
)
```

### DOM-like Structure

Widgets are organized in a tree structure similar to HTML DOM, making it easy to reason about layout and rendering:

```
Screen
└── VerticalLayout
    ├── Container
    │   └── Text
    └── Button
```

### Differential Rendering

Only parts of the screen that have changed are redrawn, ensuring smooth performance even for complex UIs.

## Why TermUI?

### Modern Python Patterns

- Async/await throughout for responsive UIs
- Type hints for better development experience
- Clean, intuitive API design

### Developer Experience

- Hot-reloadable screens and widgets
- Comprehensive error handling and logging
- Extensive customization options

### Terminal-Optimized

- Efficient rendering with minimal flicker
- Full mouse and keyboard support
- Cross-platform compatibility

### Extensible

- Create custom widgets easily
- Plugin-friendly architecture
- Composable design patterns

## Getting Started

Ready to build your first TermUI application? Check out our [Getting Started](getting_started.md) guide to learn the basics, or explore our [Examples](examples/index.md) to see TermUI in action.

For detailed API documentation, visit the [API Reference](api/index.md).
