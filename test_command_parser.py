import unittest

from command_parser import parse_command


class TestCommandParser(unittest.TestCase):
    def test_valid_command_no_args(self):
        cmd_name, args, arg_str = parse_command("/help")
        self.assertEqual(cmd_name, "/help")
        self.assertEqual(args, [])
        self.assertEqual(arg_str, "")

    def test_valid_command_simple_args(self):
        cmd_name, args, arg_str = parse_command("/load sample.csv")
        self.assertEqual(cmd_name, "/load")
        self.assertEqual(args, ["sample.csv"])
        self.assertEqual(arg_str, "sample.csv")

    def test_spaces_and_quotes(self):
        cmd_name, args, arg_str = parse_command('/replace "Old Value" "New Value" "Col Name"')
        self.assertEqual(cmd_name, "/replace")
        self.assertEqual(args, ["Old Value", "New Value", "Col Name"])
        self.assertEqual(arg_str, '"Old Value" "New Value" "Col Name"')

    def test_single_quotes(self):
        cmd_name, args, arg_str = parse_command("/replace 'Old Value' 'New Value' 'Col Name'")
        self.assertEqual(cmd_name, "/replace")
        self.assertEqual(args, ["Old Value", "New Value", "Col Name"])
        self.assertEqual(arg_str, "'Old Value' 'New Value' 'Col Name'")

    def test_missing_slash(self):
        with self.assertRaises(ValueError) as context:
            parse_command("help")
        self.assertIn("must start with '/'", str(context.exception))

    def test_mismatched_quotes(self):
        with self.assertRaises(ValueError) as context:
            parse_command('/replace "unmatched')
        self.assertIn("Command parsing error", str(context.exception))

    def test_query_preserves_spaces(self):
        # /query command should not tokenize arg_str to preserve pandas syntax
        cmd_name, args, arg_str = parse_command("/query Age > 30 and City == 'Toronto'")
        self.assertEqual(cmd_name, "/query")
        self.assertEqual(args, [])
        self.assertEqual(arg_str, "Age > 30 and City == 'Toronto'")

        cmd_name_q, args_q, arg_str_q = parse_command("/q Age > 30")
        self.assertEqual(cmd_name_q, "/q")
        self.assertEqual(args_q, [])
        self.assertEqual(arg_str_q, "Age > 30")
