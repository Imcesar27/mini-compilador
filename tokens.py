# tokens.py
from enum import Enum, auto

class TokenType(Enum):
    # Palabras reservadas
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    FUNCTION = auto()
    RETURN = auto()
    VAR = auto()
    CONST = auto()
    PRINT = auto()
    
    # Tipos de datos
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOLEAN = auto()
    
    # Literales
    NUMBER = auto()
    STRING_LITERAL = auto()
    TRUE = auto()
    FALSE = auto()
    
    # Identificadores
    IDENTIFIER = auto()
    
    # Operadores aritméticos
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    
    # Operadores de comparación
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    
    # Operadores lógicos
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Operadores de asignación
    ASSIGN = auto()
    
    # Delimitadores
    SEMICOLON = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()
    
    # Paréntesis y llaves
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    
    # Otros
    EOF = auto()
    NEWLINE = auto()
    COMMENT = auto()

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}, {self.column})"
    
    def __str__(self):
        return f"{self.type.name}: '{self.value}' at ({self.line}, {self.column})"

# Palabras reservadas
KEYWORDS = {
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'for': TokenType.FOR,
    'function': TokenType.FUNCTION,
    'return': TokenType.RETURN,
    'var': TokenType.VAR,
    'const': TokenType.CONST,
    'print': TokenType.PRINT,
    'int': TokenType.INT,
    'float': TokenType.FLOAT,
    'string': TokenType.STRING,
    'boolean': TokenType.BOOLEAN,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE
}