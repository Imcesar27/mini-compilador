# parser.py Parser para el lenguaje Lox
# Este módulo implementa el parser para el lenguaje Lox, capaz de analizar
# declaraciones, sentencias y expresiones, generando un árbol de sintaxis abstracta (AST).
from tokens import Token, TokenType
from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.type != TokenType.NEWLINE]  # Ignorar saltos de línea
        self.current = 0
        self.errors = []
    
    def parse(self):
        """Parsea el programa completo"""
        statements = []
        
        while not self.is_at_end():
            try:
                stmt = self.declaration()
                if stmt:
                    statements.append(stmt)
            except ParseError as e:
                self.errors.append(str(e))
                self.synchronize()
        
        return Program(statements)
    
    # ============ UTILIDADES ============
    
    def is_at_end(self):
        """Verifica si llegamos al final de los tokens"""
        return self.peek().type == TokenType.EOF
    
    def peek(self):
        """Mira el token actual sin consumirlo"""
        return self.tokens[self.current]
    
    def previous(self):
        """Devuelve el token anterior"""
        return self.tokens[self.current - 1]
    
    def advance(self):
        """Consume el token actual y avanza al siguiente"""
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def check(self, token_type):
        """Verifica si el token actual es del tipo especificado"""
        if self.is_at_end():
            return False
        return self.peek().type == token_type
    
    def match(self, *types):
        """Verifica si el token actual coincide con alguno de los tipos"""
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False
    
    def consume(self, token_type, message):
        """Consume un token del tipo esperado o lanza error"""
        if self.check(token_type):
            return self.advance()
        
        current = self.peek()
        raise ParseError(f"{message} en línea {current.line}, columna {current.column}. "
                        f"Se encontró '{current.value}'")
    
    def synchronize(self):
        """Recupera el parser después de un error"""
        self.advance()
        
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            
            if self.peek().type in [TokenType.IF, TokenType.FOR, TokenType.WHILE,
                                   TokenType.VAR, TokenType.FUNCTION, TokenType.RETURN,
                                   TokenType.PRINT]:
                return
            
            self.advance()
    
    # ============ DECLARACIONES ============
    
    def declaration(self):
        """Parsea una declaración"""
        try:
            if self.match(TokenType.VAR, TokenType.CONST):
                return self.var_declaration()
            
            if self.match(TokenType.FUNCTION):
                return self.function_declaration()
            
            return self.statement()
        except ParseError as e:
            raise e
    
    def var_declaration(self):
        """Parsea una declaración de variable"""
        var_type = self.previous().value  # 'var' o 'const'
        
        name = self.consume(TokenType.IDENTIFIER, "Se esperaba nombre de variable")
        
        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Se esperaba ';' después de declaración de variable")
        
        return VarDeclaration(var_type, name.value, initializer)
    
    def function_declaration(self):
        """Parsea una declaración de función"""
        name = self.consume(TokenType.IDENTIFIER, "Se esperaba nombre de función")
        
        self.consume(TokenType.LPAREN, "Se esperaba '(' después del nombre de función")
        
        parameters = []
        if not self.check(TokenType.RPAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Se esperaba nombre de parámetro"))
            while self.match(TokenType.COMMA):
                parameters.append(self.consume(TokenType.IDENTIFIER, "Se esperaba nombre de parámetro"))
        
        self.consume(TokenType.RPAREN, "Se esperaba ')' después de parámetros")
        
        self.consume(TokenType.LBRACE, "Se esperaba '{' antes del cuerpo de función")
        body = self.block_statement()
        
        return FunctionDeclaration(name.value, [p.value for p in parameters], body)
    
    # ============ SENTENCIAS ============
    
    def statement(self):
        """Parsea una sentencia"""
        if self.match(TokenType.IF):
            return self.if_statement()
        
        if self.match(TokenType.WHILE):
            return self.while_statement()
        
        if self.match(TokenType.FOR):
            return self.for_statement()
        
        if self.match(TokenType.RETURN):
            return self.return_statement()
        
        if self.match(TokenType.PRINT):
            return self.print_statement()
        
        if self.match(TokenType.LBRACE):
            return self.block_statement()
        
        return self.expression_statement()
    
    def if_statement(self):
        """Parsea una sentencia if"""
        self.consume(TokenType.LPAREN, "Se esperaba '(' después de 'if'")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Se esperaba ')' después de condición")
        
        then_branch = self.statement()
        else_branch = None
        
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        
        return IfStatement(condition, then_branch, else_branch)
    
    def while_statement(self):
        """Parsea una sentencia while"""
        self.consume(TokenType.LPAREN, "Se esperaba '(' después de 'while'")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Se esperaba ')' después de condición")
        
        body = self.statement()
        
        return WhileStatement(condition, body)
    
    def for_statement(self):
        """Parsea una sentencia for"""
        self.consume(TokenType.LPAREN, "Se esperaba '(' después de 'for'")
        
        # Inicialización
        init = None
        if self.match(TokenType.SEMICOLON):
            init = None
        elif self.match(TokenType.VAR):
            init = self.var_declaration()
        else:
            init = self.expression_statement()
        
        # Condición
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Se esperaba ';' después de condición del for")
        
        # Actualización
        update = None
        if not self.check(TokenType.RPAREN):
            update = self.expression()
        self.consume(TokenType.RPAREN, "Se esperaba ')' después de cláusulas del for")
        
        # Cuerpo
        body = self.statement()
        
        return ForStatement(init, condition, update, body)
    
    def return_statement(self):
        """Parsea una sentencia return"""
        value = None
        
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Se esperaba ';' después de return")
        
        return ReturnStatement(value)
    
    def print_statement(self):
        """Parsea una sentencia print"""
        self.consume(TokenType.LPAREN, "Se esperaba '(' después de 'print'")
        expr = self.expression()
        self.consume(TokenType.RPAREN, "Se esperaba ')' después de expresión")
        self.consume(TokenType.SEMICOLON, "Se esperaba ';' después de print")
        
        return PrintStatement(expr)
    
    def block_statement(self):
        """Parsea un bloque de código"""
        statements = []
        
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            statements.append(self.declaration())
        
        self.consume(TokenType.RBRACE, "Se esperaba '}' después del bloque")
        
        return BlockStatement(statements)
    
    def expression_statement(self):
        """Parsea una expresión como sentencia"""
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Se esperaba ';' después de expresión")
        
        return ExpressionStatement(expr)
    
    # ============ EXPRESIONES ============
    
    def expression(self):
        """Parsea una expresión"""
        return self.assignment()
    
    def assignment(self):
        """Parsea una asignación"""
        expr = self.logical_or()
        
        if self.match(TokenType.ASSIGN):
            value = self.assignment()
            
            if isinstance(expr, Identifier):
                return AssignmentExpression(expr.name, value)
            
            raise ParseError("Destino de asignación inválido")
        
        return expr
    
    def logical_or(self):
        """Parsea expresión OR lógica"""
        expr = self.logical_and()
        
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logical_and()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def logical_and(self):
        """Parsea expresión AND lógica"""
        expr = self.equality()
        
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def equality(self):
        """Parsea expresiones de igualdad"""
        expr = self.comparison()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def comparison(self):
        """Parsea expresiones de comparación"""
        expr = self.term()
        
        while self.match(TokenType.GREATER_THAN, TokenType.GREATER_EQUAL,
                          TokenType.LESS_THAN, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def term(self):
        """Parsea expresiones de suma/resta"""
        expr = self.factor()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def factor(self):
        """Parsea expresiones de multiplicación/división"""
        expr = self.unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self.previous()
            right = self.unary()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def unary(self):
        """Parsea expresiones unarias"""
        if self.match(TokenType.NOT, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return UnaryExpression(operator, right)
        
        return self.call()
    
    def call(self):
        """Parsea llamadas a función"""
        expr = self.primary()
        
        while True:
            if self.match(TokenType.LPAREN):
                expr = self.finish_call(expr)
            else:
                break
        
        return expr
    
    def finish_call(self, callee):
        """Completa el parseo de una llamada a función"""
        arguments = []
        
        if not self.check(TokenType.RPAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                arguments.append(self.expression())
        
        self.consume(TokenType.RPAREN, "Se esperaba ')' después de argumentos")
        
        return CallExpression(callee, arguments)
    
    def primary(self):
        """Parsea expresiones primarias"""
        if self.match(TokenType.TRUE):
            return BooleanLiteral(True)
        
        if self.match(TokenType.FALSE):
            return BooleanLiteral(False)
        
        if self.match(TokenType.NUMBER):
            return NumberLiteral(self.previous().value)
        
        if self.match(TokenType.STRING_LITERAL):
            return StringLiteral(self.previous().value)
        
        if self.match(TokenType.IDENTIFIER):
            return Identifier(self.previous().value)
        
        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Se esperaba ')' después de expresión")
            return expr
        
        raise ParseError(f"Expresión inesperada: '{self.peek().value}' "
                        f"en línea {self.peek().line}")

class ParseError(Exception):
    """Excepción para errores de parseo"""
    pass