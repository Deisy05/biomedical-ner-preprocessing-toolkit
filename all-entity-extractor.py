import json
import os
import sys
from pathlib import Path
from collections import defaultdict

# Define entity tags mapping
ENTITY_TAGS = {
    0: "B_AGE",                   23: "I_AGE",
    1: "B_STAGE",                 24: "I_STAGE",
    2: "B_DATE",                  25: "I_DATE",
    3: "B_IMPLICIT_DATE",         26: "I_IMPLICIT_DATE",
    4: "B_TNM",                   27: "I_TNM",
    5: "B_FAMILY",                28: "I_FAMILY",
    6: "B_OCURRENCE_EVENT",       29: "I_OCURRENCE_EVENT",
    7: "B_TOXIC_HABITS",          30: "I_TOXIC_HABITS",
    8: "B_HABIT-QUANTITY",        31: "I_HABIT-QUANTITY",
    9: "B_TREATMENT_NAME",        32: "I_TREATMENT_NAME",
    10: "B_LINE_CICLE_NUMBER",    33: "I_LINE_CICLE_NUMBER",
    11: "B_SURGERY",              34: "I_SURGERY",
    12: "B_DRUG",                 35: "I_DRUG",
    13: "B_DOSE",                 36: "I_DOSE",
    14: "B_FREQ",                 37: "I_FREQ",
    15: "B_BIOMARKER",            38: "I_BIOMARKER",
    16: "B_CLINICAL_SERVICE",     39: "I_CLINICAL_SERVICE",
    17: "B_COMORBIDITY",          40: "I_COMORBIDITY",
    18: "B_PROGRESION",           41: "I_PROGRESION",
    19: "B_GINECOLOGICAL_HISTORY", 42: "I_GINECOLOGICAL_HISTORY",
    20: "B_GINE_OBSTETRICS",      43: "I_GINE_OBSTETRICS",
    21: "B_ALLERGIES",            44: "I_ALLERGIES",
    22: "B_DURATION",             45: "I_DURATION",
    46: "B-CANCER_CONCEPT",       47: "I-CANCER_CONCEPT",
}

# Get entity type from tag number
def get_entity_type(tag_num):
    # Get base entity type by removing B_ or I_ prefix
    tag_name = ENTITY_TAGS.get(tag_num, "UNKNOWN")
    if tag_name.startswith("B_") or tag_name.startswith("B-"):
        return tag_name[2:]
    elif tag_name.startswith("I_") or tag_name.startswith("I-"):
        return tag_name[2:]
    return tag_name

# Get beginning tag for entity type
def get_beginning_tag(entity_type):
    for tag_num, tag_name in ENTITY_TAGS.items():
        if (tag_name == f"B_{entity_type}" or 
            tag_name == f"B-{entity_type}") and tag_num % 23 == tag_num % 24:
            return tag_num
    return None

# Get inside tag for entity type
def get_inside_tag(entity_type):
    for tag_num, tag_name in ENTITY_TAGS.items():
        if tag_name == f"I_{entity_type}" or tag_name == f"I-{entity_type}":
            return tag_num
    return None

def print_results(files_entities, all_entities):
    """
    Imprime los resultados del análisis de entidades por archivo y el total de entidades únicas.
    
    Args:
        files_entities (dict): Diccionario con archivos y sus entidades agrupadas por tipo
        all_entities (dict): Diccionario con todas las entidades únicas agrupadas por tipo
    """
    print("\n=== RESULTADOS POR ARCHIVO ===")
    for filename, entity_types in files_entities.items():
        print(f"\nArchivo: {filename}")
        
        for entity_type, phrases in sorted(entity_types.items()):
            print(f"\n  {entity_type}:")
            if phrases:
                for i, phrase in enumerate(sorted(phrases), 1):
                    print(f"    {i}. \"{phrase}\"")
            else:
                print(f"    No se encontraron entidades de tipo {entity_type} en este archivo.")
    
    print("\n=== ENTIDADES ENCONTRADAS POR TIPO ===")
    total_entities = 0
    
    for entity_type, phrases in sorted(all_entities.items()):
        print(f"\n{entity_type}:")
        if phrases:
            for i, phrase in enumerate(sorted(phrases), 1):
                print(f"  {i}. \"{phrase}\"")
            print(f"  Total {entity_type}: {len(phrases)}")
            total_entities += len(phrases)
        else:
            print(f"  No se encontraron entidades de tipo {entity_type} en ningún archivo.")
    
    print(f"\nTotal entidades encontradas: {total_entities}")

