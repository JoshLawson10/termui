# Contributing to TermUI

🎉 Thanks for your interest in contributing to TermUI!  
Contributions of all kinds are welcome — from bug reports and documentation improvements to new widgets and features.

---

## 🛠️ Getting Started

1. **Fork the repository** and clone your fork:

   ```bash
   git clone https://github.com/<your-username>/termui.git
   cd termui

   ```

2. **Set up a development environment with Poetry**:

   ```bash
   poetry install
   ```

   This installs TermUI along with all dev dependencies (linters, formatters, testing tools).

3. **Activate the virtual environment**:

   ```bash
   poetry shell
   ```

4. **Run the test suite** to make sure everything is working:

   ```bash
   poetry run pytest
   ```

5. **Try out the examples**:

   ```bash
   poetry run python examples/button_demo.py
   ```

---

## 📐 Code Style

TermUI follows these conventions:

- **Python version:** 3.9+
- **Linting:** [ruff](https://github.com/astral-sh/ruff)
- **Formatting:** [black](https://black.readthedocs.io/en/stable/)
- **Typing:** [mypy](https://mypy.readthedocs.io/en/stable/)

Before committing, run:

```bash
poetry run ruff check .
poetry run black .
poetry run mypy termui
poetry run pytest
```

---

## 📝 Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary) specification.
This makes the commit history readable and helps with automated changelogs.

Format:

```
<type>[optional scope]: <description>
```

Examples:

- `feat: add ProgressBar widget`
- `fix(input): correct cursor position on delete`
- `docs: update theming guide`
- `refactor: simplify diffing algorithm`

Common commit types:

- `feat` – a new feature
- `fix` – a bug fix
- `docs` – documentation only changes
- `style` – formatting, no logic changes
- `refactor` – code change that neither fixes a bug nor adds a feature
- `test` – adding or fixing tests
- `chore` – build tasks, tooling, dependencies

---

## 🧩 Adding New Widgets

1. Place your widget in `termui/widgets/`.
2. Follow the existing API pattern:

   - Use **dataclass-style attributes** for props (`padding`, `align`, `variant`).
   - Support **variants** (`primary`, `secondary`, `error`, etc.) mapped to the theme.
   - Add **event hooks** (`on_click`, `on_change`, etc.) where applicable.

3. Write tests in `tests/widgets/`.
4. Add an example under `examples/`.

---

## 🧪 Testing

We use [pytest](https://docs.pytest.org/):

```bash
poetry run pytest -v
```

When adding features, please include tests that cover:

- Basic rendering
- Variant + theming behavior
- Input handling (keyboard/mouse)

---

## 📝 Submitting Pull Requests

1. Create a feature branch:

   ```bash
   git checkout -b feat/my-new-widget
   ```

2. Commit your changes with a **Conventional Commit** message:

   ```bash
   git commit -m "feat: add RadioBox widget"
   ```

3. Push to your fork:

   ```bash
   git push origin feat/my-new-widget
   ```

4. Open a Pull Request on GitHub:

   - Describe **what the change does**.
   - Link to any relevant issues.
   - Add screenshots/gifs of widgets in action if possible.

---

## 🐛 Reporting Issues

If you find a bug, please open an [issue](https://github.com/JoshLawson10/termui/issues) and include:

- What you expected to happen
- What actually happened
- Steps to reproduce
- Your OS, Python version, and terminal emulator

---

## ❤️ Community

- Be kind and respectful.
- Small contributions matter — even fixing a typo helps!
- If you're unsure about something, open a [discussion](https://github.com/JoshLawson10/termui/discussions).

---

Thanks again for helping make TermUI better 🚀
