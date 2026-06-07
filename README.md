# Spreadsheet TUI Editor (T2D)

[![CI Build](https://github.com/SoroushRF/T2D/actions/workflows/ci.yml/badge.svg)](https://github.com/SoroushRF/T2D/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests Status](https://img.shields.io/badge/tests-passing-green.svg)](test_spreadsheet_editor.py)

A beautiful, interactive Terminal User Interface (TUI) application designed to load, inspect, modify, filter, and export spreadsheets to enterprise-styled Word Documents (.docx) and PDFs.

![Spreadsheet TUI Editor Demo](docs/assets/tui_editor_demo.png)

## What is this? (30-Second Elevator Pitch)
Spreadsheet TUI Editor brings spreadsheet processing out of heavy GUI editors directly into your terminal. Designed for power users, developers, and DevOps engineers, it combines the speed and responsiveness of a console application with the styling flexibility of Textual CSS and the analytical power of pandas. Quickly load large CSV/Excel files, perform shape operations, filter rows using pandas queries, edit cells interactively, and export publication-ready reports (PDF & Word) with a single command.

---

## Quick Start

Follow these simple steps to set up the project and run it on your machine.

### 1. Clone & Navigate
```bash
git clone https://github.com/SoroushRF/T2D.git
cd T2D
```

### 2. Set Up Virtual Environment & Install Dependencies

Select the appropriate tab/commands for your operating system:

#### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### Windows (Command Prompt)
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

#### macOS / Linux (Bash/Zsh)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Launch the App
```bash
python app.py
```

---

## Sample Walkthrough

Want to see the TUI in action right away? Follow this quick guided tour using the included sample data:

1. **Start the editor**:
   ```bash
   python app.py
   ```
2. **Load sample data**: Type the following command in the input box at the bottom and press Enter:
   ```text
   /load sample_data.csv
   ```
   *Expected Log:* `✔ Successfully loaded 'sample_data.csv'` and the table displays headers and rows.
3. **Filter the data**: Suppose you want to see only rows where age is greater than 28:
   ```text
   /query Age > 28
   ```
   *Expected Log:* `✔ Query applied: Age > 28` and the table updates to show only matching records.
4. **Modify a value**: Let's edit the salary for the first row under the filtered results:
   ```text
   /edit-cell 0 Salary 75000
   ```
   *Expected Log:* `✔ Updated cell (0, 'Salary') to '75000'.`
5. **Export the results**: Save your changes to a styled PDF:
   ```text
   /export-pdf filtered_report.pdf
   ```
   *Expected Log:* `✔ Exported to PDF successfully at: filtered_report.pdf`
6. **Exit**:
   ```text
   /exit
   ```

You will find a beautifully formatted PDF report named `filtered_report.pdf` in your project folder!

---

## Slash Commands Reference

Type any of the following commands in the input field:

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
