import sys
sys.stdout.reconfigure(encoding='utf-8')

from sintactico import (
    NodoPrograma, NodoExpresion, NodoSecuencia, NodoTermino, analizar
)

# ── Tabla de símbolos ────────────────────────────────────────────────────────

class TablaSimbolos:
    def __init__(self):
        self.reset()

    def reset(self):
        self.contexto_activo = None
        self.hay_urgencia    = False

tabla = TablaSimbolos()

# ── Categorías por token ─────────────────────────────────────────────────────

CATEGORIA = {
    'MMM':'E1','ATA':'E1','AAH':'E1','UUH':'E1','OH':'E1','SHH':'E1',
    'HMM':'E1','UFF':'E1','AY':'E1','ANA':'E1','BAH':'E1','PFF':'E1',
    'SENALA':'E2','PALMA_ARRIBA':'E2','PALMA_ABAJO':'E2','PUNO':'E2',
    'MANO_ABIERTA':'E2','TOCA':'E2','AGITA':'E2','APUNTA_SI':'E2',
    'JUNTA_DEDOS':'E2','SEPARA_MANOS':'E2','PULGAR_ARRIBA':'E2','PULGAR_ABAJO':'E2',
    'SONIDO_LARGO':'E3','SONIDO_CORTO':'E3','SONIDO_REPETIDO':'E3',
    'SONIDO_AGUDO':'E3','SONIDO_GRAVE':'E3','SONIDO_SUAVE':'E3',
    'CABEZA_SI':'E4','CABEZA_NO':'E4','CABEZA_LADO':'E4','INCLINA_CUERPO':'E4',
    'ACERCA_CUERPO':'E4','ALEJA_CUERPO':'E4','SENALA_PROPIO':'E4',
    'SENALA_EXTERNO':'E4','ENCOGE_HOMBROS':'E4','LEVANTA_BRAZO':'E4',
    'CIERRA_OJOS':'E5','ABRE_OJOS':'E5','FRUNCE_CENO':'E5','SONRIE':'E5',
    'LLANTO':'E5','BOCA_ABIERTA':'E5','MIRA_ARRIBA':'E5','MIRA_ABAJO':'E5',
    'MIRA_OBJETO':'E5','PARPADEO_RAPIDO':'E5',
    'RAPIDO':'E6','LENTO':'E6','DOBLE':'E6','TRIPLE':'E6','PAUSA':'E6',
}

# ── Significados base ────────────────────────────────────────────────────────

BASE = {
    # E1
    'mmm':             'está pensando o dudando',
    'ata':             'llama a alguien cercano',
    'aah':             'siente alivio o satisfacción',
    'uuh':             'siente incomodidad o molestia',
    'oh':              'está sorprendido',
    'shh':             'pide silencio o quiere esperar',
    'hmm':             'está indeciso',
    'uff':             'está cansado o frustrado',
    'ay':              'siente dolor agudo o se asustó',
    'ana':             'llama a una persona específica',
    'bah':             'rechaza algo',
    'pff':             'no le importa o está en desacuerdo',
    # E2
    'senala':          'quiere algo en esa dirección',
    'palma_arriba':    'está pidiendo algo',
    'palma_abajo':     'pide calma o que paren',
    'puno':            'quiere algo con mucha determinación',
    'mano_abierta':    'pide que esperen o se detengan',
    'toca':            'quiere ese objeto o ese contacto',
    'agita':           'llama la atención urgentemente',
    'apunta_si':       'confirma que eso es correcto',
    'junta_dedos':     'es exactamente eso',
    'separa_manos':    'no sabe o no tiene idea',
    'pulgar_arriba':   'está de acuerdo o se siente bien',
    'pulgar_abajo':    'no está de acuerdo o algo está mal',
    # E3
    'sonido_largo':    'necesita atención',
    'sonido_corto':    'hace una petición simple',
    'sonido_repetido': 'insiste, no ha sido atendido',
    'sonido_agudo':    'alerta o dolor agudo',
    'sonido_grave':    'está cansado o somnoliento',
    'sonido_suave':    'está tranquilo y bien',
    # E4
    'cabeza_si':       'afirma o está de acuerdo',
    'cabeza_no':       'niega o no quiere',
    'cabeza_lado':     'está indeciso',
    'inclina_cuerpo':  'muestra interés en algo',
    'acerca_cuerpo':   'quiere acercarse a algo o alguien',
    'aleja_cuerpo':    'quiere alejarse',
    'senala_propio':   'es para él o le afecta a él',
    'senala_externo':  'es para otro o está afuera',
    'encoge_hombros':  'no sabe o no le importa',
    'levanta_brazo':   'pide ayuda o atención',
    # E5
    'cierra_ojos':     'está cansado o no quiere ver',
    'abre_ojos':       'está sorprendido o asustado',
    'frunce_ceno':     'siente dolor o disgusto',
    'sonrie':          'está contento o de acuerdo',
    'llanto':          'está muy triste o tiene dolor intenso',
    'boca_abierta':    'tiene hambre o sed',
    'mira_arriba':     'está recordando o pensando algo',
    'mira_abajo':      'está triste o cansado',
    'mira_objeto':     'quiere ese objeto',
    'parpadeo_rapido': 'siente incomodidad en los ojos',
    # E6
    'rapido':  'con urgencia',
    'lento':   'suavemente',
    'doble':   'con mucho énfasis',
    'triple':  'con énfasis máximo',
    'pausa':   'hace una pausa',
}

