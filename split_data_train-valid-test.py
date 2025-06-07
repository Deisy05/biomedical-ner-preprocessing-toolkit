#!/usr/bin/env python3
"""
Este script procesa todas las carpetas y divide por archivos completos 
para armar el train, el valid y el test, en lugar de tomar líneas aleatoriamente.
Esto con el fin de no dañar el contexto de una historia médica completa
"""

import os
import json
import random
import logging
from pathlib import Path

# Configurar el sistema de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_split.log'),
        logging.StreamHandler()
    ]
)

def process_folders():
    """Procesa todas las carpetas y divide por archivos completos en lugar de líneas."""
    # Crear el directorio de salida si no existe
    output_dir = Path('output_data')
    output_dir.mkdir(exist_ok=True)
    
    # Lista para almacenar información de todos los archivos
    all_files_info = []
    error_count = 0
    
    # Carpeta a omitir
    folder_to_skip = "nuevos_andres check 2"
    
    # Obtener todas las carpetas en el directorio actual, excluyendo la carpeta a omitir
    folders = [f for f in os.listdir('.') if os.path.isdir(f) and not f.startswith('.') 
              and f != 'output_data' and f != folder_to_skip]
    
    if not folders:
        logging.warning("No se encontraron carpetas para procesar en el directorio actual.")
        return
    
    logging.info(f"Procesando {len(folders)} carpetas: {', '.join(folders)}")
    logging.info(f"Omitiendo la carpeta: {folder_to_skip}")
    
    # Recopilar información de todos los archivos JSON
    for folder in folders:
        try:
            folder_path = Path(folder)
            json_files = list(folder_path.glob('*.json'))
            
            if not json_files:
                logging.info(f"No se encontraron archivos JSON en la carpeta {folder}")
                continue
            
            logging.info(f"Encontrados {len(json_files)} archivos JSON en la carpeta {folder}")
            
            # Validar cada archivo y contar sus líneas
            for json_file in json_files:
                try:
                    file_data = []
                    with open(json_file, 'r', encoding='utf-8') as f:
                        for line_number, line in enumerate(f, 1):
                            try:
                                line = line.strip()
                                if line:  # Ignorar líneas vacías
                                    json_data = json.loads(line)
                                    # Verificar que el formato es correcto
                                    if "sentencia" in json_data and "tag" in json_data:
                                        file_data.append(json_data)
                                    else:
                                        logging.warning(f"Formato incorrecto en {json_file}, línea {line_number}")
                                        error_count += 1
                            except json.JSONDecodeError:
                                logging.error(f"Error al decodificar JSON en {json_file}, línea {line_number}")
                                error_count += 1
                    
                    # Solo agregar archivos que tengan datos válidos
                    if file_data:
                        all_files_info.append({
                            'file_path': json_file,
                            'data': file_data,
                            'count': len(file_data)
                        })
                        logging.info(f"Archivo válido: {json_file} con {len(file_data)} líneas")
                    else:
                        logging.warning(f"Archivo sin datos válidos: {json_file}")
                        
                except Exception as e:
                    logging.error(f"Error al procesar el archivo {json_file}: {str(e)}")
                    error_count += 1
        except Exception as e:
            logging.error(f"Error al procesar la carpeta {folder}: {str(e)}")
            error_count += 1
    
    # Verificar si se encontraron archivos válidos
    if not all_files_info:
        logging.error("No se encontraron archivos válidos para procesar.")
        print("❌ Error: No se encontraron archivos válidos para procesar.")
        return False
    
    # Mezclar los archivos aleatoriamente
    random.shuffle(all_files_info)
    
    # Calcular índices para la división (por número de archivos)
    total_files = len(all_files_info)
    train_files_idx = int(0.8 * total_files)
    valid_files_idx = int(0.9 * total_files)
    
    # Dividir los archivos
    train_files = all_files_info[:train_files_idx]
    valid_files = all_files_info[train_files_idx:valid_files_idx]
    test_files = all_files_info[valid_files_idx:]
    
    # Función auxiliar para escribir archivos y contar líneas
    def write_dataset(files_list, output_filename, dataset_name):
        total_lines = 0
        file_names = []
        
        with open(output_dir / output_filename, 'w', encoding='utf-8') as f:
            for file_info in files_list:
                file_names.append(file_info['file_path'].name)
                for item in file_info['data']:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
                    total_lines += 1
        
        logging.info(f"Dataset {dataset_name}:")
        logging.info(f"  - {len(files_list)} archivos ({len(files_list)/total_files:.2%})")
        logging.info(f"  - {total_lines} líneas totales")
        logging.info(f"  - Archivos incluidos: {', '.join(file_names[:5])}{'...' if len(file_names) > 5 else ''}")
        
        return total_lines, file_names
    
    # Guardar los datasets
    try:
        train_lines, train_file_names = write_dataset(train_files, 'train.json', 'ENTRENAMIENTO')
        valid_lines, valid_file_names = write_dataset(valid_files, 'valid.json', 'VALIDACIÓN')
        test_lines, test_file_names = write_dataset(test_files, 'test.json', 'PRUEBA')
        
        # Calcular totales
        total_lines = train_lines + valid_lines + test_lines
        
        # Resumen final
        print("\n" + "="*60)
        print("RESUMEN DE LA DIVISIÓN POR ARCHIVOS")
        print("="*60)
        print(f"Total de archivos procesados: {total_files}")
        print(f"Total de líneas procesadas: {total_lines}")
        print(f"\nDISTRIBUCIÓN:")
        print(f"  🟢 TRAIN:  {len(train_files):3d} archivos ({len(train_files)/total_files:.1%}) → {train_lines:5d} líneas ({train_lines/total_lines:.1%})")
        print(f"  🟡 VALID:  {len(valid_files):3d} archivos ({len(valid_files)/total_files:.1%}) → {valid_lines:5d} líneas ({valid_lines/total_lines:.1%})")
        print(f"  🔴 TEST:   {len(test_files):3d} archivos ({len(test_files)/total_files:.1%}) → {test_lines:5d} líneas ({test_lines/total_lines:.1%})")
        print("="*60)
        
        # Guardar reporte detallado
        report_path = output_dir / 'division_report.txt'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("REPORTE DETALLADO DE DIVISIÓN POR ARCHIVOS\n")
            f.write("="*50 + "\n\n")
            
            f.write(f"ARCHIVOS DE ENTRENAMIENTO ({len(train_files)}):\n")
            for i, file_info in enumerate(train_files, 1):
                f.write(f"  {i:2d}. {file_info['file_path']} ({file_info['count']} líneas)\n")
            
            f.write(f"\nARCHIVOS DE VALIDACIÓN ({len(valid_files)}):\n")
            for i, file_info in enumerate(valid_files, 1):
                f.write(f"  {i:2d}. {file_info['file_path']} ({file_info['count']} líneas)\n")
            
            f.write(f"\nARCHIVOS DE PRUEBA ({len(test_files)}):\n")
            for i, file_info in enumerate(test_files, 1):
                f.write(f"  {i:2d}. {file_info['file_path']} ({file_info['count']} líneas)\n")
        
        logging.info(f"Reporte detallado guardado en: {report_path}")
        
        if error_count > 0:
            logging.warning(f"Se encontraron {error_count} errores durante el procesamiento.")
            print(f"⚠️  Se encontraron {error_count} errores durante el procesamiento.")
            return False
        else:
            logging.info("Proceso completado sin errores.")
            print("✅ El proceso se completó correctamente sin errores.")
            return True
            
    except Exception as e:
        logging.error(f"Error al guardar los archivos de salida: {str(e)}")
        print(f"❌ Error al guardar los archivos de salida: {str(e)}")
        return False

if __name__ == "__main__":
    logging.info("Iniciando proceso de división de datos POR ARCHIVOS")
    result = process_folders()
    if result:
        print("✅ Proceso finalizado con éxito")
    else:
        print("❌ Proceso finalizado con errores")
    logging.info("Proceso finalizado")
