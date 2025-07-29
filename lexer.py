# lexer.py Lector de tokens
from tokens import Token, TokenType, KEYWORDS

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
    
    def current_char(self):
        """Obtiene el carácter actual"""
        if self.position >= len(self.source_code):
            return None
        return self.source_code[self.position]
    
    def peek_char(self, offset=1):
        """Mira el siguiente carácter sin avanzar"""
        pos = self.position + offset
        if pos >= len(self.source_code):
            return None
        return self.source_code[pos]
    
    def advance(self):
        """Avanza al siguiente carácter"""
        if self.position < len(self.source_code):
            if self.source_code[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def skip_whitespace(self):
        """Salta espacios en blanco y tabulaciones"""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        """Salta comentarios de una línea //"""
        if self.current_char() == '/' and self.peek_char() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_number(self):
        """Lee un número (entero o decimal)"""
        start_column = self.column
        number_str = ''
        has_dot = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_dot:
                    break  # Ya tiene un punto, no puede tener otro
                has_dot = True
            number_str += self.current_char()
            self.advance()
        
        return Token(TokenType.NUMBER, number_str, self.line, start_column)
    
    def read_string(self):
        """Lee una cadena de texto entre comillas"""
        start_column = self.column
        quote_char = self.current_char()  # Puede ser ' o "
        self.advance()  # Salta la comilla inicial
        
        string_value = ''
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':  # Manejo de escapes
                self.advance()
                if self.current_char() == 'n':
                    string_value += '\n'
                elif self.current_char() == 't':
                    string_value += '\t'
                elif self.current_char() == '\\':
                    string_value += '\\'
                elif self.current_char() == quote_char:
                    string_value += quote_char
                else:
                    string_value += self.current_char()
            else:
                string_value += self.current_char()
            self.advance()
        
        if self.current_char() == quote_char:
            self.advance()  # Salta la comilla final
        else:
            raise Exception(f"String sin cerrar en línea {self.line}")
        
        return Token(TokenType.STRING_LITERAL, string_value, self.line, start_column)
    
    def read_identifier(self):
        """Lee un identificador o palabra reservada"""
        start_column = self.column
        identifier = ''
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            identifier += self.current_char()
            self.advance()
        
        # Verifica si es una palabra reservada
        token_type = KEYWORDS.get(identifier.lower(), TokenType.IDENTIFIER)
        return Token(token_type, identifier, self.line, start_column)
    
    def tokenize(self):
        """Convierte el código fuente en una lista de tokens"""
        while self.position < len(self.source_code):
            self.skip_whitespace()
            
            if self.current_char() is None:
                break
            
            # Comentarios
            if self.current_char() == '/' and self.peek_char() == '/':
                self.skip_comment()
                continue
            
            # Nueva línea
            if self.current_char() == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\\n', self.line, self.column))
                self.advance()
                continue
            
            # Números
            if self.current_char().isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Strings
            if self.current_char() in '"\'':
                self.tokens.append(self.read_string())
                continue
            
            # Identificadores y palabras reservadas
            if self.current_char().isalpha() or self.current_char() == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Operadores y símbolos
            char = self.current_char()
            start_column = self.column
            
            # Operadores de dos caracteres
            if char == '=' and self.peek_char() == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.EQUAL, '==', self.line, start_column))
            elif char == '!' and self.peek_char() == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.NOT_EQUAL, '!=', self.line, start_column))
            elif char == '<' and self.peek_char() == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', self.line, start_column))
            elif char == '>' and self.peek_char() == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', self.line, start_column))
            elif char == '&' and self.peek_char() == '&':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.AND, '&&', self.line, start_column))
            elif char == '|' and self.peek_char() == '|':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.OR, '||', self.line, start_column))
            
            # Operadores de un carácter
            elif char == '+':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS, '+', self.line, start_column))
            elif char == '-':
                self.advance()
                self.tokens.append(Token(TokenType.MINUS, '-', self.line, start_column))
            elif char == '*':
                self.advance()
                self.tokens.append(Token(TokenType.MULTIPLY, '*', self.line, start_column))
            elif char == '/':
                self.advance()
                self.tokens.append(Token(TokenType.DIVIDE, '/', self.line, start_column))
            elif char == '%':
                self.advance()
                self.tokens.append(Token(TokenType.MODULO, '%', self.line, start_column))
            elif char == '=':
                self.advance()
                self.tokens.append(Token(TokenType.ASSIGN, '=', self.line, start_column))
            elif char == '<':
                self.advance()
                self.tokens.append(Token(TokenType.LESS_THAN, '<', self.line, start_column))
            elif char == '>':
                self.advance()
                self.tokens.append(Token(TokenType.GREATER_THAN, '>', self.line, start_column))
            elif char == '!':
                self.advance()
                self.tokens.append(Token(TokenType.NOT, '!', self.line, start_column))
            
            # Delimitadores
            elif char == ';':
                self.advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ';', self.line, start_column))
            elif char == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ',', self.line, start_column))
            elif char == '.':
                self.advance()
                self.tokens.append(Token(TokenType.DOT, '.', self.line, start_column))
            elif char == ':':
                self.advance()
                self.tokens.append(Token(TokenType.COLON, ':', self.line, start_column))
            
            # Paréntesis y llaves
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', self.line, start_column))
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', self.line, start_column))
            elif char == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, '{', self.line, start_column))
            elif char == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, '}', self.line, start_column))
            elif char == '[':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACKET, '[', self.line, start_column))
            elif char == ']':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, ']', self.line, start_column))
            
            else:
                raise Exception(f"Carácter inesperado '{char}' en línea {self.line}, columna {self.column}")
        
        # Añade token EOF al final
        self.tokens.append(Token(TokenType.EOF, 'EOF', self.line, self.column))
        return self.tokens