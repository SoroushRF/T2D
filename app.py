from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, LoadingIndicator, RichLog, Static

from command_parser import parse_command
from document_generator import export_to_docx, export_to_pdf
from spreadsheet_manager import SpreadsheetManager


class EmptyStatePanel(Container):
    def compose(self) -> ComposeResult:
        yield Static("No Spreadsheet Loaded", classes="empty-state-title")
        yield Static("Load a CSV or Excel file to begin editing.", classes="empty-state-desc")
        yield Button("Load Sample Data", id="load-sample-btn", variant="primary")


class SpreadsheetApp(App):
    CSS_PATH = "app.tcss"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+z", "trigger_undo", "Undo", show=True),
        Binding("ctrl+y", "trigger_redo", "Redo", show=True),
        Binding("ctrl+l", "clear_logs", "Clear Logs", show=True),
        Binding("f1", "show_help", "Help", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.manager = SpreadsheetManager()
        self.command_history = []
        self.history_index = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="main-container"):
            with Container(id="table-container"):
                yield DataTable()
                yield EmptyStatePanel(id="empty-state-panel")
            with Container(id="log-container"):
                yield RichLog(highlight=True, markup=True)
            with Container(id="input-container"):
                yield Label(" / ", id="prompt-label")
                yield Input(
                    placeholder="Type a slash command here... (e.g. /load sales.csv, /help)", id="command-input"
                )
            yield Label("[U] Undo (0)  |  [R] Redo (0)", id="history-status")
        yield Container(LoadingIndicator(), id="loading-overlay")
        yield Footer()

    def on_mount(self) -> None:
        # Title of the TUI window
        self.title = "Spreadsheet TUI Editor"
        self.log_widget = self.query_one(RichLog)

        # Focus on command input immediately
        self.input_widget = self.query_one(Input)
        self.input_widget.focus()

        # Display welcome message
        self.log_widget.write("[bold cyan]Welcome to Spreadsheet TUI Editor![/bold cyan]")
        self.log_widget.write("----------------------------------------------")
        self.log_widget.write("A professional Terminal tool to view and manipulate spreadsheets.")
        self.log_widget.write("You can use slash commands [cmd]/<command>[/cmd] in the input box below.")
        self.log_widget.write("Type [cmd]/help[/cmd] or [cmd]/h[/cmd] to list all available commands.")
        self.log_widget.write("Use [cmd]Ctrl+Q[/cmd] to exit.")
        self.log_widget.write("----------------------------------------------\n")

        self.update_table()

    def update_table(self):
        """Updates the DataTable representation of the spreadsheet thread-safely."""
        import threading

        if threading.current_thread() is threading.main_thread():
            self._update_table_internal()
        else:
            self.call_from_thread(self._update_table_internal)

    def _update_table_internal(self):
        table = self.query_one(DataTable)
        empty_panel = self.query_one(EmptyStatePanel)

        self.update_history_status()

        if self.manager.df is None:
            table.display = False
            empty_panel.display = True
            return

        table.display = True
        empty_panel.display = False
        table.clear(columns=True)

        headers = self.manager.get_headers()
        rows = self.manager.get_rows()

        # Add physical row index column first
        table.add_column("Idx", key="row_idx")
        for h in headers:
            table.add_column(h, key=h)

        for idx, row in enumerate(rows):
            table.add_row(str(idx), *row)

    def update_history_status(self):
        try:
            label = self.query_one("#history-status")
            u_size = len(self.manager.undo_stack)
            r_size = len(self.manager.redo_stack)

            u_badge = (
                f"[bold #00e5ff][U] Undo ({u_size})[/bold #00e5ff]" if u_size > 0 else "[#4a5568][U] Undo (0)[/#4a5568]"
            )
            r_badge = (
                f"[bold #00e5ff][R] Redo ({r_size})[/bold #00e5ff]" if r_size > 0 else "[#4a5568][R] Redo (0)[/#4a5568]"
            )

            label.update(f"{u_badge}  |  {r_badge}")
        except Exception:
            pass

    def log_success(self, msg: str):
        import threading

        if threading.current_thread() is threading.main_thread():
            self.log_widget.write(f"[bold green]✔[/bold green] {msg}")
        else:
            self.call_from_thread(self.log_widget.write, f"[bold green]✔[/bold green] {msg}")

    def log_error(self, msg: str):
        import threading

        if threading.current_thread() is threading.main_thread():
            self.log_widget.write(f"[bold red]✘ Error:[/bold red] [red]{msg}[/red]")
        else:
            self.call_from_thread(self.log_widget.write, f"[bold red]✘ Error:[/bold red] [red]{msg}[/red]")

    def log_info(self, msg: str):
        import threading

        if threading.current_thread() is threading.main_thread():
            self.log_widget.write(f"[bold blue]ℹ[/bold blue] {msg}")
        else:
            self.call_from_thread(self.log_widget.write, f"[bold blue]ℹ[/bold blue] {msg}")

    def show_loading(self) -> None:
        import threading

        if threading.current_thread() is threading.main_thread():
            self.query_one("#loading-overlay").display = True
        else:
            self.call_from_thread(self.show_loading)

    def hide_loading(self) -> None:
        import threading

        if threading.current_thread() is threading.main_thread():
            self.query_one("#loading-overlay").display = False
        else:
            self.call_from_thread(self.hide_loading)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "load-sample-btn":
            self.execute_command("/load sample_data.csv")

    def action_trigger_undo(self) -> None:
        self.execute_command("/undo")

    def action_trigger_redo(self) -> None:
        self.execute_command("/redo")

    def action_clear_logs(self) -> None:
        self.log_widget.clear()
        self.log_info("Logs cleared.")

    def action_show_help(self) -> None:
        self.execute_command("/help")

    def on_key(self, event) -> None:
        """Handles key binds specifically for command history navigation."""
        if event.key == "up":
            # Scroll backward in command history
            if self.command_history and self.history_index > 0:
                self.history_index -= 1
                self.input_widget.value = self.command_history[self.history_index]
                self.input_widget.cursor_position = len(self.input_widget.value)
                event.prevent_default()
        elif event.key == "down":
            # Scroll forward in command history
            if self.command_history:
                if self.history_index < len(self.command_history) - 1:
                    self.history_index += 1
                    self.input_widget.value = self.command_history[self.history_index]
                    self.input_widget.cursor_position = len(self.input_widget.value)
                    event.prevent_default()
                elif self.history_index == len(self.command_history) - 1:
                    self.history_index = len(self.command_history)
                    self.input_widget.value = ""
                    event.prevent_default()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "command-input":
            command_text = event.value.strip()
            event.input.value = ""  # Clear the input field
            if command_text:
                # Add to history
                if not self.command_history or self.command_history[-1] != command_text:
                    self.command_history.append(command_text)
                self.history_index = len(self.command_history)

                self.execute_command(command_text)

    @work(thread=True)
    def execute_command(self, raw_command: str):
        """Parses and executes a command string."""
        self.call_from_thread(self.show_loading)
        try:
            # Print command to log
            self.call_from_thread(self.log_widget.write, f"[cmd]> {raw_command}[/cmd]")

            try:
                cmd_name, args, cmd_arg_str = parse_command(raw_command)
            except ValueError as e:
                self.log_error(str(e))
                return

            try:
                # Route commands
                if cmd_name in ["/help", "/h"]:
                    self.call_from_thread(self.show_help_screen)

                elif cmd_name in ["/load"]:
                    if not args:
                        self.log_error("Usage: /load <file_path> [sheet_name]")
                        return
                    filepath = args[0]
                    sheet_name = args[1] if len(args) > 1 else None

                    self.manager.load_file(filepath, sheet_name)
                    self.update_table()
                    self.log_success(f"Successfully loaded '{filepath}'")
                    self.log_info(self.manager.get_summary_text())
                    if self.manager.available_sheets:
                        self.log_info(f"Available Sheets: {', '.join(self.manager.available_sheets)}")

                elif cmd_name in ["/delete-row", "/dr"]:
                    if not args:
                        self.log_error("Usage: /delete-row <row_index_number>")
                        return
                    try:
                        row_idx = int(args[0])
                    except ValueError:
                        self.log_error("Row index must be an integer.")
                        return

                    self.manager.delete_row(row_idx)
                    self.update_table()
                    self.log_success(f"Row {row_idx} deleted.")
                    self.log_info(self.manager.get_summary_text())

                elif cmd_name in ["/insert-row", "/ir"]:
                    if not args:
                        self.log_error("Usage: /insert-row <row_idx> [col1=val1 col2=val2 ...]")
                        return
                    try:
                        row_idx = int(args[0])
                    except ValueError:
                        self.log_error("Row index must be an integer.")
                        return

                    data_dict = {}
                    for arg in args[1:]:
                        if "=" in arg:
                            k, v = arg.split("=", 1)
                            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                                v = v[1:-1]
                            data_dict[k] = v

                    self.manager.insert_row(row_idx, data_dict)
                    self.update_table()
                    self.log_success(f"Row inserted at index {row_idx}.")
                    self.log_info(self.manager.get_summary_text())

                elif cmd_name in ["/insert-col", "/ic"]:
                    if not args:
                        self.log_error("Usage: /insert-col <col_name> [default_value] [position]")
                        return
                    col_name = args[0]
                    default_value = args[1] if len(args) > 1 else "nan"
                    position = None
                    if len(args) > 2:
                        try:
                            position = int(args[2])
                        except ValueError:
                            self.log_error("Position must be an integer.")
                            return

                    self.manager.insert_column(col_name, default_value, position)
                    self.update_table()
                    self.log_success(f"Column '{col_name}' inserted.")
                    self.log_info(self.manager.get_summary_text())

                elif cmd_name in ["/rename-col", "/rc"]:
                    if len(args) < 2:
                        self.log_error("Usage: /rename-col <old_name> <new_name>")
                        return
                    old_name = args[0]
                    new_name = args[1]

                    self.manager.rename_column(old_name, new_name)
                    self.update_table()
                    self.log_success(f"Column '{old_name}' renamed to '{new_name}'.")
                    self.log_info(self.manager.get_summary_text())

                elif cmd_name in ["/delete-col", "/dc"]:
                    if not args:
                        self.log_error("Usage: /delete-col <column_name>")
                        return
                    col_name = args[0]

                    self.manager.delete_col(col_name)
                    self.update_table()
                    self.log_success(f"Column '{col_name}' deleted.")
                    self.log_info(self.manager.get_summary_text())

                elif cmd_name in ["/edit-cell", "/ec"]:
                    if len(args) < 3:
                        self.log_error("Usage: /edit-cell <row_idx> <col_name> <new_value>")
                        return
                    try:
                        row_idx = int(args[0])
                    except ValueError:
                        self.log_error("Row index must be an integer.")
                        return
                    col_name = args[1]
                    new_value = args[2]

                    self.manager.edit_cell(row_idx, col_name, new_value)
                    self.update_table()
                    self.log_success(f"Updated cell ({row_idx}, '{col_name}') to '{new_value}'.")
                    self.log_info(self.manager.get_summary_text())

                elif cmd_name in ["/clear-cell", "/cc"]:
                    if len(args) < 2:
                        self.log_error("Usage: /clear-cell <row_idx> <col_name>")
                        return
                    try:
                        row_idx = int(args[0])
                    except ValueError:
                        self.log_error("Row index must be an integer.")
                        return
                    col_name = args[1]

                    self.manager.clear_cell(row_idx, col_name)
                    self.update_table()
                    self.log_success(f"Cleared cell ({row_idx}, '{col_name}').")
                    self.log_info(self.manager.get_summary_text())

                elif cmd_name in ["/query", "/q"]:
                    if not cmd_arg_str:
                        self.log_error("Usage: /query <pandas_query_string> (e.g. /q Age > 25 and City == 'New York')")
                        return

                    self.manager.query(cmd_arg_str)
                    self.update_table()
                    self.log_success(f"Query applied: {cmd_arg_str}")
                    self.log_info(self.manager.get_summary_text())

                elif cmd_name in ["/sort", "/s"]:
                    if not args:
                        self.log_error("Usage: /sort <column_name> [asc/desc]")
                        return
                    col_name = args[0]
                    ascending = True
                    if len(args) > 1:
                        ascending = args[1].lower() not in ["desc", "false", "0"]

                    self.manager.sort(col_name, ascending)
                    self.update_table()
                    order = "ascending" if ascending else "descending"
                    self.log_success(f"Sorted table by '{col_name}' in {order} order.")
                    self.log_info(self.manager.get_summary_text())

                elif cmd_name in ["/find"]:
                    if not args:
                        self.log_error("Usage: /find <pattern>")
                        return
                    pattern = args[0]
                    matches = self.manager.find_pattern(pattern)
                    for r, col, val in matches:
                        self.log_info(f"Match: Row {r}, Column '{col}': '{val}'")
                    self.log_success(f"Find finished. Found {len(matches)} matches.")

                elif cmd_name in ["/replace"]:
                    if len(args) < 2:
                        self.log_error("Usage: /replace <pattern> <replacement> [col_name]")
                        return
                    pattern = args[0]
                    replacement = args[1]
                    col_name = args[2] if len(args) > 2 else None

                    modified = self.manager.find_and_replace(pattern, replacement, col_name)
                    self.update_table()
                    self.log_success(f"Replace finished. Modified {modified} cell(s).")
                    self.log_info(self.manager.get_summary_text())

                elif cmd_name in ["/set-nan"]:
                    char = args[0] if args else ""
                    self.manager.nan_placeholder = char
                    self.update_table()
                    self.log_success(f"NaN placeholder set to '{char}'.")

                elif cmd_name in ["/undo", "/u"]:
                    self.manager.undo()
                    self.update_table()
                    self.log_success("Undid last operation.")
                    self.log_info(self.manager.get_summary_text())

                elif cmd_name in ["/redo"]:
                    self.manager.redo()
                    self.update_table()
                    self.log_success("Redid last operation.")
                    self.log_info(self.manager.get_summary_text())

                elif cmd_name in ["/reset", "/r"]:
                    self.manager.reset()
                    self.update_table()
                    self.log_success("Table reset to original state.")
                    self.log_info(self.manager.get_summary_text())

                elif cmd_name in ["/export-docx", "/docx"]:
                    if not args:
                        self.log_error("Usage: /export-docx <output_filepath>")
                        return
                    if self.manager.df is None:
                        self.log_error("Cannot export. No spreadsheet loaded.")
                        return
                    output_path = args[0]
                    export_to_docx(self.manager.df, output_path)
                    self.log_success(f"Exported to DOCX table successfully at: {output_path}")

                elif cmd_name in ["/export-pdf", "/pdf"]:
                    if not args:
                        self.log_error("Usage: /export-pdf <output_filepath>")
                        return
                    if self.manager.df is None:
                        self.log_error("Cannot export. No spreadsheet loaded.")
                        return
                    output_path = args[0]
                    export_to_pdf(self.manager.df, output_path)
                    self.log_success(f"Exported to PDF successfully at: {output_path}")

                elif cmd_name in ["/exit", "/quit"]:
                    self.log_info("Exiting application...")
                    self.exit()

                else:
                    self.log_error(f"Unknown command: '{cmd_name}'. Type /help for a list of valid commands.")

            except Exception as e:
                self.log_error(str(e))
        finally:
            self.call_from_thread(self.hide_loading)

    def show_help_screen(self):
        """Outputs the command manual to the console log."""
        self.log_widget.write("\n[bold cyan]SPREADSHEET TUI EDITOR MANUAL[/bold cyan]")
        self.log_widget.write("==============================================")
        self.log_widget.write("[bold green]/load <filepath> [sheet][/bold green]")
        self.log_widget.write("  Loads a spreadsheet (.csv, .xlsx, .xls) to the interface.")
        self.log_widget.write("  If an Excel sheet is specified, loads that sheet, otherwise the first.")

        self.log_widget.write(
            "[bold green]/insert-row <idx> [col1=val1 col2=val2 ...][/bold green] (or [bold green]/ir[/bold green])"
        )
        self.log_widget.write(
            "  Inserts a new row at the given positional index. Specify values using key=value pairs."
        )

        self.log_widget.write(
            "[bold green]/insert-col <col_name> [default_val] [pos][/bold green] (or [bold green]/ic[/bold green])"
        )
        self.log_widget.write("  Inserts a new column at the specified position (default: end) with a default value.")

        self.log_widget.write(
            "[bold green]/rename-col <old_name> <new_name>[/bold green] (or [bold green]/rc[/bold green])"
        )
        self.log_widget.write("  Renames an existing column to new_name.")

        self.log_widget.write("[bold green]/delete-row <index>[/bold green] (or [bold green]/dr[/bold green])")
        self.log_widget.write("  Deletes the row at the given positional index (shown in 'Idx' column).")

        self.log_widget.write("[bold green]/delete-col <col_name>[/bold green] (or [bold green]/dc[/bold green])")
        self.log_widget.write("  Deletes the column by name.")

        self.log_widget.write(
            "[bold green]/edit-cell <index> <col_name> <value>[/bold green] (or [bold green]/ec[/bold green])"
        )
        self.log_widget.write(
            "  Edits cell value at row <index> and column <col_name>. "
            "Wrap names/values in quotes if they contain spaces."
        )

        self.log_widget.write(
            "[bold green]/clear-cell <index> <col_name>[/bold green] (or [bold green]/cc[/bold green])"
        )
        self.log_widget.write("  Clears the cell at row <index> and column <col_name> (sets to NaN).")

        self.log_widget.write("[bold green]/query <expression>[/bold green] (or [bold green]/q[/bold green])")
        self.log_widget.write("  Filters the table using a pandas query string.")
        self.log_widget.write("  Examples: /q Age > 30 and Salary < 80000 | /q City == 'Toronto'")

        self.log_widget.write("[bold green]/sort <col_name> [asc/desc][/bold green] (or [bold green]/s[/bold green])")
        self.log_widget.write("  Sorts spreadsheet by column. Default order is ascending. Add 'desc' for descending.")

        self.log_widget.write("[bold green]/find <pattern>[/bold green]")
        self.log_widget.write("  Locates and lists regex matches in the spreadsheet.")

        self.log_widget.write("[bold green]/replace <pattern> <replacement> [col][/bold green]")
        self.log_widget.write("  Executes a regex find-and-replace on a column (or all columns).")

        self.log_widget.write("[bold green]/set-nan [char][/bold green]")
        self.log_widget.write("  Sets custom character display for empty/null values.")

        self.log_widget.write(
            "[bold green]/undo[/bold green] (or [bold green]/u[/bold green] or [bold green]Ctrl+Z[/bold green])"
        )
        self.log_widget.write("  Undoes the last layout/data modification.")

        self.log_widget.write("[bold green]/reset[/bold green] (or [bold green]/r[/bold green])")
        self.log_widget.write("  Resets spreadsheet to the originally loaded state.")

        self.log_widget.write("[bold green]/export-docx <output_path>[/bold green] (or [bold green]/docx[/bold green])")
        self.log_widget.write("  Exports the current view to a styled Word (.docx) file containing the table.")

        self.log_widget.write("[bold green]/export-pdf <output_path>[/bold green] (or [bold green]/pdf[/bold green])")
        self.log_widget.write("  Exports the current view to a styled PDF file.")

        self.log_widget.write(
            "[bold green]/help[/bold green] (or [bold green]/h[/bold green] or [bold green]F1[/bold green])"
        )
        self.log_widget.write("  Prints this manual.")

        self.log_widget.write(
            "[bold green]/exit[/bold green] (or [bold green]/quit[/bold green] or [bold green]Ctrl+Q[/bold green])"
        )
        self.log_widget.write("  Exits the Spreadsheet Editor.")
        self.log_widget.write("==============================================\n")


if __name__ == "__main__":
    app = SpreadsheetApp()
    app.run()
