import json
import sys
import os
import glob

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

def validate_all_jsonl_files():
    """
    Busca y valida todos los archivos .json y .jsonl en el directorio actual.
    
    Returns:
        dict: Diccionario con resultados de la validación
    """
    # Buscar todos los archivos .json y .jsonl en el directorio actual
    json_files = glob.glob("*.json") + glob.glob("*.jsonl")
    
    if not json_files:
        print("\033[93m⚠️  No se encontraron archivos .json o .jsonl en el directorio actual\033[0m")
        return {"total_files": 0, "valid_files": 0, "invalid_files": 0, "total_errors": 0, "invalid_files_list": []}
    
    total_files = len(json_files)
    valid_files = 0
    invalid_files = 0
    total_errors = 0
    invalid_files_list = []
    
    print(f"\n\033[1mValidando {total_files} archivos JSONL en el directorio actual...\033[0m\n")
    
    for json_file in json_files:
        print(f"\n\033[1m{'-' * 50}\033[0m")
        print(f"\033[1mValidando: {json_file}\033[0m")
        print(f"\033[1m{'-' * 50}\033[0m\n")
        
        error_count = validate_jsonl_file(json_file)
        total_errors += error_count
        
        if error_count == 0:
            valid_files += 1
        else:
            invalid_files += 1
            invalid_files_list.append({"file": json_file, "errors": error_count})
    
    # Resumen final
    print(f"\n\033[1m{'-' * 50}\033[0m")
    print(f"\033[1mRESUMEN DE VALIDACIÓN\033[0m")
    print(f"\033[1m{'-' * 50}\033[0m\n")
    print(f"Total de archivos analizados: {total_files}")
    print(f"\033[92mArchivos válidos: {valid_files}\033[0m")
    
    if invalid_files > 0:
        print(f"\033[91mArchivos con errores: {invalid_files}\033[0m")
        print(f"\033[91mTotal de errores encontrados: {total_errors}\033[0m")
        
        # Listar archivos con errores
        print(f"\n\033[1mLISTA DE ARCHIVOS CON ERRORES:\033[0m")
        for i, invalid_file in enumerate(invalid_files_list, 1):
            print(f"\033[91m{i}. {invalid_file['file']} - {invalid_file['errors']} errores\033[0m")
    
    return {
        "total_files": total_files,
        "valid_files": valid_files,
        "invalid_files": invalid_files,
        "total_errors": total_errors,
        "invalid_files_list": invalid_files_list
    }

# Ejecución principal
if __name__ == "__main__":
    results = validate_all_jsonl_files()
    sys.exit(1 if results["invalid_files"] > 0 else 0)
