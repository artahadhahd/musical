from compiler import Parser
from pathlib import Path
import sys

if __name__ == '__main__':
    argv = sys.argv
    if len(argv) != 2:
        print('Can only pass one argument: file to compile')
        sys.exit(1)
    parser = Parser(Path(argv[1]).read_text())
    interpreter = parser.parse()
    interpreter.run()
