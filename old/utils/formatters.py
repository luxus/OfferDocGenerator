import sys
from typing import Dict

COLOR = {
    'HEADER': '\033[95m',
    'BLUE': '\033[94m',
    'CYAN': '\033[96m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m'
}

def colorize(text: str, color: str) -> str:
    """Wrap text in ANSI color codes if output is a terminal"""
    if sys.stdout.isatty():
        return f"{COLOR[color.upper()]}{text}{COLOR['ENDC']}"
    return text
