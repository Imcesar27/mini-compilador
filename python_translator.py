# python_translator.py
from intermediate_code import IntermediateCode, OpCode
from typing import List, Dict

class PythonTranslator:
    """Traduce código intermedio a Python ejecutable"""
    
    def __init__(self):
        self.indent_level = 0
        self.output_lines = []
        self.in_function = False
        self.function_params = {}
        
    def translate(self, intermediate_code: IntermediateCode) -> str:
        """Traduce el código intermedio a Python"""
        self.output_lines = []
        
        # Añadir imports necesarios
        self._add_header()
        
        # Procesar cada instrucción
        i = 0
        while i < len(intermediate_code.instructions):
            instruction = intermediate_code.instructions[i]
            self._translate_instruction(instruction, intermediate_code, i)
            i += 1
        
        return '\n'.join(self.output_lines)
    
    def _add_header(self):
        """Añade el encabezado del programa Python"""
        self.output_lines.append("#!/usr/bin/env python3")
        self.output_lines.append("# Código generado por el compilador")
        self.output_lines.append("")
    
    def _indent(self) -> str:
        """Devuelve la indentación actual"""
        return "    " * self.indent_level
    
    def _add_line(self, line: str):
        """Añade una línea con la indentación correcta"""
        if line.strip():
            self.output_lines.append(self._indent() + line)
        else:
            self.output_lines.append("")
    
    def _translate_instruction(self, instruction, intermediate_code, index):
        """Traduce una instrucción individual"""
        op = instruction.op
        
        if op == OpCode.ASSIGN:
            self._add_line(f"{instruction.result} = {self._format_value(instruction.arg1)}")
        
        elif op in [OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV, OpCode.MOD]:
            operators = {
                OpCode.ADD: "+", OpCode.SUB: "-", OpCode.MUL: "*",
                OpCode.DIV: "/", OpCode.MOD: "%"
            }
            self._add_line(
                f"{instruction.result} = {self._format_value(instruction.arg1)} "
                f"{operators[op]} {self._format_value(instruction.arg2)}"
            )
        
        elif op in [OpCode.LT, OpCode.GT, OpCode.LE, OpCode.GE, OpCode.EQ, OpCode.NE]:
            operators = {
                OpCode.LT: "<", OpCode.GT: ">", OpCode.LE: "<=",
                OpCode.GE: ">=", OpCode.EQ: "==", OpCode.NE: "!="
            }
            self._add_line(
                f"{instruction.result} = {self._format_value(instruction.arg1)} "
                f"{operators[op]} {self._format_value(instruction.arg2)}"
            )
        
        elif op in [OpCode.AND, OpCode.OR]:
            operators = {OpCode.AND: "and", OpCode.OR: "or"}
            self._add_line(
                f"{instruction.result} = {self._format_value(instruction.arg1)} "
                f"{operators[op]} {self._format_value(instruction.arg2)}"
            )
        
        elif op == OpCode.NOT:
            self._add_line(f"{instruction.result} = not {self._format_value(instruction.arg1)}")
        
        elif op == OpCode.NEG:
            self._add_line(f"{instruction.result} = -{self._format_value(instruction.arg1)}")
        
        elif op == OpCode.LABEL:
            # Las etiquetas se manejan implícitamente con la estructura de control
            pass
        
        elif op == OpCode.GOTO:
            # Los GOTOs se manejan con la estructura de control de Python
            pass
        
        elif op == OpCode.IF_TRUE or op == OpCode.IF_FALSE:
            # Buscar el patrón de if-else
            self._translate_if_pattern(instruction, intermediate_code, index)
        
        elif op == OpCode.PRINT:
            self._add_line(f"print({self._format_value(instruction.arg1)})")
        
        elif op == OpCode.FUNC_BEGIN:
            self._translate_function_begin(instruction, intermediate_code, index)
        
        elif op == OpCode.FUNC_END:
            self.indent_level -= 1
            self._add_line("")
            self.in_function = False
        
        elif op == OpCode.RETURN:
            if instruction.arg1:
                self._add_line(f"return {self._format_value(instruction.arg1)}")
            else:
                self._add_line("return")
        
        elif op == OpCode.CALL:
            args_count = instruction.arg2
            # Recolectar los parámetros de las instrucciones PARAM anteriores
            params = []
            j = index - 1
            while j >= 0 and len(params) < args_count:
                if intermediate_code.instructions[j].op == OpCode.PARAM:
                    params.insert(0, self._format_value(intermediate_code.instructions[j].arg1))
                j -= 1
            
            args_str = ", ".join(params)
            if instruction.result:
                self._add_line(f"{instruction.result} = {instruction.arg1}({args_str})")
            else:
                self._add_line(f"{instruction.arg1}({args_str})")
        
        elif op == OpCode.PARAM:
            # Los PARAM se procesan junto con CALL
            pass
    
    def _translate_if_pattern(self, instruction, intermediate_code, index):
        """Traduce el patrón de if-else detectando la estructura"""
        # Buscar el patrón completo del if
        if instruction.op == OpCode.IF_FALSE:
            condition = instruction.arg1
            else_label = instruction.arg2
            
            # Buscar el GOTO antes del else
            goto_end_index = self._find_goto_before_label(intermediate_code, else_label, index)
            
            if goto_end_index >= 0:
                end_label = intermediate_code.instructions[goto_end_index].arg1
                
                # Generar el if
                self._add_line(f"if {self._format_value(condition)}:")
                self.indent_level += 1
                
                # Procesar el bloque then
                self._process_block_until(intermediate_code, index + 1, goto_end_index)
                
                self.indent_level -= 1
                
                # Verificar si hay else
                else_index = self._find_label_index(intermediate_code, else_label)
                end_index = self._find_label_index(intermediate_code, end_label)
                
                if else_index < end_index - 1:  # Hay código en el else
                    self._add_line("else:")
                    self.indent_level += 1
                    self._process_block_until(intermediate_code, else_index + 1, end_index)
                    self.indent_level -= 1
    
    def _translate_function_begin(self, instruction, intermediate_code, index):
        """Traduce el inicio de una función"""
        func_name = instruction.arg1
        
        # Buscar los parámetros de la función
        params = []
        # Los parámetros están definidos en el AST, aquí simplificamos
        
        self._add_line(f"def {func_name}():")
        self.indent_level += 1
        self.in_function = True
    
    def _find_label_index(self, intermediate_code, label):
        """Encuentra el índice de una etiqueta"""
        for i, inst in enumerate(intermediate_code.instructions):
            if inst.op == OpCode.LABEL and inst.arg1 == label:
                return i
        return -1
    
    def _find_goto_before_label(self, intermediate_code, label, start_index):
        """Encuentra un GOTO antes de una etiqueta"""
        label_index = self._find_label_index(intermediate_code, label)
        for i in range(start_index, label_index):
            if intermediate_code.instructions[i].op == OpCode.GOTO:
                return i
        return -1
    
    def _process_block_until(self, intermediate_code, start, end):
        """Procesa un bloque de instrucciones sin traducirlas individualmente"""
        i = start
        while i < end:
            inst = intermediate_code.instructions[i]
            if inst.op not in [OpCode.LABEL, OpCode.GOTO]:
                self._translate_instruction(inst, intermediate_code, i)
            i += 1
    
    def _format_value(self, value):
        """Formatea un valor para Python"""
        if value is None:
            return "None"
        elif isinstance(value, bool):
            return "True" if value else "False"
        elif isinstance(value, str):
            # Si ya tiene comillas, devolverlo tal cual
            if value.startswith('"') and value.endswith('"'):
                return value
            # Si es un temporal o variable, devolverlo sin comillas
            elif value.startswith('t') or value.isidentifier():
                return value
            # Si es true/false en minúsculas, convertir a Python
            elif value == "true":
                return "True"
            elif value == "false":
                return "False"
            else:
                return f'"{value}"'
        else:
            return str(value)
    
    def save_to_file(self, code: str, filename: str):
        """Guarda el código traducido en un archivo"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"\n✓ Código Python guardado en: {filename}")

class SimplifiedPythonTranslator:
    """Versión simplificada del traductor que genera código Python más directo"""
    
    def __init__(self):
        self.code_lines = []
        self.temp_vars = set()
        
    def translate(self, intermediate_code: IntermediateCode) -> str:
        """Traduce el código intermedio a Python de forma simplificada"""
        self.code_lines = []
        self.code_lines.append("#!/usr/bin/env python3")
        self.code_lines.append("# Código generado automáticamente")
        self.code_lines.append("")
        
        # Declarar variables temporales al inicio
        for inst in intermediate_code.instructions:
            if inst.result and inst.result.startswith('t'):
                self.temp_vars.add(inst.result)
        
        if self.temp_vars:
            self.code_lines.append("# Variables temporales")
            for temp in sorted(self.temp_vars):
                self.code_lines.append(f"{temp} = None")
            self.code_lines.append("")
        
        # Traducir instrucciones directamente
        self.code_lines.append("# Código principal")
        for inst in intermediate_code.instructions:
            line = self._translate_simple(inst)
            if line:
                self.code_lines.append(line)
        
        return '\n'.join(self.code_lines)
    
    def _translate_simple(self, inst):
        """Traduce una instrucción de forma simple"""
        op = inst.op
        
        if op == OpCode.ASSIGN:
            return f"{inst.result} = {inst.arg1}"
        
        elif op in [OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV, OpCode.MOD]:
            ops = {OpCode.ADD: "+", OpCode.SUB: "-", OpCode.MUL: "*", 
                   OpCode.DIV: "/", OpCode.MOD: "%"}
            return f"{inst.result} = {inst.arg1} {ops[op]} {inst.arg2}"
        
        elif op in [OpCode.LT, OpCode.GT, OpCode.LE, OpCode.GE, OpCode.EQ, OpCode.NE]:
            ops = {OpCode.LT: "<", OpCode.GT: ">", OpCode.LE: "<=",
                   OpCode.GE: ">=", OpCode.EQ: "==", OpCode.NE: "!="}
            return f"{inst.result} = {inst.arg1} {ops[op]} {inst.arg2}"
        
        elif op == OpCode.PRINT:
            return f"print({inst.arg1})"
        
        elif op == OpCode.LABEL:
            return f"# {inst.arg1}:"
        
        elif op == OpCode.GOTO:
            return f"# goto {inst.arg1}"
        
        elif op == OpCode.IF_FALSE:
            return f"# if not {inst.arg1}: goto {inst.arg2}"
        
        elif op == OpCode.FUNC_BEGIN:
            return f"\n# Función {inst.arg1}"
        
        elif op == OpCode.FUNC_END:
            return f"# Fin de {inst.arg1}\n"
        
        elif op == OpCode.RETURN:
            if inst.arg1:
                return f"# return {inst.arg1}"
            else:
                return "# return"
        
        return None