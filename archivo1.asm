ld hl, 0070h; cargamos hl en la localidad 2000h
ld b, (hl); cargamos el número de letras que desean ingresar, guardando ese número en el registro b
ld d,0; me ayudará para guardar la localidad de l (al encontrar palabra) (primera parte de la localidad)
ld e,0; me ayudará para escribir localidad de h (al encontrar palabra) (segunda parte de la localidad)
ld iy, 00a0h; cargamos iy en localida 00a0h para ahí guardar localidades donde se encuentran palabras 
ld c, 0; cargamos registro c con 0, siendo este nuestro contador
comparar: ld a,0; cargamos registro a con 0
          cp b; realizando comparación
          jp z, fin; si comparación es cero (iguales), nos vamos a fin (caso en el que el arreglo no tenga nada con que comparar)
          ld a, (0080h); guarda lo que hay en la localidad 0080h ("h" ó 48h) en registro a
          inc (hl); estamos en siguiente localidad de memoria 
          cp (hl); comparamos la letra "h" con la letra que se encuentre en esa localidad
          jp nz, again; si comparación no es cero (no son iguales), nos vamos a again
          ld e, l;
		  ld d, h;
          dec b; decrementamos el número de letras que 
          ld a,0; cargamos registro a con 0
          cp b; realizando comparación
          jp z, fin; si comparación es cero (iguales), nos vamos a fin
          ld a, (0081h);  guarda lo que hay en la localidad 1001h ("o" ó 4fh) en registro a
          inc (hl); estamos en siguiente localidad de memoria 
          cp (hl); comparamos la letra "o" con la letra que se encuentre en localidad 2...h
          jp nz, again; si comparación no es cero (no son iguales), nos vamos a again
          dec b; decrementamos el número de letras que 
          ld a,0; cargamos registro a con 0
          cp b; realizando comparación
          jp z, fin; si comparación es cero (iguales), nos vamos a fin
          ld a, (0082h);  guarda lo que hay en la localidad 1002h ("l" ó 4ch) en registro a
          inc (hl); estamos en siguiente localidad de memoria 
          cp (hl); comparamos la letra "l" con la letra que se encuentre en localidad 2...h
          jp nz, again; si comparación no es cero (no son iguales), nos vamos a again
          dec b; decrementamos el número de letras que 
          ld a,0; cargamos registro a con 0
          cp b; realizando comparación
          jp z, fin; si comparación es cero (iguales), nos vamos a fin
          ld a, (0083h);  guarda lo que hay en la localidad 1003h ("a" ó 41h) en registro a
          inc (hl); estamos en siguiente localidad de memoria 
          cp (hl); comparamos la letra "a" con la letra que se encuentre en localidad 2...h
          jp nz, again; si comparación no es cero (no son iguales), nos vamos a again
          jp contador; saltamos a contador para aumentarlo ya que encontró una palabra
again:    dec b; decrementamos el número de letras que ingresamos
          jp comparar; vamos a comparar
contador: inc c; incrementamos nuestro contador (nos guarda cuantos "hola" ha encontrado)
		  inc iy; pasamos a la siguiente localidad para guardar nuevas localidades
          inc iy; pasamos a siguiente localidad para guardar nuevas localidades
          jp again; vamos a again para ver si existen más localidades por comparar, si no es el caso, nos mandará a fin
fin:      ld a,c; guardamos nuestro contador en registro a
          ld (0090h), a; cargamos nuestro contador en localidad 0070h
          halt; fin del programa
