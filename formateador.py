
class MustExecuteAsScript(Exception):
    def __init__(self, mensaje):
        self.mensaje = mensaje
        
    pass

class NotPythonFile(Exception):
    def __init__(self, mensaje):
        self.mensaje = mensaje
        
    pass

class NotOnFormatter(Exception):
    def __init__(self, mensaje):
        self.mensaje = mensaje
        
    pass

if __name__ != '__main__':
    raise MustExecuteAsScript('DEBE EJECUTARSE COMO UN SCRIPT Y NO COMO UN MODULO.')

import re, sys, logging

archivo = sys.argv[1]
if archivo.endswith('formateador.py'):
    raise NotOnFormatter('EL FORMATEADOR NO PUEDE FORMATEARSE A SI MISMO ¿¿¿ACASO QUIERES QUE EL UNIVERSO EXPLOTE???')

if not archivo.endswith('.py'):
    raise NotPythonFile('EL ARCHIVO A FORMATEAR DEBE SER UN ARCHIVO DE PYTHON.')

    re_string = re.compile(r'''
\'\'\'.*?\'\'\'| # triples comillas simples y todo lo que esté dentro (non-greedy)
""".*?"""| # triples comillas dobles y todo lo que esté dentro de ellas (non-greedy)
\'.*?\'| # comillas simples y todo lo que esté dentro de ellas (non-greedy)
\".*?\" #comillas dobles y todo lo que esté dentro de ellas (non-greedy)
''',
re.VERBOSE)


    # aqui estarán las ubicaciones de los pares de comillas en el string
    # where
    ubicacion_comillas = [[comillas.start(), comillas.end() - 1] for comillas in re_string.finditer(string_where)]

    lista_caracteres = list(string_where)
    for indice, caracter in enumerate( lista_caracteres ):
        if caracter == ' ':

            # esto significa que el caracter está dentro de una comilla multilineas

            try:
                if lista_caracteres[indice + 1] == ' ':
                    if ubicacion_comillas:
                        # en inicio y fin se guarda donde empiezan
                        # y terminan los pares de comillas 
                        
                        for inicio, fin in ubicacion_comillas:
                            
                            # si el indice del caracter actual es mayor que el inicio del par
                            # de comillas actuales y tambien es menor que el fin del mismo
                            # par de comillas, significa que el espacio doble está dentro
                            # de comillas y por lo tanto no se sustituye el espacio
                            if indice > inicio:
                                if indice < fin:
                                    break
                                # si el indice es mayor al inicio, pero menor al fin de las
                                # comillas, convierte el caracter indice en nada('  ')
                                elif indice > fin:
                                    lista_caracteres[indice] = ''
                            # si el indice es menor al inicio de las
                            # comillas, convierte el caracter actual en nada('')
                            elif indice < inicio:
                                lista_caracteres[indice] = ''
                    # si ubicacion comillas está vacio, entonces el caracter actual
                    # se convierte en nada ('')
                    elif not ubicacion_comillas:
                        lista_caracteres[indice] = ''

            # si da error de indice (si el caracter actual es el ultimo caracter),
            # break
            except IndexError:
                break

    # ahora string_where es la lista de caracteres modificada con los espacios dobles
    # quitados
    string_where = ''.join( lista_caracteres )
    # print(string_where)
    # print()

    return string_where



