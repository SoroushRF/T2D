import os
import unittest
import pandas as pd
import numpy as np

from spreadsheet_manager import SpreadsheetManager
from document_generator import export_to_docx, export_to_pdf

class TestSpreadsheetManager(unittest.TestCase):
    def setUp(self):
        # Create a small temp CSV for testing
        self.test_filename = "temp_test_data.csv"
        self.data = {
            "Name": ["Alice", "Bob", "Charlie"],
            "Age": [25, 30, 35],
            "Salary": [50000.0, 60000.0, 70000.0],
            "Active": [True, False, True]
        }
        pd.DataFrame(self.data).to_csv(self.test_filename, index=False)
        self.manager = SpreadsheetManager()
        self.manager.load_file(self.test_filename)

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)
        # Clean up exported test files if any
        for f in ["test_out.docx", "test_out.pdf"]:
            if os.path.exists(f):
                os.remove(f)

    def test_load_file(self):
        self.assertEqual(len(self.manager.df), 3)
        self.assertListEqual(self.manager.get_headers(), ["Name", "Age", "Salary", "Active"])

    def test_delete_row(self):
        # Delete row 1 (Bob)
        self.manager.delete_row(1)
        self.assertEqual(len(self.manager.df), 2)
        # Position 1 should now be Charlie
        self.assertEqual(self.manager.df.iloc[1]["Name"], "Charlie")
        
        # Test index out of bounds
        with self.assertRaises(IndexError):
            self.manager.delete_row(5)

    def test_delete_col(self):
        # Delete "Salary" column
        self.manager.delete_col("Salary")
        self.assertNotIn("Salary", self.manager.df.columns)
        self.assertEqual(len(self.manager.get_headers()), 3)

        # Test delete non-existent column
        with self.assertRaises(ValueError):
            self.manager.delete_col("NonExistent")

    def test_edit_cell(self):
        # Edit Alice's age to 26 (integer column)
        self.manager.edit_cell(0, "Age", "26")
        self.assertEqual(self.manager.df.iloc[0]["Age"], 26)

        # Edit Bob's salary to 65000.5 (float column)
        self.manager.edit_cell(1, "Salary", "65000.5")
        self.assertEqual(self.manager.df.iloc[1]["Salary"], 65000.5)

        # Test case insensitivity in column name
        self.manager.edit_cell(0, "name", "Alicia")
        self.assertEqual(self.manager.df.iloc[0]["Name"], "Alicia")

    def test_clear_cell(self):
        # Clear Charlie's salary
        self.manager.clear_cell(2, "Salary")
        self.assertTrue(pd.isna(self.manager.df.iloc[2]["Salary"]))

    def test_query(self):
        # Filter where Age > 28
        self.manager.query("Age > 28")
        self.assertEqual(len(self.manager.df), 2)  # Bob (30), Charlie (35)
        self.assertEqual(self.manager.df.iloc[0]["Name"], "Bob")

        # Test invalid query string
        with self.assertRaises(ValueError):
            self.manager.query("Invalid Expression Syntax")

    def test_undo(self):
        # Modify and then undo
        original_age = self.manager.df.iloc[0]["Age"]
        self.manager.edit_cell(0, "Age", "99")
        self.assertEqual(self.manager.df.iloc[0]["Age"], 99)

        self.manager.undo()
        self.assertEqual(self.manager.df.iloc[0]["Age"], original_age)

        # Test empty undo stack
        with self.assertRaises(ValueError):
            self.manager.undo()

    def test_reset(self):
        self.manager.delete_row(0)
        self.manager.delete_col("Salary")
        self.assertEqual(len(self.manager.df), 2)
        
        self.manager.reset()
        self.assertEqual(len(self.manager.df), 3)
        self.assertIn("Salary", self.manager.df.columns)

    def test_insert_row(self):
        # Insert a row at index 1
        self.manager.insert_row(1, {"Name": "David", "Age": 28, "Salary": 55000.0, "Active": True})
        self.assertEqual(len(self.manager.df), 4)
        self.assertEqual(self.manager.df.iloc[1]["Name"], "David")
        self.assertEqual(self.manager.df.iloc[2]["Name"], "Bob")

    def test_insert_column(self):
        # Insert a column at index 1
        self.manager.insert_column("Role", "Engineer", 1)
        self.assertIn("Role", self.manager.df.columns)
        self.assertEqual(self.manager.df.iloc[0]["Role"], "Engineer")
        self.assertEqual(self.manager.get_headers()[1], "Role")

    def test_rename_column(self):
        # Rename "Salary" to "Wage"
        self.manager.rename_column("Salary", "Wage")
        self.assertNotIn("Salary", self.manager.df.columns)
        self.assertIn("Wage", self.manager.df.columns)

    def test_find_pattern(self):
        # Find matches for "Alice"
        matches = self.manager.find_pattern("Alice")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0][0], 0)
        self.assertEqual(matches[0][1], "Name")

        # Find matches for numeric pattern
        matches = self.manager.find_pattern(r"^3\d$") # Matches 30 or 35
        self.assertEqual(len(matches), 2)

    def test_find_and_replace(self):
        # Replace "Alice" with "Alicia"
        modified = self.manager.find_and_replace("Alice", "Alicia")
        self.assertEqual(modified, 1)
        self.assertEqual(self.manager.df.iloc[0]["Name"], "Alicia")

        # Regex replace ending 'e' with 'a' in Name column
        modified = self.manager.find_and_replace("e$", "a", "Name")
        # Charlie ends with 'e', should become Charlia
        self.assertEqual(self.manager.df.iloc[2]["Name"], "Charlia")

    def test_type_aware_validation(self):
        # Age column is integer
        with self.assertRaises(ValueError):
            self.manager.edit_cell(0, "Age", "not_an_int")

        # Salary column is float
        with self.assertRaises(ValueError):
            self.manager.edit_cell(0, "Salary", "not_a_float")

        # Active column is boolean
        with self.assertRaises(ValueError):
            self.manager.edit_cell(0, "Active", "not_a_bool")

    def test_auto_date_detection_and_formatting(self):
        # Create a temp file with date strings
        temp_date_file = "temp_date_test.csv"
        date_data = {
            "Event": ["Start", "End"],
            "Date": ["2026-06-07", "2026-06-08 12:30:00"]
        }
        pd.DataFrame(date_data).to_csv(temp_date_file, index=False)
        
        try:
            m = SpreadsheetManager()
            m.load_file(temp_date_file)
            
            # Verify it is parsed as datetime
            self.assertTrue(pd.api.types.is_datetime64_any_dtype(m.df["Date"].dtype))
            
            # Verify rows are formatted consistently
            rows = m.get_rows()
            self.assertEqual(rows[0][1], "2026-06-07")
            self.assertEqual(rows[1][1], "2026-06-08 12:30:00")
        finally:
            if os.path.exists(temp_date_file):
                os.remove(temp_date_file)

    def test_nan_placeholder(self):
        # Clear a cell
        self.manager.clear_cell(0, "Salary")
        # Default placeholder is ""
        self.assertEqual(self.manager.get_rows()[0][2], "")
        
        # Set custom placeholder
        self.manager.nan_placeholder = "N/A"
        self.assertEqual(self.manager.get_rows()[0][2], "N/A")

    def test_export_docx(self):
        export_to_docx(self.manager.df, "test_out.docx")
        self.assertTrue(os.path.exists("test_out.docx"))

    def test_export_pdf(self):
        export_to_pdf(self.manager.df, "test_out.pdf")
        self.assertTrue(os.path.exists("test_out.pdf"))


if __name__ == "__main__":
    unittest.main()
