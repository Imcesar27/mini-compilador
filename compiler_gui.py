# compiler_gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
from lexer import Lexer
from parser import Parser
from ast_printer import ASTPrinter
from symbol_table_builder import SymbolTableBuilder
from code_generator import CodeGenerator
from python_translator import SimplifiedPythonTranslator
import subprocess
import sys

class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Compilador - Python")
        self.root.geometry("1400x800")
        
        # Colores personalizados
        self.colors = {
            'bg_dark': '#1a1a1a',
            'bg_medium': '#2d2d2d',
            'bg_light': '#3d3d3d',
            'purple': '#9d4edd',
            'purple_dark': '#7b2cbf',
            'purple_light': '#c77dff',
            'gray': '#808080',
            'white': '#ffffff',
            'green': '#00ff00',
            'red': '#ff4444',
            'yellow': '#ffff00'
        }
        
        # Configurar estilo
        self.setup_styles()
        
        # Configurar la ventana principal
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Crear la interfaz
        self.create_widgets()
        
        # Variables para almacenar resultados
        self.current_tokens = []
        self.current_ast = None
        self.current_symbol_table = None
        self.current_intermediate_code = None
        
    def setup_styles(self):
        """Configura los estilos personalizados"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores para los widgets ttk
        style.configure('Purple.TButton',
                       background=self.colors['purple'],
                       foreground=self.colors['white'],
                       borderwidth=0,
                       focuscolor='none',
                       font=('Arial', 10, 'bold'))
        style.map('Purple.TButton',
                 background=[('active', self.colors['purple_light'])])
        
        style.configure('Dark.TFrame',
                       background=self.colors['bg_dark'])
        
        style.configure('Dark.TLabel',
                       background=self.colors['bg_dark'],
                       foreground=self.colors['white'],
                       font=('Arial', 10))
        
        style.configure('Title.TLabel',
                       background=self.colors['bg_dark'],
                       foreground=self.colors['purple_light'],
                       font=('Arial', 12, 'bold'))
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel superior con botones
        self.create_button_panel(main_frame)
        
        # Panel central con pestañas
        self.create_tabbed_panel(main_frame)
        
        # Panel inferior con estado
        self.create_status_panel(main_frame)
    
    def create_button_panel(self, parent):
        """Crea el panel de botones"""
        button_frame = ttk.Frame(parent, style='Dark.TFrame')
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones de archivo
        ttk.Button(button_frame, text="📁 Abrir", 
                  command=self.open_file,
                  style='Purple.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="💾 Guardar", 
                  command=self.save_file,
                  style='Purple.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="🆕 Nuevo", 
                  command=self.new_file,
                  style='Purple.TButton').pack(side=tk.LEFT, padx=5)
        
        # Separador
        ttk.Separator(button_frame, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Botones de compilación
        ttk.Button(button_frame, text="▶️ Compilar", 
                  command=self.compile_code,
                  style='Purple.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="🔧 Solo Análisis", 
                  command=self.analyze_only,
                  style='Purple.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="🐍 Ejecutar Python", 
                  command=self.run_python,
                  style='Purple.TButton').pack(side=tk.LEFT, padx=5)
        
        # Separador
        ttk.Separator(button_frame, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Botón de ayuda
        ttk.Button(button_frame, text="❓ Ayuda", 
                  command=self.show_help,
                  style='Purple.TButton').pack(side=tk.LEFT, padx=5)
    
    def create_tabbed_panel(self, parent):
        """Crea el panel con pestañas"""
        # Crear el notebook
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Personalizar el estilo del notebook
        style = ttk.Style()
        style.configure('Dark.TNotebook', background=self.colors['bg_dark'])
        style.configure('Dark.TNotebook.Tab', 
                       background=self.colors['bg_medium'],
                       foreground=self.colors['white'],
                       padding=[20, 10])
        style.map('Dark.TNotebook.Tab',
                 background=[('selected', self.colors['purple'])],
                 foreground=[('selected', self.colors['white'])])
        
        self.notebook.configure(style='Dark.TNotebook')
        
        # Crear las pestañas
        self.create_source_tab()
        self.create_tokens_tab()
        self.create_ast_tab()
        self.create_symbols_tab()
        self.create_intermediate_tab()
        self.create_output_tab()
    
    def create_source_tab(self):
        """Crea la pestaña del código fuente"""
        source_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(source_frame, text="Código Fuente")
        
        # Editor de código
        self.source_text = scrolledtext.ScrolledText(
            source_frame,
            wrap=tk.WORD,
            font=('Consolas', 12),
            bg=self.colors['bg_medium'],
            fg=self.colors['white'],
            insertbackground=self.colors['purple_light'],
            selectbackground=self.colors['purple'],
            selectforeground=self.colors['white']
        )
        self.source_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Agregar números de línea
        self.add_line_numbers(source_frame, self.source_text)
        
        # Código de ejemplo
        example_code = """// Programa de ejemplo