def extract_entities(sentencia, tag):
    """
    Extrae entidades de una sentencia y sus etiquetas.
    
    Args:
        sentencia (list): Lista de palabras en la sentencia
        tag (list): Lista de etiquetas correspondientes a cada palabra
        
    Returns:
        dict: Diccionario con entidades agrupadas por tipo
    """
    entities_by_type = defaultdict(set)
    i = 0
    
    while i < len(tag):
        # Detectar si es una etiqueta de inicio (B_)
        if tag[i] in ENTITY_TAGS and ENTITY_TAGS[tag[i]].startswith('B'):
            entity_type = get_entity_type(tag[i])
            inside_tag = get_inside_tag(entity_type)
            
            # Recolectar palabras de la entidad
            entity_words = [sentencia[i]]
            j = i + 1
            
            # Continuar mientras sea una etiqueta inside (I_) del mismo tipo
            while j < len(tag) and tag[j] == inside_tag:
                entity_words.append(sentencia[j])
                j += 1
            
            # Agregar la entidad completa al conjunto correspondiente
            if entity_words:
                entities_by_type[entity_type].add(' '.join(entity_words))
            
            i = j
        else:
            i += 1
            
    return entities_by_type

def process_single_file(file_path):
    """
    Procesa un único archivo JSON y extrae las entidades.
    
    Args:
        file_path (str): Ruta al archivo JSON a procesar
        
    Returns:
        tuple: (dict con el archivo y sus entidades por tipo, dict con todas las entidades por tipo)
    """
    all_entities = defaultdict(set)
    files_entities = {}
    
    try:
        filename = os.path.basename(file_path)
        current_file_entities = defaultdict(set)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    data = json.loads(line.strip())
                    sentencia = data['sentencia']
                    tag = data['tag']
                    
                    # Extraer entidades de la línea actual
                    entities = extract_entities(sentencia, tag)
                    
                    # Actualizar entidades del archivo actual
                    for entity_type, phrases in entities.items():
                        current_file_entities[entity_type].update(phrases)
                        all_entities[entity_type].update(phrases)
                    
                except json.JSONDecodeError as e:
                    print(f"Error al decodificar línea en {filename}: {e}")
                    continue
        
        files_entities[filename] = current_file_entities
    except Exception as e:
        print(f"Error al procesar el archivo {filename}: {e}")
    
    return files_entities, all_entities

def extract_entities_from_directory(directory_path='.'):
    """
    Extrae entidades de todos los archivos JSON en el directorio especificado.
    
    Args:
        directory_path (str): Ruta al directorio a procesar
        
    Returns:
        tuple: (dict con archivos y sus entidades por tipo, dict con todas las entidades por tipo)
    """
    all_entities = defaultdict(set)
    files_entities = {}
    
    # Procesar solo archivos JSON en el directorio
    for filename in [f for f in os.listdir(directory_path) if f.endswith('.json')]:
        file_path = os.path.join(directory_path, filename)
        file_results, file_entities = process_single_file(file_path)
        files_entities.update(file_results)
        
        # Actualizar todas las entidades
        for entity_type, phrases in file_entities.items():
            all_entities[entity_type].update(phrases)
            
    return files_entities, all_entities

def main():
    try:
        # Verificar si se proporcionó un archivo específico como argumento
        if len(sys.argv) > 1 and sys.argv[1].endswith('.json'):
            file_path = sys.argv[1]
            if os.path.isfile(file_path):
                print(f"Procesando archivo específico: {file_path}")
                files_entities, all_entities = process_single_file(file_path)
            else:
                print(f"El archivo {file_path} no existe.")
                return
        else:
            # Si no se proporciona un archivo específico, procesar todos los archivos JSON en el directorio actual
            print("Procesando todos los archivos JSON en el directorio actual.")
            files_entities, all_entities = extract_entities_from_directory()
        
        print_results(files_entities, all_entities)
        
        # Guardar resultados en un archivo
        output_filename = 'resultados_entidades.txt'
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write("=== ENTIDADES ENCONTRADAS POR TIPO ===\n")
            total_entities = 0
            
            for entity_type, phrases in sorted(all_entities.items()):
                f.write(f"\n{entity_type}:\n")
                if phrases:
                    for i, phrase in enumerate(sorted(phrases), 1):
                        f.write(f"  {i}. \"{phrase}\"\n")
                    f.write(f"  Total {entity_type}: {len(phrases)}\n")
                    total_entities += len(phrases)
                else:
                    f.write(f"  No se encontraron entidades de tipo {entity_type}.\n")
            
            f.write(f"\nTotal entidades encontradas: {total_entities}\n")
        
        print(f"\nLos resultados se han guardado en {output_filename}")
                
    except Exception as e:
        print(f"Error durante la ejecución: {e}")

if __name__ == "__main__":
    main()
