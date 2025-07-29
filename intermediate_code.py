# intermediate_code.py Generador de código intermedio
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Union, List

class OpCode(Enum):
    """Códigos de operación para instrucciones de tres direcciones"""
    # Operaciones aritméticas
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"
    NEG = "NEG"     # Negación unaria
    
    # Operaciones lógicas
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    # Operaciones de comparación
    LT = "LT"       # Less than
    GT = "GT"       # Greater than
    LE = "LE"       # Less or equal
    GE = "GE"       # Greater or equal
    EQ = "EQ"       # Equal
    NE = "NE"       # Not equal
    
    # Asignación y movimiento
    ASSIGN = "ASSIGN"
    
    # Control de flujo
    GOTO = "GOTO"
    IF_TRUE = "IF_TRUE"    # Salta si verdadero
    IF_FALSE = "IF_FALSE"  # Salta si falso
    
    # Funciones
    CALL = "CALL"
    RETURN = "RETURN"
    PARAM = "PARAM"        # Pasar parámetro
    
    # Entrada/Salida
    PRINT = "PRINT"
    
    # Etiquetas
    LABEL = "LABEL"
    
    # Inicio/Fin de función
    FUNC_BEGIN = "FUNC_BEGIN"
    FUNC_END = "FUNC_END"

@dataclass
class Instruction:
    """Representa una instrucción de código intermedio"""
    op: OpCode
    arg1: Optional[Union[str, int, float]] = None
    arg2: Optional[Union[str, int, float]] = None
    result: Optional[str] = None
    
    def __str__(self):
        if self.op == OpCode.ASSIGN:
            return f"{self.result} = {self.arg1}"
        
        elif self.op in [OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV, OpCode.MOD]:
            return f"{self.result} = {self.arg1} {self.op.value} {self.arg2}"
        
        elif self.op in [OpCode.AND, OpCode.OR]:
            return f"{self.result} = {self.arg1} {self.op.value} {self.arg2}"
        
        elif self.op in [OpCode.LT, OpCode.GT, OpCode.LE, OpCode.GE, OpCode.EQ, OpCode.NE]:
            op_symbols = {
                OpCode.LT: "<", OpCode.GT: ">", OpCode.LE: "<=",
                OpCode.GE: ">=", OpCode.EQ: "==", OpCode.NE: "!="
            }
            return f"{self.result} = {self.arg1} {op_symbols[self.op]} {self.arg2}"
        
        elif self.op == OpCode.NEG:
            return f"{self.result} = -{self.arg1}"
        
        elif self.op == OpCode.NOT:
            return f"{self.result} = !{self.arg1}"
        
        elif self.op == OpCode.GOTO:
            return f"GOTO {self.arg1}"
        
        elif self.op == OpCode.IF_TRUE:
            return f"IF {self.arg1} GOTO {self.arg2}"
        
        elif self.op == OpCode.IF_FALSE:
            return f"IF_FALSE {self.arg1} GOTO {self.arg2}"
        
        elif self.op == OpCode.LABEL:
            return f"{self.arg1}:"
        
        elif self.op == OpCode.CALL:
            if self.result:
                return f"{self.result} = CALL {self.arg1}, {self.arg2}"
            else:
                return f"CALL {self.arg1}, {self.arg2}"
        
        elif self.op == OpCode.RETURN:
            if self.arg1:
                return f"RETURN {self.arg1}"
            else:
                return "RETURN"
        
        elif self.op == OpCode.PARAM:
            return f"PARAM {self.arg1}"
        
        elif self.op == OpCode.PRINT:
            return f"PRINT {self.arg1}"
        
        elif self.op == OpCode.FUNC_BEGIN:
            return f"FUNC_BEGIN {self.arg1}"
        
        elif self.op == OpCode.FUNC_END:
            return f"FUNC_END {self.arg1}"
        
        else:
            return f"{self.op.value} {self.arg1} {self.arg2} {self.result}"

class IntermediateCode:
    """Gestiona el código intermedio generado"""
    def __init__(self):
        self.instructions: List[Instruction] = []
        self.temp_counter = 0
        self.label_counter = 0
    
    def add_instruction(self, instruction: Instruction):
        """Añade una instrucción"""
        self.instructions.append(instruction)
    
    def new_temp(self) -> str:
        """Genera un nuevo temporal"""
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def new_label(self) -> str:
        """Genera una nueva etiqueta"""
        self.label_counter += 1
        return f"L{self.label_counter}"
    
    def emit(self, op: OpCode, arg1=None, arg2=None, result=None):
        """Emite una nueva instrucción"""
        instruction = Instruction(op, arg1, arg2, result)
        self.add_instruction(instruction)
        return instruction
    
    def emit_label(self, label: str):
        """Emite una etiqueta"""
        self.emit(OpCode.LABEL, label)
    
    def emit_goto(self, label: str):
        """Emite un salto incondicional"""
        self.emit(OpCode.GOTO, label)
    
    def emit_if_true(self, condition: str, label: str):
        """Emite un salto condicional si verdadero"""
        self.emit(OpCode.IF_TRUE, condition, label)
    
    def emit_if_false(self, condition: str, label: str):
        """Emite un salto condicional si falso"""
        self.emit(OpCode.IF_FALSE, condition, label)
    
    def print_code(self):
        """Imprime el código intermedio"""
        print("\n=== CÓDIGO INTERMEDIO (Three-Address Code) ===")
        print("-" * 50)
        
        for i, instruction in enumerate(self.instructions):
            # Numeración de líneas para referencia
            line_num = f"{i:3d}:"
            print(f"{line_num} {instruction}")
    
    def get_code(self) -> List[str]:
        """Devuelve el código como lista de strings"""
        return [str(instruction) for instruction in self.instructions]
    
    def optimize(self):
        """Realiza optimizaciones básicas (opcional)"""
        # TODO: Implementar optimizaciones como:
        # - Eliminación de código muerto
        # - Propagación de constantes
        # - Eliminación de subexpresiones comunes
        pass