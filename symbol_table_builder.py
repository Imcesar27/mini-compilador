# symbol_table_builder.py
from ast_nodes import ASTVisitor
from symbol_table import SymbolTable, SymbolType, DataType, SymbolTableError, infer_data_type

class SymbolTableBuilder(ASTVisitor):
    """Construye la tabla de símbolos a partir del AST"""
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.current_function = None
    
    def build(self, ast):
        """Construye la tabla de símbolos"""
        try:
            ast.accept(self)
        except SymbolTableError as e:
            self.errors.append(str(e))
        return self.symbol_table
    
    # ============ VISITORS ============
    
    def visit_program(self, node):
        """Visita el nodo programa"""
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_var_declaration(self, node):
        """Procesa declaración de variable"""
        # Inferir tipo de dato si hay inicializador
        data_type = DataType.UNKNOWN
        value = None
        
        if node.initializer:
            # Evaluar el inicializador
            value = self._evaluate_expression(node.initializer)
            if value is not None:
                data_type = infer_data_type(value)
        
        # Determinar si es variable o constante
        symbol_type = SymbolType.CONSTANT if node.var_type == 'const' else SymbolType.VARIABLE
        
        try:
            self.symbol_table.declare_variable(
                name=node.identifier,
                data_type=data_type,
                symbol_type=symbol_type,
                line=1,  # TODO: Agregar info de línea al AST
                column=1,
                value=value
            )
        except SymbolTableError as e:
            self.errors.append(str(e))
    
    def visit_function_declaration(self, node):
        """Procesa declaración de función"""
        try:
            # Declarar la función en el ámbito actual
            self.symbol_table.declare_function(
                name=node.name,
                return_type=DataType.UNKNOWN,  # TODO: Agregar tipos de retorno
                parameters=node.params,
                line=1,
                column=1
            )
            
            # Entrar a un nuevo ámbito para el cuerpo de la función
            self.symbol_table.enter_scope()
            self.current_function = node.name
            
            # Declarar los parámetros
            for param in node.params:
                self.symbol_table.declare_parameter(
                    name=param,
                    data_type=DataType.UNKNOWN,
                    line=1,
                    column=1
                )
            
            # Procesar el cuerpo
            node.body.accept(self)
            
            # Salir del ámbito
            self.symbol_table.exit_scope()
            self.current_function = None
            
        except SymbolTableError as e:
            self.errors.append(str(e))
    
    def visit_block_statement(self, node):
        """Procesa un bloque de código"""
        # Entrar a un nuevo ámbito
        self.symbol_table.enter_scope()
        
        # Procesar las sentencias
        for stmt in node.statements:
            stmt.accept(self)
        
        # Salir del ámbito
        self.symbol_table.exit_scope()
    
    def visit_if_statement(self, node):
        """Procesa sentencia if"""
        # Verificar la condición
        node.condition.accept(self)
        
        # Procesar el then (sin crear nuevo ámbito si no es un bloque)
        if hasattr(node.then_branch, '__class__') and node.then_branch.__class__.__name__ != 'BlockStatement':
            self.symbol_table.enter_scope()
            node.then_branch.accept(self)
            self.symbol_table.exit_scope()
        else:
            node.then_branch.accept(self)
        
        # Procesar el else si existe
        if node.else_branch:
            if hasattr(node.else_branch, '__class__') and node.else_branch.__class__.__name__ != 'BlockStatement':
                self.symbol_table.enter_scope()
                node.else_branch.accept(self)
                self.symbol_table.exit_scope()
            else:
                node.else_branch.accept(self)
    
    def visit_while_statement(self, node):
        """Procesa sentencia while"""
        node.condition.accept(self)
        
        if hasattr(node.body, '__class__') and node.body.__class__.__name__ != 'BlockStatement':
            self.symbol_table.enter_scope()
            node.body.accept(self)
            self.symbol_table.exit_scope()
        else:
            node.body.accept(self)
    
    def visit_for_statement(self, node):
        """Procesa sentencia for"""
        # El for crea su propio ámbito
        self.symbol_table.enter_scope()
        
        if node.init:
            node.init.accept(self)
        if node.condition:
            node.condition.accept(self)
        if node.update:
            node.update.accept(self)
        
        # Procesar el cuerpo
        if hasattr(node.body, '__class__') and node.body.__class__.__name__ != 'BlockStatement':
            self.symbol_table.enter_scope()
            node.body.accept(self)
            self.symbol_table.exit_scope()
        else:
            node.body.accept(self)
        
        self.symbol_table.exit_scope()
    
    def visit_return_statement(self, node):
        """Procesa sentencia return"""
        if node.value:
            node.value.accept(self)
    
    def visit_print_statement(self, node):
        """Procesa sentencia print"""
        node.expression.accept(self)
    
    def visit_expression_statement(self, node):
        """Procesa expresión como sentencia"""
        node.expression.accept(self)
    
    def visit_binary_expression(self, node):
        """Procesa expresión binaria"""
        node.left.accept(self)
        node.right.accept(self)
    
    def visit_unary_expression(self, node):
        """Procesa expresión unaria"""
        node.operand.accept(self)
    
    def visit_assignment_expression(self, node):
        """Procesa asignación"""
        # Verificar que la variable existe
        symbol = self.symbol_table.lookup(node.identifier)
        if not symbol:
            self.errors.append(f"Variable '{node.identifier}' no declarada")
        else:
            # Evaluar el valor y actualizar
            value = self._evaluate_expression(node.value)
            if symbol.symbol_type == SymbolType.CONSTANT:
                self.errors.append(f"No se puede modificar la constante '{node.identifier}'")
            else:
                try:
                    self.symbol_table.update_symbol_value(node.identifier, value)
                except SymbolTableError as e:
                    self.errors.append(str(e))
        
        node.value.accept(self)
    
    def visit_call_expression(self, node):
        """Procesa llamada a función"""
        # Verificar que la función existe
        if hasattr(node.callee, 'name'):
            func_name = node.callee.name
            symbol = self.symbol_table.lookup(func_name)
            if not symbol:
                self.errors.append(f"Función '{func_name}' no declarada")
            elif symbol.symbol_type != SymbolType.FUNCTION:
                self.errors.append(f"'{func_name}' no es una función")
        
        node.callee.accept(self)
        for arg in node.arguments:
            arg.accept(self)
    
    def visit_identifier(self, node):
        """Procesa identificador"""
        # Verificar que el identificador existe
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            self.errors.append(f"Identificador '{node.name}' no declarado")
    
    def visit_number_literal(self, node):
        """Procesa literal numérico"""
        pass
    
    def visit_string_literal(self, node):
        """Procesa literal de string"""
        pass
    
    def visit_boolean_literal(self, node):
        """Procesa literal booleano"""
        pass
    
    # ============ UTILIDADES ============
    
    def _evaluate_expression(self, expr):
        """Intenta evaluar una expresión simple para obtener su valor"""
        # Para literales, devolver el valor directamente
        if hasattr(expr, '__class__'):
            class_name = expr.__class__.__name__
            
            if class_name == 'NumberLiteral':
                return expr.value
            elif class_name == 'StringLiteral':
                return expr.value
            elif class_name == 'BooleanLiteral':
                return expr.value
            elif class_name == 'Identifier':
                # Buscar el valor de la variable
                symbol = self.symbol_table.lookup(expr.name)
                if symbol and symbol.is_initialized:
                    return symbol.value
        
        # Para expresiones más complejas, devolver None por ahora
        return None