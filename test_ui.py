import os
import unittest
import pandas as pd
from app import SpreadsheetApp, EmptyStatePanel
from textual.widgets import DataTable

class TestSpreadsheetAppTUI(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Create a small temp CSV for testing
        self.test_filename = "temp_ui_test_data.csv"
        self.data = {
            "Name": ["Alice", "Bob"],
            "Age": [25, 30]
        }
        pd.DataFrame(self.data).to_csv(self.test_filename, index=False)

    async def asyncTearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)
        # Clean up any loaded df in the app manager to release locks
        
    async def test_empty_state_active_by_default(self):
        app = SpreadsheetApp()
        async with app.run_test() as pilot:
            empty_panel = app.query_one(EmptyStatePanel)
            datatable = app.query_one(DataTable)
            self.assertTrue(empty_panel.display)
            self.assertFalse(datatable.display)

    async def test_load_command_toggles_empty_state(self):
        app = SpreadsheetApp()
        async with app.run_test() as pilot:
            # Trigger load command
            app.execute_command(f"/load {self.test_filename}")
            # Wait for background thread worker to finish execution and dispatch to main loop
            await pilot.pause(0.2)
            
            empty_panel = app.query_one(EmptyStatePanel)
            datatable = app.query_one(DataTable)
            
            # Now EmptyStatePanel should be hidden and DataTable should be displayed
            self.assertFalse(empty_panel.display)
            self.assertTrue(datatable.display)
            
            # Verify DataTable has elements
            self.assertGreater(datatable.row_count, 0)
