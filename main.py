from compiler import Parser
from pathlib import Path
import sys

if __name__ == '__main__':
    parser = Parser(Path("test.musical").read_text())
    interpreter = parser.parse()
    interpreter.run()
