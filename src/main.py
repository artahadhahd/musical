from compiler import Parser
from pathlib import Path
import sys

if __name__ == '__main__':
    argv = sys.argv
    if len(argv) != 2:
        print('Can only pass one argument: file to compile')
        sys.exit(1)
    try:
        parser = Parser(Path(argv[1]).read_text())
        interpreter = parser.parse()
        interpreter.run()
    except FileNotFoundError:
        print(f"{argv[1]}: source does not exist")
        sys.exit(1)
