import shlex
from typing import Tuple, List

def parse_command(raw_command: str) -> Tuple[str, List[str], str]:
    """Parses a raw command string.
    
    Args:
        raw_command: The raw input string from the command line.
        
    Returns:
        A tuple of (cmd_name, args, cmd_arg_str).
        
    Raises:
        ValueError: If command does not start with '/' or fails shlex parsing.
    """
    raw_command = raw_command.strip()
    if not raw_command.startswith('/'):
        raise ValueError("Commands must start with '/'. Type /help for usage instructions.")
        
    parts = raw_command.split(None, 1)
    cmd_name = parts[0].lower()
    cmd_arg_str = parts[1] if len(parts) > 1 else ""
    
    args: List[str] = []
    if cmd_arg_str and cmd_name not in ['/query', '/q']:
        try:
            args = shlex.split(cmd_arg_str)
        except ValueError as e:
            raise ValueError(f"Command parsing error: {e}. Check your quotes.")
            
    return cmd_name, args, cmd_arg_str
