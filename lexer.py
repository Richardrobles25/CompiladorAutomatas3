import ply.lex as lex

# lista de todos los tokens
tokens = (
    # E1 sonidos vocales
    'MMM', 'ATA', 'AAH', 'UUH', 'OH', 'SHH', 'HMM',
    'UFF', 'AY', 'ANA', 'BAH', 'PFF',


    # E2 gestos de manos
    'SENALA', 'PALMA_ARRIBA', 'PALMA_ABAJO', 'PUNO',
    'MANO_ABIERTA', 'TOCA', 'AGITA', 'APUNTA_SI',
    'JUNTA_DEDOS', 'SEPARA_MANOS', 'PULGAR_ARRIBA', 'PULGAR_ABAJO',

    # E3 vocalizaciones
    'SONIDO_LARGO', 'SONIDO_CORTO', 'SONIDO_REPETIDO',
    'SONIDO_AGUDO', 'SONIDO_GRAVE', 'SONIDO_SUAVE',

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

)

# mapeo de texto a token
token_map = {
    'mmm': 'MMM', 'ata': 'ATA', 'aah': 'AAH', 'uuh': 'UUH',
    'oh': 'OH', 'shh': 'SHH', 'hmm': 'HMM', 'uff': 'UFF',
    'ay': 'AY', 'ana': 'ANA', 'bah': 'BAH', 'pff': 'PFF',
    'senala': 'SENALA', 'palma_arriba': 'PALMA_ARRIBA',
    'palma_abajo': 'PALMA_ABAJO', 'puno': 'PUNO',
    'mano_abierta': 'MANO_ABIERTA', 'toca': 'TOCA',
    'agita': 'AGITA', 'apunta_si': 'APUNTA_SI',
    'junta_dedos': 'JUNTA_DEDOS', 'separa_manos': 'SEPARA_MANOS',
    'pulgar_arriba': 'PULGAR_ARRIBA', 'pulgar_abajo': 'PULGAR_ABAJO',
    'sonido_largo': 'SONIDO_LARGO', 'sonido_corto': 'SONIDO_CORTO',
    'sonido_repetido': 'SONIDO_REPETIDO', 'sonido_agudo': 'SONIDO_AGUDO',
    'sonido_grave': 'SONIDO_GRAVE', 'sonido_suave': 'SONIDO_SUAVE',
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

def t_TOKEN(t):
    r'[a-z][a-z0-9_]*'
    tipo = token_map.get(t.value)
    if tipo:
        t.type = tipo
        return t
    else:
        print(f"Token no reconocido: '{t.value}'")

t_ignore = ' \t\n'

def t_error(t):
    print(f"Carácter no válido: '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()