import sys

from interpreter import Interpreter
from lexer import Lexer
from myparser import Parser

if len(sys.argv) < 2:
    print("Usage: python main.py <file>")
    exit()

with open(sys.argv[1], "r") as f:
    code = f.read()

tokens = Lexer(code).tokenize()
ast = Parser(tokens).parse()
Interpreter(ast).run()
