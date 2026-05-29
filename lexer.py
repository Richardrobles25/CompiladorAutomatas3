import ply.lex as lex
import difflib

tokens = (
    # E1 sonidos vocales (11)
    'MMM', 'ATA', 'AAH', 'UUH', 'OH', 'SHH',
    'UFF', 'AY', 'ANA', 'BAH', 'PFF',

    # E2 gestos de manos (14)
    'SENALA', 'PALMA_ARRIBA', 'PALMA_ABAJO', 'PUNO',
    'MANO_ABIERTA', 'TOCA', 'AGITA', 'APUNTA_SI',
    'JUNTA_DEDOS', 'SEPARA_MANOS',
    'DEDOINDICE_BOCA', 'MUEVE_PULGARES',
    'MANO_DERECHA_A_IZQUIERDA', 'MANOS_PALMAS_HACIA_ARRIBA',

    # E3 vocalizaciones (7)
    'SONIDO_LARGO', 'SONIDO_CORTO', 'SONIDO_REPETIDO',
    'SONIDO_AGUDO', 'SONIDO_GRAVE', 'SONIDO_SUAVE',
    'SONIDO_RONQUIDO',

    # E4 movimientos corporales
    'CABEZA_SI', 'CABEZA_NO', 'CABEZA_LADO', 'INCLINA_CUERPO',
    'ACERCA_CUERPO', 'ALEJA_CUERPO', 'SENALA_PROPIO',
    'SENALA_EXTERNO', 'ENCOGE_HOMBROS', 'LEVANTA_BRAZO',

    # E5 expresiones faciales
    'CIERRA_OJOS', 'ABRE_OJOS', 'FRUNCE_CENO', 'SONRIE',
    'LLANTO', 'BOCA_ABIERTA', 'MIRA_ARRIBA', 'MIRA_ABAJO',
    'MIRA_OBJETO', 'PARPADEO_RAPIDO',

    # E6 modificadores
    'RAPIDO', 'LENTO', 'DOBLE', 'TRIPLE', 'PAUSA',

    # Operadores
    'MAS',       # +  secuencia
    'O',         # |  alternativa
    'URGENTE',   # !  urgencia (postfijo)
    'NEG',       # ~  negación (prefijo)
    'FIN_EXPR',  # ;  nueva idea

    # Agrupación
    'LPAREN',    # (  abre grupo / alternativa explícita
    'RPAREN',    # )  cierra grupo

    # Contexto temporal/situacional
    'CONTEXTO',
)

CONTEXTOS_VALIDOS = {'manana', 'noche', 'tarde', 'dolor'}

token_map = {
    'mmm': 'MMM', 'ata': 'ATA', 'aah': 'AAH', 'uuh': 'UUH',
    'oh': 'OH', 'shh': 'SHH', 'uff': 'UFF',
    'ay': 'AY', 'ana': 'ANA', 'bah': 'BAH', 'pff': 'PFF',
    'senala': 'SENALA', 'palma_arriba': 'PALMA_ARRIBA',
    'palma_abajo': 'PALMA_ABAJO', 'puno': 'PUNO',
    'mano_abierta': 'MANO_ABIERTA', 'toca': 'TOCA',
    'agita': 'AGITA', 'apunta_si': 'APUNTA_SI',
    'junta_dedos': 'JUNTA_DEDOS', 'separa_manos': 'SEPARA_MANOS',
    'dedoindice_boca': 'DEDOINDICE_BOCA', 'mueve_pulgares': 'MUEVE_PULGARES',
    'mano_derecha_a_izquierda': 'MANO_DERECHA_A_IZQUIERDA',
    'manos_palmas_hacia_arriba': 'MANOS_PALMAS_HACIA_ARRIBA',
    'sonido_largo': 'SONIDO_LARGO', 'sonido_corto': 'SONIDO_CORTO',
    'sonido_repetido': 'SONIDO_REPETIDO', 'sonido_agudo': 'SONIDO_AGUDO',
    'sonido_grave': 'SONIDO_GRAVE', 'sonido_suave': 'SONIDO_SUAVE',
    'sonido_ronquido': 'SONIDO_RONQUIDO',
    'cabeza_si': 'CABEZA_SI', 'cabeza_no': 'CABEZA_NO',
    'cabeza_lado': 'CABEZA_LADO', 'inclina_cuerpo': 'INCLINA_CUERPO',
    'acerca_cuerpo': 'ACERCA_CUERPO', 'aleja_cuerpo': 'ALEJA_CUERPO',
    'senala_propio': 'SENALA_PROPIO', 'senala_externo': 'SENALA_EXTERNO',
    'encoge_hombros': 'ENCOGE_HOMBROS', 'levanta_brazo': 'LEVANTA_BRAZO',
    'cierra_ojos': 'CIERRA_OJOS', 'abre_ojos': 'ABRE_OJOS',
    'frunce_ceno': 'FRUNCE_CENO', 'sonrie': 'SONRIE',
    'llanto': 'LLANTO', 'boca_abierta': 'BOCA_ABIERTA',
    'mira_arriba': 'MIRA_ARRIBA', 'mira_abajo': 'MIRA_ABAJO',
    'mira_objeto': 'MIRA_OBJETO', 'parpadeo_rapido': 'PARPADEO_RAPIDO',
    'rapido': 'RAPIDO', 'lento': 'LENTO', 'doble': 'DOBLE',
    'triple': 'TRIPLE', 'pausa': 'PAUSA',
}

