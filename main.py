# main.py
from lexer import Lexer
from tokens import TokenType
from parser import Parser
from ast_printer import ASTPrinter
from symbol_table_builder import SymbolTableBuilder

def test_lexer():
    # Código de prueba
    test_code = """
    // Este es un comentario
    var x = 10;
    var y = 20.5;
    var nombre = "Hola Mundo";
    
    if (x < y) {
        print("x es menor que y");
    } else {
        print("x es mayor o igual que y");
    }
    
    function suma(a, b) {
        return a + b;
    }
    
    while (x <= 100) {
        x = x + 1;
    }
    """
    
    print("=== CÓDIGO FUENTE ===")
    print(test_code)
    print("\n=== TOKENS GENERADOS ===")
    
    # Crear el lexer y tokenizar
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    # Mostrar los tokens en formato tabla
    print(f"{'Token Type':<20} {'Value':<20} {'Line':<6} {'Column':<6}")
    print("-" * 60)
    
    for token in tokens:
        # Filtrar los saltos de línea para mejor visualización
        if token.type != TokenType.NEWLINE:
            value_display = repr(token.value) if token.type == TokenType.STRING_LITERAL else token.value
            print(f"{token.type.name:<20} {value_display:<20} {token.line:<6} {token.column:<6}")
    
    print(f"\nTotal de tokens: {len(tokens)}")
    
    # Prueba adicional con expresiones matemáticas
    print("\n\n=== PRUEBA CON EXPRESIONES MATEMÁTICAS ===")
    math_code = "resultado = (5 + 3) * 2 / 4 - 1;"
    print(f"Código: {math_code}")
    
    lexer2 = Lexer(math_code)
    tokens2 = lexer2.tokenize()
    
    print("\nTokens:")
    for token in tokens2:
        if token.type != TokenType.EOF:
            print(f"  {token}")

def test_error_handling():
    print("\n\n=== PRUEBA DE MANEJO DE ERRORES ===")
    
    # Prueba con string sin cerrar
    try:
        error_code = 'var text = "Hola mundo'
        lexer = Lexer(error_code)
        lexer.tokenize()
    except Exception as e:
        print(f"✓ Error detectado correctamente: {e}")
    
    # Prueba con carácter inválido
    try:
        error_code = 'var x = 10 @ 5;'
        lexer = Lexer(error_code)
        lexer.tokenize()
    except Exception as e:
        print(f"✓ Error detectado correctamente: {e}")

def test_from_file(filename):
    """Lee y procesa un archivo de código fuente"""
    print(f"\n\n=== PROCESANDO ARCHIVO: {filename} ===")
    
    try:
        # Leer el archivo
        with open(filename, 'r', encoding='utf-8') as file:
            code = file.read()
        
        print("=== CÓDIGO FUENTE ===")
        print(code)
        
        # Tokenizar
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        print("\n=== TOKENS GENERADOS ===")
        print(f"{'Token Type':<20} {'Value':<20} {'Line':<6} {'Column':<6}")
        print("-" * 60)
        
        for token in tokens:
            if token.type != TokenType.NEWLINE:
                value_display = repr(token.value) if token.type == TokenType.STRING_LITERAL else token.value
                print(f"{token.type.name:<20} {value_display:<20} {token.line:<6} {token.column:<6}")
        
        print(f"\nTotal de tokens: {len(tokens)}")
        
        # Parsear
        print("\n\n=== ANÁLISIS SINTÁCTICO ===")
        parser = Parser(tokens)
        ast = parser.parse()
        
        if parser.errors:
            print("❌ Errores encontrados durante el parseo:")
            for error in parser.errors:
                print(f"   - {error}")
        else:
            print("✓ Parseo exitoso!\n")
            print("=== ÁRBOL DE SINTAXIS ABSTRACTA (AST) ===")
            printer = ASTPrinter()
            printer.print_ast(ast)
            
            # Construir tabla de símbolos
            print("\n\n=== CONSTRUCCIÓN DE TABLA DE SÍMBOLOS ===")
            builder = SymbolTableBuilder()
            symbol_table = builder.build(ast)
            
            if builder.errors:
                print("⚠️  Advertencias encontradas:")
                for error in builder.errors:
                    print(f"   - {error}")
            else:
                print("✓ Tabla de símbolos construida exitosamente!")
            
            # Mostrar la tabla
            symbol_table.print_table()
            symbol_table.print_scope_tree()
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{filename}'")
        print(f"   Asegúrate de que el archivo existe en la misma carpeta que main.py")
    except Exception as e:
        print(f"❌ Error al procesar el archivo: {e}")