# ── Overrides por contexto ───────────────────────────────────────────────────

OVERRIDE = {
    'manana': {
        'boca_abierta':  'quiere desayunar',
        'cierra_ojos':   'aún quiere dormir más',
        'sonrie':        'está de buen humor al despertar',
        'uff':           'no quiere levantarse todavía',
        'levanta_brazo': 'necesita ayuda para levantarse',
        'sonido_largo':  'no quiere despertarse aún',
        'palma_arriba':  'quiere que le den el desayuno',
        'mira_objeto':   'quiere algo del desayuno',
        'sonido_grave':  'sigue con sueño, no quiere levantarse',
        'cabeza_no':     'no quiere levantarse',
        'agita':         'necesita algo urgente antes de levantarse',
    },
    'tarde': {
        'boca_abierta':    'quiere almorzar o merendar',
        'senala_externo':  'quiere salir a pasear',
        'sonrie':          'está disfrutando la tarde',
        'cierra_ojos':     'quiere descansar un rato',
        'agita':           'quiere actividad o entretenimiento',
        'inclina_cuerpo':  'quiere participar en algo',
        'palma_arriba':    'quiere algo para la tarde',
        'mira_objeto':     'quiere ese objeto para entretenerse',
        'acerca_cuerpo':   'quiere compañía o actividad compartida',
    },
    'noche': {
        'cierra_ojos':   'quiere dormir ya',
        'boca_abierta':  'quiere cenar',
        'sonido_grave':  'está listo para dormir',
        'uff':           'está muy cansado del día',
        'levanta_brazo': 'necesita ayuda para acostarse',
        'sonido_largo':  'no puede dormir, necesita ayuda',
        'palma_abajo':   'quiere que bajen la voz o apaguen la luz',
        'mira_abajo':    'está cansado y listo para descansar',
        'sonido_suave':  'está bien, listo para dormir',
        'palma_arriba':  'quiere algo antes de dormir',
    },
    'dolor': {
        'uff':           'está sufriendo',
        'ay':            'siente un dolor muy intenso',
        'sonido_largo':  'tiene mucho dolor, necesita ayuda urgente',
        'frunce_ceno':   'el dolor es intenso',
        'llanto':        'el dolor es insoportable',
        'senala_propio': 'le duele algo en su cuerpo',
        'levanta_brazo': 'necesita atención o medicina',
        'sonido_agudo':  'dolor agudo muy intenso',
        'agita':         'el dolor es urgente, necesita ayuda ya',
        'uuh':           'siente malestar físico constante',
        'encoge_hombros':'no sabe cómo describir el dolor',
        'mira_abajo':    'está abatido por el dolor',
        'abre_ojos':     'el dolor lo asustó',
    },
}

# ── Grupos para detección de patrones ────────────────────────────────────────

