import sys
import ply.yacc as yacc
from lexer import tokens, lexer

sys.stdout.reconfigure(encoding='utf-8')

# ── Nodos del AST ────────────────────────────────────────────────────────────

class NodoPrograma:
    def __init__(self, expresiones):
        self.expresiones = expresiones  # lista de NodoExpresion

    def __repr__(self):
        return f"Programa({len(self.expresiones)} expresion(es))"


class NodoExpresion:
    def __init__(self, alternativas, contexto=None):
        self.contexto    = contexto      # string: 'manana', 'noche', etc. o None
        self.alternativas = alternativas  # lista de NodoSecuencia

    def __repr__(self):
        ctx = f"[{self.contexto}] " if self.contexto else ""
        return f"Expresion({ctx}{len(self.alternativas)} alternativa(s))"


class NodoSecuencia:
    def __init__(self, terminos):
        self.terminos = terminos  # lista de NodoTermino

    def __repr__(self):
        return f"Secuencia({len(self.terminos)} termino(s))"


class NodoTermino:
    def __init__(self, token_valor, token_tipo, negado=False, urgente=False):
        self.token_valor = token_valor  # 'mmm', 'sonrie', etc.
        self.token_tipo  = token_tipo   # 'MMM', 'SONRIE', etc.
        self.negado      = negado       # True si fue precedido por ~
        self.urgente     = urgente      # True si fue seguido por !

    def __repr__(self):
        mod = ("~" if self.negado else "") + ("!" if self.urgente else "")
        return f"Termino({mod}{self.token_valor})"


# ── Precedencia de operadores ────────────────────────────────────────────────
#   De menor a mayor prioridad (el último tiene mayor prioridad)

precedence = (
    ('left',  'O'),        # |  alternativa        — menor prioridad
    ('left',  'MAS'),      # +  secuencia
    ('left',  'URGENTE'),  # !  urgencia (postfijo)
    ('right', 'NEG'),      # ~  negación (prefijo)  — mayor prioridad
)


# ── Reglas gramaticales ──────────────────────────────────────────────────────

# programa : una o varias expresiones separadas por ;
def p_programa(p):
    'programa : expresion'
    p[0] = NodoPrograma([p[1]])

def p_programa_multiples(p):
    'programa : programa FIN_EXPR expresion'
    p[1].expresiones.append(p[3])
    p[0] = p[1]


# expresion : secuencia sola, con contexto, o unidas por |
def p_expresion_simple(p):
    'expresion : secuencia'
    p[0] = NodoExpresion([p[1]])

def p_expresion_con_contexto(p):
    'expresion : CONTEXTO secuencia'
    p[0] = NodoExpresion([p[2]], contexto=p[1])

def p_expresion_alternativa(p):
    'expresion : expresion O secuencia'
    p[1].alternativas.append(p[3])
    p[0] = p[1]


# secuencia : uno o varios términos unidos por +
def p_secuencia_simple(p):
    'secuencia : termino'
    p[0] = NodoSecuencia([p[1]])

def p_secuencia_mas(p):
    'secuencia : secuencia MAS termino'
    p[1].terminos.append(p[3])
    p[0] = p[1]


# termino : token solo, negado con ~ o urgente con !
def p_termino_base(p):
    'termino : token_base'
    p[0] = p[1]

def p_termino_negado(p):
    'termino : NEG termino'
    p[2].negado = True
    p[0] = p[2]

def p_termino_urgente(p):
    'termino : termino URGENTE'
    p[1].urgente = True
    p[0] = p[1]


