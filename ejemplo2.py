import openpyxl
import re

TRegistros = {"B": "000", "C": "001", "D": "010", "E": "011", "H": "100", "L": "101", "A": "111", "BC": "00",
              "DE": "01", "HL": "10", "IX": "10", "IY": "10", "SP": "11", "AF": "11"}
etiquetas_info = {}  # Diccionario para almacenar información de etiquetas
cl = 0   # contador de localidades

def leer_excel(archivo_excel, columna_expresiones, columna_cl):
    wb = openpyxl.load_workbook(archivo_excel)
    hoja = wb.active
    expresiones_regulares = {
        str(celda_expresion.value): (str(celda_cl.value), celda_expresion.row) for celda_expresion, celda_cl in
        zip(hoja[columna_expresiones][1:316], hoja[columna_cl][1:316])}
    wb.close()
    return expresiones_regulares

def comparar(archivo_asm, expresiones_regulares):
    global cl
    with open(archivo_asm, 'r', encoding='utf-8', errors='ignore') as f:
        lineas_asm = f.readlines()

    lineas_sin_coincidencias = set(range(1, len(lineas_asm) + 1))
    coincidencias = []  # Almacenar las coincidencias aquí

    for j, linea in enumerate(lineas_asm, start=1):
        # PARA Etiquetas
        etiqueta_match = re.match(r'^\s*([a-zA-Z_]\w*)\s*:\s*(.*)$', linea)
        if etiqueta_match:
            etiqueta = etiqueta_match.group(1)
            contenido_despues_dos_puntos = etiqueta_match.group(2).strip()

            if etiqueta in etiquetas_info:
                # Si existe, verificar si su valor_cl es menor al cl actual
                if etiquetas_info[etiqueta]['valor_cl'] is None or etiquetas_info[etiqueta]['valor_cl'] < cl:
                    etiquetas_info[etiqueta]['es_declaracion'] = True
                    
            else:
                # Si no existe, agregar la información de la etiqueta al diccionario
                etiquetas_info[etiqueta] = {
                    'valor_cl': cl,
                    'es_declaracion': True
                }                
            

        else:
            etiqueta = None
            contenido_despues_dos_puntos = linea.strip()

        # Detener la comparación al encontrar un punto y coma
        if ';' in contenido_despues_dos_puntos:
            contenido_despues_dos_puntos = contenido_despues_dos_puntos.split(';', 1)[0].strip()

        # Elimina espacios y convierte a minúsculas a mayúsculas
        contenido_limpio = contenido_despues_dos_puntos.lower()

        for expresion_regular, (codigo_objeto, num_fila_excel) in expresiones_regulares.items():
            # Aceptando espacios antes y después de la coma
            expresion_limpia = expresion_regular.strip().lower().replace(',', r'\s*,\s*')

            # Añade anclas de inicio y fin para garantizar una coincidencia completa
            patron = re.compile(rf'^{expresion_limpia}$', re.IGNORECASE | re.UNICODE)
            coincidencia = patron.search(contenido_limpio)

            # Agrega la lógica para manejar los casos de 'jp' y 'jr'
            jp_jr_match = re.match(
                r'^(((jr)\s*(c|nc|z|nz)?\s*)|((jp)\s*(nz|z|nc|c|po|pe|p|m)?\s*)),?\s*([^"]*)\s*$',
                contenido_limpio, re.IGNORECASE)
            if jp_jr_match:
                etiqueta = jp_jr_match.group(8)  # Extrae la etiqueta (el texto entre comillas)
                if etiqueta not in etiquetas_info or not etiquetas_info[etiqueta]['es_declaracion']:
                    etiquetas_info[etiqueta] = {
                        'valor_cl': None,
                        'es_declaracion': False
                    }
            if coincidencia:
                lineas_sin_coincidencias.discard(j)
                coincidencias.append(
                    (j, linea, codigo_objeto, num_fila_excel))  # Almacenar la línea, la coincidencia, el código de objeto y el número de fila en el Excel
                '''  esto nos va servir luego 
                print(
                    f"Línea {coincidencia.start() + 1}: {linea.strip()}, Código de objeto: {codigo_objeto}, Número de fila en Excel: {num_fila_excel}")
                print(codigo_objeto)
                '''
                if codigo_objeto != 'None':
                    cl += int(codigo_objeto)
    fallo=0
    for etiqueta, info in etiquetas_info.items():
        if info['es_declaracion'] is False:
            print(f"Error: ({etiqueta})--->  esta etiqueta no esta definida  en el programa")
            fallo = 1

    if lineas_sin_coincidencias:
        print("\nNo se encontraron coincidencias en las siguientes líneas:")
        for linea_sin_coincidencia in lineas_sin_coincidencias:
            print(f"Línea {linea_sin_coincidencia}: {lineas_asm[linea_sin_coincidencia - 1].strip()}")
    else:
        if fallo != 1:
            print("\n -------- Pasada numero 1 completada ")

def SegundaPasada():
    x=7

if __name__ == "__main__":
    archivo_excel = 'Tabla_neumonicos.xlsx'
    columna_expresiones = 'B'
    columna_cl = 'L'
    archivo_asm = 'archivo.asm'

    expresiones_regulares = leer_excel(archivo_excel, columna_expresiones, columna_cl)
    comparar(archivo_asm, expresiones_regulares)
    print(etiquetas_info)
 