TOKENS_DOLOR     = {'UFF','AY','UUH','FRUNCE_CENO','SONIDO_AGUDO'}
TOKENS_URGENCIA  = {'AGITA','LEVANTA_BRAZO','SONIDO_LARGO','SONIDO_REPETIDO','ATA'}
TOKENS_PETICION  = {'PALMA_ARRIBA','SENALA','TOCA','MIRA_OBJETO','SONIDO_CORTO','PUNO'}
TOKENS_POSITIVO  = {'SONRIE','AAH','PULGAR_ARRIBA','APUNTA_SI'}
TOKENS_NEGATIVO  = {'LLANTO','MIRA_ABAJO','BAH','PFF','PULGAR_ABAJO','ALEJA_CUERPO'}
TOKENS_CONFIRM   = {'CABEZA_SI','CABEZA_NO','CABEZA_LADO','PULGAR_ARRIBA','PULGAR_ABAJO','APUNTA_SI','JUNTA_DEDOS'}
TOKENS_CANSANCIO = {'CIERRA_OJOS','SONIDO_GRAVE','MIRA_ABAJO'}
TOKENS_HAMBRE    = {'BOCA_ABIERTA'}

# ── Obtener significado de un token (con override de contexto) ───────────────

def significado_token(valor, tipo, contexto, negado):
    sig = (OVERRIDE.get(contexto, {}).get(valor)
           if contexto else None) or BASE.get(valor, valor)
    if negado:
        sig = f'no {sig}'
    return sig

# ── Detectar patrón dominante ────────────────────────────────────────────────

def detectar_patron(tipos, contexto, hay_urgente, negados=None):
    if negados is None:
        negados = [False] * len(tipos)

    # tipos_activos: solo los tokens que NO están negados
    # (un token negado no puede activar su propio patrón semántico)
    tipos_activos = {t for t, n in zip(tipos, negados) if not n}
    tipos_set     = set(tipos)   # todos, para comprobaciones de contexto

    # Urgencia y dolor: el contexto [dolor] tiene peso propio aunque todo esté negado
    if hay_urgente or (TOKENS_URGENCIA & tipos_activos):
        if contexto == 'dolor' or (TOKENS_DOLOR & tipos_activos):
            return 'dolor_urgente'
        return 'urgencia'

    if contexto == 'dolor' or (TOKENS_DOLOR & tipos_activos):
        return 'dolor'

    if TOKENS_POSITIVO & tipos_activos:
        return 'emocional_positivo'

    if TOKENS_HAMBRE & tipos_activos:
        if contexto in ('manana', 'noche', 'tarde'):
            return 'hambre_ctx'
        return 'hambre'

    # Tokens exclusivamente negativos (no compartidos con cansancio)
    negativo_exclusivo = TOKENS_NEGATIVO - TOKENS_CANSANCIO
    if negativo_exclusivo & tipos_activos:
        return 'emocional_negativo'

    if TOKENS_CANSANCIO & tipos_activos:
        if contexto == 'noche':
            return 'sueno_noche'
        if contexto == 'manana':
            return 'sueno_manana'
        return 'cansancio'

    if tipos_activos and (tipos_activos <= TOKENS_CONFIRM or
                          (TOKENS_CONFIRM & tipos_activos and len(tipos_activos) <= 2)):
        return 'confirmacion'

    if TOKENS_NEGATIVO & tipos_activos:
        return 'emocional_negativo'

    if TOKENS_PETICION & tipos_activos:
        return 'peticion'

    return 'general'

# ── Generar frase por patrón ─────────────────────────────────────────────────

