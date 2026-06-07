# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-07

### Added
- **Onboarding Experience**: Beautiful demo screenshots/assets and comprehensive step-by-step setup guides in `README.md`.
- **UI Refinement**: Design variables (CSS tokens), rounded panel borders, alternating zebra-styled row colors, reactive `EmptyStatePanel`, and threaded `LoadingScreen` overlay.
- **Rich Spreadsheet Features**: Structural shape operations (`/insert-row`, `/insert-col`, `/rename-col`) and regular expression find-and-replace command APIs (`/find`, `/replace`).
- **Data Integrity**: Type-aware input validation, automatic date-format detection/parsing on file load, and configurable NaN placeholder characters (`/set-nan`).
- **Undo/Redo Engine**: Dual-stack differential patch structure for low memory consumption, `/redo` command, `Ctrl+Y` Redo keyboard shortcut, and reactive history status badges.
- **Engineering Tooling**: Specialized `command_parser.py` module, PEP 484 type annotations, git pre-commit hooks (ruff, ruff-format, unit tests), and a multi-python matrix GitHub Actions CI pipeline.
- **Testing Suite**: Command parser tokenization tests, table boundary/edge-case tests (empty files, duplicate headers), and Textual `AppTest` client TUI integration tests.
- **Hygiene & Templates**: `.editorconfig` file, MIT `LICENSE`, `CONTRIBUTING.md`, bug/feature issue templates, and a pull request template.
- **Architecture Docs**: `ARCHITECTURE.md` describing component interactions, sequence diagrams, and technology constraints.
- **Enterprise Exports**: Auto-fitting PDF table widths, custom orientations, paper sizes, filename template substitutions, headers/footers with page number metrics, and Excel/CSV round-trip exporters.
