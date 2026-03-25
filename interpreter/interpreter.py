class Interpreter:
    def __init__(self, tokens):
        self.tokens = tokens; self.pos = 0; self.current = self.tokens[self.pos]
        self.functions = {}; self.structs = {}; self.stack = [{}]; 
        self.ret_val = 0; self.is_ret = False

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens): self.current = self.tokens[self.pos]

    def run(self):
        idx = 0
        while idx < len(self.tokens):
            if self.tokens[idx].value == "FUNCTION": self.functions[self.tokens[idx+1].value] = idx
            if self.tokens[idx].value == "STRUCT":
                name = self.tokens[idx+1].value; members = []; j = idx + 2
                while self.tokens[j].value != "STRUCT_END":
                    if self.tokens[j].type == "IDENTIFIER": members.append(self.tokens[j].value)
                    j += 1
                self.structs[name] = members
            idx += 1
        entry = next((i for i, t in enumerate(self.tokens) if t.value == "ENTRY"), None)
        if entry is not None:
            self.pos = entry; self.advance()
            while self.current.value != "EXIT": self.execute()
        print("✅ Program Finished")

    def execute(self):
        if self.is_ret: return 
        if self.current.value in ["FUNCTION", "STRUCT"]:
            target = "FUNC_END" if self.current.value == "FUNCTION" else "STRUCT_END"
            while self.current.value != target: self.advance()
            self.advance()
        elif self.current.value == "IF":
            self.advance(); self.advance(); cond = self.eval_expr(); self.advance()
            if cond: self.execute()
            else:
                while self.current.type != "NEWLINE" and self.current.type != "EOF": self.advance()
                self.advance()
        elif self.current.value == "PRINT":
            self.advance(); self.advance(); print(self.eval_expr()); self.advance()
        elif self.current.value == "RETURN":
            self.advance(); self.ret_val = self.eval_expr(); self.is_ret = True
        elif self.current.type == "IDENTIFIER":
            if self.pos+1 < len(self.tokens) and self.tokens[self.pos+1].value == "(": self.call_func()
            else: self.assign()
        else: self.advance()

    def assign(self):
        name = self.current.value; self.advance()
        if self.current.value == ".":
            self.advance(); member = self.current.value; self.advance(); self.advance()
            val = self.eval_expr()
            obj = self.stack[-1].get(name, self.stack[0].get(name))
            if isinstance(obj, dict): obj[member] = val
        else:
            self.advance(); val = self.eval_expr()
            if val in self.structs: self.stack[-1][name] = {m: 0 for m in self.structs[val]}
            else: self.stack[-1][name] = val

    def call_func(self):
        name = self.current.value; self.advance(); self.advance()
        args = []
        while self.current.value != ")":
            args.append(self.eval_expr())
            if self.current.value == ",": self.advance()
        self.advance()
        if name in self.functions:
            old_p = self.pos; self.pos = self.functions[name]
            self.advance(); self.advance(); self.advance()
            params = []
            while self.current.value != ")":
                params.append(self.current.value); self.advance()
                if self.current.value == ",": self.advance()
            self.advance()
            new_frame = {params[i]: args[i] for i in range(min(len(params), len(args)))}
            self.stack.append(new_frame); prev_ret = self.is_ret; self.is_ret = False
            while self.current.value != "FUNC_END" and not self.is_ret: self.execute()
            res = self.ret_val; self.stack.pop(); self.pos = old_p; self.is_ret = prev_ret
            return res
        return 0

    def eval_expr(self):
        left = self.eval_term()
        while self.current.value in ["+", "-", "==", "!=", ">", "<", ">=", "<="]:
            op = self.current.value; self.advance(); right = self.eval_term()
            if op == "+":
                # FIX: Handle mixed string/number concatenation
                if isinstance(left, str) or isinstance(right, str):
                    left = str(left) + str(right)
                else:
                    left += right
            elif op == "-": left -= right
            elif op == "==": left = 1 if left == right else 0
            elif op == "!=": left = 1 if left != right else 0
            elif op == ">": left = 1 if left > right else 0
            elif op == "<": left = 1 if left < right else 0
            elif op == ">=": left = 1 if left >= right else 0
            elif op == "<=": left = 1 if left <= right else 0
        return left

    def eval_term(self):
        left = self.eval_fact()
        while self.current.value in ["*", "/"]:
            op = self.current.value; self.advance(); right = self.eval_fact()
            left = (left * right) if op == "*" else (left / right)
        return left

    def eval_fact(self):
        t = self.current
        if t.type == "NUMBER":
            v = float(t.value) if "." in t.value else int(t.value); self.advance(); return v
        if t.type == "STRING": v = t.value; self.advance(); return v
        
        # INPUT logic
        if t.value == "INPUT":
            self.advance(); self.advance()
            prompt = self.current.value if self.current.type == "STRING" else ""
            if prompt: self.advance()
            self.advance()
            raw = input(prompt)
            # Try to convert to number, otherwise keep as string
            try:
                if "." in raw: return float(raw)
                return int(raw)
            except ValueError:
                return raw

        if t.type == "IDENTIFIER":
            if t.value in self.structs: name = t.value; self.advance(); return name
            if self.pos+1 < len(self.tokens) and self.tokens[self.pos+1].value == "(": return self.call_func()
            name = t.value; self.advance()
            if self.current.value == ".":
                self.advance(); m = self.current.value; self.advance()
                obj = self.stack[-1].get(name, self.stack[0].get(name))
                return obj.get(m, 0) if isinstance(obj, dict) else 0
            return self.stack[-1].get(name, self.stack[0].get(name, 0))
        return 0