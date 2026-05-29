"""
interpretador_ia.py
Capa de interpretación semántica potenciada por IA (Claude de Anthropic).

Recibe los tokens ya analizados por el compilador y devuelve una frase en
español natural que describe lo que la persona está comunicando.

Uso:
    from interpretador_ia import interpretar_con_ia, ia_disponible

    frase = interpretar_con_ia(infos, contexto, hay_urgente)
    if frase is None:
        # usar interpretación basada en reglas como respaldo
        ...

Requiere:
    pip install anthropic
    Variable de entorno: ANTHROPIC_API_KEY=<tu clave>
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ── Intentar importar el SDK de Anthropic ────────────────────────────────────

try:
    import anthropic as _anthropic_sdk
    _IA_DISPONIBLE = True
except ImportError:
    _anthropic_sdk = None
    _IA_DISPONIBLE = False


# ── Prompt del sistema ───────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
Eres un asistente especializado en comunicación aumentativa y alternativa (CAA).
Ayudas a los cuidadores de una persona con autismo no verbal a entender sus señales.

El sistema de comunicación usa tokens que representan gestos, sonidos y movimientos:

E1 – Sonidos vocales:
  mmm=duda/pensamiento | ata=llama a alguien | aah=alivio/satisfacción
  uuh=incomodidad      | oh=sorpresa          | shh=ganas de ir al baño
  uff=cansancio/frustración | ay=dolor agudo  | ana=llama a "Ana"
  bah=rechazo          | pff=desinterés/desacuerdo

E2 – Gestos de manos:
  senala=quiere algo en esa dirección  | palma_arriba=pide algo
  palma_abajo=pide calma/que paren     | puno=quiere algo con determinación
  mano_abierta=pide que esperen        | toca=quiere ese objeto/contacto
  agita=llama atención urgentemente    | apunta_si=confirma que sí
  junta_dedos=poca cantidad            | separa_manos=no sabe/no tiene
  dedoindice_boca=pide silencio        | mueve_pulgares=quiere jugar videojuegos
  mano_derecha_a_izquierda=algo se acabó
  manos_palmas_hacia_arriba=quiere que le den la razón

E3 – Vocalizaciones:
  sonido_largo=necesita atención     | sonido_corto=petición simple
  sonido_repetido=insiste/no atendido| sonido_agudo=alerta o dolor agudo
  sonido_grave=somnoliento/cansado   | sonido_suave=tranquilo y bien
  sonido_ronquido=quiere irse a dormir

E4 – Movimientos corporales:
  cabeza_si=afirma/acuerdo  | cabeza_no=niega/no quiere
  cabeza_lado=indeciso      | inclina_cuerpo=muestra interés
  acerca_cuerpo=quiere acercarse | aleja_cuerpo=quiere alejarse
  senala_propio=es para él  | senala_externo=es para otro/afuera
  encoge_hombros=no sabe    | levanta_brazo=pide ayuda/atención

E5 – Expresiones faciales:
  cierra_ojos=cansado/no quiere ver | abre_ojos=sorprendido/asustado
  frunce_ceno=dolor o disgusto      | sonrie=contento/de acuerdo
  llanto=tristeza o dolor intenso   | boca_abierta=hambre/sed
  mira_arriba=recuerda o piensa     | mira_abajo=triste/cansado
  mira_objeto=quiere ese objeto     | parpadeo_rapido=incomodidad ocular

E6 – Modificadores de intensidad:
  rapido=con urgencia | lento=suavemente | doble=con énfasis
  triple=énfasis máximo | pausa=hace una pausa

Contextos temporales/situacionales:
  [manana] = momento del despertar o la mañana
  [tarde]  = hora de la tarde, actividades diurnas
  [noche]  = hora de dormir
  [dolor]  = la persona está experimentando dolor físico

Operadores:
  ~ antes de un token = NEGACIÓN (lo opuesto de ese token)
  ! después de un token = URGENCIA MÁXIMA (necesita atención inmediata)

INSTRUCCIONES PARA TU RESPUESTA:
- Genera UNA SOLA ORACIÓN en español natural (máximo 2 oraciones cortas).
- Usa tercera persona ("Quiere...", "Está...", "Siente...").
- Sé empático y claro; usa lenguaje cotidiano, no técnico.
- NO incluyas prefijos de contexto como "En la mañana:" ni "Con señales de dolor:".
  El sistema los agrega automáticamente; solo describe lo que comunica la persona.
- Si hay urgencia (!), refleja la urgencia en la oración con lenguaje como
  "necesita atención urgente" o "necesita que lo atiendan ahora".
- Responde ÚNICAMENTE con la oración. Sin comillas, sin explicaciones, sin saludo.\
"""


# ── Caché para no llamar la API dos veces con la misma entrada ───────────────

_cache: dict = {}


# ── Cliente (inicialización diferida) ────────────────────────────────────────

_cliente_ia = None


def _obtener_cliente():
    global _cliente_ia
    if _cliente_ia is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "La variable de entorno ANTHROPIC_API_KEY no está definida.\n"
                "Agrégala con: export ANTHROPIC_API_KEY='sk-ant-...'"
            )
        _cliente_ia = _anthropic_sdk.Anthropic(api_key=api_key)
    return _cliente_ia


# ── Funciones auxiliares ─────────────────────────────────────────────────────

def _clave_cache(infos: list, contexto, hay_urgente: bool) -> str:
    tokens_str = "|".join(
        f"{'~' if i['negado'] else ''}{i['tipo']}{'!' if i['urgente'] else ''}"
        for i in infos
    )
    return f"{contexto or ''}:{tokens_str}:{hay_urgente}"