def generar_frase(infos, patron, contexto, hay_urgente):
    tipos  = [i['tipo']  for i in infos]
    valores = [i['valor'] for i in infos]
    sigs   = [i['significado'] for i in infos]
    intensidad = _intensidad(tipos)

    if patron == 'dolor_urgente':
        base = _frase_dolor(infos, contexto)
        return f'¡{base}! Necesita atención urgente ahora mismo.'

    if patron == 'urgencia':
        sigs_filtrados = [s for s, t in zip(sigs, tipos) if t not in ('RAPIDO','LENTO','DOBLE','TRIPLE','PAUSA')]
        desc = ' y '.join(sigs_filtrados) if sigs_filtrados else 'necesita atención'
        return f'¡{desc.capitalize()}! Es urgente.{intensidad}'

    if patron == 'dolor':
        return _frase_dolor(infos, contexto) + intensidad

    if patron == 'hambre_ctx':
        ctx_map = {'manana': 'desayunar', 'tarde': 'almorzar o merendar', 'noche': 'cenar'}
        accion = ctx_map.get(contexto, 'comer o tomar algo')
        extra = _extra_peticion(tipos, valores)
        return f'Quiere {accion}{extra}.{intensidad}'

    if patron == 'hambre':
        extra = _extra_peticion(tipos, valores)
        return f'Tiene hambre o sed{extra}.{intensidad}'

    if patron == 'sueno_noche':
        return f'Está listo para dormir.{intensidad}'

    if patron == 'sueno_manana':
        return f'Aún quiere dormir, no quiere levantarse.{intensidad}'

    if patron == 'cansancio':
        return f'Está muy cansado.{intensidad}'

    if patron == 'confirmacion':
        return _frase_confirmacion(infos) + intensidad

    if patron == 'emocional_positivo':
        return _frase_positiva(infos) + intensidad

    if patron == 'emocional_negativo':
        return _frase_negativa(infos) + intensidad

    if patron == 'peticion':
        return _frase_peticion(infos, contexto) + intensidad

    # general: combinar todos los significados
    sigs_filtrados = [s for s, t in zip(sigs, tipos)
                      if t not in ('RAPIDO','LENTO','DOBLE','TRIPLE','PAUSA')]
    if not sigs_filtrados:
        # Todos los tokens eran modificadores E6 (ej. solo 'pausa')
        # Usar el significado de todos sin filtrar
        sigs_filtrados = list(sigs)
    return f'{". ".join(s.capitalize() for s in sigs_filtrados)}.{intensidad}'


def _intensidad(tipos):
    if 'TRIPLE' in tipos: return ' (con mucho énfasis)'
    if 'DOBLE'  in tipos: return ' (con énfasis)'
    if 'RAPIDO' in tipos: return ' (urgente)'
    if 'LENTO'  in tipos: return ' (suavemente)'
    return ''

def _extra_peticion(tipos, valores):
    if 'MIRA_OBJETO' in tipos: return ', lo que está mirando'
    if 'SENALA'      in tipos: return ', lo que está señalando'
    if 'TOCA'        in tipos: return ', lo que está tocando'
    return ''

def _frase_dolor(infos, contexto):
    tipos = [i['tipo'] for i in infos]
    if 'LLANTO' in tipos:
        return 'El dolor es insoportable, está llorando'
    if 'SONIDO_AGUDO' in tipos and 'FRUNCE_CENO' in tipos:
        return 'Siente un dolor agudo e intenso'
    if 'SENALA_PROPIO' in tipos:
        return 'Le duele algo en su cuerpo y pide ayuda'
    if 'AY' in tipos:
        return 'Siente un dolor agudo'
    if 'FRUNCE_CENO' in tipos:
        return 'Tiene dolor o malestar'
    if 'UFF' in tipos and contexto == 'dolor':
        return 'Está sufriendo'
    return 'Siente dolor o malestar'

def _frase_confirmacion(infos):
    tipos = [i['tipo'] for i in infos]
    negados = [i['negado'] for i in infos]

    if 'CABEZA_SI' in tipos and not negados[tipos.index('CABEZA_SI') if 'CABEZA_SI' in tipos else 0]:
        if 'PULGAR_ARRIBA' in tipos:
            return 'Confirma con mucho énfasis que sí, está completamente de acuerdo'
        if 'APUNTA_SI' in tipos:
            return 'Confirma que sí, eso es exactamente lo correcto'
        return 'Está de acuerdo, dice que sí'

    if 'CABEZA_NO' in tipos:
        if 'PALMA_ABAJO' in tipos:
            return 'No quiere eso y pide que paren'
        if 'ALEJA_CUERPO' in tipos:
            return 'No quiere y se aleja'
        return 'No quiere, dice que no'

    if 'CABEZA_LADO' in tipos:
        if 'ENCOGE_HOMBROS' in tipos:
            return 'Está indeciso, no tiene claro qué quiere'
        if 'HMM' in tipos:
            return 'Está dudando, necesita pensarlo'
        return 'No está seguro'

    if 'PULGAR_ARRIBA' in tipos:
        return 'Está bien y de acuerdo'
    if 'PULGAR_ABAJO' in tipos:
        return 'No está de acuerdo o algo está mal'

    return 'Está respondiendo algo'

