import copy
import re

from myparser import (
    ArrayLiteral,
    Assignment,
    BinaryExpression,
    Block,
    CallExpression,
    CastExpression,
    ExpressionStatement,
    ForStatement,
    FunctionDefinition,
    IfStatement,
    IndexAccess,
    InputExpression,
    Literal,
    MemberAccess,
    PrintStatement,
    Program,
    ReturnStatement,
    StructDeclaration,
    UnaryExpression,
    Variable,
)


class InterpreterError(Exception):
    pass


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}

    def define(self, name, value):
        self.values[name] = value

    def contains_here(self, name):
        return name in self.values

    def contains(self, name):
        if name in self.values:
            return True
        if self.parent is not None:
            return self.parent.contains(name)
        return False

    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
            return
        if self.parent is not None and self.parent.contains(name):
            self.parent.assign(name, value)
            return
        self.values[name] = value

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise InterpreterError(f"Undefined variable '{name}'")


class Interpreter:
    def __init__(self, program):
        if not isinstance(program, Program):
            try:
                from myparser import Parser

                program = Parser(program).parse()
            except Exception as exc:
                raise InterpreterError("Interpreter expects the parsed AST from Parser.parse()") from exc
        self.program = program
        self.global_env = Environment()

    def run(self):
        self._execute_block(self.program.main, self.global_env)

    def _execute_block(self, block, env):
        for statement in block.statements:
            self._execute(statement, env)

    def _execute(self, statement, env):
        if isinstance(statement, Assignment):
            value = self._evaluate(statement.value, env)
            self._assign_target(statement.target, value, env)
            return value

        if isinstance(statement, PrintStatement):
            value = self._evaluate(statement.expression, env)
            print(self._stringify(value, env))
            return None

        if isinstance(statement, ExpressionStatement):
            return self._evaluate(statement.expression, env)

        if isinstance(statement, IfStatement):
            for condition, block in statement.branches:
                if self._is_truthy(self._evaluate(condition, env)):
                    self._execute_block(block, Environment(env))
                    return None
            if statement.else_block is not None:
                self._execute_block(statement.else_block, Environment(env))
            return None

        if isinstance(statement, ForStatement):
            loop_env = Environment(env)
            if statement.init is not None:
                self._execute(statement.init, loop_env)
            while self._is_truthy(self._evaluate(statement.condition, loop_env)):
                self._execute_block(statement.body, Environment(loop_env))
                if statement.update is not None:
                    self._execute(statement.update, loop_env)
            return None

        if isinstance(statement, ReturnStatement):
            raise ReturnSignal(self._evaluate(statement.expression, env))

        if isinstance(statement, StructDeclaration):
            env.define(statement.variable_name, self._create_struct_instance(statement.struct_name, env))
            return None

        raise InterpreterError(f"Unsupported statement type: {type(statement).__name__}")

    def _evaluate(self, expr, env):
        if isinstance(expr, Literal):
            return expr.value

        if isinstance(expr, Variable):
            return env.get(expr.name)

        if isinstance(expr, ArrayLiteral):
            return [self._evaluate(element, env) for element in expr.elements]

        if isinstance(expr, MemberAccess):
            obj = self._evaluate(expr.obj, env)
            if not isinstance(obj, dict):
                raise InterpreterError(f"'{self._describe_target(expr.obj)}' is not a struct")
            if expr.member not in obj:
                raise InterpreterError(f"Struct field '{expr.member}' is not defined")
            return obj[expr.member]

        if isinstance(expr, IndexAccess):
            obj = self._evaluate(expr.obj, env)
            index = self._evaluate(expr.index, env)
            if not isinstance(index, int):
                raise InterpreterError("Array index must be an integer")
            try:
                return obj[index]
            except (TypeError, IndexError):
                raise InterpreterError("Array index out of range")

        if isinstance(expr, UnaryExpression):
            value = self._evaluate(expr.operand, env)
            if expr.operator == "-":
                return -value
            if expr.operator == "+":
                return value
            raise InterpreterError(f"Unsupported unary operator '{expr.operator}'")

        if isinstance(expr, BinaryExpression):
            left = self._evaluate(expr.left, env)
            right = self._evaluate(expr.right, env)
            return self._apply_binary(expr.operator, left, right)

        if isinstance(expr, InputExpression):
            prompt = self._stringify(self._evaluate(expr.prompt, env), env)
            raw = input(prompt)
            return self._auto_convert(raw)

        if isinstance(expr, CastExpression):
            value = self._evaluate(expr.expression, env)
            return self._cast_value(expr.cast_type, value)

        if isinstance(expr, CallExpression):
            return self._call_function(expr.callee, expr.args, env)

        if isinstance(expr, Assignment):
            value = self._evaluate(expr.value, env)
            self._assign_target(expr.target, value, env)
            return value

        raise InterpreterError(f"Unsupported expression type: {type(expr).__name__}")

    def _apply_binary(self, operator, left, right):
        if operator == "+":
            if isinstance(left, str) or isinstance(right, str):
                return self._stringify(left, self.global_env) + self._stringify(right, self.global_env)
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == "/":
            return left / right
        if operator == "%":
            return left % right
        if operator == "==":
            return 1 if left == right else 0
        if operator == "!=":
            return 1 if left != right else 0
        if operator == ">":
            return 1 if left > right else 0
        if operator == "<":
            return 1 if left < right else 0
        if operator == ">=":
            return 1 if left >= right else 0
        if operator == "<=":
            return 1 if left <= right else 0
        raise InterpreterError(f"Unsupported operator '{operator}'")

    def _assign_target(self, target, value, env):
        if isinstance(target, Variable):
            env.assign(target.name, value)
            return

        if isinstance(target, MemberAccess):
            obj = self._evaluate(target.obj, env)
            if not isinstance(obj, dict):
                raise InterpreterError("Only struct members can be assigned with '.'")
            obj[target.member] = value
            return

        if isinstance(target, IndexAccess):
            obj = self._evaluate(target.obj, env)
            index = self._evaluate(target.index, env)
            if not isinstance(index, int):
                raise InterpreterError("Array index must be an integer")
            if not isinstance(obj, list):
                raise InterpreterError("Index assignment requires an array")
            if index < 0 or index >= len(obj):
                raise InterpreterError("Array index out of range")
            obj[index] = value
            return

        raise InterpreterError("Invalid assignment target")

    def _call_function(self, name, arg_exprs, env):
        function = self.program.functions.get(name)
        if function is None:
            raise InterpreterError(f"Undefined function '{name}'")

        args = [self._evaluate(arg, env) for arg in arg_exprs]
        if len(args) != len(function.params):
            raise InterpreterError(
                f"Function '{name}' expects {len(function.params)} arguments but got {len(args)}"
            )

        call_env = Environment(self.global_env)
        for param, value in zip(function.params, args):
            call_env.define(param, value)

        try:
            self._execute_block(function.body, call_env)
        except ReturnSignal as signal:
            return signal.value
        return None

    def _create_struct_instance(self, struct_name, env):
        struct_def = self.program.structs.get(struct_name)
        if struct_def is None:
            raise InterpreterError(f"Undefined struct '{struct_name}'")

        instance = {}
        for field_name, expr in struct_def.fields.items():
            instance[field_name] = copy.deepcopy(self._evaluate(expr, env))
        return instance

    def _cast_value(self, cast_type, value):
        cast_type = cast_type.lower()
        if cast_type == "int":
            if isinstance(value, str) and value.strip() == "":
                return 0
            return int(float(value))
        if cast_type == "float":
            return float(value)
        if cast_type == "string":
            return self._stringify(value, self.global_env)
        if cast_type == "char":
            text = self._stringify(value, self.global_env)
            return text[0] if text else ""
        raise InterpreterError(f"Unsupported cast type '{cast_type}'")

    def _auto_convert(self, raw):
        text = raw.strip()
        if text == "":
            return ""
        try:
            if "." in text:
                return float(text)
            return int(text)
        except ValueError:
            return raw

    def _is_truthy(self, value):
        return value not in (0, 0.0, "", None, False)

    def _stringify(self, value, env):
        if isinstance(value, str):
            return self._interpolate_string(value, env)
        if isinstance(value, list):
            return "[" + ", ".join(self._stringify(item, env) for item in value) + "]"
        if isinstance(value, dict):
            parts = [f"{key}: {self._stringify(item, env)}" for key, item in value.items()]
            return "{ " + ", ".join(parts) + " }"
        return str(value)

    def _interpolate_string(self, text, env):
        pattern = re.compile(r"\{([^{}]+)\}")

        def replace(match):
            expression_text = match.group(1).strip()
            try:
                from lexer import Lexer
                from myparser import Parser

                tokens = Lexer(expression_text).tokenize()
                parser = Parser(tokens)
                expression = parser._parse_expression()
                return self._stringify(self._evaluate(expression, env), env)
            except Exception:
                return match.group(0)

        return pattern.sub(replace, text)

    def _describe_target(self, expr):
        if isinstance(expr, Variable):
            return expr.name
        if isinstance(expr, MemberAccess):
            return f"{self._describe_target(expr.obj)}.{expr.member}"
        if isinstance(expr, IndexAccess):
            return f"{self._describe_target(expr.obj)}[...]"
        return type(expr).__name__
