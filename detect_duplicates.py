def normalizar_texto(texto):
    return ' '.join(texto)
    #return ' '.join(texto).lower()

def detectar_duplicados_en_subcarpetas(carpeta_base):
    sentencias = defaultdict(list)  # clave: sentencia -> lista de (ruta, línea)

    for root, _, files in os.walk(carpeta_base):
        for archivo in files:
            if archivo.endswith('.json'):
                ruta = os.path.join(root, archivo)
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        for num_linea, linea in enumerate(f, start=1):
                            if not linea.strip():
                                continue
                            try:
                                entrada = json.loads(linea)
                                clave = normalizar_texto(entrada['sentencia'])
                                sentencias[clave].append((ruta, num_linea))
                            except json.JSONDecodeError as e:
                                print(f"[ERROR] JSON mal formado en {ruta}, línea {num_linea}: {e}")
                except Exception as e:
                    print(f"[ERROR] No se pudo leer {ruta}: {e}")

    # Filtrar las sentencias que aparecen en más de un archivo o en varias líneas
    duplicadas = {s: ubicaciones for s, ubicaciones in sentencias.items() if len(ubicaciones) > 1}

    if not duplicadas:
        print("✅ No se encontraron sentencias duplicadas entre archivos.")
    else:
        print("🔁 Sentencias duplicadas encontradas:\n")
        for sentencia, ocurrencias in duplicadas.items():
            print(f"- Sentencia: \"{sentencia}\"")
            for archivo, linea in ocurrencias:
                print(f"  ↳ Archivo: {archivo}, línea: {linea}")
            print()

if __name__ == "__main__":
    carpeta_actual = os.getcwd()
    detectar_duplicados_en_subcarpetas(carpeta_actual)

