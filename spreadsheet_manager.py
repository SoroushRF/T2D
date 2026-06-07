import os
import pandas as pd
import numpy as np

class SpreadsheetManager:
    def __init__(self):
        self.filepath = None
        self.df = None
        self.original_df = None
        self.history = []  # Stack of (df_copy) for undo operations
        self.sheet_name = None
        self.available_sheets = []

    def load_file(self, filepath, sheet_name=None):
        """Loads a CSV or Excel file into a pandas DataFrame."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        ext = os.path.splitext(filepath)[1].lower()
        self.filepath = filepath
        self.sheet_name = sheet_name

        if ext == '.csv':
            self.df = pd.read_csv(filepath)
            self.available_sheets = []
        elif ext in ['.xlsx', '.xls']:
            excel_file = pd.ExcelFile(filepath)
            self.available_sheets = excel_file.sheet_names
            if not sheet_name:
                self.sheet_name = self.available_sheets[0]
            elif sheet_name not in self.available_sheets:
                raise ValueError(f"Sheet '{sheet_name}' not found. Available sheets: {', '.join(self.available_sheets)}")
            
            self.df = pd.read_excel(filepath, sheet_name=self.sheet_name)
        else:
            raise ValueError("Unsupported file format. Please load a CSV or Excel file (.csv, .xlsx, .xls).")

        # Clean column names to make querying easier (remove spaces and special characters for ease of use, but keep originals)
        # Actually, let's keep original columns, but handle string stripping
        self.df.columns = [str(col).strip() for col in self.df.columns]
        
        # Save original copy for resets
        self.original_df = self.df.copy()
        self.history = []

    def _save_to_history(self):
        """Pushes a copy of the current dataframe to history stack."""
        if self.df is not None:
            self.history.append(self.df.copy())
            # Limit history size to 50 items to prevent memory issues
            if len(self.history) > 50:
                self.history.pop(0)

    def undo(self):
        """Restores the last state from history."""
        if not self.history:
            raise ValueError("Nothing to undo.")
        self.df = self.history.pop()

    def reset(self):
        """Resets the dataframe to its original loaded state."""
        if self.original_df is None:
            raise ValueError("No file loaded.")
        self._save_to_history()
        self.df = self.original_df.copy()

    def insert_row(self, row_idx, data_dict=None):
        """Inserts a row at the given 0-based positional index."""
        if self.df is None:
            raise ValueError("No file loaded.")
        if row_idx < 0 or row_idx > len(self.df):
            raise IndexError(f"Row index {row_idx} is out of bounds (0 to {len(self.df)}).")
        
        self._save_to_history()
        new_row_data = {col: np.nan for col in self.df.columns}
        if data_dict:
            for k, v in data_dict.items():
                if k in new_row_data:
                    new_row_data[k] = v
        new_row_df = pd.DataFrame([new_row_data])
        
        df_top = self.df.iloc[:row_idx]
        df_bottom = self.df.iloc[row_idx:]
        self.df = pd.concat([df_top, new_row_df, df_bottom]).reset_index(drop=True)

    def insert_column(self, col_name, default_value=np.nan, position=None):
        """Inserts a new column at the specified position."""
        if self.df is None:
            raise ValueError("No file loaded.")
        if col_name in self.df.columns:
            raise ValueError(f"Column '{col_name}' already exists.")
        
        self._save_to_history()
        if position is None:
            position = len(self.df.columns)
        elif position < 0 or position > len(self.df.columns):
            raise IndexError(f"Position {position} is out of bounds (0 to {len(self.df.columns)}).")
            
        self.df.insert(loc=position, column=col_name, value=default_value)

    def rename_column(self, old_name, new_name):
        """Renames a column, checking for name clashes."""
        if self.df is None:
            raise ValueError("No file loaded.")
        if old_name not in self.df.columns:
            matching_cols = [col for col in self.df.columns if col.lower() == old_name.lower()]
            if len(matching_cols) == 1:
                old_name = matching_cols[0]
            else:
                raise ValueError(f"Column '{old_name}' not found.")
        
        if new_name in self.df.columns:
            raise ValueError(f"Column '{new_name}' already exists.")
            
        self._save_to_history()
        self.df = self.df.rename(columns={old_name: new_name})

    def delete_row(self, row_idx):
        """Deletes a row by its positional 0-based index."""
        if self.df is None:
            raise ValueError("No file loaded.")
        if row_idx < 0 or row_idx >= len(self.df):
            raise IndexError(f"Row index {row_idx} is out of bounds (0 to {len(self.df) - 1}).")

        self._save_to_history()
        # Drop by positional index
        self.df = self.df.drop(self.df.index[row_idx]).reset_index(drop=True)

    def delete_col(self, col_name):
        """Deletes a column by name."""
        if self.df is None:
            raise ValueError("No file loaded.")
        
        # Check exact match
        if col_name not in self.df.columns:
            # Check case-insensitive match
            matching_cols = [col for col in self.df.columns if col.lower() == col_name.lower()]
            if len(matching_cols) == 1:
                col_name = matching_cols[0]
            else:
                raise ValueError(f"Column '{col_name}' not found. Available columns: {', '.join(self.df.columns)}")

        self._save_to_history()
        self.df = self.df.drop(columns=[col_name])

    def edit_cell(self, row_idx, col_name, new_value):
        """Edits a specific cell value at 0-based row index and column name."""
        if self.df is None:
            raise ValueError("No file loaded.")
        if row_idx < 0 or row_idx >= len(self.df):
            raise IndexError(f"Row index {row_idx} is out of bounds (0 to {len(self.df) - 1}).")
        
        if col_name not in self.df.columns:
            matching_cols = [col for col in self.df.columns if col.lower() == col_name.lower()]
            if len(matching_cols) == 1:
                col_name = matching_cols[0]
            else:
                raise ValueError(f"Column '{col_name}' not found. Available columns: {', '.join(self.df.columns)}")

        self._save_to_history()
        
        # Type conversion attempt
        col_idx = self.df.columns.get_loc(col_name)
        dtype = self.df.dtypes.iloc[col_idx]
        
        converted_value = new_value
        if new_value == "" or new_value.lower() == "nan" or new_value.lower() == "none":
            converted_value = np.nan
        else:
            try:
                if pd.api.types.is_integer_dtype(dtype):
                    converted_value = int(new_value)
                elif pd.api.types.is_float_dtype(dtype):
                    converted_value = float(new_value)
                elif pd.api.types.is_bool_dtype(dtype):
                    converted_value = new_value.lower() in ('true', '1', 'yes', 'y', 't')
            except ValueError:
                # Keep it as string if conversion fails
                pass

        self.df.iloc[row_idx, col_idx] = converted_value

    def clear_cell(self, row_idx, col_name):
        """Clears (sets to NaN) a specific cell value."""
        self.edit_cell(row_idx, col_name, "nan")

    def find_pattern(self, pattern):
        """Finds regex matches in the spreadsheet and returns list of (row_idx, col_name, val)."""
        import re
        if self.df is None:
            raise ValueError("No file loaded.")
        
        try:
            regex = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
            
        matches = []
        for col in self.df.columns:
            col_idx = self.df.columns.get_loc(col)
            for row_idx in range(len(self.df)):
                val = self.df.iloc[row_idx, col_idx]
                val_str = "" if pd.isna(val) else str(val)
                if regex.search(val_str):
                    matches.append((row_idx, col, val_str))
        return matches

    def find_and_replace(self, pattern, replacement, col_name=None):
        """Regex find and replace on the specified column or all columns."""
        import re
        if self.df is None:
            raise ValueError("No file loaded.")
        
        cols_to_process = []
        if col_name:
            if col_name not in self.df.columns:
                matching_cols = [col for col in self.df.columns if col.lower() == col_name.lower()]
                if len(matching_cols) == 1:
                    col_name = matching_cols[0]
                else:
                    raise ValueError(f"Column '{col_name}' not found.")
            cols_to_process = [col_name]
        else:
            cols_to_process = list(self.df.columns)
            
        self._save_to_history()
        
        try:
            regex = re.compile(pattern)
        except re.error as e:
            self.history.pop()
            raise ValueError(f"Invalid regex pattern: {e}")
            
        cells_modified = 0
        for col in cols_to_process:
            col_idx = self.df.columns.get_loc(col)
            dtype = self.df.dtypes.iloc[col_idx]
            
            for row_idx in range(len(self.df)):
                val = self.df.iloc[row_idx, col_idx]
                val_str = "" if pd.isna(val) else str(val)
                
                if regex.search(val_str):
                    new_val_str = regex.sub(replacement, val_str)
                    if new_val_str != val_str:
                        converted_value = new_val_str
                        if new_val_str == "" or new_val_str.lower() == "nan" or new_val_str.lower() == "none":
                            converted_value = np.nan
                        else:
                            try:
                                if pd.api.types.is_integer_dtype(dtype):
                                    converted_value = int(new_val_str)
                                elif pd.api.types.is_float_dtype(dtype):
                                    converted_value = float(new_val_str)
                                elif pd.api.types.is_bool_dtype(dtype):
                                    converted_value = new_val_str.lower() in ('true', '1', 'yes', 'y', 't')
                            except ValueError:
                                pass
                        
                        self.df.iloc[row_idx, col_idx] = converted_value
                        cells_modified += 1
                        
        return cells_modified

    def query(self, query_str):
        """Filters the dataframe using a pandas query string."""
        if self.df is None:
            raise ValueError("No file loaded.")
        
        self._save_to_history()
        try:
            # We filter and keep the matching rows, reset index to maintain positional logic
            filtered_df = self.df.query(query_str)
            self.df = filtered_df.reset_index(drop=True)
        except Exception as e:
            # Revert history since the query failed and didn't apply
            self.history.pop()
            raise ValueError(f"Invalid query: {e}")

    def sort(self, col_name, ascending=True):
        """Sorts the dataframe by a column."""
        if self.df is None:
            raise ValueError("No file loaded.")
        
        if col_name not in self.df.columns:
            matching_cols = [col for col in self.df.columns if col.lower() == col_name.lower()]
            if len(matching_cols) == 1:
                col_name = matching_cols[0]
            else:
                raise ValueError(f"Column '{col_name}' not found. Available columns: {', '.join(self.df.columns)}")

        self._save_to_history()
        self.df = self.df.sort_values(by=col_name, ascending=ascending).reset_index(drop=True)

    def get_headers(self):
        """Returns list of column names."""
        if self.df is None:
            return []
        return list(self.df.columns)

    def get_rows(self):
        """Returns rows as a list of lists/tuples, handling NaN formatting."""
        if self.df is None:
            return []
        
        rows = []
        for i, row in self.df.iterrows():
            formatted_row = []
            for val in row:
                if pd.isna(val):
                    formatted_row.append("")
                else:
                    # Format floats nicely
                    if isinstance(val, float):
                        if val.is_integer():
                            formatted_row.append(str(int(val)))
                        else:
                            formatted_row.append(f"{val:.4g}")
                    else:
                        formatted_row.append(str(val))
            rows.append(formatted_row)
        return rows

    def get_summary_text(self):
        """Returns brief text summarizing the current sheet status."""
        if self.df is None:
            return "No spreadsheet loaded."
        
        num_rows, num_cols = self.df.shape
        undo_avail = len(self.history)
        msg = f"File: {os.path.basename(self.filepath)}"
        if self.sheet_name:
            msg += f" | Sheet: {self.sheet_name}"
        msg += f" | Shape: {num_rows} rows x {num_cols} columns | Undo stack: {undo_avail}"
        return msg
