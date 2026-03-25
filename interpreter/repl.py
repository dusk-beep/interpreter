from lexer import Lexer
from parser import Parser
from interpreter import Interpreter


def run_code(code):
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    parser.parse()

    interpreter = Interpreter(tokens)
    interpreter.run()


def repl():
    print("🌴 Welcome to the Monne Manglish Language REPL")
    print("Type 'exit' to quit\n")

    while True:
        try:
            line = input(">>> ")

            if line.strip() == "exit":
                print("nanni 👋")
                break

            # Wrap with program keywords
            code = f"""
namaskaram
{line}
nanni
"""

            run_code(code)

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    repl()