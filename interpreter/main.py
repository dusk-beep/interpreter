import sys
import os
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

def main():
    # 1. Check if a filename was provided in the command line
    if len(sys.argv) < 2:
        print("Usage: python main.py <filename.mgl>")
        return

    filename = sys.argv[1]

    # 2. Check if the file exists
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    try:
        # 3. Read the Manglish source code
        with open(filename, "r") as f:
            code = f.read()

        # 4. Lexical Analysis (Break into tokens)
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        # 5. Syntax Analysis (Validate structure)
        # This will now accept functions outside of the entry block
        parser = Parser(tokens)
        parser.parse()

        # 6. Execution (The Interpreter)
        # This will scan for 'pravarthanam' and then jump to 'namaskaram'
        interpreter = Interpreter(tokens)
        interpreter.run()

    except Exception as e:
        print(f"\n❌ Run-time Error: {e}")

if __name__ == "__main__":
    main()