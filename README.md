# Spreadsheet TUI Editor

A beautiful, interactive Terminal User Interface (TUI) application to load, modify, filter, and export spreadsheets to styled Word Documents (.docx) and PDFs.

Built using **Python 3**, **Textual** (for modern, rich terminal layout & CSS styling), **pandas** (for data processing), **python-docx**, and **fpdf2** (for document export generation).

## Features

- **Beautiful Dark Theme Terminal UI** with fully responsive spreadsheet grid, scrolling command history log, and slash-command input.
- **Support for Excel (.xlsx, .xls) and CSV (.csv)** formats.
- **Positional editing & column manipulations**: delete rows, delete columns, clear cells, and update cell values directly.
- **Pandas query engine integration**: run search queries and filters on your spreadsheet instantly (e.g. `/q Age > 21 and City == 'New York'`).
- **State undo support**: simple `/undo` (or `Ctrl+Z`) to reverse mistakes.
- **Zebra-striped styled export tables** to:
  - **Word DOCX** (`/export-docx output.docx`) - styled margins, bold header color, automatic cell alignments.
  - **PDF** (`/export-pdf output.pdf`) - landscape orientation fallback for wide tables, grid borders, styled backgrounds.

## Installation

Ensure you have Python 3.14+ (or any 3.9+ version) and `pip` installed.

1. Navigate to the project folder.
2. Initialize virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - **Windows PowerShell**:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - **Windows Command Prompt**:
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - **macOS / Linux**:
     ```bash
     source .venv/bin/activate
     ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To run the application:
```bash
python app.py
```

## Slash Commands reference

Once in the app, type any of these commands in the input field at the bottom:

| Command | Description | Example |
|---|---|---|
| `/load <filepath> [sheet]` | Load a CSV or Excel file (optionally a sheet) | `/load sales.csv` or `/load data.xlsx sheet1` |
| `/delete-row <idx>` | Delete row at index `idx` (seen in `Idx` column) | `/delete-row 4` or `/dr 4` |
| `/delete-col <col>` | Delete column named `<col>` | `/delete-col Name` or `/dc Age` |
| `/edit-cell <idx> <col> <val>` | Change value at row index and column name | `/edit-cell 2 Salary 65000` or `/ec 0 Name "Bob"` |
| `/clear-cell <idx> <col>` | Clear value in cell to NaN / empty | `/clear-cell 1 Age` or `/cc 1 Email` |
| `/query <expression>` | Filter the table using a pandas query expression | `/query Age > 30` or `/q City == 'Toronto'` |
| `/sort <col> [asc/desc]` | Sort table by a specific column | `/sort Age desc` or `/s Name` |
| `/undo` | Undo the last modification operation | `/undo` or `/u` (Shortcut: `Ctrl+Z`) |
| `/reset` | Revert to the original spreadsheet load state | `/reset` or `/r` |
| `/export-docx <path>` | Export current view to a styled Word Document table | `/export-docx export.docx` or `/docx out.docx` |
| `/export-pdf <path>` | Export current view to a styled PDF table | `/export-pdf report.pdf` or `/pdf out.pdf` |
| `/help` | Print help manual | `/help` or `/h` (Shortcut: `F1`) |
| `/exit` | Exit the application | `/exit` or `/quit` (Shortcut: `Ctrl+Q`) |

*Note: Use double quotes around names/values if they contain spaces. E.g., `/edit-cell 0 City "San Francisco"`.*
