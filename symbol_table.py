# symbol_table.py
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

class SymbolType(Enum):
    """Tipos de símbolos en la tabla"""
    VARIABLE = auto()
    CONSTANT = auto()
    FUNCTION = auto()
    PARAMETER = auto()

class DataType(Enum):
    """Tipos de datos"""
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    VOID = "void"
    UNKNOWN = "unknown"

@dataclass
class Symbol:
    """Representa un símbolo en la tabla"""
    name: str
    symbol_type: SymbolType
    data_type: DataType
    scope: int
    line: int
    column: int
    value: Any = None
    is_initialized: bool = False
    parameters: Optional[List[str]] = None  # Para funciones

class Scope:
    """Representa un ámbito (scope)"""
    def __init__(self, level: int, parent=None):
        self.level = level
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.children: List[Scope] = []
    
    def add_symbol(self, symbol: Symbol):
        """Agrega un símbolo al ámbito actual"""
        if symbol.name in self.symbols:
            raise SymbolTableError(f"Símbolo '{symbol.name}' ya está declarado en este ámbito")
        self.symbols[symbol.name] = symbol
    
    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Busca un símbolo solo en el ámbito local"""
        return self.symbols.get(name)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Busca un símbolo en este ámbito y sus padres"""
        symbol = self.lookup_local(name)
        if symbol:
            return symbol
        if self.parent:
            return self.parent.lookup(name)
        return None

class SymbolTable:
    """Tabla de símbolos principal"""
    def __init__(self):
        self.global_scope = Scope(0)
        self.current_scope = self.global_scope
        self.scope_counter = 0
        self.all_symbols: List[Symbol] = []
    
    def enter_scope(self):
        """Entra a un nuevo ámbito"""
        self.scope_counter += 1
        new_scope = Scope(self.scope_counter, self.current_scope)
        self.current_scope.children.append(new_scope)
        self.current_scope = new_scope
        return new_scope
    
    def exit_scope(self):
        """Sale del ámbito actual"""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
        else:
            raise SymbolTableError("No se puede salir del ámbito global")
    
    def declare_variable(self, name: str, data_type: DataType, symbol_type: SymbolType, 
                        line: int, column: int, value=None):
        """Declara una nueva variable o constante"""
        symbol = Symbol(
            name=name,
            symbol_type=symbol_type,
            data_type=data_type,
            scope=self.current_scope.level,
            line=line,
            column=column,
            value=value,
            is_initialized=(value is not None)
        )
        self.current_scope.add_symbol(symbol)
        self.all_symbols.append(symbol)
        return symbol
    
    def declare_function(self, name: str, return_type: DataType, parameters: List[str],
                        line: int, column: int):
        """Declara una nueva función"""
        symbol = Symbol(
            name=name,
            symbol_type=SymbolType.FUNCTION,
            data_type=return_type,
            scope=self.current_scope.level,
            line=line,
            column=column,
            parameters=parameters
        )
        self.current_scope.add_symbol(symbol)
        self.all_symbols.append(symbol)
        return symbol
    
    def declare_parameter(self, name: str, data_type: DataType, line: int, column: int):
        """Declara un parámetro de función"""
        symbol = Symbol(
            name=name,
            symbol_type=SymbolType.PARAMETER,
            data_type=data_type,
            scope=self.current_scope.level,
            line=line,
            column=column,
            is_initialized=True
        )
        self.current_scope.add_symbol(symbol)
        self.all_symbols.append(symbol)
        return symbol
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Busca un símbolo en la tabla"""
        return self.current_scope.lookup(name)
    
    def update_symbol_value(self, name: str, value: Any):
        """Actualiza el valor de un símbolo"""
        symbol = self.lookup(name)
        if not symbol:
            raise SymbolTableError(f"Variable '{name}' no declarada")
        if symbol.symbol_type == SymbolType.CONSTANT:
            raise SymbolTableError(f"No se puede modificar la constante '{name}'")
        symbol.value = value
        symbol.is_initialized = True
    
    def print_table(self):
        """Imprime la tabla de símbolos de forma legible"""
        print("\n=== TABLA DE SÍMBOLOS ===")
        print(f"{'Nombre':<15} {'Tipo':<10} {'Tipo Dato':<10} {'Ámbito':<8} {'Línea':<6} {'Valor':<15} {'Inicializado':<12}")
        print("-" * 100)
        
        for symbol in self.all_symbols:
            tipo = symbol.symbol_type.name
            tipo_dato = symbol.data_type.value
            valor = str(symbol.value) if symbol.value is not None else "None"
            init = "Sí" if symbol.is_initialized else "No"
            
            print(f"{symbol.name:<15} {tipo:<10} {tipo_dato:<10} {symbol.scope:<8} {symbol.line:<6} {valor:<15} {init:<12}")
            
            if symbol.symbol_type == SymbolType.FUNCTION and symbol.parameters:
                print(f"  └─ Parámetros: {', '.join(symbol.parameters)}")
    
    def print_scope_tree(self):
        """Imprime el árbol de ámbitos"""
        print("\n=== ÁRBOL DE ÁMBITOS ===")
        self._print_scope_recursive(self.global_scope, 0)
    
    def _print_scope_recursive(self, scope: Scope, indent: int):
        """Imprime recursivamente los ámbitos"""
        indent_str = "  " * indent
        print(f"{indent_str}Ámbito {scope.level}:")
        for name, symbol in scope.symbols.items():
            print(f"{indent_str}  - {name} ({symbol.symbol_type.name})")
        
        for child in scope.children:
            self._print_scope_recursive(child, indent + 1)

class SymbolTableError(Exception):
    """Excepción para errores en la tabla de símbolos"""
    pass

# Función auxiliar para inferir tipo de dato desde un literal
def infer_data_type(value) -> DataType:
    """Infiere el tipo de dato desde un valor"""
    if isinstance(value, bool):
        return DataType.BOOLEAN
    elif isinstance(value, int):
        return DataType.INT
    elif isinstance(value, float):
        return DataType.FLOAT
    elif isinstance(value, str):
        return DataType.STRING
    else:
        return DataType.UNKNOWN