def test_parser():
    """Prueba el parser con código predefinido"""
    test_code = """
    // Declaración de variables
    var x = 10;
    var y = 20;
    
    // Función simple
    function suma(a, b) {
        return a + b;
    }
    
    // Condicional
    if (x < y) {
        print("x es menor que y");
    } else {
        print("x es mayor o igual");
    }
    
    // Bucle while
    while (x < 15) {
        x = x + 1;
        print(x);
    }
    
    // Llamada a función
    var resultado = suma(5, 3);
    print(resultado);
    """
    
    print("=== PRUEBA DEL PARSER ===")
    print("=== CÓDIGO FUENTE ===")
    print(test_code)
    
    # Tokenizar
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    # Parsear
    print("\n=== ANÁLISIS SINTÁCTICO ===")
    parser = Parser(tokens)
    ast = parser.parse()
    
    if parser.errors:
        print("❌ Errores encontrados:")
        for error in parser.errors:
            print(f"   - {error}")
    else:
        print("✓ Parseo exitoso!\n")
        print("=== ÁRBOL DE SINTAXIS ABSTRACTA (AST) ===")
        printer = ASTPrinter()
        printer.print_ast(ast)

def test_parser_errors():
    """Prueba el manejo de errores del parser"""
    print("\n\n=== PRUEBA DE MANEJO DE ERRORES ===")
    
    error_cases = [
        ("var x = ;", "Falta valor en asignación"),
        ("if (x < 10 { print(x); }", "Falta paréntesis de cierre"),
        ("function test( { }", "Falta parámetros y paréntesis"),
        ("x = 10", "Falta punto y coma"),
        ("print(\"hola\";", "Falta paréntesis de cierre")
    ]
    
    for code, description in error_cases:
        print(f"\nPrueba: {description}")
        print(f"Código: {code}")
        
        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            
            if parser.errors:
                print(f"✓ Error detectado: {parser.errors[0]}")
            else:
                print("❌ No se detectó el error esperado")
        except Exception as e:
            print(f"✓ Error detectado: {e}")

def test_symbol_table():
    """Prueba específica de la tabla de símbolos"""
    test_code = """
    // Variables globales
    var global_var = 100;
    const PI = 3.14159;
    
    // Función con parámetros
    function calcular(x, y) {
        var resultado = x + y;
        return resultado;
    }
    
    // Variables en diferentes ámbitos
    var a = 10;
    if (a > 5) {
        var b = 20;
        var c = a + b;
    }
    
    // Bucle con su propio ámbito
    for (var i = 0; i < 10; i = i + 1) {
        var temp = i * 2;
    }
    
    // Uso de variables no declaradas (debe generar error)
    z = 50;
    
    // Intento de modificar constante (debe generar error)
    PI = 3.14;
    """
    
    print("=== PRUEBA DE TABLA DE SÍMBOLOS ===")
    print("=== CÓDIGO FUENTE ===")
    print(test_code)
    
    # Tokenizar
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    # Parsear
    parser = Parser(tokens)
    ast = parser.parse()
    
    if not parser.errors:
        # Construir tabla de símbolos
        print("\n=== CONSTRUCCIÓN DE TABLA DE SÍMBOLOS ===")
        builder = SymbolTableBuilder()
        symbol_table = builder.build(ast)
        
        if builder.errors:
            print("\n⚠️  Advertencias y errores semánticos:")
            for error in builder.errors:
                print(f"   - {error}")
        
        # Mostrar la tabla
        symbol_table.print_table()
        symbol_table.print_scope_tree()

if __name__ == "__main__":
    # Menú de opciones actualizado
    print("=== MINI COMPILADOR ===")
    print("1. Probar solo el Analizador Léxico")
    print("2. Probar el Parser con código predefinido")
    print("3. Procesar archivo test.txt (Léxico + Sintáctico + Símbolos)")
    print("4. Procesar otro archivo")
    print("5. Probar manejo de errores")
    print("6. Probar tabla de símbolos")
    print("7. Todas las pruebas")
    
    opcion = input("\nElige una opción (1-7): ")
    
    if opcion == "1":
        test_lexer()
    elif opcion == "2":
        test_parser()
    elif opcion == "3":
        test_from_file("test.txt")
    elif opcion == "4":
        filename = input("Ingresa el nombre del archivo: ")
        test_from_file(filename)
    elif opcion == "5":
        test_parser_errors()
    elif opcion == "6":
        test_symbol_table()
    elif opcion == "7":
        test_lexer()
        test_parser()
        test_parser_errors()
        test_symbol_table()
        test_from_file("test.txt")
    else:
        print("Opción no válida")
    
    print("\n\n=== ANÁLISIS COMPLETADO ✓ ===")