# Comentarios: líneas que empiezan con # se descartan completas
def t_COMMENT(t):
    r'\#[^\n]*'
    pass

# Contexto entre corchetes: [manana], [noche], [tarde], [dolor]
def t_CONTEXTO(t):
    r'\[[a-z]+\]'
    valor = t.value[1:-1]
    if valor not in CONTEXTOS_VALIDOS:
        col = _columna(t)
        print(f"[LEX-002] Error léxico — línea {t.lineno}, col {col}: "
              f"contexto '[{valor}]' no válido.")
        sugs = difflib.get_close_matches(valor, CONTEXTOS_VALIDOS, n=1, cutoff=0.5)
        if sugs:
            print(f"  → ¿Quisiste decir: [{sugs[0]}]?")
        else:
            validos = ', '.join(f'[{c}]' for c in sorted(CONTEXTOS_VALIDOS))
            print(f"  → Contextos válidos: {validos}")
        return None
    t.value = valor
    return t

# Operadores
def t_MAS(t):
    r'\+'
    return t

def t_O(t):
    r'\|'
    return t

def t_URGENTE(t):
    r'\!'
    return t

def t_NEG(t):
    r'\~'
    return t

def t_FIN_EXPR(t):
    r'\;'
    return t

def t_LPAREN(t):
    r'\('
    return t

def t_RPAREN(t):
    r'\)'
    return t

# Contador de líneas para rastrear posición en errores
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_TOKEN(t):
    r'[a-z][a-z0-9_]*'
    tipo = token_map.get(t.value)
    if tipo:
        t.type = tipo
        return t
    col = _columna(t)
    print(f"[LEX-001] Error léxico — línea {t.lineno}, col {col}: "
          f"token '{t.value}' no reconocido.")
    sugs = difflib.get_close_matches(t.value, token_map.keys(), n=2, cutoff=0.6)
    if sugs:
        print(f"  → ¿Quisiste decir: {' o '.join(sugs)}?")
    else:
        print(f"  → Usa uno de los 57 tokens del alfabeto (ej. mmm, sonrie, dedoindice_boca).")

def t_error(t):
    col = _columna(t)
    c = t.value[0]
    print(f"[LEX-003] Error léxico — línea {t.lineno}, col {col}: "
          f"carácter '{c}' no válido.")
    sugs_char = {
        '@': "los tokens solo usan letras minúsculas, números y '_'.",
        '{': "el lenguaje no usa llaves; usa ( ) para agrupar alternativas.",
        '}': "el lenguaje no usa llaves; usa ( ) para agrupar alternativas.",
        ',': "usa '+' para separar tokens en secuencia.",
        '.': "los tokens no llevan punto.",
    }
    sug = sugs_char.get(c, "solo se permiten: letras minúsculas, +  |  !  ~  ;  [ ]")
    print(f"  → {sug}")
    t.lexer.skip(1)

def _columna(t):
    ultimo_salto = t.lexer.lexdata.rfind('\n', 0, t.lexpos)
    return t.lexpos - ultimo_salto


lexer = lex.lex()


if __name__ == '__main__':
    casos = [
        ("Secuencia basica",                 "mmm + palma_arriba + sonido_largo"),
        ("Con contexto manana",              "[manana] boca_abierta + senala_propio"),
        ("Con contexto dolor",               "[dolor] uff + sonido_largo + encoge_hombros"),
        ("Urgencia  !",                      "[dolor] sonido_largo + frunce_ceno !"),
        ("Negacion  ~",                      "~cabeza_no + sonrie"),
        ("Alternativa  |",                   "palma_arriba | mira_objeto"),
        ("Dos ideas  ;",                     "[manana] sonrie + cabeza_si ; [dolor] ay + senala_propio"),
        ("Combinado complejo",               "[dolor] ~sonrie + uff + sonido_largo !"),
        ("Comentario ignorado",              "# el paciente se desperto agitado\n[noche] agita + sonido_largo !"),
        ("Token no reconocido",              "token_invalido"),
        ("Contexto invalido",                "[desayuno] mmm"),
        ("Caracter invalido",                "mmm @ palma_arriba"),
    ]

    for descripcion, entrada in casos:
        print(f"\n--- {descripcion} ---")
        print(f"Entrada: {entrada!r}")
        lexer.input(entrada)
        lexer.lineno = 1
        toks = list(lexer)
        if toks:
            print(f"  {'TIPO':<22} {'VALOR':<20} LINEA")
            print(f"  {'-'*22} {'-'*20} -----")
            for tok in toks:
                print(f"  {tok.type:<22} {repr(tok.value):<20} {tok.lineno}")
            print(f"  Total: {len(toks)} token(s)")
        else:
            print("  (sin tokens validos)")
