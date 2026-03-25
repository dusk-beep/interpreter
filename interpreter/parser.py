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
            if self.current.value == "FUNCTION": self.parse_function()
            elif self.current.value == "STRUCT": self.parse_struct()
            elif self.current.value == "ENTRY": self.parse_main()
            else: self.advance()
        print("✅ Parsing Successful")

    def parse_struct(self):
        self.eat("KEYWORD", "STRUCT"); self.eat("IDENTIFIER")
        while self.current.value != "STRUCT_END": self.advance()
        self.eat("KEYWORD", "STRUCT_END")

    def parse_function(self):
        self.eat("KEYWORD", "FUNCTION"); self.eat("IDENTIFIER"); self.eat("OPERATOR", "(")
        while self.current.value != ")":
            if self.current.type == "IDENTIFIER": self.advance()
            if self.current.value == ",": self.advance()
        self.eat("OPERATOR", ")")
        while self.current.value != "FUNC_END": self.advance()
        self.eat("KEYWORD", "FUNC_END")

    def parse_main(self):
        self.eat("KEYWORD", "ENTRY")
        while self.current.value != "EXIT": self.advance()
        self.eat("KEYWORD", "EXIT")