# añade un espacio antes y despues de la ubicacion de todas las 
# coincidencias de regex
# toma como parametros una lista de strings, la expresion regular a buscar 
# en esos strings y una excepcion que impedira que se añada el espacio
# antes o despues
def añadir_espacios(list_string_where, re_target, re_excepciones = None, despues = True, antes = True ):

    # la funcion lanza una excepcion si el primer argumento posicional
    # no es una lista
    assert antes or despues, 'SI NO QUERIAS ESPACIOS, PARA QUE LLAMAS LA FUNCION'
    if isinstance(list_string_where, list):
        logging.basicConfig(level = logging.INFO, filename = 'formateo.log', filemode='w', format = 'INFORMACION: %(asctime)s %(message)s')
        # !!! ERRORJ: esto no encuentra comillas triples multi_start, en su lugar encuentra solo las dos primeras comillas. debo resolver este error
        re_string = re.compile(r'''
\'\'\'.*?\'\'\'| # triples comillas simples y todo lo que esté dentro (non-greedy)
""".*?"""| # triples comillas dobles y todo lo que esté dentro de ellas (non-greedy)
""".*| # comillas dobles triples y multi_start
\'\'\'.*| # comillas triples simples y multi_start
\'.*?\'| # comillas simples y todo lo que esté dentro de ellas (non-greedy)
\".*?\" #comillas dobles y todo lo que esté dentro de ellas (non-greedy)
    ''',
    re.VERBOSE)



        # buscar comentarios
        re_sharp = re.compile(r'#.*')
        strings = []
        multi_type = False

        # recorre la lista dada como argumento. el elemento actual de la
        # lista de strings a partir de ahora será llamado string actual
        for indice, string_where in enumerate( list_string_where ):
            continuar = False
            multi_start = False
            multi_end = False
            comillas_ubicacion = []
            # este es el string_where sin cambios. se usará para comparar con el string_where modificado mas tarde
            original_string = string_where
            # string_where es el string_where pero sin los espacios de indentacion
            string_where, indent_count = guardar_indentacion(string_where) 
            # aqui estarán las ubicaciones de los pares de comillas en 
            # el string where


            if multi_type and not multi_type in string_where:
                strings.append(string_where)
                # print(f'multilinea indeterminada: {indice + 1}')
                # continuar = True
                continue

            for coincidencia in re_string.finditer(string_where):
                texto = string_where[coincidencia.start(): coincidencia.end()]

                if multi_type:
                    if multi_type == '\'\'\'':
                        re_multiend = re.compile('.*?\'\'\'')
                    elif multi_type == '"""':
                        re_multiend = re.compile('.*?"""')
                # si existe multi_type quiere decir que se encontró comilla multilinea
                # entonces al entrar en este bucle verificará si la coincidencia
                # termina con lo que empieza la multilinea, y si es asi multi_end es
                # igual a el end de esa coincidencia

                    # de lo contrario, continua con la otra linea
                    # verifica que la multilinea termine en la linea actual
                    if multi_type in string_where:
                    # este es el indice del caracter donde termina la comilla multilinea
                        # print(f'multilinea acaba en linea {indice + 1}')
                        multi_end = re_multiend.search(string_where).end() - 1
                        multi_type = False


                elif texto.startswith('\'\'\''):
                    if not texto.endswith('\'\'\''):
                        # print(f'multilinea simple: {indice + 1}')
                        multi_start = coincidencia.start()
                        multi_type = '\'\'\''
                        break

                    else:
                        comillas_ubicacion.append([coincidencia.start(), coincidencia.end() - 1])
                        multi_type = False


                elif texto.startswith('"""'):

                    if not texto.endswith('"""'):
                        # print(f'multilinea doble: {indice + 1}')
                        multi_start = coincidencia.start()
                        multi_type = '"""'
                        break

                    else:
                        comillas_ubicacion.append([coincidencia.start(), coincidencia.end() - 1])
                        multi_type = False

                else:
                    comillas_ubicacion.append([coincidencia.start(), coincidencia.end() - 1])


            # aqui se guardarán las ubicaciones de los comentarios. 
            # solo se añadirá su ubicacion si el comentario comienza antes de unas comillas 
            # o termina luego del final de las comillas
            comentarios = []

            # si el string multilinea comienza al principio de la linea, 
            # no vale la pena intentar cambiar algo, asi que de una salta a la siguiente linea


            if comillas_ubicacion:
                for inicio, fin in comillas_ubicacion:
                    for comentario in re_sharp.finditer(string_where):
                        if comentario.start() == 0:
                            comentarios.append(comentario.start())
                            continue
                        elif comentario.start() > fin or comentario.start() < inicio :
                            continue
                        else:
                            break
                        # si se ejecuta este else, quiere decir que el bucle for no breakeo y 
                        # por lo tanto el sharp estaba dentro de un par de comillas, asi
                        # que sigue con el siguiente sharp encontrado en la linea actual
                    else:
                        continue
                    comentarios.append(comentario.start())

                        # añade el inicio del comentario

            else:
                for comentario in re_sharp.finditer(string_where):
                    if comentario.start() == 0:
                        comentarios.append(comentario.start())
                        continue

                    # añade el inicio del comentario
                    comentarios.append(comentario.start())



            ubicacion_re = []
            # aqui van el indice del elemento de antes y despues 
            # de la coincidencia
            if re_excepciones:
                caracter_antes = []
                caracter_despues = []
            
            for encontrado in re_target.finditer(string_where):
                if comentarios:
                    for comentario in comentarios:
                        if encontrado.start() > comentario:
                            break
                    else:
                        if multi_start != False and encontrado.start() > multi_start:
                            continue
                        elif multi_end != False and encontrado.start() < multi_end:
                            continue
                        ubicacion_re.append(encontrado.start())
                        if re_excepciones:
                            caracter_antes.append(encontrado.start()-1)
                            caracter_despues.append(encontrado.start() + 1)
                else:
                    if multi_start != False and encontrado.start() > multi_start:
                        continue
                    elif multi_end != False and encontrado.start() < multi_end:
                        continue
                    ubicacion_re.append(encontrado.start())
                    if re_excepciones:
                        caracter_antes.append(encontrado.start()-1)
                        caracter_despues.append(encontrado.start() + 1)


                # si se definio una excepcion en la llamada de la
                # funcion, el indice del caracter que le antecede y el que
                # le sigue se añaden a dos arrais


            # convierte en una lista el string actual
            caracteres_str = list(string_where)

            # si se añadio una regex como excepcion
            if re_excepciones:
                # comprueba si los caracteres de antes y despues de las coincidencias
                # son coincidencia de la regex re_excepciones
                if antes:
                    for posicion in caracter_antes: 
                        # si el caracter de antes es menor que 0, se producirá un error al
                        # intentar agregar un espacio porque no existe.
                        # para soluciionarlo, verifico si (posicion) es menor que
                        # 0 

                        if posicion == -1:
                            caracteres_str[0] = ' ' + caracteres_str[0]
                            continue



                        for inicio, fin in comillas_ubicacion:


                            # si encuentra la coincidencia pero esta se encuentra dentro
                            # de comillas, no la agrega al array y por lo tanto no
                            # se le agregan espacios a los lados
                            if posicion < fin and posicion > inicio:
                                break

                        else:
                            excepcion_antes = re_excepciones.search(caracteres_str[posicion])
                            # de ser asi, suma el espacio despues del elemento anterior-1 al
                            # elemento coincidencia, para que quede justo antes del elemento anterior
                            if excepcion_antes:
                                # si el caracter que antecede al caracter antes de re_target es
                                # un espacio, no se añade otro nuevo espacio
                                if not caracteres_str[ posicion-1] == ' ':
                                    caracteres_str[posicion-1] += ' '
                            elif not excepcion_antes:
                                # si el caracter que antecede al caracter despues de re_target es
                                # un espacio, no se añade otro nuevo espacio
                                if not caracteres_str[ posicion ] == ' ':
                                    caracteres_str[posicion ] += ' '

                        continue

                if despues:
                    for posicion in caracter_despues: 
                        if posicion > len(caracteres_str) - 1 :
                            caracteres_str[posicion - 1] += ' '
                            break
                             
                        for inicio, fin in comillas_ubicacion:


                            # si encuentra la coincidencia pero esta se encuentra dentro
                            # de comillas, no la agrega al array y por lo tanto no
                            # se le agregan espacios a los lados
                            if posicion < fin and posicion > inicio:
                                break
                        else:
                            excepcion_despues = re_excepciones.search(caracteres_str[posicion])
                            # aqui añade el espacio despues del elemento conincidencia
                            # haciendo lo contrario a lo anterior
                            if excepcion_despues:
                                # si el caracter que sigue al caracter despues de re_target es
                                # un espacio, no se añade otro nuevo espacio
                                if not caracteres_str[ posicion + 1] == ' ':
                                    caracteres_str[posicion] += ' '
                                    
                            elif not excepcion_despues:
                                # si el caracter que sigue al re_target es
                                # un espacio, no se añade otro nuevo espacio
                                if not caracteres_str[ posicion] == ' ':
                                    caracteres_str[posicion-1] += ' '

                            
                        
            # si no hay re_excepciones
            elif not re_excepciones:
                # añade el espacio justo antes y despues del elemento coincidencia
                for coordenada in ubicacion_re:
                    for inicio, fin in comillas_ubicacion:


                        # si encuentra la coincidencia pero esta se encuentra dentro
                        # de comillas, no la agrega al array y por lo tanto no
                        # se le agregan espacios a los lados
                        if coordenada < fin  and coordenada > inicio:
                            break
                    else:
                
                        if antes:
                            if coordenada == 0:
                                caracteres_str[coordenada] = ' ' + caracteres_str[coordenada]
                                continue
                            # si el caracter que antecede al re_target es
                            # un espacio, no se añade otro nuevo espacio
                            elif not caracteres_str[ coordenada-1] == ' ':
                                caracteres_str[coordenada-1] += ' '

                        if despues:
                            if len(caracteres_str) > coordenada + 1:
                            # si el caracter que sigue al re_target es
                            # un espacio, no se añade otro nuevo espacio
                                if not caracteres_str[ coordenada + 1] == ' ':
                                    caracteres_str[coordenada] += ' '

            # añade al array strings el string actual, pero con los espacios
            caracteres_str = ''.join( caracteres_str ) 
            # si string_where empieza con espacios, remueve esos espacios del principio
            # (para que no sean removidos por el otro while de espacios dobles) y suma 1 
            # a un contador para agregar de nuevo esos espacios luego de las sustituciones

                
            

            if multi_start:
                if multi_start == 0:
                    sin_espacios = caracteres_str
                else:
                    antes_inicio = caracteres_str[: multi_start ]
                    despues_inicio = caracteres_str[multi_start: ]
                    # print(f'antes_inicio = {antes_inicio}: despues_inicio = {despues_inicio}')
                    sin_espacios = quitar_espacio_doble(antes_inicio)
                    sin_espacios = antes_inicio + despues_inicio
            elif multi_end:
                if multi_end == len( caracteres_str ) - 1:
                    sin_espacios = caracteres_str
                    # print('multi_end == len')

                else:
                    antes_final = caracteres_str[: multi_end + 1]
                    despues_final = caracteres_str[multi_end + 1 : ]
                    # print(f'antes_final = {antes_final}: despues_final = {despues_final}')
                    sin_espacios = quitar_espacio_doble(despues_final)
                    sin_espacios = antes_final + despues_final

            else:
            # este es caracteres_str sin los espacios dobles
                sin_espacios = quitar_espacio_doble(caracteres_str)

            # print(sin_espacios)
            # print()

            # print(f'llegué a quitar espacio, valor: {original_string}, indice: {indice}')
            # aqui regreso los espacios de indentacion al string
            sin_espacios = ' ' * indent_count + sin_espacios

            strings.append(sin_espacios)


            if not sin_espacios == original_string:
                logging.info(f'''CAMBIO EN LINEA #{indice + 1}: 
    ORIGINAL: {original_string}
    NUEVO:    {sin_espacios}
''')





        # retorna el array con todos los strings con los espacios
        return strings

    else:
        raise Exception(f'{list_string_where} is not a list. the first positional argument must be a list.')