var radio = 5;
var pi = 3.14159;

// Calcular el área de un círculo
function calcularArea(r) {
    var area = pi * r * r;
    return area;
}

// Programa principal
var resultado = calcularArea(radio);
print("El área del círculo es:");
print(resultado);

// Condicional
if (resultado > 50) {
    print("Es un círculo grande");
} else {
    print("Es un círculo pequeño");
}"""
        self.source_text.insert('1.0', example_code)
    
    def create_tokens_tab(self):
        """Crea la pestaña de tokens"""
        tokens_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(tokens_frame, text="Tokens")
        
        # Título
        ttk.Label(tokens_frame, text="Tokens Generados", 
                 style='Title.TLabel').pack(pady=5)
        
        # Tabla de tokens
        columns = ('Tipo', 'Valor', 'Línea', 'Columna')
        self.tokens_tree = ttk.Treeview(tokens_frame, columns=columns, show='headings')
        
        # Configurar columnas
        for col in columns:
            self.tokens_tree.heading(col, text=col)
            self.tokens_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tokens_frame, orient='vertical', command=self.tokens_tree.yview)
        self.tokens_tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        self.tokens_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar colores
        self.tokens_tree.tag_configure('keyword', foreground=self.colors['purple_light'])
        self.tokens_tree.tag_configure('number', foreground='#00ff88')
        self.tokens_tree.tag_configure('string', foreground='#ffaa00')
        self.tokens_tree.tag_configure('operator', foreground='#ff6666')
    
    def create_ast_tab(self):
        """Crea la pestaña del AST"""
        ast_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(ast_frame, text="AST")
        
        # Título
        ttk.Label(ast_frame, text="Árbol de Sintaxis Abstracta", 
                 style='Title.TLabel').pack(pady=5)
        
        # Área de texto para el AST
        self.ast_text = scrolledtext.ScrolledText(
            ast_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg=self.colors['bg_medium'],
            fg=self.colors['white'],
            state='disabled'
        )
        self.ast_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_symbols_tab(self):
        """Crea la pestaña de la tabla de símbolos"""
        symbols_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(symbols_frame, text="Tabla de Símbolos")
        
        # Título
        ttk.Label(symbols_frame, text="Tabla de Símbolos", 
                 style='Title.TLabel').pack(pady=5)
        
        # Tabla de símbolos
        columns = ('Nombre', 'Tipo', 'Tipo Dato', 'Ámbito', 'Valor', 'Inicializado')
        self.symbols_tree = ttk.Treeview(symbols_frame, columns=columns, show='headings')
        
        # Configurar columnas
        for col in columns:
            self.symbols_tree.heading(col, text=col)
            self.symbols_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(symbols_frame, orient='vertical', command=self.symbols_tree.yview)
        self.symbols_tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        self.symbols_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar colores
        self.symbols_tree.tag_configure('function', foreground=self.colors['purple_light'])
        self.symbols_tree.tag_configure('variable', foreground='#00ff88')
        self.symbols_tree.tag_configure('constant', foreground='#ffaa00')
    
    def create_intermediate_tab(self):
        """Crea la pestaña del código intermedio"""
        intermediate_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(intermediate_frame, text="Código Intermedio")
        
        # Título
        ttk.Label(intermediate_frame, text="Código de Tres Direcciones", 
                 style='Title.TLabel').pack(pady=5)
        
        # Área de texto
        self.intermediate_text = scrolledtext.ScrolledText(
            intermediate_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg=self.colors['bg_medium'],
            fg=self.colors['white'],
            state='disabled'
        )
        self.intermediate_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_output_tab(self):
        """Crea la pestaña del código generado"""
        output_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(output_frame, text="Código Python")
        
        # Título
        ttk.Label(output_frame, text="Código Python Generado", 
                 style='Title.TLabel').pack(pady=5)
        
        # Área de texto
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg=self.colors['bg_medium'],
            fg=self.colors['white']
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_status_panel(self, parent):
        """Crea el panel de estado"""
        status_frame = ttk.Frame(parent, style='Dark.TFrame')
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(
            status_frame, 
            text="Listo para compilar",
            style='Dark.TLabel'
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Indicador de estado
        self.status_indicator = tk.Canvas(
            status_frame, 
            width=20, 
            height=20,
            bg=self.colors['bg_dark'],
            highlightthickness=0
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=10)
        self.update_status_indicator('ready')
    
    def add_line_numbers(self, parent, text_widget):
        """Añade números de línea al editor"""
        # Por simplicidad, no implementamos números de línea dinámicos
        # pero podrías añadirlos con un widget Text adicional
        pass
    
    def update_status_indicator(self, status):
        """Actualiza el indicador de estado"""
        self.status_indicator.delete('all')
        colors = {
            'ready': self.colors['gray'],
            'success': self.colors['green'],
            'error': self.colors['red'],
            'processing': self.colors['yellow']
        }
        color = colors.get(status, self.colors['gray'])
        self.status_indicator.create_oval(5, 5, 15, 15, fill=color, outline='')
    
    # ============ FUNCIONES DE COMPILACIÓN ============
    
    def compile_code(self):
        """Compila el código completo"""
        self.status_label.config(text="Compilando...")
        self.update_status_indicator('processing')
        self.root.update()
        
        try:
            source_code = self.source_text.get('1.0', tk.END)
            
            # 1. Análisis Léxico
            lexer = Lexer(source_code)
            self.current_tokens = lexer.tokenize()
            self.display_tokens()
            
            # 2. Análisis Sintáctico
            parser = Parser(self.current_tokens)
            self.current_ast = parser.parse()
            
            if parser.errors:
                raise Exception("Errores de sintaxis:\n" + "\n".join(parser.errors))
            
            self.display_ast()
            
            # 3. Tabla de Símbolos
            builder = SymbolTableBuilder()
            self.current_symbol_table = builder.build(self.current_ast)
            self.display_symbols()
            
            # 4. Código Intermedio
            generator = CodeGenerator()
            self.current_intermediate_code = generator.generate(self.current_ast)
            self.display_intermediate_code()
            
            # 5. Traducción a Python
            translator = SimplifiedPythonTranslator()
            python_code = translator.translate(self.current_intermediate_code)
            self.display_python_code(python_code)
            
            self.status_label.config(text="Compilación exitosa")
            self.update_status_indicator('success')
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            self.update_status_indicator('error')
            messagebox.showerror("Error de Compilación", str(e))
    
    def analyze_only(self):
        """Solo realiza el análisis sin generar código"""
        self.status_label.config(text="Analizando...")
        self.update_status_indicator('processing')
        self.root.update()
        
        try:
            source_code = self.source_text.get('1.0', tk.END)
            
            # Análisis Léxico
            lexer = Lexer(source_code)
            self.current_tokens = lexer.tokenize()
            self.display_tokens()
            
            # Análisis Sintáctico
            parser = Parser(self.current_tokens)
            self.current_ast = parser.parse()
            
            if parser.errors:
                raise Exception("Errores de sintaxis:\n" + "\n".join(parser.errors))
            
            self.display_ast()
            
            # Tabla de Símbolos
            builder = SymbolTableBuilder()
            self.current_symbol_table = builder.build(self.current_ast)
            self.display_symbols()
            
            self.status_label.config(text="Análisis completado")
            self.update_status_indicator('success')
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            self.update_status_indicator('error')
            messagebox.showerror("Error de Análisis", str(e))
    
    def display_tokens(self):
        """Muestra los tokens en la tabla"""
        # Limpiar tabla
        for item in self.tokens_tree.get_children():
            self.tokens_tree.delete(item)
        
        # Añadir tokens
        for token in self.current_tokens:
            if token.type.name != 'NEWLINE' and token.type.name != 'EOF':
                # Determinar el tag para el color
                tag = ''
                if token.type.name in ['IF', 'ELSE', 'WHILE', 'FOR', 'FUNCTION', 'RETURN', 'VAR', 'CONST']:
                    tag = 'keyword'
                elif token.type.name == 'NUMBER':
                    tag = 'number'
                elif token.type.name == 'STRING_LITERAL':
                    tag = 'string'
                elif token.type.name in ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'ASSIGN']:
                    tag = 'operator'
                
                values = (token.type.name, token.value, token.line, token.column)
                self.tokens_tree.insert('', tk.END, values=values, tags=(tag,))
    
    def display_ast(self):
        """Muestra el AST en el área de texto"""
        import io
        import sys
        
        # Capturar la salida del ASTPrinter
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        printer = ASTPrinter()
        printer.print_ast(self.current_ast)
        
        ast_output = buffer.getvalue()
        sys.stdout = old_stdout
        
        # Mostrar en el área de texto
        self.ast_text.config(state='normal')
        self.ast_text.delete('1.0', tk.END)
        self.ast_text.insert('1.0', ast_output)
        self.ast_text.config(state='disabled')
    
    def display_symbols(self):
        """Muestra la tabla de símbolos"""
        # Limpiar tabla
        for item in self.symbols_tree.get_children():
            self.symbols_tree.delete(item)
        
        # Añadir símbolos
        for symbol in self.current_symbol_table.all_symbols:
            tag = ''
            if symbol.symbol_type.name == 'FUNCTION':
                tag = 'function'
            elif symbol.symbol_type.name == 'CONSTANT':
                tag = 'constant'
            else:
                tag = 'variable'
            
            values = (
                symbol.name,
                symbol.symbol_type.name,
                symbol.data_type.value,
                symbol.scope,
                str(symbol.value) if symbol.value else '',
                'Sí' if symbol.is_initialized else 'No'
            )
            self.symbols_tree.insert('', tk.END, values=values, tags=(tag,))
    
    def display_intermediate_code(self):
        """Muestra el código intermedio"""
        self.intermediate_text.config(state='normal')
        self.intermediate_text.delete('1.0', tk.END)
        
        for i, instruction in enumerate(self.current_intermediate_code.instructions):
            line = f"{i:3d}: {instruction}\n"
            self.intermediate_text.insert(tk.END, line)
        
        self.intermediate_text.config(state='disabled')
    
    def display_python_code(self, code):
        """Muestra el código Python generado"""
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert('1.0', code)
    
    # ============ FUNCIONES DE ARCHIVO ============
    
    def new_file(self):
        """Crea un nuevo archivo"""
        self.source_text.delete('1.0', tk.END)
        self.status_label.config(text="Nuevo archivo creado")
        self.update_status_indicator('ready')
    
    def open_file(self):
        """Abre un archivo"""
        filename = filedialog.askopenfilename(
            title="Abrir archivo",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            self.source_text.delete('1.0', tk.END)
            self.source_text.insert('1.0', content)
            self.status_label.config(text=f"Archivo abierto: {os.path.basename(filename)}")
    
    def save_file(self):
        """Guarda el archivo actual"""
        filename = filedialog.asksaveasfilename(
            title="Guardar archivo",
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if filename:
            content = self.source_text.get('1.0', tk.END)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            self.status_label.config(text=f"Archivo guardado: {os.path.basename(filename)}")
    
    def run_python(self):
        """Ejecuta el código Python generado"""
        python_code = self.output_text.get('1.0', tk.END)
        if not python_code.strip():
            messagebox.showwarning("Advertencia", "Primero debes compilar el código")
            return
        
        # Guardar temporalmente y ejecutar
        with open('temp_output.py', 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        try:
            result = subprocess.run([sys.executable, 'temp_output.py'], 
                                  capture_output=True, text=True)
            
            output_window = tk.Toplevel(self.root)
            output_window.title("Salida del Programa")
            output_window.geometry("600x400")
            output_window.configure(bg=self.colors['bg_dark'])
            
            output_text = scrolledtext.ScrolledText(
                output_window,
                bg=self.colors['bg_medium'],
                fg=self.colors['white'],
                font=('Consolas', 10)
            )
            output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            if result.stdout:
                output_text.insert(tk.END, "=== SALIDA ===\n")
                output_text.insert(tk.END, result.stdout)
            
            if result.stderr:
                output_text.insert(tk.END, "\n=== ERRORES ===\n")
                output_text.insert(tk.END, result.stderr)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar: {str(e)}")
        finally:
            if os.path.exists('temp_output.py'):
                os.remove('temp_output.py')
    
    def show_help(self):
        """Muestra la ventana de ayuda"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Ayuda - Mini Compilador")
        help_window.geometry("700x500")
        help_window.configure(bg=self.colors['bg_dark'])
        
        help_text = scrolledtext.ScrolledText(
            help_window,
            bg=self.colors['bg_medium'],
            fg=self.colors['white'],
            font=('Arial', 10),
            wrap=tk.WORD
        )
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_content = """
MINI COMPILADOR - AYUDA

=== SINTAXIS DEL LENGUAJE ===

DECLARACIONES:
• var nombre = valor;       // Variable
• const PI = 3.14;         // Constante
• function nombre(params) { ... }  // Función

TIPOS DE DATOS:
• Números: 10, 3.14
• Strings: "Hola", 'Mundo'
• Booleanos: true, false

SENTENCIAS:
• if (condición) { ... } else { ... }
• while (condición) { ... }
• for (init; condición; update) { ... }
• return valor;
• print(expresión);

OPERADORES:
• Aritméticos: +, -, *, /, %
• Comparación: <, >, <=, >=, ==, !=
• Lógicos: &&, ||, !

COMENTARIOS:
• // Comentario de una línea

=== USO DEL COMPILADOR ===

1. Escribir código en la pestaña "Código Fuente"
2. Click en "Compilar" para compilar el código
3. Ver los resultados en las diferentes pestañas:
   - Tokens: Análisis léxico
   - AST: Árbol de sintaxis
   - Tabla de Símbolos: Variables y funciones
   - Código Intermedio: Representación intermedia
   - Código Python: Código generado

4. Click en "Ejecutar Python" para ejecutar el código generado

=== EJEMPLO ===

var x = 10;
var y = 20;
var suma = x + y;

if (suma > 25) {
    print("La suma es mayor que 25");
} else {
    print("La suma es 25 o menor");
}
"""
        help_text.insert('1.0', help_content)
        help_text.config(state='disabled')

def main():
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()