from dataclasses import dataclass, field
from typing import Any


class ParserError(Exception):
    pass


@dataclass
class Program:
    structs: dict[str, "StructDefinition"] = field(default_factory=dict)
    functions: dict[str, "FunctionDefinition"] = field(default_factory=dict)
    main: "Block | None" = None


@dataclass
class Block:
    statements: list[Any]


@dataclass
class StructDefinition:
    name: str
    fields: dict[str, Any]


@dataclass
class FunctionDefinition:
    name: str
    params: list[str]
    body: Block


@dataclass
class Assignment:
    target: Any
    value: Any


@dataclass
class PrintStatement:
    expression: Any


@dataclass
class ExpressionStatement:
    expression: Any


@dataclass
class ReturnStatement:
    expression: Any


@dataclass
class IfStatement:
    branches: list[tuple[Any, Block]]
    else_block: Block | None


@dataclass
class ForStatement:
    init: Any
    condition: Any
    update: Any
    body: Block


@dataclass
class StructDeclaration:
    struct_name: str
    variable_name: str


@dataclass
class Variable:
    name: str


@dataclass
class MemberAccess:
    obj: Any
    member: str


@dataclass
class IndexAccess:
    obj: Any
    index: Any


@dataclass
class Literal:
    value: Any


@dataclass
class ArrayLiteral:
    elements: list[Any]


@dataclass
class BinaryExpression:
    left: Any
    operator: str
    right: Any


@dataclass
class UnaryExpression:
    operator: str
    operand: Any


@dataclass
class CallExpression:
    callee: str
    args: list[Any]


@dataclass
class InputExpression:
    prompt: Any


