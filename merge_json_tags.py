import json
import sys

'''
Une todas las oraciones y etiquetas, y devuelve un único objeto JSON.
'''

def merge_json_lines(input_file_path):
    """
    Función que lee un archivo JSON (una línea por cada objeto JSON),
    une todas las oraciones y etiquetas, y devuelve un único objeto JSON.
    """
    merged_sentences = []
    merged_tags = []
    
    try:
        # Leer el archivo JSON línea por línea
        with open(input_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:  # Saltar líneas vacías
                    continue
                    
                # Cargar el objeto JSON de la línea
                data = json.loads(line)
                
                # Verificar que el objeto tenga las claves necesarias
                if 'sentencia' not in data or 'tag' not in data:
                    print(f"Advertencia: Línea no tiene formato correcto: {line}")
                    continue
                    
                # Agregar las palabras y etiquetas a las listas
                merged_sentences.extend(data['sentencia'])
                merged_tags.extend(data['tag'])
    
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {input_file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: El archivo no contiene JSON válido. {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)
    
    # Crear el objeto JSON resultante
    result = {
        "sentencia": merged_sentences,
        "tag": merged_tags
    }
    
    return result

def main():
    # Verificar que se proporcionó un archivo de entrada
    if len(sys.argv) < 2:
        print("Uso: python3 script.py archivo.json")
        sys.exit(1)
    
    input_file_path = sys.argv[1]
    # Crear nombre del archivo de salida con el formato nombre_merged.json
    output_file_path = input_file_path.replace('.json', '_merged.json')
    
    # Fusionar las líneas JSON
    merged_data = merge_json_lines(input_file_path)
    
    # Escribir el resultado en un archivo nuevo
    try:
        with open(output_file_path, 'w', encoding='utf-8') as file:
            json.dump(merged_data, file, ensure_ascii=False)
        print(f"\nArchivo procesado exitosamente.\nResultado guardado en {output_file_path}")
    except Exception as e:
        print(f"Error al escribir el archivo de salida: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