# expresiones regulares a ser formateadas

re_operadores = re.compile(r'[-!+*/=<>]{1}')
re_igual = re.compile(r'=')
re_coma = re.compile(r',')
re_slash = re.compile(r'/')
re_menos = re.compile('-')
re_mas = re.compile(r'\+')
re_por = re.compile(r'\*')
re_dospuntos = re.compile(r':')
re_mayor = re.compile(r'>')
re_menor = re.compile(r'<')
re_porcentaje = re.compile(r'%')
re_igualpor = re.compile(r'[*=]')

def formatear(file_route) :
    with open(file_route) as file:
        file = file.read()
        lineas_archivo = file.splitlines()

    
    # añadir espacios antes y despues de los signos de igual, a menos que se cumpla la excepcion
    strings = añadir_espacios(lineas_archivo, re_igual, re_excepciones = re_operadores)
    # añadir espacios despues de las comas
    strings = añadir_espacios(strings, re_coma, antes = False)
    # añadir espacios antes y despues de cada signo de operacion matematica basica
    strings = añadir_espacios(strings, re_slash )
    strings = añadir_espacios(strings, re_mas, re_igual )
    strings = añadir_espacios(strings, re_menos, re_igual )
    strings = añadir_espacios(strings, re_por, re_igualpor)
    # añadir espacios despues de los dos puntos
    strings = añadir_espacios(strings, re_dospuntos, antes = False)
    # añadir espacios antes y despues de los signos de mayor y menor
    strings = añadir_espacios(strings, re_menor, re_igual)
    strings = añadir_espacios(strings, re_mayor, re_igual)
    # añadir espacio antes a signo de porcentaje
    strings = añadir_espacios(strings, re_porcentaje, despues = False)

    with open(file_route, 'w') as file_target:
        with open(file_route, 'a') as file_target:
            for string in strings:
                file_target.write(string + '\n')


formatear(archivo)