def _frase_positiva(infos):
    tipos = [i['tipo'] for i in infos]
    if 'SONRIE' in tipos and 'PULGAR_ARRIBA' in tipos:
        return 'Está muy contento y feliz'
    if 'SONRIE' in tipos and 'CABEZA_SI' in tipos:
        return 'Está contento y de acuerdo'
    if 'AAH' in tipos and 'SONRIE' in tipos:
        return 'Siente alivio y está contento'
    if 'AAH' in tipos and 'PULGAR_ARRIBA' in tipos:
        return 'Se siente bien y está satisfecho'
    if 'SONRIE' in tipos:
        return 'Está contento'
    if 'AAH' in tipos:
        return 'Siente alivio y satisfacción'
    return 'Está bien'

def _frase_negativa(infos):
    tipos = [i['tipo'] for i in infos]
    if 'LLANTO' in tipos and 'MIRA_ABAJO' in tipos:
        return 'Está muy triste y decaído'
    if 'BAH' in tipos and 'ALEJA_CUERPO' in tipos:
        return 'Rechaza algo y quiere alejarse'
    if 'FRUNCE_CENO' in tipos and 'CABEZA_NO' in tipos:
        return 'Está disgustado y no quiere'
    if 'PFF' in tipos and 'PALMA_ABAJO' in tipos:
        return 'No le importa y pide que paren'
    if 'LLANTO' in tipos:
        return 'Está muy triste'
    if 'BAH' in tipos:
        return 'Rechaza algo'
    if 'MIRA_ABAJO' in tipos:
        return 'Está triste o decaído'
    return 'No está bien emocionalmente'

def _frase_peticion(infos, contexto):
    tipos  = [i['tipo']  for i in infos]
    valores = [i['valor'] for i in infos]

    if 'PALMA_ARRIBA' in tipos and 'MIRA_OBJETO' in tipos:
        return 'Quiere ese objeto que está mirando'
    if 'PALMA_ARRIBA' in tipos and 'SENALA' in tipos:
        return 'Pide algo que está señalando'
    if 'SENALA' in tipos and 'APUNTA_SI' in tipos:
        return 'Quiere exactamente lo que está señalando'
    if 'TOCA' in tipos and 'CABEZA_SI' in tipos:
        return 'Quiere ese objeto o ese contacto, confirma que sí'
    if 'MMM' in tipos and 'PALMA_ARRIBA' in tipos:
        return 'Está pidiendo algo, no está seguro qué'
    if 'SONIDO_REPETIDO' in tipos:
        return 'Lleva rato pidiendo algo y no ha sido atendido'
    if 'PUNO' in tipos:
        return 'Quiere algo con mucha determinación'
    if 'PALMA_ARRIBA' in tipos:
        return 'Está pidiendo algo'
    if 'SENALA' in tipos:
        return 'Quiere algo en esa dirección'
    if 'MIRA_OBJETO' in tipos:
        return 'Quiere ese objeto que está mirando'
    return 'Está haciendo una petición'

# ── Procesar alternativa (operador |) ────────────────────────────────────────

def interpretar_alternativa(frases):
    if len(frases) == 1:
        return frases[0]
    opciones = ' o '.join(f'"{f.rstrip(".")}"' for f in frases)
    return f'No está claro qué quiere exactamente: {opciones}.'

# ── Interpretar una secuencia completa ───────────────────────────────────────

