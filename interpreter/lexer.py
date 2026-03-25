import re

KEYWORDS = {
    "ezhutuka": "PRINT", "edukuka": "INPUT", "namaskaram": "ENTRY",
    "nanni": "EXIT", "pravarthanam": "FUNCTION", "thirike": "RETURN", "kainhu": "FUNC_END"
}

OPERATORS = ["+", "-", "*", "/", "=", "(", ")", ">", "<", "==", "!=", ">=", "<=", ",", "[", "]"]

class Token:
    def __init__(self, type_, value):
        self.type = type_; self.value = value
    def __repr__(self):
        return f"{self.type}:{self.value}"

class Lexer:
    def __init__(self, text):
        self.text = text; self.tokens = []
    def tokenize(self):
        lines = self.text.split("\n")
        for line in lines:
            line = line.strip()
            if not line: continue
            string_pattern = r'"(.*?)"'
            strings = re.findall(string_pattern, line)
            temp_line = re.sub(string_pattern, "STRING", line)
            words = re.findall(r'\d+\.\d+|\w+|==|!=|>=|<=|[()\[\],+\-*/=><]', temp_line)
            string_index = 0
            for word in words:
                if word == "STRING":
                    self.tokens.append(Token("STRING", strings[string_index])); string_index += 1
                elif word in KEYWORDS:
                    self.tokens.append(Token("KEYWORD", KEYWORDS[word]))
                elif re.match(r'^\d+\.\d+$', word) or word.isdigit():
                    self.tokens.append(Token("NUMBER", word))
                elif word in OPERATORS:
                    self.tokens.append(Token("OPERATOR", word))
                else:
                    self.tokens.append(Token("IDENTIFIER", word))
            self.tokens.append(Token("NEWLINE", "\\n"))
        self.tokens.append(Token("EOF", "EOF"))
        return self.tokens