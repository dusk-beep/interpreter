import sys
import os

# Priority to local files fixes "ImportError: cannot import name 'Parser' from 'parser'"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <filename.mgl>")
        return
    
    filename = sys.argv[1]
    try:
        with open(filename, "r") as f:
            code = f.read()

        lexer = Lexer(code)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        parser.parse()

        interpreter = Interpreter(tokens)
        interpreter.run()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()