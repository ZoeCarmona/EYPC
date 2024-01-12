import openpyxl
import re
import copy

TRegistros = {"b": "000", "c": "001", "d": "010", "e": "011", "h": "100", "l": "101", "a": "111", "bc": "00",
              "de": "01", "hl": "10", "ix": "10", "iy": "10", "sp": "11", "af": "11"}
ccregistros={"nz": "000","z": "001","nc": "010","c": "011","po": "100",
              "pe": "101","p": "110","m": "111"}
etiquetas_info = {}  # Diccionario para almacenar información de etiquetas
cl = 0   # contador de localidades
detalles_coincidencias = {}  # Diccionario para almacenar detalles de coincidencias

def leer_excel(archivo_excel, columna_expresiones, columna_cl, columna_codigo_binario):
    wb = openpyxl.load_workbook(archivo_excel)
    hoja = wb.active
    expresiones_regulares = {}

    for celda_expresion, celda_cl, celda_codigo_binario in zip(
        hoja[columna_expresiones][1:200],
        hoja[columna_cl][1:200],
        hoja[columna_codigo_binario][1:200]
    ):
        expresion = str(celda_expresion.value)
        codigo_objeto = str(celda_cl.value)
        codigo_binario = str(celda_codigo_binario.value)
        num_fila_excel = celda_expresion.row
        expresiones_regulares[expresion] = (codigo_objeto, codigo_binario, num_fila_excel)

    wb.close()
    return expresiones_regulares

def comparar(archivo_asm, expresiones_regulares):
    global cl
    with open(archivo_asm, 'r', encoding='utf-8', errors='ignore') as f:
        lineas_asm = f.readlines()

    lineas_sin_coincidencias = set(range(1, len(lineas_asm) + 1))
    coincidencias = []  # Almacenar las coincidencias aquí

    for j, linea in enumerate(lineas_asm, start=1):
        if not linea.strip():
            lineas_sin_coincidencias.discard(j)
            continue
        # PARA Etiquetas
        etiqueta_match = re.match(r'^\s*([a-zA-Z_]\w*)\s*:\s*(.*)$', linea)
        if etiqueta_match:
            etiqueta = etiqueta_match.group(1)
            contenido_despues_dos_puntos = etiqueta_match.group(2).strip()

            if etiqueta in etiquetas_info:
                # Si existe, verificar si su valor_cl es menor al cl actual
                if etiquetas_info[etiqueta]['valor_cl'] is None or etiquetas_info[etiqueta]['valor_cl'] < cl:
                    etiquetas_info[etiqueta]['es_declaracion'] = True
                    etiquetas_info[etiqueta]['valor_cl'] = cl
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

        for expresion_regular, (codigo_objeto, codigo_binario, num_fila_excel) in expresiones_regulares.items():
            # Aceptando espacios antes y después de la coma
            expresion_limpia = expresion_regular.strip().lower().replace(',', r'\s*,\s*')

            # Añade anclas de inicio y fin para garantizar una coincidencia completa
            patron = re.compile(rf'^{expresion_limpia}$', re.IGNORECASE | re.UNICODE)
            coincidencia = patron.search(contenido_limpio)

            # Agrega la lógica para manejar los casos de 'jp' y 'jr'
            jp_jr_match = re.match(
                r'^(((jr)\s*(c,|nc,|z,|nz,)?\s*)|((jp)\s*(nz,|z,|nc,|c,|po,|pe,|p,|m,)?\s*)),?\s*([^"]*)\s*$',
                contenido_limpio, re.IGNORECASE)

            if jp_jr_match:
                etiqueta = jp_jr_match.group(8)  # Extrae la etiqueta (el texto entre comillas)
                
                # Comprueba si la etiqueta es un número hexadecimal
                if re.match(r'^([0-9a-fA-F]+)|([0-9a-fA-F]+H)$', etiqueta):
                    
                    es_declaracion = True
                else:
                    
                    es_declaracion = False

                if etiqueta not in etiquetas_info or not etiquetas_info[etiqueta]['es_declaracion']:
                    etiquetas_info[etiqueta] = {
                        'valor_cl': None,
                        'es_declaracion': es_declaracion
                    }

            if coincidencia:
                lineas_sin_coincidencias.discard(j)
                if linea.strip():
                    detalles_coincidencias[j] = {
                        'linea_contenido': linea,
                        'codigo_objeto': codigo_objeto,
                        'Codigo_binario': codigo_binario,
                        'num_fila_excel': num_fila_excel,
                        'Cl_especifico':cl
                    }
                coincidencias.append(
                    (j, linea, codigo_objeto, codigo_binario, num_fila_excel))  # Almacenar la línea, la coincidencia, el código de objeto y el número de fila en el Excel
                if codigo_objeto != 'None':
                    cl += int(codigo_objeto)
    fallo = 0
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
    '''
    print("\nDiccionario de Expresiones Regulares:")
    for expresion, valores in expresiones_regulares.items():
        print(f"Expresión: {expresion}, Valores: {valores}")
    '''
    '''
    print("\nDetalles de coincidencias:")
    for num_linea, detalle in detalles_coincidencias.items():
        print(f"Línea {num_linea}: Contenido: {detalle['linea_contenido'].strip()}, "
              f"Código de objeto: {detalle['codigo_objeto']}, "
              f"Codigo_binario {detalle['Codigo_binario']}, "
              f"Número de fila en Excel: {detalle['num_fila_excel']}")
   '''
