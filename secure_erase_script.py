import os
import json
from collections import defaultdict
import datetime

def normalizar_texto(texto):
    return ' '.join(texto)
    #return ' '.join(texto).lower()

def eliminar_duplicados_automaticamente(carpeta_base, carpeta_prioritaria="nuevos_andres check 2"):
    sentencias = defaultdict(list)  # clave: sentencia -> lista de (ruta, línea, entrada_completa)
    print(f"🔍 Buscando duplicados en: {carpeta_base}")
    print(f"🌟 Carpeta prioritaria: {carpeta_prioritaria}")
    
    # Paso 1: Recopilar todas las sentencias y sus ubicaciones
    archivos_procesados = 0
    lineas_procesadas = 0
    
    for root, _, files in os.walk(carpeta_base):
        for archivo in files:
            if archivo.endswith('.json'):
                ruta = os.path.join(root, archivo)
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        lineas = f.readlines()
                        for num_linea, linea in enumerate(lineas, start=1):
                            if not linea.strip():
                                continue
                            try:
                                entrada = json.loads(linea)
                                clave = normalizar_texto(entrada['sentencia'])
                                # Guardamos si el archivo está en la carpeta prioritaria
                                es_prioritario = carpeta_prioritaria in ruta
                                sentencias[clave].append((ruta, num_linea, linea.strip(), es_prioritario))
                                lineas_procesadas += 1
                            except json.JSONDecodeError as e:
                                print(f"[ERROR] JSON mal formado en {ruta}, línea {num_linea}: {e}")
                except Exception as e:
                    print(f"[ERROR] No se pudo leer {ruta}: {e}")
                archivos_procesados += 1
    
    print(f"✅ Procesados {archivos_procesados} archivos con {lineas_procesadas} líneas JSON.")
    
    # Paso 2: Filtrar las sentencias que aparecen en más de un archivo o en varias líneas
    duplicadas = {s: ubicaciones for s, ubicaciones in sentencias.items() if len(ubicaciones) > 1}

    if not duplicadas:
        print("✅ No se encontraron sentencias duplicadas entre archivos.")
        return

    # Paso 3: Organizar las eliminaciones (dando prioridad a la carpeta especificada)
    print(f"🔁 Se encontraron {len(duplicadas)} sentencias duplicadas.")
    
    # Agrupar por archivo para minimizar el número de operaciones de escritura
    cambios_por_archivo = defaultdict(list)
    total_a_eliminar = 0
    
    # Para el reporte
    reporte = []
    
    for sentencia, ocurrencias in duplicadas.items():
        # Verificar si hay alguna ocurrencia en la carpeta prioritaria
        ocurrencias_prioritarias = [o for o in ocurrencias if o[3]]  # o[3] es el flag es_prioritario
        
        if ocurrencias_prioritarias:
            # Si hay ocurrencias en la carpeta prioritaria, conservamos la primera de ellas
            conservar = ocurrencias_prioritarias[0]
            # Eliminamos todas las demás que NO estén en la carpeta prioritaria
            eliminar = [o for o in ocurrencias if not o[3]]
            # Añadimos también las duplicadas dentro de la carpeta prioritaria, excepto la primera
            eliminar.extend(ocurrencias_prioritarias[1:])
        else:
            # Si no hay ocurrencias en la carpeta prioritaria, comportamiento original:
            # conservamos la primera ocurrencia
            conservar = ocurrencias[0]
            # eliminamos las demás
            eliminar = ocurrencias[1:]
        
        # Crear entradas para el reporte
        for archivo, linea, contenido, _ in eliminar:
            reporte.append({
                "archivo": archivo,
                "linea": linea,
                "contenido": contenido,
                "conservada_en": f"{conservar[0]}, línea {conservar[1]}"
            })
            cambios_por_archivo[archivo].append(linea)
            total_a_eliminar += 1
    
    print(f"⚠️ Se eliminarán {total_a_eliminar} entradas duplicadas, priorizando mantener la carpeta '{carpeta_prioritaria}'.")
    
    # Paso 4: Realizar las eliminaciones
    archivos_modificados = 0
    lineas_eliminadas = 0
    
    for archivo, lineas_a_eliminar in cambios_por_archivo.items():
        try:
            # Ordenar líneas en orden descendente para eliminar desde el final
            lineas_a_eliminar.sort(reverse=True)
            
            with open(archivo, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
            
            # Eliminar las líneas marcadas (ajustando el índice porque las líneas comienzan en 1)
            for linea_num in lineas_a_eliminar:
                del lineas[linea_num - 1]
                lineas_eliminadas += 1
            
            # Escribir el archivo actualizado
            with open(archivo, 'w', encoding='utf-8') as f:
                f.writelines(lineas)
            
            archivos_modificados += 1
            
        except Exception as e:
            print(f"[ERROR] Error al modificar el archivo {archivo}: {e}")
    
    # Paso 5: Generar reporte
    ahora = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nombre_reporte = f"reporte_duplicados_{ahora}.txt"
    
    # Agrupar por archivo para el reporte
    reporte_por_archivo = defaultdict(list)
    for item in reporte:
        reporte_por_archivo[item["archivo"]].append(item)
    
    with open(nombre_reporte, 'w', encoding='utf-8') as f:
        f.write(f"REPORTE DE ELIMINACIÓN DE DUPLICADOS\n")
        f.write(f"Fecha y hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Carpeta prioritaria: {carpeta_prioritaria}\n")
        f.write(f"Total de sentencias duplicadas: {len(duplicadas)}\n")
        f.write(f"Total de entradas eliminadas: {lineas_eliminadas}\n")
        f.write(f"Total de archivos modificados: {archivos_modificados}\n\n")
        
        f.write("DETALLE DE ELIMINACIONES POR ARCHIVO:\n")
        f.write("=" * 80 + "\n\n")
        
        for archivo, items in reporte_por_archivo.items():
            f.write(f"ARCHIVO: {archivo}\n")
            f.write("-" * 80 + "\n")
            
            for item in items:
                f.write(f"• Línea {item['linea']}: {item['contenido']}\n")
                f.write(f"  Conservada en: {item['conservada_en']}\n\n")
            
            f.write("\n")
    
    print(f"\n✅ Proceso completado: {archivos_modificados} archivos modificados, {lineas_eliminadas} líneas eliminadas.")
    print(f"📝 Se ha generado un reporte detallado en: {nombre_reporte}")

if __name__ == "__main__":
    carpeta_actual = os.getcwd()
    eliminar_duplicados_automaticamente(carpeta_actual)
