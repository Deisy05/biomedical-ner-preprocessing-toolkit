import re
import json
import sys
import os

def tokenize_line(line):
    # Expresión regular para dividir palabras, números, símbolos y mantener juntos casos como "3+", "90%", "HER2/neu"
    tokens = re.findall(r'''
        \d+[+\-]?%?      # Números con +/- o % (ej: 3+, 90%)
        |\d+\.\d+        # Decimales (ej: 3.5)
        |\w+[\-/]\w+     # Palabras con guiones o barras (ej: HER2/neu, ki-67)
        |\w+              # Palabras normales
        |[^\s]            # Símbolos individuales (ej: (, ), /, :)
    ''', line, re.X | re.UNICODE)
    
    return tokens

def txt_to_jsonl(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:
        
        for line in f_in:
            line = line.strip()
            if line:
                tokens = tokenize_line(line)
                json_obj = {
                    "sentencia": tokens,
                    "tag": [48] * len(tokens)  # Todos los tags a 48 (ajusta según necesidades)
                }
                f_out.write(json.dumps(json_obj, ensure_ascii=False) + '\n')

def main():
    # Verificar si se proporcionó un archivo como argumento
    if len(sys.argv) != 2:
        print("Uso: python3 script_tokenizar_textos.py archivo.txt")
        sys.exit(1)
    
    # Obtener el nombre del archivo de entrada
    input_file = sys.argv[1]
    
    # Verificar que el archivo exista
    if not os.path.isfile(input_file):
        print(f"Error: El archivo '{input_file}' no existe.")
        sys.exit(1)
    
    # Verificar que sea un archivo .txt
    if not input_file.lower().endswith('.txt'):
        print("Error: El archivo debe tener extensión .txt")
        sys.exit(1)
    
    # Generar el nombre del archivo de salida
    # Quitar la extensión .txt y añadir _valid.json
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}_valid.json"
    
    # Procesar el archivo
    txt_to_jsonl(input_file, output_file)
    print(f"Archivo procesado correctamente. \nResultado guardado en: '{output_file}'")

if __name__ == "__main__":
    main()
