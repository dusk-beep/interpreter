from dataclasses import dataclass


KEYWORD_PHRASES = [
    ("anengil enkil", "ELIF"),
    ("anengil engil", "ELIF"),
    ("thirike koduku", "RETURN"),
    ("thirike kodku", "RETURN"),
    ("pravarthanam", "FUNCTION"),
    ("namaskaram", "ENTRY"),
    ("allengil", "ELSE"),
    ("avarthikuka", "FOR"),
    ("avartikuka", "FOR"),
    ("ghatana", "STRUCT"),
    ("parayuka", "PRINT"),
    ("ezhutuka", "PRINT"),
    ("anengil", "IF"),
    ("parayu", "PRINT"),
    ("eyutu", "PRINT"),
    ("ezhutu", "PRINT"),
    ("edukuka", "INPUT"),
    ("eduku", "INPUT"),
    ("nanni", "EXIT"),
]

MULTI_CHAR_OPERATORS = {"==", "!=", ">=", "<=", "++", "--"}
SINGLE_CHAR_OPERATORS = set("{}()[];,=+-*/%<>.")


@dataclass(frozen=True)
class Token:
    type: str
    value: str
    line: int
    column: int

    def __repr__(self):
        return f"{self.type}:{self.value}@{self.line}:{self.column}"


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def tokenize(self):
        while not self._is_at_end():
            char = self._peek()

            if char in " \t\r":
                self._advance()
                continue

            if char == "\n":
                self._add_token("NEWLINE", "\\n")
                self._advance()
                continue

            if self._starts_with("/*"):
                self._consume_block_comment()
                continue

            if char == "#":
                self._consume_line_comment()
                continue

            if char == '"':
                self._tokenize_string()
                continue

            if char == "'":
                self._tokenize_char()
                continue

            if char.isdigit():
                self._tokenize_number()
                continue

            if char.isalpha() or char == "_":
                self._tokenize_identifier_or_keyword()
                continue

            two = self.text[self.pos:self.pos + 2]
            if two in MULTI_CHAR_OPERATORS:
                self._add_token("OPERATOR", two)
                self._advance()
                self._advance()
                continue

            if char in SINGLE_CHAR_OPERATORS:
                self._add_token("OPERATOR", char)
                self._advance()
                continue

            raise LexerError(f"Unexpected character '{char}' at line {self.line}, column {self.column}")

        self.tokens.append(Token("EOF", "EOF", self.line, self.column))
        return self.tokens

    def _tokenize_string(self):
        start_line = self.line
        start_column = self.column
        self._advance()
        chars = []

        while not self._is_at_end() and self._peek() != '"':
            char = self._peek()
            if char == "\\":
                self._advance()
                if self._is_at_end():
                    break
                escape = self._peek()
                chars.append({
                    "n": "\n",
                    "t": "\t",
                    '"': '"',
                    "\\": "\\",
                }.get(escape, escape))
                self._advance()
                continue
            chars.append(char)
            self._advance()

        if self._is_at_end():
            raise LexerError(f"Unterminated string at line {start_line}, column {start_column}")

        self._advance()
        self.tokens.append(Token("STRING", "".join(chars), start_line, start_column))

    def _tokenize_char(self):
        start_line = self.line
        start_column = self.column
        self._advance()

        if self._is_at_end():
            raise LexerError(f"Unterminated char literal at line {start_line}, column {start_column}")

        value = self._peek()
        self._advance()

        if self._is_at_end() or self._peek() != "'":
            raise LexerError(f"Char literal must contain exactly one character at line {start_line}, column {start_column}")

        self._advance()
        self.tokens.append(Token("CHAR", value, start_line, start_column))

    def _tokenize_number(self):
        start_line = self.line
        start_column = self.column
        chars = []
        dot_count = 0

        while not self._is_at_end():
            char = self._peek()
            if char == ".":
                if dot_count == 1:
                    break
                dot_count += 1
                chars.append(char)
                self._advance()
                continue
            if not char.isdigit():
                break
            chars.append(char)
            self._advance()

        self.tokens.append(Token("NUMBER", "".join(chars), start_line, start_column))

    def _tokenize_identifier_or_keyword(self):
        for phrase, token_type in KEYWORD_PHRASES:
            if self._matches_phrase(phrase):
                self._add_token("KEYWORD", token_type)
                for _ in phrase:
                    self._advance()
                return

        start_line = self.line
        start_column = self.column
        chars = []

        while not self._is_at_end():
            char = self._peek()
            if not (char.isalnum() or char == "_"):
                break
            chars.append(char)
            self._advance()

        self.tokens.append(Token("IDENTIFIER", "".join(chars), start_line, start_column))

    def _matches_phrase(self, phrase):
        chunk = self.text[self.pos:self.pos + len(phrase)]
        if chunk != phrase:
            return False

        before_ok = self.pos == 0 or not (self.text[self.pos - 1].isalnum() or self.text[self.pos - 1] == "_")
        after_pos = self.pos + len(phrase)
        after_ok = after_pos >= len(self.text) or not (self.text[after_pos].isalnum() or self.text[after_pos] == "_")
        return before_ok and after_ok

    def _consume_line_comment(self):
        while not self._is_at_end() and self._peek() != "\n":
            self._advance()

    def _consume_block_comment(self):
        self._advance()
        self._advance()
        while not self._is_at_end() and not self._starts_with("*/"):
            self._advance()

        if self._is_at_end():
            raise LexerError("Unterminated block comment")

        self._advance()
        self._advance()

    def _add_token(self, token_type, value):
        self.tokens.append(Token(token_type, value, self.line, self.column))

    def _starts_with(self, text):
        return self.text[self.pos:self.pos + len(text)] == text

    def _peek(self):
        return self.text[self.pos]

    def _advance(self):
        if self._is_at_end():
            return
        current = self.text[self.pos]
        self.pos += 1
        if current == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

    def _is_at_end(self):
        return self.pos >= len(self.text)