def _construir_mensaje(infos: list, contexto, hay_urgente: bool) -> str:
    """Convierte los datos del analizador semántico en texto comprensible para Claude."""
    partes = []

    if contexto:
        desc_ctx = {
            'manana': 'mañana (momento de levantarse/despertarse)',
            'tarde':  'tarde (actividades diurnas)',
            'noche':  'noche (hora de dormir)',
            'dolor':  'dolor (la persona está sufriendo dolor físico)',
        }
        partes.append(f"Contexto: {desc_ctx.get(contexto, contexto)}")

    descripciones_tokens = []
    for info in infos:
        token = info['valor']
        sig   = info['significado']
        if info['negado']:
            desc = f"~{token} [NEGADO → {sig}]"
        else:
            desc = f"{token} ({sig})"
        if info['urgente']:
            desc += " ¡URGENTE!"
        descripciones_tokens.append(desc)

    partes.append("Señales: " + ", ".join(descripciones_tokens))

    if hay_urgente:
        partes.append("⚠ Hay señal de URGENCIA MÁXIMA.")

    return "\n".join(partes)


# ── Función principal ─────────────────────────────────────────────────────────

def interpretar_con_ia(infos: list, contexto, hay_urgente: bool):
    """
    Interpreta una secuencia de tokens usando la API de Claude.

    Parámetros
    ----------
    infos       : lista de dicts con claves: valor, tipo, significado, negado, urgente
    contexto    : 'manana' | 'tarde' | 'noche' | 'dolor' | None
    hay_urgente : True si algún token lleva '!'

    Retorna
    -------
    str  – frase interpretada en español natural
    None – si la IA no está disponible o ocurrió un error (usar reglas de respaldo)
    """
    if not _IA_DISPONIBLE:
        return None

    # Revisar caché primero
    clave = _clave_cache(infos, contexto, hay_urgente)
    if clave in _cache:
        return _cache[clave]

    try:
        cliente   = _obtener_cliente()
        contenido = _construir_mensaje(infos, contexto, hay_urgente)

        respuesta = cliente.messages.create(
            model="claude-opus-4-7",
            max_tokens=200,
            system=_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": contenido}
            ],
        )

        frase = respuesta.content[0].text.strip()

        # Guardar en caché
        _cache[clave] = frase
        return frase

    except EnvironmentError as e:
        # API key no configurada — avisar una sola vez
        if not getattr(interpretar_con_ia, '_aviso_key_mostrado', False):
            print(f"\n[IA] {e}")
            print("[IA] El compilador continuará usando interpretación basada en reglas.\n")
            interpretar_con_ia._aviso_key_mostrado = True
        return None

    except Exception as e:
        print(f"[IA] No se pudo obtener interpretación de Claude → {type(e).__name__}: {e}")
        print("[IA] Usando interpretación basada en reglas como respaldo.")
        return None


def ia_disponible() -> bool:
    """
    Comprueba si la IA está disponible (SDK instalado + API key configurada).
    Útil para mostrar el estado en la interfaz.
    """
    if not _IA_DISPONIBLE:
        return False
    try:
        _obtener_cliente()
        return True
    except EnvironmentError:
        return False


# ── Prueba rápida al ejecutar directamente ───────────────────────────────────

if __name__ == '__main__':
    if not _IA_DISPONIBLE:
        print("✗ SDK de Anthropic no instalado. Ejecuta: pip install anthropic")
        sys.exit(1)

    if not ia_disponible():
        print("✗ ANTHROPIC_API_KEY no está configurada.")
        print("  Agrega: export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    print("✓ IA disponible. Probando interpretación...\n")

    casos_prueba = [
        (
            [{'valor':'boca_abierta','tipo':'BOCA_ABIERTA','significado':'tiene hambre o sed','negado':False,'urgente':False},
             {'valor':'palma_arriba','tipo':'PALMA_ARRIBA','significado':'quiere que le den el desayuno','negado':False,'urgente':False}],
            'manana', False
        ),
        (
            [{'valor':'ay','tipo':'AY','significado':'siente un dolor muy intenso','negado':False,'urgente':False},
             {'valor':'senala_propio','tipo':'SENALA_PROPIO','significado':'le duele algo en su cuerpo','negado':False,'urgente':True}],
            'dolor', True
        ),
        (
            [{'valor':'sonrie','tipo':'SONRIE','significado':'está contento','negado':False,'urgente':False},
             {'valor':'cabeza_si','tipo':'CABEZA_SI','significado':'afirma o está de acuerdo','negado':False,'urgente':False}],
            None, False
        ),
        (
            [{'valor':'mueve_pulgares','tipo':'MUEVE_PULGARES','significado':'quiere jugar videojuegos','negado':False,'urgente':False},
             {'valor':'agita','tipo':'AGITA','significado':'llama la atención urgentemente','negado':False,'urgente':False}],
            'tarde', False
        ),
    ]

    for infos, ctx, urgente in casos_prueba:
        tokens_str = " + ".join(
            ("~" if i["negado"] else "") + i["valor"] + ("!" if i["urgente"] else "")
            for i in infos
        )
        entrada = f"[{ctx}] {tokens_str}" if ctx else tokens_str
        print(f"Entrada:  {entrada}")
        resultado = interpretar_con_ia(infos, ctx, urgente)
        print(f"IA:       {resultado}")
        print("-" * 55)
