# ast_printer.py
from ast_nodes import ASTVisitor

class ASTPrinter(ASTVisitor):
    """Imprime el AST en formato de árbol"""
    
    def __init__(self):
        self.indent_level = 0
        self.indent_string = "  "
    
    def indent(self):
        """Devuelve la indentación actual"""
        return self.indent_string * self.indent_level
    
    def print_ast(self, node):
        """Punto de entrada para imprimir el AST"""
        return node.accept(self)
    
    # ============ IMPLEMENTACIÓN DE VISITORS ============
    
    def visit_program(self, node):
        print(f"{self.indent()}Program")
        self.indent_level += 1
        for stmt in node.statements:
            stmt.accept(self)
        self.indent_level -= 1
    
    def visit_var_declaration(self, node):
        print(f"{self.indent()}VarDeclaration")
        self.indent_level += 1
        print(f"{self.indent()}type: {node.var_type}")
        print(f"{self.indent()}name: {node.identifier}")
        if node.initializer:
            print(f"{self.indent()}initializer:")
            self.indent_level += 1
            node.initializer.accept(self)
            self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_function_declaration(self, node):
        print(f"{self.indent()}FunctionDeclaration")
        self.indent_level += 1
        print(f"{self.indent()}name: {node.name}")
        print(f"{self.indent()}params: {node.params}")
        print(f"{self.indent()}body:")
        self.indent_level += 1
        node.body.accept(self)
        self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_block_statement(self, node):
        print(f"{self.indent()}BlockStatement")
        self.indent_level += 1
        for stmt in node.statements:
            stmt.accept(self)
        self.indent_level -= 1
    
    def visit_if_statement(self, node):
        print(f"{self.indent()}IfStatement")
        self.indent_level += 1
        print(f"{self.indent()}condition:")
        self.indent_level += 1
        node.condition.accept(self)
        self.indent_level -= 1
        print(f"{self.indent()}then:")
        self.indent_level += 1
        node.then_branch.accept(self)
        self.indent_level -= 1
        if node.else_branch:
            print(f"{self.indent()}else:")
            self.indent_level += 1
            node.else_branch.accept(self)
            self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_while_statement(self, node):
        print(f"{self.indent()}WhileStatement")
        self.indent_level += 1
        print(f"{self.indent()}condition:")
        self.indent_level += 1
        node.condition.accept(self)
        self.indent_level -= 1
        print(f"{self.indent()}body:")
        self.indent_level += 1
        node.body.accept(self)
        self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_for_statement(self, node):
        print(f"{self.indent()}ForStatement")
        self.indent_level += 1
        if node.init:
            print(f"{self.indent()}init:")
            self.indent_level += 1
            node.init.accept(self)
            self.indent_level -= 1
        if node.condition:
            print(f"{self.indent()}condition:")
            self.indent_level += 1
            node.condition.accept(self)
            self.indent_level -= 1
        if node.update:
            print(f"{self.indent()}update:")
            self.indent_level += 1
            node.update.accept(self)
            self.indent_level -= 1
        print(f"{self.indent()}body:")
        self.indent_level += 1
        node.body.accept(self)
        self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_return_statement(self, node):
        print(f"{self.indent()}ReturnStatement")
        if node.value:
            self.indent_level += 1
            node.value.accept(self)
            self.indent_level -= 1
    
    def visit_print_statement(self, node):
        print(f"{self.indent()}PrintStatement")
        self.indent_level += 1
        node.expression.accept(self)
        self.indent_level -= 1
    
    def visit_expression_statement(self, node):
        print(f"{self.indent()}ExpressionStatement")
        self.indent_level += 1
        node.expression.accept(self)
        self.indent_level -= 1
    
    def visit_binary_expression(self, node):
        print(f"{self.indent()}BinaryExpression")
        self.indent_level += 1
        print(f"{self.indent()}operator: {node.operator.value}")
        print(f"{self.indent()}left:")
        self.indent_level += 1
        node.left.accept(self)
        self.indent_level -= 1
        print(f"{self.indent()}right:")
        self.indent_level += 1
        node.right.accept(self)
        self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_unary_expression(self, node):
        print(f"{self.indent()}UnaryExpression")
        self.indent_level += 1
        print(f"{self.indent()}operator: {node.operator.value}")
        print(f"{self.indent()}operand:")
        self.indent_level += 1
        node.operand.accept(self)
        self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_assignment_expression(self, node):
        print(f"{self.indent()}AssignmentExpression")
        self.indent_level += 1
        print(f"{self.indent()}identifier: {node.identifier}")
        print(f"{self.indent()}value:")
        self.indent_level += 1
        node.value.accept(self)
        self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_call_expression(self, node):
        print(f"{self.indent()}CallExpression")
        self.indent_level += 1
        print(f"{self.indent()}callee:")
        self.indent_level += 1
        node.callee.accept(self)
        self.indent_level -= 1
        print(f"{self.indent()}arguments:")
        self.indent_level += 1
        for arg in node.arguments:
            arg.accept(self)
        self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_identifier(self, node):
        print(f"{self.indent()}Identifier: {node.name}")
    
    def visit_number_literal(self, node):
        print(f"{self.indent()}Number: {node.value}")
    
    def visit_string_literal(self, node):
        print(f"{self.indent()}String: \"{node.value}\"")
    
    def visit_boolean_literal(self, node):
        print(f"{self.indent()}Boolean: {node.value}")