# token_base : cualquiera de los 55 tokens del alfabeto
def p_token_base(p):
    '''token_base : MMM
                  | ATA
                  | AAH
                  | UUH
                  | OH
                  | SHH
                  | HMM
                  | UFF
                  | AY
                  | ANA
                  | BAH
                  | PFF
                  | SENALA
                  | PALMA_ARRIBA
                  | PALMA_ABAJO
                  | PUNO
                  | MANO_ABIERTA
                  | TOCA
                  | AGITA
                  | APUNTA_SI
                  | JUNTA_DEDOS
                  | SEPARA_MANOS
                  | PULGAR_ARRIBA
                  | PULGAR_ABAJO
                  | SONIDO_LARGO
                  | SONIDO_CORTO
                  | SONIDO_REPETIDO
                  | SONIDO_AGUDO
                  | SONIDO_GRAVE
                  | SONIDO_SUAVE
                  | CABEZA_SI
                  | CABEZA_NO
                  | CABEZA_LADO
                  | INCLINA_CUERPO
                  | ACERCA_CUERPO
                  | ALEJA_CUERPO
                  | SENALA_PROPIO
                  | SENALA_EXTERNO
                  | ENCOGE_HOMBROS
                  | LEVANTA_BRAZO
                  | CIERRA_OJOS
                  | ABRE_OJOS
                  | FRUNCE_CENO
                  | SONRIE
                  | LLANTO
                  | BOCA_ABIERTA
                  | MIRA_ARRIBA
                  | MIRA_ABAJO
                  | MIRA_OBJETO
                  | PARPADEO_RAPIDO
                  | RAPIDO
                  | LENTO
                  | DOBLE
                  | TRIPLE
                  | PAUSA'''
    p[0] = NodoTermino(token_valor=p[1], token_tipo=p.slice[1].type)


# ── Recuperación de errores ──────────────────────────────────────────────────

def p_secuencia_error_mas(p):
    'secuencia : secuencia MAS error'
    print(f"Error sintáctico en línea {p.lineno(3)}: "
          f"se esperaba un token después de '+'")
    p[0] = p[1]

def p_error(p):
    if p:
        print(f"Error sintáctico en línea {p.lineno}: "
              f"token inesperado '{p.value}' (tipo {p.type})")
        parser.errok()
    else:
        print("Error sintáctico: la entrada terminó de forma inesperada")


# ── Construcción del parser ──────────────────────────────────────────────────

parser = yacc.yacc()


# ── Visualización del AST ────────────────────────────────────────────────────

def imprimir_ast(nodo, prefijo="", es_ultimo=True):
    conector = "└── " if es_ultimo else "├── "
    print(prefijo + conector + repr(nodo))
    prefijo_hijo = prefijo + ("    " if es_ultimo else "│   ")

    if isinstance(nodo, NodoPrograma):
        for i, expr in enumerate(nodo.expresiones):
            imprimir_ast(expr, prefijo_hijo, i == len(nodo.expresiones) - 1)

    elif isinstance(nodo, NodoExpresion):
        for i, seq in enumerate(nodo.alternativas):
            imprimir_ast(seq, prefijo_hijo, i == len(nodo.alternativas) - 1)

    elif isinstance(nodo, NodoSecuencia):
        for i, term in enumerate(nodo.terminos):
            imprimir_ast(term, prefijo_hijo, i == len(nodo.terminos) - 1)


def analizar(entrada):
    lexer.lineno = 1
    resultado = parser.parse(entrada, lexer=lexer)
    return resultado


# ── Pruebas ──────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    casos = [
        ("Secuencia básica",          "mmm + palma_arriba + sonido_largo"),
        ("Con contexto",              "[manana] boca_abierta + senala_propio"),
        ("Con negación",              "~cabeza_no + sonrie"),
        ("Con urgencia",              "[dolor] sonido_largo + frunce_ceno !"),
        ("Con alternativa",           "palma_arriba | mira_objeto"),
        ("Dos expresiones con ;",     "[manana] sonrie + cabeza_si ; [dolor] ay + senala_propio"),
        ("Combinado complejo",        "[dolor] ~sonrie + uff + sonido_largo !"),
        ("Error: empieza con +",      "+ mmm"),
        ("Error: doble operador",     "mmm + + palma_arriba"),
        ("Error: ! al inicio",        "! sonido_largo"),
    ]

    for descripcion, entrada in casos:
        print(f"\n{'='*55}")
        print(f"  {descripcion}")
        print(f"  Entrada: {entrada}")
        print(f"{'='*55}")
        ast = analizar(entrada)
        if ast:
            imprimir_ast(ast)
        else:
            print("  (no se pudo construir el AST)")
