# main.py
from lexer import Lexer
from tokens import TokenType

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
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{filename}'")
        print(f"   Asegúrate de que el archivo existe en la misma carpeta que main.py")
    except Exception as e:
        print(f"❌ Error al procesar el archivo: {e}")

if __name__ == "__main__":
    # Menú de opciones
    print("=== MINI COMPILADOR - ANALIZADOR LÉXICO ===")
    print("1. Ejecutar pruebas predefinidas")
    print("2. Procesar archivo test.txt")
    print("3. Procesar otro archivo")
    print("4. Todas las pruebas")
    
    opcion = input("\nElige una opción (1-4): ")
    
    if opcion == "1":
        test_lexer()
        test_error_handling()
    elif opcion == "2":
        test_from_file("test.txt")
    elif opcion == "3":
        filename = input("Ingresa el nombre del archivo: ")
        test_from_file(filename)
    elif opcion == "4":
        test_lexer()
        test_error_handling()
        test_from_file("test.txt")
    else:
        print("Opción no válida")
    
    print("\n\n=== ANALIZADOR LÉXICO COMPLETADO ✓ ===")