# Contributing to T2D (Spreadsheet TUI Editor)

Thank you for your interest in contributing to T2D! To maintain high code quality and consistency, please follow these guidelines.

## Onboarding & Getting Started

1. Clone the repository.
2. Initialize virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate

   pip install -r requirements.txt
   ```
3. Set up pre-commit hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Development Workflow

### Branch Naming Conventions
- `feat/feature-name` for new features
- `fix/bug-name` for bug fixes
- `docs/documentation-update` for documentation changes
- `chore/chore-name` for setup or dependencies

### Coding Standards
- Follow standard Python styling (Black configuration with 120-character line limit).
- All files must pass linting and styling checks via Ruff.
- Use explicit type annotations (PEP 484) on all functions.

### Testing Rules
- Every pull request must include corresponding unit and/or integration tests.
- Run tests locally before making a pull request:
  ```bash
  python -m unittest test_spreadsheet_editor.py test_ui.py test_command_parser.py
  ```
- All unit and integration tests must pass. Do not commit failing code.
