import pytest
from lexer import Lexer


def tokenize(code):
    lexer = Lexer(code)
    return lexer.tokenize()


# -------------------------
# Test ENTRY keyword
# -------------------------

def test_entry_keyword():

    code = "namaskaram"

    tokens = tokenize(code)

    assert tokens[0].type == "KEYWORD"
    assert tokens[0].value == "ENTRY"


# -------------------------
# Test EXIT keyword
# -------------------------

def test_exit_keyword():

    code = "nanni"

    tokens = tokenize(code)

    assert tokens[0].type == "KEYWORD"
    assert tokens[0].value == "EXIT"


# -------------------------
# Test PRINT keyword
# -------------------------

def test_print_keyword():

    code = 'ezhutuka("hello")'

    tokens = tokenize(code)

    assert tokens[0].value == "PRINT"


# -------------------------
# Test INPUT keyword
# -------------------------

def test_input_keyword():

    code = 'edukuka("enter")'

    tokens = tokenize(code)

    assert tokens[0].value == "INPUT"


# -------------------------
# Test Identifier
# -------------------------

def test_identifier():

    code = "x"

    tokens = tokenize(code)

    assert tokens[0].type == "IDENTIFIER"
    assert tokens[0].value == "x"


# -------------------------
# Test Number
# -------------------------

def test_number():

    code = "123"

    tokens = tokenize(code)

    assert tokens[0].type == "NUMBER"
    assert tokens[0].value == "123"


# -------------------------
# Test String
# -------------------------

def test_string():

    code = '"hello"'

    tokens = tokenize(code)

    assert tokens[0].type == "STRING"
    assert tokens[0].value == "hello"


# -------------------------
# Test Operator
# -------------------------

def test_operator():

    code = "x + y"

    tokens = tokenize(code)

    assert tokens[1].type == "OPERATOR"
    assert tokens[1].value == "+"


# -------------------------
# Test Assignment
# -------------------------

def test_assignment():

    code = "x = 5"

    tokens = tokenize(code)

    assert tokens[1].value == "="
    assert tokens[2].value == "5"


# -------------------------
# Test Full Statement
# -------------------------

def test_full_statement():

    code = 'ezhutuka("hello")'

    tokens = tokenize(code)

    assert tokens[0].value == "PRINT"
    assert tokens[1].value == "("
    assert tokens[2].value == "hello"
    assert tokens[3].value == ")"


def test_array_tokens():

    code = """
namaskaram
a = [1,2,3]
nanni
"""

    lexer = Lexer(code)
    tokens = lexer.tokenize()

    values = [t.value for t in tokens]

    assert "[" in values
    assert "]" in values
    assert "," in values
    assert "1" in values
    assert "2" in values
    assert "3" in values