def limpiar_linea(linea, etiquetas_info):
    # Eliminar caracteres no imprimibles y espacios en blanco al principio y al final
    linea_limpia = ''.join(c for c in linea if c.isprintable()).strip()

    # Eliminar todo después del punto y coma (;)
    if ';' in linea_limpia:
        linea_limpia = linea_limpia.split(';', 1)[0].strip()

    # Limpiar etiquetas
    for etiqueta, info in etiquetas_info.items():
        if etiqueta + ':' in linea_limpia:
            # Eliminar la etiqueta y los dos puntos
            linea_limpia = linea_limpia.replace(etiqueta + ':', '').strip()

    return linea_limpia
def decimal_a_hexadecimal(decimal):
    try:
        # Convertir el número decimal a hexadecimal y eliminar el prefijo '0x'
        hex_resultado = format(int(decimal), '04x')
        
        return hex_resultado
    except ValueError:
        return "Error: ingrese un número decimal válido de 4 dígitos."
    
def SegundaPasada(etiquetas_info, detalles_coincidencias):
    #primero limpiamos la linea para procesar las lineas bien
    hex_pattern = r'\(([0-9a-fA-F]+h)\)'
    nn =  r',\s*([0-9a-fA-F]+h)'
    expresion = r'(adc|sub|sbc|and|or|xor|cp|adc|dec|inc)'
    numero=r'(\d+)'  
    cc=r'(nz\s*,|z\s*,|nc\s*,|c\s*,|po\s*,|pe\s*,|p\s*,|m\s*,)'
    iyix=r'\((ix|iy)\s*\+\s*[0-9]+\)'
    for num_linea, detalle in detalles_coincidencias.items():
        detalle['linea_contenido'] = limpiar_linea(detalle['linea_contenido'], etiquetas_info)
        if 'jp' in detalle['linea_contenido']:
            print(detalle['linea_contenido'])
            cc_match = re.search(cc, detalle['linea_contenido'])
            if cc_match:
                condicion=cc_match.group()
                condicion=condicion.replace(",","")
                if condicion in ccregistros:
                    detalle['Codigo_binario'] = detalle['Codigo_binario'].replace('cc', ccregistros[condicion])

            for etiqueta, info in etiquetas_info.items():
                if etiqueta in detalle['linea_contenido']:
                    
                    cl=info['valor_cl']
                    cl=str(cl).zfill(4)
                    cl=decimal_a_hexadecimal(cl)
                    
                    mitad = len(cl) // 2
                    parte1 = cl[:mitad]+"&"
                    parte2 = cl[mitad:]+"&"
                    detalle['Codigo_binario'] = detalle['Codigo_binario'].replace('n', parte2,1).replace('n', parte1,1) 
                    
        if 'jr' in detalle['linea_contenido']:
            print(detalle['linea_contenido'])
            print("entre en caso de jr")
            for etiqueta, info in etiquetas_info.items():
                if etiqueta in detalle['linea_contenido']:
                    codigosig=detalle['Cl_especifico']+int(detalle['codigo_objeto'])
                    cl=(info['valor_cl'])-codigosig
                    cl=str(cl).zfill(4)
                    cl=decimal_a_hexadecimal(cl)
                    
                    detalle['Codigo_binario'] = detalle['Codigo_binario'].replace('e-2', cl)  
                
        
      
        match = re.search(expresion, detalle['linea_contenido'])
        if match: 
            detalle['linea_contenido'] = re.sub(expresion, '', detalle['linea_contenido'])
            match = re.match(r'\s(a|b|c|d|e|h|l)', detalle['linea_contenido'])
            if match:   
                # Recuperar las letras y almacenarlas en las variables r
                r = match.group(1)
                detalle['Codigo_binario'] = detalle['Codigo_binario'].replace('r', r, 1)
            match = re.match(r'add\s(a|b|c|d|e|h|l)', detalle['linea_contenido'])
            for x in ['a', 'b', 'c', 'd', 'e', 'h', 'l']:
                if x in detalle['linea_contenido']:
                    detalle['Codigo_binario'] = detalle['Codigo_binario'].replace('r', x)
            
        if 'ld' in detalle['linea_contenido']:
            print(detalle['linea_contenido'])
            match = re.match(r'ld\s(a|b|c|d|e|h|l),(a|b|c|d|e|h|l)', detalle['linea_contenido'])
            if match:   
                r = match.group(1)
                t = match.group(2)
                detalle['Codigo_binario'] = detalle['Codigo_binario'].replace('r', r, 1).replace('r', t, 1)
            match = re.match(r'ld\s(a|b|c|d|e|h|l),(a|b|c|d|e|h|l)', detalle['linea_contenido'])
            for x in ['a', 'b', 'c', 'd', 'e', 'h', 'l']:
                if x in detalle['linea_contenido']:
                    detalle['Codigo_binario'] = detalle['Codigo_binario'].replace('r', x)
            hex_match = re.search(hex_pattern, detalle['linea_contenido'])
            if hex_match:
                print("entre a caso hexa")
                hex_char = hex_match.group()
                hex_char=hex_char.strip('()').replace('h',"")
                hex_char = hex_char.zfill(4)
                mitad = len(hex_char) // 2
                parte1 = hex_char[:mitad]+"&"
                parte2 = hex_char[mitad:]+"&"
                detalle['Codigo_binario'] = detalle['Codigo_binario'].replace('n', parte2,1).replace('n', parte1,1)
            nn_match = re.search(nn, detalle['linea_contenido'])
            if nn_match:
                print("entre a caso nn")
                nn=nn_match.group()
                nn=nn.replace('h',"").replace(",","")
                nn = nn.zfill(4)
                
                print(nn)
                mitad = len(nn) // 2
                parte1 = nn[:mitad]+"&"
                parte2 = nn[mitad:]+"&"
                
                detalle['Codigo_binario'] = detalle['Codigo_binario'].replace('n', parte2,1).replace('n', parte1,1)
            num_match = re.search(numero, detalle['linea_contenido'])
            if num_match:
                print("entre a caso num")      
                num=num_match.group()
                num=num.replace(",","")
                num=num.zfill(2)+"&"
                print(detalle['Codigo_binario'],"------------")
                detalle['Codigo_binario'] = detalle['Codigo_binario'].replace('n', num)
                
        iyix_match = re.search(iyix, detalle['linea_contenido'])
        if iyix_match:
            iy_ix=iyix_match.group()
            iy_ix=iy_ix.strip('()').replace("ix+","").replace("iy+","")
            iy_ix = iy_ix.zfill(2)+"&"
            print(iy_ix)
            detalle['Codigo_binario'] = detalle['Codigo_binario'].replace('d', iy_ix)
        numeromatch=re.search(numero, detalle['linea_contenido'])
        if numeromatch:
            numer=numeromatch.group()
            numer=numer.zfill(2)+"&"
            detalle['Codigo_binario'] = detalle['Codigo_binario'].replace('n', numer)
    for num_linea, detalle in detalles_coincidencias.items():
        detalle['Codigo_binario'] = detalle['Codigo_binario'].split(',')
    for num_linea, detalle in detalles_coincidencias.items():
        for i in range(len(detalle['Codigo_binario'])):
            
            # Verificar si hay un '&' en el valor
            if '&' in detalle['Codigo_binario'][i]:
                # Si hay un '&', simplemente quitarlo
                detalle['Codigo_binario'][i] = detalle['Codigo_binario'][i]
                
            else:
                for caracter in detalle['Codigo_binario'][i]:
                    if caracter in TRegistros:
                        detalle['Codigo_binario'][i] = detalle['Codigo_binario'][i].replace(caracter, TRegistros[caracter])
    for num_linea, detalle in detalles_coincidencias.items():
        for i in range(len(detalle['Codigo_binario'])):
            if '&' in detalle['Codigo_binario'][i]:
                # Si hay un '&', simplemente quitarlo en el diccionario
                detalle['Codigo_binario'][i] = detalle['Codigo_binario'][i].replace('&', '')
            else:
                # Convertir a hexadecimal y actualizar en el diccionario
                detalle['Codigo_binario'][i] = binario_a_hexadecimal(detalle['Codigo_binario'][i])
                  
