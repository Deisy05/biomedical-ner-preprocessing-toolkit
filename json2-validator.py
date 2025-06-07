import json
import sys

def validate_jsonl_file(file_path):
    """
    Valida un archivo JSONL que contiene anotaciones de tokens y etiquetas.
    
    Args:
        file_path (str): Ruta al archivo JSONL a validar
        
    Returns:
        int: Número de errores encontrados
    """
    error_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, 1):
                try:
                    # Verificar que la línea no esté vacía
                    if not line.strip():
                        print(f"\033[93m⚠️  Línea {line_number}: Línea vacía (permitida en JSONL)\033[0m")
                        error_count += 1
                        continue
                    
                    # Intentar parsear el JSON
                    data = json.loads(line)
                    
                    # Verificar que el JSON tiene las claves requeridas
                    if not all(key in data for key in ['sentencia', 'tag']):
                        print(f"\033[91m❌ Línea {line_number}: Faltan claves requeridas 'sentencia' o 'tag'\033[0m")
                        error_count += 1
                        continue
                    
                    # Verificar que los valores son listas
                    if not isinstance(data['sentencia'], list) or not isinstance(data['tag'], list):
                        print(f"\033[91m❌ Línea {line_number}: 'sentencia' y 'tag' deben ser listas\033[0m")
                        error_count += 1
                        continue
                    
                    # Verificar que las longitudes coinciden
                    if len(data['sentencia']) != len(data['tag']):
                        print(f"\033[91m❌ Línea {line_number}: Longitud discrepante | Sentencia: {len(data['sentencia'])} vs Tag: {len(data['tag'])}\033[0m")
                        error_count += 1
                        continue
                    
                    # Verificar que todos los elementos en 'tag' son números
                    if not all(isinstance(tag, (int, float)) for tag in data['tag']):
                        print(f"\033[91m❌ Línea {line_number}: Todos los elementos en 'tag' deben ser números\033[0m")
                        error_count += 1
                        continue
                    
                    # Verificar que todos los elementos en 'sentencia' son strings
                    if not all(isinstance(token, str) for token in data['sentencia']):
                        print(f"\033[91m❌ Línea {line_number}: Todos los elementos en 'sentencia' deben ser strings\033[0m")
                        error_count += 1
                        continue
                    
                except json.JSONDecodeError as e:
                    print(f"\033[91m❌ Línea {line_number}: {str(e)}\033[0m")
                    error_count += 1
                    
    except FileNotFoundError:
        print(f"\033[91m❌ Error: No se pudo encontrar el archivo '{file_path}'\033[0m")
        return 1
    except Exception as e:
        print(f"\033[91m❌ Error inesperado: {str(e)}\033[0m")
        return 1
    
    if error_count == 0:
        print(f"\033[92m✅ {file_path} válido con la estructura requerida.\033[0m")
    else:
        print(f"\n\033[91m❌ Se encontraron {error_count} errores en {file_path}\033[0m")
    
    return error_count

# Ejemplo de uso
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("\033[93mUso: python validator.py <ruta_al_archivo.json>\033[0m")
        sys.exit(1)
        
    file_path = sys.argv[1]
    error_count = validate_jsonl_file(file_path)
    sys.exit(1 if error_count > 0 else 0)
