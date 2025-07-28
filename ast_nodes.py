# ast_nodes.py
from abc import ABC, abstractmethod

class ASTNode(ABC):
    """Clase base para todos los nodos del AST"""
    @abstractmethod
    def accept(self, visitor):
        pass

# ============ DECLARACIONES ============

class Program(ASTNode):
    """Nodo raíz del programa"""
    def __init__(self, statements):
        self.statements = statements
    
    def accept(self, visitor):
        return visitor.visit_program(self)

class VarDeclaration(ASTNode):
    """Declaración de variable: var x = 10;"""
    def __init__(self, var_type, identifier, initializer=None):
        self.var_type = var_type  # 'var' o 'const'
        self.identifier = identifier
        self.initializer = initializer
    
    def accept(self, visitor):
        return visitor.visit_var_declaration(self)

class FunctionDeclaration(ASTNode):
    """Declaración de función"""
    def __init__(self, name, params, body):
        self.name = name
        self.params = params  # Lista de parámetros
        self.body = body      # BlockStatement
    
    def accept(self, visitor):
        return visitor.visit_function_declaration(self)

# ============ SENTENCIAS ============

class BlockStatement(ASTNode):
    """Bloque de código: { ... }"""
    def __init__(self, statements):
        self.statements = statements
    
    def accept(self, visitor):
        return visitor.visit_block_statement(self)

class IfStatement(ASTNode):
    """Sentencia if-else"""
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    
    def accept(self, visitor):
        return visitor.visit_if_statement(self)

class WhileStatement(ASTNode):
    """Sentencia while"""
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_while_statement(self)

class ForStatement(ASTNode):
    """Sentencia for"""
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_for_statement(self)

class ReturnStatement(ASTNode):
    """Sentencia return"""
    def __init__(self, value=None):
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_return_statement(self)

class PrintStatement(ASTNode):
    """Sentencia print"""
    def __init__(self, expression):
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_print_statement(self)

class ExpressionStatement(ASTNode):
    """Una expresión usada como sentencia"""
    def __init__(self, expression):
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_expression_statement(self)

# ============ EXPRESIONES ============

class BinaryExpression(ASTNode):
    """Expresión binaria: a + b, a < b, etc."""
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_binary_expression(self)

class UnaryExpression(ASTNode):
    """Expresión unaria: -x, !x"""
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand
    
    def accept(self, visitor):
        return visitor.visit_unary_expression(self)

class AssignmentExpression(ASTNode):
    """Expresión de asignación: x = 10"""
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_assignment_expression(self)

class CallExpression(ASTNode):
    """Llamada a función: suma(a, b)"""
    def __init__(self, callee, arguments):
        self.callee = callee
        self.arguments = arguments
    
    def accept(self, visitor):
        return visitor.visit_call_expression(self)

class Identifier(ASTNode):
    """Identificador: x, suma, etc."""
    def __init__(self, name):
        self.name = name
    
    def accept(self, visitor):
        return visitor.visit_identifier(self)

class NumberLiteral(ASTNode):
    """Literal numérico: 10, 3.14"""
    def __init__(self, value):
        self.value = float(value) if '.' in value else int(value)
    
    def accept(self, visitor):
        return visitor.visit_number_literal(self)

class StringLiteral(ASTNode):
    """Literal de string: "Hola"""
    def __init__(self, value):
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_string_literal(self)

class BooleanLiteral(ASTNode):
    """Literal booleano: true, false"""
    def __init__(self, value):
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_boolean_literal(self)

# ============ VISITOR BASE ============

class ASTVisitor(ABC):
    """Clase base para el patrón visitor"""
    @abstractmethod
    def visit_program(self, node): pass
    
    @abstractmethod
    def visit_var_declaration(self, node): pass
    
    @abstractmethod
    def visit_function_declaration(self, node): pass
    
    @abstractmethod
    def visit_block_statement(self, node): pass
    
    @abstractmethod
    def visit_if_statement(self, node): pass
    
    @abstractmethod
    def visit_while_statement(self, node): pass
    
    @abstractmethod
    def visit_for_statement(self, node): pass
    
    @abstractmethod
    def visit_return_statement(self, node): pass
    
    @abstractmethod
    def visit_print_statement(self, node): pass
    
    @abstractmethod
    def visit_expression_statement(self, node): pass
    
    @abstractmethod
    def visit_binary_expression(self, node): pass
    
    @abstractmethod
    def visit_unary_expression(self, node): pass
    
    @abstractmethod
    def visit_assignment_expression(self, node): pass
    
    @abstractmethod
    def visit_call_expression(self, node): pass
    
    @abstractmethod
    def visit_identifier(self, node): pass
    
    @abstractmethod
    def visit_number_literal(self, node): pass
    
    @abstractmethod
    def visit_string_literal(self, node): pass
    
    @abstractmethod
    def visit_boolean_literal(self, node): pass