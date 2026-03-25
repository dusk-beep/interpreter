import pytest
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter


def run_program(code, inputs, monkeypatch, capsys):

    # fake user input
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(input_iter))

    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    parser.parse()

    interpreter = Interpreter(tokens)
    interpreter.run()

    captured = capsys.readouterr()

    return captured.out


# -------------------------
# Test Print String
# -------------------------

def test_print_string(monkeypatch, capsys):

    code = """
namaskaram
ezhutuka("hello")
nanni
"""

    output = run_program(code, [], monkeypatch, capsys)

    assert "hello" in output


# -------------------------
# Test Variable Assignment
# -------------------------

def test_variable_assignment(monkeypatch, capsys):

    code = """
namaskaram
x = 5
ezhutuka(x)
nanni
"""

    output = run_program(code, [], monkeypatch, capsys)

    assert "5" in output


# -------------------------
# Test Addition
# -------------------------

def test_addition(monkeypatch, capsys):

    code = """
namaskaram
a = 5
b = 3
c = a + b
ezhutuka(c)
nanni
"""

    output = run_program(code, [], monkeypatch, capsys)

    assert "8" in output


# -------------------------
# Test Float Addition
# -------------------------

def test_float_addition(monkeypatch, capsys):

    code = """
namaskaram
a = 2.5
b = 1.6
c = a + b
ezhutuka(c)
nanni
"""

    output = run_program(code, [], monkeypatch, capsys)

    assert "4.1" in output


# -------------------------
# Test Input Integer
# -------------------------

def test_input_integer(monkeypatch, capsys):

    code = """
namaskaram
x = edukuka("Enter:")
ezhutuka(x)
nanni
"""

    output = run_program(code, ["10"], monkeypatch, capsys)

    assert "10" in output


# -------------------------
# Test Input Float
# -------------------------

def test_input_float(monkeypatch, capsys):

    code = """
namaskaram
x = edukuka("Enter:")
ezhutuka(x)
nanni
"""

    output = run_program(code, ["3.14"], monkeypatch, capsys)

    assert "3.14" in output


# -------------------------
# Test Input String
# -------------------------

def test_input_string(monkeypatch, capsys):

    code = """
namaskaram
name = edukuka("Name:")
ezhutuka(name)
nanni
"""

    output = run_program(code, ["Arun"], monkeypatch, capsys)

    assert "Arun" in output


# -------------------------
# Test String Concatenation
# -------------------------

def test_string_concat(monkeypatch, capsys):

    code = """
namaskaram
name = edukuka("Name:")
ezhutuka("Hello " + name)
nanni
"""

    output = run_program(code, ["Rahul"], monkeypatch, capsys)

    assert "Hello Rahul" in output


# -------------------------
# Test Sum Program
# -------------------------

def test_sum_program(monkeypatch, capsys):

    code = """
namaskaram
n1 = edukuka("Enter1:")
n2 = edukuka("Enter2:")
sum = n1 + n2
ezhutuka("sum:" + sum)
nanni
"""

    output = run_program(code, ["5", "7"], monkeypatch, capsys)

    assert "sum:12" in output


def test_array_print(monkeypatch, capsys):

    code = """
namaskaram
a = [1,2,3]
ezhutuka(a)
nanni
"""

    output = run_program(code, [], monkeypatch, capsys)

    assert "[1, 2, 3]" in output