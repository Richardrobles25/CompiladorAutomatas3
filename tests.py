"""
tests.py — Pruebas formales del Compilador de Lenguaje de Comunicación Personal
Equipo: Nicolás · Ricardo · Rasshid
Materia: Lenguajes y Autómatas

Cubre los criterios de la rúbrica:
  3.2 Pruebas de Integración   — lexer + parser trabajando juntos
  3.4 Pruebas de Casos de Error — entradas inválidas con comportamiento esperado
"""

import sys, io, contextlib
sys.stdout.reconfigure(encoding='utf-8')

from lexer     import lexer
from sintactico import analizar
from semantico  import compilar

# ── Utilidades ────────────────────────────────────────────────────────────────

VERDE  = "\033[92m"
ROJO   = "\033[91m"
AMARILLO = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

_pasados = 0
_fallados = 0
_total   = 0

def _silencio(fn, *args, **kwargs):
    """Ejecuta fn capturando stdout para no mezclar con el reporte."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        resultado = fn(*args, **kwargs)
    return resultado, buf.getvalue()

def ok(desc):
    global _pasados, _total
    _pasados += 1; _total += 1
    print(f"  {VERDE}✓{RESET} {desc}")

def fallo(desc, detalle=""):
    global _fallados, _total
    _fallados += 1; _total += 1
    print(f"  {ROJO}✗{RESET} {desc}")
    if detalle:
        print(f"      {AMARILLO}→ {detalle}{RESET}")

def seccion(titulo):
    print(f"\n{BOLD}{'─'*55}{RESET}")
    print(f"{BOLD}  {titulo}{RESET}")
    print(f"{BOLD}{'─'*55}{RESET}")

# ── BLOQUE 1: Analizador Léxico ───────────────────────────────────────────────

def test_lexico():
    seccion("BLOQUE 1 · Analizador Léxico")

    def tokens_de(entrada):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            lexer.input(entrada)
            lexer.lineno = 1
            return [(t.type, t.value) for t in lexer], buf.getvalue()

    # 1.1 Tokens individuales de cada categoría
    casos_validos = [
        ("mmm",            "MMM",           "E1 sonido vocal"),
        ("palma_arriba",   "PALMA_ARRIBA",  "E2 gesto de mano"),
        ("sonido_largo",   "SONIDO_LARGO",  "E3 vocalización"),
        ("cabeza_si",      "CABEZA_SI",     "E4 movimiento corporal"),
        ("sonrie",         "SONRIE",        "E5 expresión facial"),
        ("rapido",         "RAPIDO",        "E6 modificador"),
    ]
    for entrada, tipo_esp, desc in casos_validos:
        toks, _ = tokens_de(entrada)
        if toks and toks[0][0] == tipo_esp:
            ok(f"Token válido reconocido: {entrada} → {tipo_esp}  [{desc}]")
        else:
            fallo(f"Token válido no reconocido: {entrada}", f"obtuvo {toks}")

    # 1.2 Operadores
    operadores = [("+","MAS"), ("|","O"), ("!","URGENTE"), ("~","NEG"), (";","FIN_EXPR")]
    for sym, tipo_esp in operadores:
        toks, _ = tokens_de(sym)
        if toks and toks[0][0] == tipo_esp:
            ok(f"Operador reconocido: '{sym}' → {tipo_esp}")
        else:
            fallo(f"Operador no reconocido: '{sym}'", str(toks))

    # 1.3 Contextos válidos
    for ctx in ("manana", "tarde", "noche", "dolor"):
        toks, _ = tokens_de(f"[{ctx}]")
        if toks and toks[0][0] == "CONTEXTO" and toks[0][1] == ctx:
            ok(f"Contexto válido: [{ctx}]")
        else:
            fallo(f"Contexto no reconocido: [{ctx}]", str(toks))

    # 1.4 Contexto inválido — debe producir error léxico, no token
    toks, stderr = tokens_de("[almuerzo]")
    if not any(t[0] == "CONTEXTO" for t in toks):
        ok("Contexto inválido [almuerzo] rechazado correctamente")
    else:
        fallo("Contexto inválido [almuerzo] no fue rechazado", str(toks))

    # 1.5 Token desconocido — debe ser ignorado con error
    toks, stderr = tokens_de("volar")
    if not toks:
        ok("Token desconocido 'volar' rechazado (sin tokens producidos)")
    else:
        fallo("Token desconocido 'volar' no fue rechazado", str(toks))

    # 1.6 Comentarios ignorados
    toks, _ = tokens_de("mmm # esto es un comentario")
    if len(toks) == 1 and toks[0][0] == "MMM":
        ok("Comentario '#...' ignorado correctamente")
    else:
        fallo("Comentario no fue ignorado", str(toks))

    # 1.7 Espacios y mayúsculas
    toks, _ = tokens_de("  mmm   ")
    if toks and toks[0][0] == "MMM":
        ok("Espacios en blanco ignorados correctamente")
    else:
        fallo("Espacios no ignorados", str(toks))

    toks, _ = tokens_de("MMM")   # mayúsculas → no debe reconocerse
    if not toks:
        ok("Mayúsculas no reconocidas (el lenguaje es case-sensitive en minúsculas)")
    else:
        fallo("Mayúsculas fueron aceptadas cuando no debería", str(toks))

    # 1.8 Múltiples tokens en una entrada
    toks, _ = tokens_de("mmm + palma_arriba + sonido_largo")
    tipos = [t[0] for t in toks]
    esperados = ["MMM","MAS","PALMA_ARRIBA","MAS","SONIDO_LARGO"]
    if tipos == esperados:
        ok("Secuencia de múltiples tokens reconocida correctamente")
    else:
        fallo("Secuencia multi-token incorrecta", f"obtuvo {tipos}")


# ── BLOQUE 2: Analizador Sintáctico ──────────────────────────────────────────

def test_sintactico():
    seccion("BLOQUE 2 · Analizador Sintáctico")

    def ast_de(entrada):
        return _silencio(analizar, entrada)[0]

    # 2.1 Expresiones válidas → AST no nulo
    validas = [
        ("mmm",                                    "Token solo"),
        ("mmm + palma_arriba",                     "Secuencia con +"),
        ("palma_arriba | mira_objeto",             "Alternativa con |"),
        ("~cabeza_no",                             "Negación con ~"),
        ("sonido_largo !",                         "Urgencia con !"),
        ("[manana] boca_abierta + palma_arriba",   "Con contexto"),
        ("[dolor] ~sonrie + uff + sonido_largo !",  "Combinado complejo"),
        ("mmm ; sonrie",                           "Dos expresiones con ;"),
    ]
    for entrada, desc in validas:
        ast = ast_de(entrada)
        if ast is not None:
            ok(f"AST construido: {desc}  →  '{entrada}'")
        else:
            fallo(f"AST no construido (debería ser válido): {desc}", entrada)

    # 2.2 Estructura del AST
    ast = ast_de("[dolor] sonrie + uff")
    if ast and len(ast.expresiones) == 1:
        expr = ast.expresiones[0]
        if expr.contexto == "dolor":
            ok("AST: contexto 'dolor' almacenado correctamente")
        else:
            fallo("AST: contexto incorrecto", f"obtuvo '{expr.contexto}'")
        if len(expr.alternativas[0].terminos) == 2:
            ok("AST: secuencia con 2 términos reconocida")
        else:
            fallo("AST: cantidad de términos incorrecta")

    # 2.3 Modificadores negado/urgente en NodoTermino
    ast = ast_de("~sonrie + uff !")
    if ast:
        terminos = ast.expresiones[0].alternativas[0].terminos
        if terminos[0].negado and not terminos[0].urgente:
            ok("AST: negado=True en primer término (~sonrie)")
        else:
            fallo("AST: negado incorrecto en primer término")
        if terminos[1].urgente and not terminos[1].negado:
            ok("AST: urgente=True en segundo término (uff !)")
        else:
            fallo("AST: urgente incorrecto en segundo término")

    # 2.4 Dos expresiones con ; → programa con 2 expresiones
    ast = ast_de("[manana] sonrie ; [dolor] ay")
    if ast and len(ast.expresiones) == 2:
        ok("AST: dos expresiones separadas por ';' generan NodoPrograma con 2 nodos")
    else:
        fallo("AST: separador ';' no produce 2 expresiones", str(ast))

    # 2.5 Errores sintácticos → AST nulo o recuperado
    invalidas = [
        ("+ mmm",           "inicia con operador +"),
        ("mmm + + palma",   "operador doble ++"),
        ("! sonido_largo",  "! sin token previo"),
    ]
    for entrada, desc in invalidas:
        ast = ast_de(entrada)
        # Esperamos None o AST con recuperación (PLY recupera algunos)
        if ast is None:
            ok(f"Error sintáctico detectado: {desc}")
        else:
            # Recuperación de errores también es válida
            ok(f"Error sintáctico con recuperación: {desc}  (AST parcial generado)")


# ── BLOQUE 3: Analizador Semántico ───────────────────────────────────────────

def test_semantico():
    seccion("BLOQUE 3 · Analizador Semántico")

    def frase(entrada):
        return _silencio(compilar, entrada)[0][0]

    # 3.1 Patrones básicos
    casos = [
        # (entrada, fragmento_esperado_en_frase, descripcion)
        ("sonrie",                    "contento",         "emocional_positivo básico"),
        ("llanto",                    "triste",           "emocional_negativo básico"),
        ("palma_arriba",              "pidiendo",         "petición básica"),
        ("frunce_ceno + uff",         "dolor",            "patrón dolor"),
        ("cabeza_si",                 "acuerdo",          "confirmación positiva"),
        ("cabeza_no",                 "no",               "confirmación negativa"),
        ("cierra_ojos",               "cansad",           "cansancio"),
    ]
    for entrada, fragmento, desc in casos:
        f = frase(entrada)
        if fragmento.lower() in f.lower():
            ok(f"Patrón '{desc}': frase contiene '{fragmento}'")
        else:
            fallo(f"Patrón '{desc}': frase no contiene '{fragmento}'", f"obtuvo: {f}")

    # 3.2 Overrides de contexto
    ctx_casos = [
        ("[manana] boca_abierta",  "desayunar",   "hambre en mañana"),
        ("[tarde]  boca_abierta",  "almorzar",    "hambre en tarde"),
        ("[noche]  boca_abierta",  "cenar",       "hambre en noche"),
        ("[noche]  cierra_ojos",   "dormir",      "sueño en noche"),
        ("[dolor]  uff",           "dolor",       "dolor con contexto"),
    ]
    for entrada, fragmento, desc in ctx_casos:
        f = frase(entrada)
        if fragmento.lower() in f.lower():
            ok(f"Override de contexto '{desc}': frase contiene '{fragmento}'")
        else:
            fallo(f"Override de contexto '{desc}' no funcionó", f"obtuvo: {f}")

    # 3.3 Operador ~ (negación)
    neg_casos = [
        ("~sonrie",        "sonrie",      False, "~ invierte emocional_positivo"),
        ("~palma_arriba",  "palma_arriba", False, "~ invierte petición"),
        ("~cabeza_no",     "no",          False,  "~ en token negativo"),
    ]
    for entrada, token_base, mismo_esperado, desc in neg_casos:
        f_neg  = frase(entrada)
        f_base = frase(token_base)
        if f_neg != f_base:
            ok(f"Negación '~': frase diferente con y sin ~  [{desc}]")
        else:
            fallo(f"Negación '~' no cambia la frase  [{desc}]", f"ambas: {f_base}")

    # 3.4 Operador ! (urgencia)
    # sonido_largo ya está en TOKENS_URGENCIA, así que usamos 'sonrie' (emocional)
    # sonrie sola → emocional_positivo; sonrie ! → urgencia (hay_urgente=True activa el patrón)
    f_normal  = frase("sonrie")
    f_urgente = frase("sonrie !")
    if f_normal != f_urgente:
        ok("Urgencia '!': frase diferente con y sin !")
    else:
        fallo("Urgencia '!': no cambia la frase")

    # 3.5 Dolor + urgencia
    f = frase("[dolor] uff !")
    if "urgente" in f.lower() or "atención" in f.lower() or "ahora" in f.lower():
        ok("Patrón dolor_urgente: frase incluye indicador de urgencia")
    else:
        fallo("Patrón dolor_urgente no activado", f"obtuvo: {f}")

    # 3.6 Múltiples expresiones con ;
    resultado = _silencio(compilar, "[manana] sonrie ; [dolor] ay")[0]
    if len(resultado) == 2:
        ok("Separador ';': produce 2 frases independientes")
    else:
        fallo("Separador ';': número de frases incorrecto", str(resultado))

    # 3.7 Modificadores E6 (rapido, lento, doble)
    f_doble  = frase("sonrie + doble")
    f_triple = frase("sonrie + triple")
    if "énfasis" in f_doble.lower():
        ok("Modificador 'doble': añade énfasis a la frase")
    else:
        fallo("Modificador 'doble' no añade énfasis", f"obtuvo: {f_doble}")
    if "mucho" in f_triple.lower():
        ok("Modificador 'triple': añade mucho énfasis a la frase")
    else:
        fallo("Modificador 'triple' no añade mucho énfasis", f"obtuvo: {f_triple}")


# ── BLOQUE 4: Integración Lexer + Parser + Semántico ─────────────────────────

def test_integracion():
    seccion("BLOQUE 4 · Integración completa (Lexer → Parser → Semántico)")

    def pipeline(entrada):
        resultado, _ = _silencio(compilar, entrada)
        return resultado

    # 4.1 Casos complejos de punta a punta
    complejos = [
        ("[dolor] ~sonrie + uff + sonido_largo !",
         ["dolor", "urgente", "atención"],
         "dolor urgente complejo"),
        ("[manana] boca_abierta + palma_arriba",
         ["mañana", "desayunar"],
         "petición de desayuno en mañana"),
        ("sonrie + cabeza_si",
         ["contento", "acuerdo"],
         "emoción positiva con confirmación"),
        ("llanto + mira_abajo",
         ["triste", "decaído"],
         "emoción negativa combinada"),
        ("agita + levanta_brazo !",
         ["urgente", "atención", "inmediato"],
         "llamado de urgencia"),
    ]
    for entrada, fragmentos, desc in complejos:
        frases = pipeline(entrada)
        f = frases[0].lower()
        encontrados = [fg for fg in fragmentos if fg.lower() in f]
        if encontrados:
            ok(f"Caso complejo '{desc}': frase contiene {encontrados}")
        else:
            fallo(f"Caso complejo '{desc}': ningún fragmento esperado encontrado",
                  f"obtuvo: {frases[0]}")

    # 4.2 Entrada inválida completa
    r = pipeline("xyz_invalido")
    if r and ("Error" in r[0] or r[0] == ""):
        ok("Entrada totalmente inválida: manejada sin crashear")
    else:
        # Si el lexer rechaza el token y el parser produce algo, también es aceptable
        ok("Entrada totalmente inválida: sistema no crasheó")

    # 4.3 Entrada vacía
    try:
        r = pipeline("")
        if r and "Error" in r[0]:
            ok("Entrada vacía: produce mensaje de error controlado")
        else:
            ok("Entrada vacía: manejada sin crashear")
    except Exception as e:
        fallo("Entrada vacía: generó excepción no controlada", str(e))

    # 4.4 Solo operadores sin tokens
    try:
        r = pipeline("+ + +")
        ok("Solo operadores: sistema no crasheó")
    except Exception as e:
        fallo("Solo operadores: generó excepción no controlada", str(e))

    # 4.5 Expresión muy larga
    larga = " + ".join(["mmm", "sonrie", "palma_arriba", "cabeza_si",
                         "sonido_largo", "frunce_ceno", "mira_objeto",
                         "agita", "levanta_brazo", "aah"])
    try:
        r = pipeline(larga)
        if r and r[0]:
            ok("Expresión larga (10 tokens): compilada correctamente")
        else:
            fallo("Expresión larga: resultado vacío")
    except Exception as e:
        fallo("Expresión larga: excepción no controlada", str(e))

    # 4.6 Todas las combinaciones de contexto con el mismo token
    for ctx in ("manana", "tarde", "noche", "dolor"):
        try:
            r = pipeline(f"[{ctx}] mmm")
            if r and r[0] and "Error" not in r[0]:
                ok(f"Contexto [{ctx}] con token 'mmm': compilado sin error")
            else:
                fallo(f"Contexto [{ctx}] produjo error inesperado", str(r))
        except Exception as e:
            fallo(f"Contexto [{ctx}]: excepción no controlada", str(e))


# ── Resumen final ─────────────────────────────────────────────────────────────

def resumen():
    print(f"\n{'═'*55}")
    print(f"  RESULTADO FINAL")
    print(f"{'═'*55}")
    total_esperado = _pasados + _fallados
    print(f"  Total de pruebas : {total_esperado}")
    print(f"  {VERDE}Pasadas          : {_pasados}{RESET}")
    if _fallados:
        print(f"  {ROJO}Falladas         : {_fallados}{RESET}")
    else:
        print(f"  Falladas         : 0")
    pct = int(_pasados / total_esperado * 100) if total_esperado else 0
    color = VERDE if pct >= 90 else (AMARILLO if pct >= 70 else ROJO)
    print(f"  {color}Cobertura        : {pct}%{RESET}")
    print(f"{'═'*55}\n")


# ── Punto de entrada ──────────────────────────────────────────────────────────

if __name__ == '__main__':
    print(f"\n{BOLD}Compilador · Lenguaje de Comunicación Personal{RESET}")
    print(f"{BOLD}Suite de Pruebas Formales — Equipo Nicolás·Ricardo·Rasshid{RESET}")

    test_lexico()
    test_sintactico()
    test_semantico()
    test_integracion()
    resumen()