@dataclass
class CastExpression:
    cast_type: str
    expression: Any


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        program = Program()
        self._skip_separators()

        while not self._check("EOF"):
            if self._match_keyword("STRUCT"):
                struct_def = self._parse_struct_definition()
                program.structs[struct_def.name] = struct_def
            elif self._match_keyword("FUNCTION"):
                function_def = self._parse_function_definition()
                program.functions[function_def.name] = function_def
            elif self._match_keyword("ENTRY"):
                if program.main is not None:
                    raise self._error("Only one namaskaram block is allowed")
                program.main = self._parse_main_block()
            else:
                token = self._peek()
                raise self._error(f"Unexpected top-level token '{token.value}'")
            self._skip_separators()

        if program.main is None:
            raise self._error("Program must contain namaskaram ... nanni")

        return program

    def _parse_main_block(self):
        statements = []
        self._skip_separators()
        while not self._check_keyword("EXIT"):
            if self._check("EOF"):
                raise self._error("Expected nanni before end of file")
            statements.append(self._parse_statement())
            self._skip_separators()
        self._consume_keyword("EXIT", "Expected nanni to close namaskaram block")
        return Block(statements)

    def _parse_struct_definition(self):
        name = self._consume("IDENTIFIER", "Expected struct name").value
        self._skip_separators()
        self._consume_operator("{", "Expected '{' after struct name")
        self._skip_separators()

        fields = {}
        while not self._check_operator("}"):
            field_name = self._consume("IDENTIFIER", "Expected struct field name").value
            self._consume_operator("=", "Expected '=' in struct field")
            fields[field_name] = self._parse_expression()
            self._consume_statement_end()
            self._skip_separators()

        self._consume_operator("}", "Expected '}' after struct body")
        if self._match_operator(";"):
            self._skip_separators()
        return StructDefinition(name, fields)

    def _parse_function_definition(self):
        name = self._consume("IDENTIFIER", "Expected function name after pravarthanam").value
        self._consume_operator("(", "Expected '(' after function name")

        params = []
        if not self._check_operator(")"):
            while True:
                params.append(self._consume("IDENTIFIER", "Expected parameter name").value)
                if not self._match_operator(","):
                    break

        self._consume_operator(")", "Expected ')' after parameters")
        self._skip_separators()
        body = self._parse_statement_block()
        return FunctionDefinition(name, params, body)

    def _parse_statement_block(self):
        if self._match_operator("{"):
            self._skip_separators()
            statements = []
            while not self._check_operator("}"):
                if self._check("EOF"):
                    raise self._error("Expected '}' before end of file")
                statements.append(self._parse_statement())
                self._skip_separators()
            self._consume_operator("}", "Expected '}' after block")
            return Block(statements)

        statement = self._parse_statement()
        return Block([statement])

    def _parse_statement(self):
        self._skip_separators()

        if self._check_keyword("PRINT"):
            return self._parse_print()
        if self._check_keyword("IF"):
            return self._parse_if()
        if self._check_keyword("FOR"):
            return self._parse_for()
        if self._check_keyword("RETURN"):
            return self._parse_return()
        if self._check_keyword("STRUCT"):
            return self._parse_struct_declaration()
        if self._is_array_declaration():
            name = self._advance().value
            self._consume_operator("[", "Expected '[' in array declaration")
            self._consume_operator("]", "Expected ']' in array declaration")
            self._consume_operator("=", "Expected '=' after [] in array declaration")
            value = self._parse_expression()
            self._consume_statement_end()
            return Assignment(Variable(name), value)

        expr = self._parse_expression()
        if self._match_operator("="):
            if not isinstance(expr, (Variable, MemberAccess, IndexAccess)):
                raise self._error("Left side of assignment must be a variable, member, or array index")
            value = self._parse_expression()
            self._consume_statement_end()
            return Assignment(expr, value)

        if isinstance(expr, Variable) and self._match_operator("["):
            self._consume_operator("]", "Expected ']' in array declaration")
            self._consume_operator("=", "Expected '=' after [] in array declaration")
            value = self._parse_expression()
            self._consume_statement_end()
            return Assignment(expr, value)

        if not isinstance(expr, (CallExpression, Assignment)):
            raise self._error("Invalid standalone statement")

        self._consume_statement_end()
        return ExpressionStatement(expr)

    def _parse_print(self):
        self._consume_keyword("PRINT", "Expected print keyword")
        if self._match_operator("("):
            expr = self._parse_expression()
            self._consume_operator(")", "Expected ')' after print expression")
        else:
            expr = self._parse_expression()
        self._consume_statement_end()
        return PrintStatement(expr)

    def _parse_if(self):
        branches = []
        self._consume_keyword("IF", "Expected anengil")
        self._consume_operator("(", "Expected '(' after anengil")
        condition = self._parse_expression()
        self._consume_operator(")", "Expected ')' after if condition")
        self._skip_separators()
        branches.append((condition, self._parse_statement_block()))
        self._skip_separators()

        while self._match_keyword("ELIF"):
            self._consume_operator("(", "Expected '(' after anengil enkil")
            elif_condition = self._parse_expression()
            self._consume_operator(")", "Expected ')' after else-if condition")
            self._skip_separators()
            branches.append((elif_condition, self._parse_statement_block()))
            self._skip_separators()

        else_block = None
        if self._match_keyword("ELSE"):
            self._skip_separators()
            else_block = self._parse_statement_block()

        return IfStatement(branches, else_block)

    def _parse_for(self):
        self._consume_keyword("FOR", "Expected avarthikuka")
        self._consume_operator("(", "Expected '(' after avarthikuka")

        init = None
        if not self._check_operator(";"):
            init = self._parse_for_component()
        self._consume_operator(";", "Expected ';' after for initializer")

        condition = Literal(1)
        if not self._check_operator(";"):
            condition = self._parse_expression()
        self._consume_operator(";", "Expected ';' after for condition")

        update = None
        if not self._check_operator(")"):
            update = self._parse_for_component()
        self._consume_operator(")", "Expected ')' after for update")

        self._skip_separators()
        body = self._parse_statement_block()
        return ForStatement(init, condition, update, body)

    def _parse_for_component(self):
        expr = self._parse_expression()
        if self._match_operator("="):
            if not isinstance(expr, (Variable, MemberAccess, IndexAccess)):
                raise self._error("Invalid for-loop assignment target")
            value = self._parse_expression()
            return Assignment(expr, value)
        return ExpressionStatement(expr)

    def _parse_return(self):
        self._consume_keyword("RETURN", "Expected return")
        expression = self._parse_expression()
        self._consume_statement_end()
        return ReturnStatement(expression)

    def _parse_struct_declaration(self):
        self._consume_keyword("STRUCT", "Expected ghatana")
        struct_name = self._consume("IDENTIFIER", "Expected struct type name").value
        variable_name = self._consume("IDENTIFIER", "Expected struct variable name").value
        self._consume_statement_end()
        return StructDeclaration(struct_name, variable_name)

    def _parse_expression(self):
        return self._parse_equality()

    def _parse_equality(self):
        expr = self._parse_comparison()
        while self._match_operator("==", "!="):
            operator = self._previous().value
            right = self._parse_comparison()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def _parse_comparison(self):
        expr = self._parse_term()
        while self._match_operator(">", "<", ">=", "<="):
            operator = self._previous().value
            right = self._parse_term()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def _parse_term(self):
        expr = self._parse_factor()
        while self._match_operator("+", "-"):
            operator = self._previous().value
            right = self._parse_factor()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def _parse_factor(self):
        expr = self._parse_unary()
        while self._match_operator("*", "/", "%"):
            operator = self._previous().value
            right = self._parse_unary()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def _parse_unary(self):
        if self._match_operator("-", "+"):
            operator = self._previous().value
            return UnaryExpression(operator, self._parse_unary())

        if self._check_operator("(") and self._check_type_cast():
            self._consume_operator("(", "Expected '(' for cast")
            cast_type = self._consume("IDENTIFIER", "Expected cast type").value
            self._consume_operator(")", "Expected ')' after cast type")
            return CastExpression(cast_type, self._parse_unary())

        return self._parse_postfix()

    def _parse_postfix(self):
        expr = self._parse_primary()

        while True:
            if self._match_operator("("):
                if not isinstance(expr, Variable):
                    raise self._error("Only named functions can be called")
                args = []
                if not self._check_operator(")"):
                    while True:
                        args.append(self._parse_expression())
                        if not self._match_operator(","):
                            break
                self._consume_operator(")", "Expected ')' after function call")
                expr = CallExpression(expr.name, args)
                continue

            if self._match_operator("["):
                index = self._parse_expression()
                self._consume_operator("]", "Expected ']' after index")
                expr = IndexAccess(expr, index)
                continue

            if self._match_operator("."):
                member = self._consume("IDENTIFIER", "Expected member name after '.'").value
                expr = MemberAccess(expr, member)
                continue

            if self._match_operator("++"):
                expr = Assignment(expr, BinaryExpression(expr, "+", Literal(1)))
                continue

            if self._match_operator("--"):
                expr = Assignment(expr, BinaryExpression(expr, "-", Literal(1)))
                continue

            break

        return expr

    def _parse_primary(self):
        if self._match("NUMBER"):
            raw = self._previous().value
            if "." in raw:
                return Literal(float(raw))
            return Literal(int(raw))

        if self._match("STRING"):
            return Literal(self._previous().value)

        if self._match("CHAR"):
            return Literal(self._previous().value)

        if self._match_keyword("INPUT"):
            return self._parse_input_expression()

        if self._match("IDENTIFIER"):
            return Variable(self._previous().value)

        if self._match_operator("["):
            elements = []
            if not self._check_operator("]"):
                while True:
                    elements.append(self._parse_expression())
                    if not self._match_operator(","):
                        break
            self._consume_operator("]", "Expected ']' after array literal")
            return ArrayLiteral(elements)

        if self._match_operator("{"):
            elements = []
            if not self._check_operator("}"):
                while True:
                    elements.append(self._parse_expression())
                    if not self._match_operator(","):
                        break
            self._consume_operator("}", "Expected '}' after array literal")
            return ArrayLiteral(elements)

        if self._match_operator("("):
            expr = self._parse_expression()
            self._consume_operator(")", "Expected ')' after expression")
            return expr

        token = self._peek()
        raise self._error(f"Unexpected token '{token.value}'")

    def _parse_input_expression(self):
        if self._match_operator("("):
            prompt = Literal("")
            if not self._check_operator(")"):
                prompt = self._parse_expression()
            self._consume_operator(")", "Expected ')' after input prompt")
            return InputExpression(prompt)

        if self._check("STRING"):
            return InputExpression(self._parse_primary())

        return InputExpression(Literal(""))

    def _consume_statement_end(self):
        while self._match_operator(";"):
            pass
        if self._match("NEWLINE"):
            while self._match("NEWLINE"):
                pass

    def _skip_separators(self):
        while self._match("NEWLINE"):
            pass

    def _is_array_declaration(self):
        if self.pos + 3 >= len(self.tokens):
            return False
        first = self.tokens[self.pos]
        second = self.tokens[self.pos + 1]
        third = self.tokens[self.pos + 2]
        fourth = self.tokens[self.pos + 3]
        return (
            first.type == "IDENTIFIER"
            and second.type == "OPERATOR"
            and second.value == "["
            and third.type == "OPERATOR"
            and third.value == "]"
            and fourth.type == "OPERATOR"
            and fourth.value == "="
        )

    def _check_type_cast(self):
        if self.pos + 2 >= len(self.tokens):
            return False
        first = self.tokens[self.pos]
        second = self.tokens[self.pos + 1]
        third = self.tokens[self.pos + 2]
        return (
            first.type == "OPERATOR"
            and first.value == "("
            and second.type == "IDENTIFIER"
            and second.value in {"int", "float", "string", "char"}
            and third.type == "OPERATOR"
            and third.value == ")"
        )

    def _consume(self, token_type, message):
        if self._check(token_type):
            return self._advance()
        raise self._error(message)

    def _consume_operator(self, value, message):
        if self._check_operator(value):
            return self._advance()
        raise self._error(message)

    def _consume_keyword(self, value, message):
        if self._check_keyword(value):
            return self._advance()
        raise self._error(message)

    def _match(self, *token_types):
        if self._check(*token_types):
            self._advance()
            return True
        return False

    def _match_operator(self, *values):
        if self._check_operator(*values):
            self._advance()
            return True
        return False

    def _match_keyword(self, *values):
        if self._check_keyword(*values):
            self._advance()
            return True
        return False

    def _check(self, *token_types):
        if self._is_at_end():
            return "EOF" in token_types
        return self._peek().type in token_types

    def _check_operator(self, *values):
        if self._is_at_end():
            return False
        token = self._peek()
        return token.type == "OPERATOR" and token.value in values

    def _check_keyword(self, *values):
        if self._is_at_end():
            return False
        token = self._peek()
        return token.type == "KEYWORD" and token.value in values

    def _advance(self):
        if not self._is_at_end():
            self.pos += 1
        return self.tokens[self.pos - 1]

    def _is_at_end(self):
        return self._peek().type == "EOF"

    def _peek(self):
        return self.tokens[self.pos]

    def _previous(self):
        return self.tokens[self.pos - 1]

    def _error(self, message):
        token = self._peek()
        return ParserError(f"{message} at line {token.line}, column {token.column}")
