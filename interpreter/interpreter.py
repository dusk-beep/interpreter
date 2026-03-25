class Interpreter:
    def __init__(self, tokens):
        self.tokens = tokens; self.pos = 0; self.current = self.tokens[self.pos]
        self.variables = {}; self.functions = {}; self.return_val = None; self.is_returning = False

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens): self.current = self.tokens[self.pos]

    def run(self):
        # 1. Map all functions first (C-style global lookup)
        for i in range(len(self.tokens)):
            if self.tokens[i].value == "FUNCTION": self.functions[self.tokens[i+1].value] = i
        
        # 2. Find and jump to the 'namaskaram' entry point
        entry_pos = next((i for i, t in enumerate(self.tokens) if t.value == "ENTRY"), None)
        if entry_pos is not None:
            self.pos = entry_pos; self.current = self.tokens[self.pos]; self.advance()
            while self.current.value != "EXIT":
                self.execute_statement()
        print("✅ Program Finished")

    def execute_statement(self):
        if self.current.value == "FUNCTION": # Skip definitions during main run
            while self.current.value != "FUNC_END": self.advance()
            self.advance()
        elif self.current.value == "RETURN":
            self.advance(); self.return_val = self.evaluate_expression(); self.is_returning = True
        elif self.current.value == "PRINT":
            self.advance(); self.advance(); print(self.evaluate_expression()); self.advance()
        elif self.current.type == "IDENTIFIER":
            if self.pos+1 < len(self.tokens) and self.tokens[self.pos+1].value == "(": self.execute_func_call()
            else: self.execute_assignment()
        else: self.advance()

    def execute_assignment(self):
        var = self.current.value; self.advance(); self.advance()
        self.variables[var] = self.evaluate_expression()

    def execute_func_call(self):
        name = self.current.value; self.advance(); self.advance()
        args = []
        while self.current.value != ")":
            args.append(self.evaluate_expression())
            if self.current.value == ",": self.advance()
        self.advance()
        if name in self.functions:
            old_pos = self.pos; self.pos = self.functions[name]
            self.advance(); self.advance(); self.advance() # FUNCTION name (
            params = []
            while self.current.value != ")":
                params.append(self.current.value); self.advance()
                if self.current.value == ",": self.advance()
            self.advance()
            old_vars = self.variables.copy()
            for i in range(min(len(params), len(args))): self.variables[params[i]] = args[i]
            self.is_returning = False
            while self.current.value != "FUNC_END" and not self.is_returning: self.execute_statement()
            res = self.return_val; self.variables = old_vars; self.pos = old_pos; self.is_returning = False
            return res

    def evaluate_expression(self):
        left = self.evaluate_term()
        while self.current.value in ["+", "-"]:
            op = self.current.value; self.advance(); right = self.evaluate_term()
            left = (left + right) if op == "+" else (left - right)
        return left

    def evaluate_term(self):
        left = self.evaluate_factor()
        while self.current.value in ["*", "/"]:
            op = self.current.value; self.advance(); right = self.evaluate_factor()
            left = (left * right) if op == "*" else (left / right)
        return left

    def evaluate_factor(self):
        t = self.current
        if t.type == "NUMBER":
            val = float(t.value) if "." in t.value else int(t.value); self.advance(); return val
        if t.type == "STRING": val = t.value; self.advance(); return val
        if t.value == "INPUT":
            self.advance(); self.advance() # (
            prompt = self.current.value if self.current.type == "STRING" else ""
            if prompt: self.advance()
            self.advance() # )
            raw = input(prompt)
            try: return float(raw) if "." in raw else int(raw)
            except: return raw
        if t.type == "IDENTIFIER":
            if self.pos+1 < len(self.tokens) and self.tokens[self.pos+1].value == "(": return self.execute_func_call()
            val = self.variables.get(t.value, 0); self.advance(); return val
        return 0