def interpretar_secuencia(secuencia, contexto):
    infos = []
    hay_urgente = False
    for term in secuencia.terminos:
        if term.urgente:
            hay_urgente = True
        sig = significado_token(term.token_valor, term.token_tipo, contexto, term.negado)
        infos.append({
            'valor':      term.token_valor,
            'tipo':       term.token_tipo,
            'significado': sig,
            'negado':     term.negado,
            'urgente':    term.urgente,
        })
    tipos   = [i['tipo']   for i in infos]
    negados = [i['negado'] for i in infos]
    patron  = detectar_patron(tipos, contexto, hay_urgente, negados)

    # ── Advertencias semánticas ──────────────────────────────────────────────
    if patron == 'general':
        print("[SEM-001] Advertencia semántica: combinación sin patrón específico.")
        print("  → Agrega 'palma_arriba' para petición, 'sonrie' para emoción positiva,")
        print("    o usa [contexto] para más precisión.")

    if negados and all(negados):
        print("[SEM-002] Advertencia semántica: todos los tokens están negados (~).")
        print("  → Una secuencia de puros '~' puede ser difícil de interpretar.")

    if tipos == ['PAUSA']:
        print("[SEM-003] Advertencia semántica: 'pausa' sola no comunica una intención.")
        print("  → Usa 'pausa' junto con otros tokens. Ejemplo: mmm + pausa + palma_arriba")

    if len(tipos) > 6:
        print(f"[SEM-004] Advertencia semántica: secuencia larga ({len(tipos)} tokens).")
        print("  → Considera dividir con ';' para dos mensajes más claros.")

    return generar_frase(infos, patron, contexto, hay_urgente)

# ── Interpretar una expresión completa ───────────────────────────────────────

def interpretar_expresion(expresion):
    contexto = expresion.contexto
    tabla.contexto_activo = contexto

    frases_alternativas = [
        interpretar_secuencia(seq, contexto)
        for seq in expresion.alternativas
    ]

    frase = interpretar_alternativa(frases_alternativas)

    if contexto:
        prefijos = {
            'manana': 'En la mañana',
            'tarde':  'En la tarde',
            'noche':  'En la noche',
            'dolor':  'Con señales de dolor',
        }
        frase = f'{prefijos[contexto]}: {frase[0].lower()}{frase[1:]}'

    return frase

# ── Punto de entrada principal ───────────────────────────────────────────────

def compilar(entrada):
    tabla.reset()
    ast = analizar(entrada)
    if not ast:
        return ['Error: no se pudo analizar la entrada.']

    frases = []
    for expresion in ast.expresiones:
        frase = interpretar_expresion(expresion)
        frases.append(frase)
    return frases


# ── Pruebas ──────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    casos = [
        # Peticiones
        "mmm + palma_arriba",
        "palma_arriba + mira_objeto",
        "senala + apunta_si",
        "sonido_repetido + agita",
        # Emociones positivas
        "sonrie + cabeza_si",
        "aah + pulgar_arriba",
        "sonrie + pulgar_arriba",
        # Emociones negativas
        "llanto + mira_abajo",
        "bah + aleja_cuerpo",
        "frunce_ceno + cabeza_no",
        # Dolor
        "frunce_ceno + sonido_largo",
        "ay + senala_propio",
        "llanto + levanta_brazo",
        # Urgencia
        "agita + sonido_largo",
        "levanta_brazo !",
        "sonido_largo + frunce_ceno !",
        # Con contexto
        "[manana] boca_abierta + palma_arriba",
        "[manana] cierra_ojos + cabeza_no + uff",
        "[noche] cierra_ojos + sonido_grave",
        "[noche] boca_abierta + mira_objeto",
        "[dolor] uff + sonido_largo",
        "[dolor] ay + senala_propio + levanta_brazo !",
        "[tarde] sonrie + acerca_cuerpo",
        # Negación
        "~sonrie + frunce_ceno",
        "~cabeza_no + pulgar_arriba",
        # Alternativa
        "palma_arriba | mira_objeto",
        "sonrie | cabeza_si",
        "uff | frunce_ceno",
        # Modificadores
        "uff + doble",
        "sonido_largo + rapido",
        "sonrie + lento",
        # Dos ideas con ;
        "[manana] sonrie + cabeza_si ; [dolor] ay + senala_propio",
        # Confirmación
        "cabeza_si + pulgar_arriba",
        "cabeza_no + palma_abajo",
        "cabeza_lado + encoge_hombros",
        # Complejo
        "[dolor] ~sonrie + uff + sonido_largo !",
        "[noche] palma_abajo + cierra_ojos + sonido_grave",
    ]

    for entrada in casos:
        print(f'\nEntrada:  {entrada}')
        resultados = compilar(entrada)
        for r in resultados:
            print(f'Frase:    {r}')
        print('-' * 60)
