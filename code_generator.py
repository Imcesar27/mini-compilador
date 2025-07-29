# code_generator.py Generador de código intermedio
from ast_nodes import ASTVisitor
from intermediate_code import IntermediateCode, OpCode
from tokens import TokenType

class CodeGenerator(ASTVisitor):
    """Genera código intermedio a partir del AST"""
    
    def __init__(self):
        self.code = IntermediateCode()
        self.current_function = None
        self.break_labels = []  # Para manejar break en bucles
        self.continue_labels = []  # Para manejar continue en bucles
    
    def generate(self, ast):
        """Genera código intermedio para el AST"""
        ast.accept(self)
        return self.code
    
    # ============ VISITORS ============
    
    def visit_program(self, node):
        """Genera código para el programa completo"""
        # Generar código para todas las declaraciones
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_var_declaration(self, node):
        """Genera código para declaración de variable"""
        if node.initializer:
            # Generar código para el inicializador
            value = node.initializer.accept(self)
            # Asignar el valor a la variable
            self.code.emit(OpCode.ASSIGN, value, None, node.identifier)
        # Si no hay inicializador, no se genera código (la variable existe pero no tiene valor)
    
    def visit_function_declaration(self, node):
        """Genera código para declaración de función"""
        self.current_function = node.name
        
        # Marcar inicio de función
        self.code.emit(OpCode.FUNC_BEGIN, node.name)
        
        # El cuerpo de la función
        node.body.accept(self)
        
        # Si la función no tiene return explícito, añadir uno
        if (not self.code.instructions or 
            self.code.instructions[-1].op != OpCode.RETURN):
            self.code.emit(OpCode.RETURN)
        
        # Marcar fin de función
        self.code.emit(OpCode.FUNC_END, node.name)
        
        self.current_function = None
    
    def visit_block_statement(self, node):
        """Genera código para un bloque"""
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_if_statement(self, node):
        """Genera código para sentencia if"""
        # Evaluar la condición
        condition = node.condition.accept(self)
        
        # Generar etiquetas
        else_label = self.code.new_label()
        end_label = self.code.new_label()
        
        # Saltar a else si la condición es falsa
        self.code.emit_if_false(condition, else_label)
        
        # Código del then
        node.then_branch.accept(self)
        
        # Saltar al final después del then
        self.code.emit_goto(end_label)
        
        # Etiqueta else
        self.code.emit_label(else_label)
        
        # Código del else (si existe)
        if node.else_branch:
            node.else_branch.accept(self)
        
        # Etiqueta final
        self.code.emit_label(end_label)
    
    def visit_while_statement(self, node):
        """Genera código para sentencia while"""
        # Etiquetas
        start_label = self.code.new_label()
        end_label = self.code.new_label()
        
        # Guardar etiquetas para break/continue
        self.break_labels.append(end_label)
        self.continue_labels.append(start_label)
        
        # Etiqueta de inicio
        self.code.emit_label(start_label)
        
        # Evaluar condición
        condition = node.condition.accept(self)
        
        # Salir si es falsa
        self.code.emit_if_false(condition, end_label)
        
        # Cuerpo del bucle
        node.body.accept(self)
        
        # Volver al inicio
        self.code.emit_goto(start_label)
        
        # Etiqueta de fin
        self.code.emit_label(end_label)
        
        # Restaurar etiquetas
        self.break_labels.pop()
        self.continue_labels.pop()
    
    def visit_for_statement(self, node):
        """Genera código para sentencia for"""
        # Inicialización
        if node.init:
            node.init.accept(self)
        
        # Etiquetas
        start_label = self.code.new_label()
        end_label = self.code.new_label()
        continue_label = self.code.new_label()
        
        # Guardar etiquetas
        self.break_labels.append(end_label)
        self.continue_labels.append(continue_label)
        
        # Etiqueta de inicio
        self.code.emit_label(start_label)
        
        # Condición
        if node.condition:
            condition = node.condition.accept(self)
            self.code.emit_if_false(condition, end_label)
        
        # Cuerpo
        node.body.accept(self)
        
        # Etiqueta continue (para actualización)
        self.code.emit_label(continue_label)
        
        # Actualización
        if node.update:
            node.update.accept(self)
        
        # Volver al inicio
        self.code.emit_goto(start_label)
        
        # Etiqueta de fin
        self.code.emit_label(end_label)
        
        # Restaurar etiquetas
        self.break_labels.pop()
        self.continue_labels.pop()
    
    def visit_return_statement(self, node):
        """Genera código para sentencia return"""
        if node.value:
            value = node.value.accept(self)
            self.code.emit(OpCode.RETURN, value)
        else:
            self.code.emit(OpCode.RETURN)
    
    def visit_print_statement(self, node):
        """Genera código para sentencia print"""
        value = node.expression.accept(self)
        self.code.emit(OpCode.PRINT, value)
    
    def visit_expression_statement(self, node):
        """Genera código para expresión como sentencia"""
        node.expression.accept(self)
    
    def visit_binary_expression(self, node):
        """Genera código para expresión binaria"""
        # Generar código para operandos
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        # Crear temporal para resultado
        result = self.code.new_temp()
        
        # Mapear operadores a opcodes
        op_map = {
            TokenType.PLUS: OpCode.ADD,
            TokenType.MINUS: OpCode.SUB,
            TokenType.MULTIPLY: OpCode.MUL,
            TokenType.DIVIDE: OpCode.DIV,
            TokenType.MODULO: OpCode.MOD,
            TokenType.LESS_THAN: OpCode.LT,
            TokenType.GREATER_THAN: OpCode.GT,
            TokenType.LESS_EQUAL: OpCode.LE,
            TokenType.GREATER_EQUAL: OpCode.GE,
            TokenType.EQUAL: OpCode.EQ,
            TokenType.NOT_EQUAL: OpCode.NE,
            TokenType.AND: OpCode.AND,
            TokenType.OR: OpCode.OR,
        }
        
        opcode = op_map.get(node.operator.type)
        if opcode:
            self.code.emit(opcode, left, right, result)
        
        return result
    
    def visit_unary_expression(self, node):
        """Genera código para expresión unaria"""
        operand = node.operand.accept(self)
        result = self.code.new_temp()
        
        if node.operator.type == TokenType.MINUS:
            self.code.emit(OpCode.NEG, operand, None, result)
        elif node.operator.type == TokenType.NOT:
            self.code.emit(OpCode.NOT, operand, None, result)
        
        return result
    
    def visit_assignment_expression(self, node):
        """Genera código para asignación"""
        value = node.value.accept(self)
        self.code.emit(OpCode.ASSIGN, value, None, node.identifier)
        return node.identifier
    
    def visit_call_expression(self, node):
        """Genera código para llamada a función"""
        # Pasar argumentos
        for arg in node.arguments:
            arg_value = arg.accept(self)
            self.code.emit(OpCode.PARAM, arg_value)
        
        # Llamar a la función
        result = self.code.new_temp()
        func_name = node.callee.name if hasattr(node.callee, 'name') else 'unknown'
        self.code.emit(OpCode.CALL, func_name, len(node.arguments), result)
        
        return result
    
    def visit_identifier(self, node):
        """Genera código para identificador"""
        return node.name
    
    def visit_number_literal(self, node):
        """Genera código para literal numérico"""
        return node.value
    
    def visit_string_literal(self, node):
        """Genera código para literal de string"""
        return f'"{node.value}"'
    
    def visit_boolean_literal(self, node):
        """Genera código para literal booleano"""
        return str(node.value).lower()