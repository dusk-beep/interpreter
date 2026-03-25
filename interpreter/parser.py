class Parser:
    def __init__(self, tokens):
        self.tokens = tokens; self.pos = 0; self.current = self.tokens[self.pos]
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens): self.current = self.tokens[self.pos]
    def eat(self, t_type, val=None):
        if self.current.type == t_type and (val is None or self.current.value == val):
            self.advance(); return
        raise Exception(f"Syntax Error: Expected {t_type} {val} but got {self.current.value}")

    def parse(self):
        while self.current.type != "EOF":
            if self.current.value == "FUNCTION":
                self.function_definition()
            elif self.current.value == "ENTRY":
                self.main_block()
            else:
                self.advance() # Skip junk/newlines outside blocks
        print("✅ Parsing Successful")

    def main_block(self):
        self.eat("KEYWORD", "ENTRY")
        while self.current.value != "EXIT":
            self.statement()
        self.eat("KEYWORD", "EXIT")

    def function_definition(self):
        self.eat("KEYWORD", "FUNCTION")
        self.eat("IDENTIFIER") # name
        self.eat("OPERATOR", "(")
        while self.current.value != ")":
            self.eat("IDENTIFIER")
            if self.current.value == ",": self.advance()
        self.eat("OPERATOR", ")")
        while self.current.value != "FUNC_END":
            self.statement()
        self.eat("KEYWORD", "FUNC_END")

    def statement(self):
        if self.current.value == "PRINT":
            self.advance(); self.eat("OPERATOR", "("); self.expression(); self.eat("OPERATOR", ")")
        elif self.current.value == "RETURN":
            self.advance(); self.expression()
        elif self.current.type == "IDENTIFIER":
            self.advance()
            if self.current.value == "=": self.advance(); self.expression()
            elif self.current.value == "(": # call
                self.advance()
                while self.current.value != ")":
                    self.expression()
                    if self.current.value == ",": self.advance()
                self.advance()
        else: self.advance()

    def expression(self):
        self.term()
        while self.current.value in ["+", "-"]: self.advance(); self.term()
    def term(self):
        self.factor()
        while self.current.value in ["*", "/"]: self.advance(); self.factor()
    def factor(self):
        if self.current.type in ["NUMBER", "STRING", "IDENTIFIER"]:
            if self.current.type == "IDENTIFIER" and self.pos+1 < len(self.tokens) and self.tokens[self.pos+1].value == "(":
                self.advance(); self.advance()
                while self.current.value != ")":
                    self.expression()
                    if self.current.value == ",": self.advance()
                self.advance()
            else: self.advance()
        elif self.current.value == "INPUT":
            self.advance(); self.eat("OPERATOR", "(")
            if self.current.type == "STRING": self.advance()
            self.eat("OPERATOR", ")")
        else: self.advance()