def binario_a_hexadecimal(binario):
    try:
        # Verificar si la cadena binaria está vacía
        if not binario:
            return ""

        # Verificar si la cadena binaria tiene menos de 8 dígitos
        if len(binario) < 8:
            return binario

        # Convertir binario a decimal y luego a hexadecimal
        decimal = int(binario, 2)
        hexadecimal = format(decimal, '02x')

        return hexadecimal
    except ValueError as e:
        return str(e)
                  
if __name__ == "__main__":
    archivo_excel = 'TablaNemonicos.xlsx'
    columna_expresiones = 'B'
    columna_cl = 'C'
    columna_codigo_binario = 'D'
    archivo_asm = 'archivo3.asm'

    expresiones_regulares = leer_excel(archivo_excel, columna_expresiones, columna_cl, columna_codigo_binario)
    comparar(archivo_asm, expresiones_regulares)  
    print("-------------------------------------")
    for etiqueta, info in etiquetas_info.items():
        print(f"Etiqueta: {etiqueta}, Valor_CL: {info['valor_cl']}, Es_Declaracion: {info['es_declaracion']}")
    print("-------------------------")


    detalles_coincidencias_copia = copy.deepcopy(detalles_coincidencias)


    SegundaPasada(etiquetas_info,detalles_coincidencias)
    print("-------------------------------------------")
    for num_linea, detalle in detalles_coincidencias.items():
            print(f"Línea {num_linea}: Contenido: {detalle['linea_contenido'].strip()}, "
                f"Codigo_binario {detalle['Codigo_binario']},"
                f"Cl especifico  {detalle['Cl_especifico']}, "
                f"Cl especifico  {detalle['num_fila_excel']}, ")
