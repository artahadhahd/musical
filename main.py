from compiler import Lexer
from pathlib import Path
import sys

if __name__ == '__main__':
    lexer = Lexer(Path("test.musical").read_text())
    lexer.parse()
