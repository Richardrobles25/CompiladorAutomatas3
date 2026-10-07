# Contexto Técnico del Compilador
## Lenguaje de Comunicación Personal — Lenguajes y Autómatas 2026
**Equipo:** Nicolás · Ricardo · Rasshid

---

## ¿Qué es este compilador?

Un compilador que traduce secuencias de **tokens** — cada uno representando un sonido, gesto o expresión corporal — a frases en español natural. El cuidador observa a la persona, escribe los tokens en la interfaz, y el compilador valida y traduce.

El compilador **NO** reconoce voz ni gestos automáticamente. Todo el peso de observación lo lleva el cuidador. El compilador formaliza, valida y traduce lo que el cuidador ingresa.

---

## Archivos del proyecto

```
CompiladorAutomatas3/
│
├── main.py                        ← Punto de entrada. Verifica dependencias y lanza la GUI.
│                                    Ejecutar con: python main.py
│
├── lexer.py                       ← FASE 1 · Analizador léxico (PLY lex).
│                                    Define los 62 tokens con expresiones regulares.
│                                    Detecta errores LEX-001/002/003 y sugiere correcciones.
│
├── sintactico.py                  ← FASE 2 · Analizador sintáctico (PLY yacc, LALR-1).
│                                    Define la gramática BNF y construye el AST.
│                                    Contiene los 5 nodos: Programa, Expresion,
│                                    Secuencia, Termino, Grupo.
│                                    Detecta errores SIN-001 al SIN-010.
│
├── semantico.py                   ← FASE 3 · Analizador semántico.
│                                    Tabla de símbolos, significados base, overrides
│                                    por contexto, 13 patrones de detección y
│                                    generación de frases. Errores SEM-001 al SEM-004.
│
├── interpretador_ia.py            ← Capa opcional de IA (API de Claude / Anthropic).
│                                    Reemplaza la generación de frases por reglas con
│                                    una llamada a Claude. Incluye caché, manejo de
│                                    errores y modo de respaldo automático.
│
├── interfaz.py                    ← Interfaz gráfica (Tkinter).
│                                    Panel de tokens, selector de contexto, caja de
│                                    expresión, operadores, traducción, síntesis de
│                                    voz (PowerShell) e historial de compilaciones.
│
├── tests.py                       ← 70 pruebas formales (100% pasando).
│                                    4 bloques: léxico (21), sintáctico (16),
│                                    semántico (20), integración (13).
│
├── probar_lexer.py                ← Herramienta de prueba rápida del léxico
│                                    desde la terminal, sin abrir la interfaz.
│
├── parsetab.py                    ← [AUTO] Tabla LALR-1 generada por PLY.
│                                    No editar manualmente.
│
├── parser.out                     ← [AUTO] Log de diagnóstico del parser (PLY).
│                                    Muestra estados del autómata y conflictos.
│
├── BITACORA.md                    ← Registro cronológico del desarrollo:
│                                    decisiones, bugs, soluciones y etapas.
│
├── MANUAL_COMPILADOR.md           ← Manual interno: tokens, operadores,
│                                    contextos, gramática BNF y ejemplos.
│
├── .gitignore                     ← Archivos ignorados por Git (venv, __pycache__, etc.)
│
└── Documentacion/
    ├── Contexto.md                ← Este archivo. Descripción técnica del backend.
    │
    ├── Contexto/
    │   ├── BITACORA.md            ← Copia/versión de la bitácora de desarrollo.
    │   ├── COMBINACIONES.md       ← Tabla de combinaciones de tokens y sus frases.
    │   ├── CONTEXTO_COMPILADOR.md ← Notas de contexto del proyecto.
    │   └── MANUAL_COMPILADOR.md   ← Copia del manual interno.
    │
    ├── CompiladorLenguajesyAutomatas.pptx  ← Presentación del proyecto para clase.
    ├── Evaluación Proyecto LAI.pdf          ← Rúbrica de evaluación de la maestra.
    ├── PropuestaCompilador.docx             ← Propuesta inicial entregada al inicio.
    ├── EstadoDelArte.docx                   ← Estado del arte: sistemas de CAA.
    ├── JustificacionHatersMU.docx           ← Justificación del proyecto.
    └── Observaciones.docx                   ← Observaciones y retroalimentación.
```

---

## Arquitectura general

```
Entrada de texto (cuidador escribe tokens)
           ↓
   ┌───────────────┐
   │   FASE 1      │  lexer.py
   │   LÉXICO      │  Tokeniza la entrada
   └──────┬────────┘
          ↓
   ┌───────────────┐
   │   FASE 2      │  sintactico.py
   │  SINTÁCTICO   │  Valida gramática y construye AST
   └──────┬────────┘
          ↓
   ┌───────────────┐
   │   FASE 3      │  semantico.py + interpretador_ia.py
   │  SEMÁNTICO    │  Interpreta significado y genera frase
   └──────┬────────┘
          ↓
   Frase en español natural (texto + voz)
```

**Librería base:** PLY (Python Lex-Yacc) — implementación pura en Python de las herramientas clásicas `lex` y `yacc` de C. Genera autómatas y parsers automáticamente a partir de reglas definidas como funciones Python.

---

## Algoritmos del compilador — ¿cómo funciona cada fase?

Cada una de las 3 fases usa un algoritmo distinto. No todo es expresiones regulares.

| Fase | Archivo | Algoritmo | Tipo de autómata |
|---|---|---|---|
| Léxico | `lexer.py` | Expresiones regulares → AFD | Autómata Finito Determinista |
| Sintáctico | `sintactico.py` | LALR(1) | Autómata de Pila (Push-Down) |
| Semántico | `semantico.py` | Operaciones de conjuntos + diccionarios | Sin autómata — lógica pura |

---

### Fase 1 — Expresiones Regulares y AFD

El léxico **sí usa expresiones regulares**. Cada regla `t_ALGO` tiene un patrón regex como docstring. PLY toma todos esos patrones, los combina en una sola expresión regular gigante y construye internamente un **Autómata Finito Determinista (AFD)** que los reconoce todos a la vez.

#### Expresiones regulares del lexer

| Función | Regex | Qué reconoce | Ejemplo |
|---|---|---|---|
| `t_COMMENT` | `\#[^\n]*` | Línea de comentario completa | `# esto es un comentario` |
| `t_CONTEXTO` | `\[[a-z]+\]` | Corchete con letras minúsculas | `[manana]`, `[dolor]` |
| `t_MAS` | `\+` | Símbolo más | `+` |
| `t_O` | `\|` | Barra vertical | `\|` |
| `t_URGENTE` | `\!` | Signo de exclamación | `!` |
| `t_NEG` | `\~` | Virgulilla | `~` |
| `t_FIN_EXPR` | `\;` | Punto y coma | `;` |
| `t_TOKEN` | `[a-z][a-z0-9_]*` | Cualquier palabra minúscula | `mmm`, `palma_arriba` |
| `t_newline` | `\n+` | Uno o más saltos de línea | (cuenta líneas para errores) |
| `t_ignore` | ` \t` | Espacios y tabuladores | (se ignoran silenciosamente) |

#### Explicación de cada regex

```
\#[^\n]*
  \#       → el carácter # literal
  [^\n]*   → cualquier carácter excepto salto de línea, cero o más veces
  Resultado: consume toda la línea desde # hasta el final

\[[a-z]+\]
  \[       → corchete abierto literal (escapado porque [ tiene significado especial)
  [a-z]+   → una o más letras minúsculas de la a a la z
  \]       → corchete cerrado literal
  Resultado: reconoce [manana], [noche], [dolor], [tarde]

[a-z][a-z0-9_]*
  [a-z]    → exactamente una letra minúscula al inicio (no puede empezar con número ni _)
  [a-z0-9_]* → cero o más letras, números o guión bajo después
  Resultado: reconoce mmm, palma_arriba, sonido_largo, cabeza_si...
```

#### ¿Cómo construye PLY el AFD?
PLY combina todas las reglas en una sola regex con grupos nombrados:
```
(?P<COMMENT>\#[^\n]*)|(?P<CONTEXTO>\[[a-z]+\])|(?P<MAS>\+)|...
```
Luego usa el módulo `re` de Python para hacer match. Internamente Python convierte esa regex en un AFD usando el algoritmo de Thompson (NFA → DFA → minimización). Por eso el lexer es muy rápido: una sola pasada sobre la cadena.

#### Prioridad entre reglas
Cuando dos patrones podrían hacer match en el mismo punto, PLY aplica estas reglas de prioridad:
1. Las funciones (`t_CONTEXTO`, `t_TOKEN`, etc.) tienen prioridad sobre las variables
2. Entre funciones, se usa el **orden en que están definidas** en el archivo
3. En caso de empate, gana el patrón **más largo**

Por eso `t_CONTEXTO` (función) tiene prioridad sobre `t_TOKEN` (función también, pero definida después): si el lexer ve `[manana]`, lo reconoce como CONTEXTO completo y no intenta tokenizar `manana` por separado.

---

### Fase 2 — Algoritmo LALR(1)

El parser **no usa expresiones regulares**. Usa un algoritmo llamado **LALR(1)** que opera sobre un **Autómata de Pila** (también llamado Push-Down Automaton o PDA).

#### ¿Qué es LALR(1)?
- **L** → Left-to-right: lee los tokens de izquierda a derecha
- **A** → usa derivación por la derecha (Rightmost derivation) en reversa
- **LR** → construye el árbol de abajo hacia arriba (bottom-up)
- **(1)** → solo necesita ver **1 token adelante** (lookahead) para decidir qué hacer

#### Las dos operaciones del parser

En cada paso el parser decide entre dos acciones mirando el token actual y el estado de la pila:

| Operación | ¿Qué hace? | Cuándo ocurre |
|---|---|---|
| **SHIFT** (desplazar) | Empuja el token actual a la pila y avanza | Cuando el token puede continuar una regla |
| **REDUCE** (reducir) | Saca elementos de la pila y los reemplaza por un nodo del AST | Cuando una regla gramatical está completa |

#### Ejemplo paso a paso: `mmm + sonrie`

```
Tokens: MMM  MAS  SONRIE  $fin

Paso 1: SHIFT MMM
  Pila: [MMM]

Paso 2: REDUCE por "token_base : MMM"
  Pila: [token_base]

Paso 3: REDUCE por "termino : token_base"
  Pila: [termino]

Paso 4: REDUCE por "secuencia : termino"
  Pila: [secuencia]

Paso 5: SHIFT MAS
  Pila: [secuencia, MAS]

Paso 6: SHIFT SONRIE
  Pila: [secuencia, MAS, SONRIE]

Paso 7: REDUCE por "token_base : SONRIE"
  Pila: [secuencia, MAS, token_base]

Paso 8: REDUCE por "termino : token_base"
  Pila: [secuencia, MAS, termino]

Paso 9: REDUCE por "secuencia : secuencia MAS termino"
  Pila: [secuencia]   ← NodoSecuencia con 2 términos

Paso 10: REDUCE por "expresion : secuencia"
  Pila: [expresion]   ← NodoExpresion

Paso 11: REDUCE por "programa : expresion"
  Pila: [programa]    ← NodoPrograma ✓
```

#### La tabla de parsing (`parsetab.py`)
PLY genera automáticamente la tabla LALR(1) la primera vez que se corre el parser y la guarda en `parsetab.py`. Esta tabla tiene dos partes:
- **ACTION**: para cada estado + token, dice si hacer SHIFT, REDUCE o ERROR
- **GOTO**: para cada estado + símbolo no-terminal, dice a qué estado ir

Si se modifica la gramática, PLY regenera este archivo automáticamente.

#### La tabla de precedencia
La tabla de precedencia en `sintactico.py` resuelve ambigüedades del tipo "¿`a + b | c` es `(a+b)|c` o `a+(b|c)`?":

```python
precedence = (
    ('left', 'O'),        # | tiene la menor prioridad
    ('left', 'MAS'),      # + tiene más prioridad que |
    ('left', 'URGENTE'),  # ! tiene más prioridad que +
    ('right', 'NEG'),     # ~ se asocia de derecha a izquierda
    ('left', 'LPAREN', 'RPAREN'),  # () tienen la mayor prioridad
)
```

`right` en NEG significa que `~~sonrie` se lee como `~(~sonrie)` (de afuera hacia adentro).

---

### Fase 3 — Operaciones de Conjuntos

El semántico **no usa ni expresiones regulares ni autómatas**. Trabaja con **operaciones matemáticas sobre conjuntos** (sets de Python) y **búsquedas en diccionarios**.

#### Operaciones de conjuntos usadas

```python
# Intersección: ¿hay algún token de dolor en la secuencia activa?
if TOKENS_DOLOR & tipos_activos:
    return 'dolor'

# Subconjunto: ¿todos los tokens activos son de confirmación?
if tipos_activos <= TOKENS_CONFIRM:
    return 'confirmacion'

# Diferencia: tokens negativos que NO son también de cansancio
negativo_exclusivo = TOKENS_NEGATIVO - TOKENS_CANSANCIO
if negativo_exclusivo & tipos_activos:
    return 'emocional_negativo'
```

| Operación | Símbolo Python | Significado |
|---|---|---|
| Intersección | `A & B` | Tokens que están en ambos conjuntos |
| Diferencia | `A - B` | Tokens de A que no están en B |
| Subconjunto | `A <= B` | Todos los tokens de A están en B |
| Pertenencia | `x in A` | El token x está en el conjunto |

#### Búsquedas en diccionarios (O(1))
El significado de cada token se obtiene con una búsqueda directa en diccionario:

```python
sig = (OVERRIDE.get(contexto, {}).get(valor)   # busca override primero
       if contexto else None) or BASE.get(valor, valor)  # si no, usa base
```

Esto es O(1) — no importa cuántos tokens haya en el diccionario, siempre tarda lo mismo.

#### Complejidad del semántico
- Construir `tipos_activos`: O(n) donde n = número de tokens en la secuencia
- Detectar patrón: O(1) — son intersecciones de conjuntos de tamaño fijo
- Generar frase: O(n) — recorre la lista de significados una vez

En la práctica, con secuencias de máximo 6-8 tokens, todo es instantáneo.

---

### ¿Qué hace?
Lee la cadena de entrada carácter por carácter y la divide en **tokens**: las unidades mínimas del lenguaje. Es como separar una oración en palabras antes de analizarla.

### ¿Cómo funciona internamente?
PLY construye un **Autómata Finito Determinista (AFD)** a partir de expresiones regulares. Cada función `t_ALGO` define una regla que, si hace match, produce un token de ese tipo.

```python
# Ejemplo de regla léxica
def t_MAS(t):
    r'\+'          # expresión regular: el símbolo +
    return t       # devuelve el token MAS
```

El reconocimiento de palabras se hace mediante el `token_map`, un diccionario que mapea cada palabra en minúsculas a su tipo de token:

```python
token_map = {
    'mmm': 'MMM',
    'sonrie': 'SONRIE',
    'palma_arriba': 'PALMA_ARRIBA',
    # ... 62 tokens en total
}
```

### Reglas especiales

| Función | Expresión Regular | Qué hace |
|---|---|---|
| `t_COMMENT` | `\#[^\n]*` | Ignora líneas que empiezan con `#` |
| `t_CONTEXTO` | `\[[a-z]+\]` | Reconoce `[manana]`, `[noche]`, etc. |
| `t_TOKEN` | `[a-z][a-z0-9_]*` | Reconoce cualquier palabra en minúsculas |
| `t_newline` | `\n+` | Cuenta líneas para reportar errores con número de línea |
| `t_ignore` | espacio, tabulador | Los ignora silenciosamente |

### Sugerencias con `difflib`
Cuando un token no se reconoce, usa `difflib.get_close_matches` para encontrar el token más parecido del alfabeto y sugerirlo al usuario:

```
Token 'sonri' no reconocido.
→ ¿Quisiste decir: sonrie?
```

### Errores léxicos

| Código | Cuándo ocurre | Ejemplo |
|---|---|---|
| `[LEX-001]` | Token no reconocido | `sonri`, `palma_ariba` |
| `[LEX-002]` | Contexto inválido | `[mañana]`, `[desayuno]` |
| `[LEX-003]` | Carácter ilegal | `@`, `,`, `.` |

### Tokens del lenguaje (62 total)

#### E1 — Sonidos vocales (12)
`mmm` `ata` `aah` `uuh` `oh` `shh` `hmm` `uff` `ay` `ana` `bah` `pff`

#### E2 — Gestos de manos (16)
`senala` `palma_arriba` `palma_abajo` `puno` `mano_abierta` `toca` `agita` `apunta_si` `junta_dedos` `separa_manos` `pulgar_arriba` `pulgar_abajo` `dedoindice_boca` `mueve_pulgares` `mano_derecha_a_izquierda` `manos_palmas_hacia_arriba`

#### E3 — Vocalizaciones (7)
`sonido_largo` `sonido_corto` `sonido_repetido` `sonido_agudo` `sonido_grave` `sonido_suave` `sonido_ronquido`

#### E4 — Movimientos corporales (10)
`cabeza_si` `cabeza_no` `cabeza_lado` `inclina_cuerpo` `acerca_cuerpo` `aleja_cuerpo` `senala_propio` `senala_externo` `encoge_hombros` `levanta_brazo`

#### E5 — Expresiones faciales (10)
`cierra_ojos` `abre_ojos` `frunce_ceno` `sonrie` `llanto` `boca_abierta` `mira_arriba` `mira_abajo` `mira_objeto` `parpadeo_rapido`

#### E6 — Modificadores de intensidad (5)
`rapido` `lento` `doble` `triple` `pausa`

#### Operadores (5)
`+` (MAS) · `|` (O) · `!` (URGENTE) · `~` (NEG) · `;` (FIN_EXPR)

#### Contextos (1 tipo de token, 4 valores válidos)
`[manana]` `[tarde]` `[noche]` `[dolor]`

---

## FASE 2 — Análisis Sintáctico (`sintactico.py`)

### ¿Qué hace?
Recibe la lista de tokens del léxico y verifica que estén organizados según la **gramática del lenguaje**. Si la estructura es válida, construye el **AST** (Árbol de Sintaxis Abstracta).

### ¿Qué es un AST?
Un árbol donde cada nodo representa una parte de la expresión. Por ejemplo:

```
Entrada: [manana] sonrie + cabeza_si

AST:
└── Programa
    └── Expresion([manana])
        └── Secuencia
            ├── Termino(sonrie)
            └── Termino(cabeza_si)
```

### Tipo de parser: LALR(1)
PLY yacc genera un parser **LALR(1)** (Left-to-right, Rightmost derivation, 1 token de anticipación):
- Lee de izquierda a derecha
- Construye el árbol de abajo hacia arriba (bottom-up)
- Solo necesita ver 1 token adelante para decidir qué regla aplicar

### Gramática BNF del lenguaje

```bnf
programa     ::= expresion
              |  programa ';' expresion

expresion    ::= secuencia
              |  CONTEXTO secuencia
              |  expresion '|' secuencia

secuencia    ::= termino
              |  secuencia '+' termino

termino      ::= token_base
              |  '~' termino
              |  termino '!'
              |  '(' expresion ')'
              |  '(' expresion ')' '!'

token_base   ::= MMM | ATA | AAH | ... (62 tokens)
```

### Tabla de precedencia de operadores

| Nivel | Operador | Tipo | Prioridad |
|---|---|---|---|
| 1 (mayor) | `( )` | Agrupación | Mayor |
| 2 | `~` | Prefijo unario | Alta |
| 3 | `!` | Postfijo unario | Media-alta |
| 4 | `+` | Binario izq→der | Media |
| 5 (menor) | `\|` | Binario izq→der | Menor |

Esto significa que `a + b | c` se lee como `(a + b) | c`, y `~a + b` se lee como `(~a) + b`.

### Nodos del AST

#### `NodoPrograma`
La raíz del árbol. Contiene una lista de expresiones (separadas por `;`).
```python
class NodoPrograma:
    def __init__(self, expresiones):
        self.expresiones = expresiones  # lista de NodoExpresion
```

#### `NodoExpresion`
Representa una idea completa. Guarda el contexto (`manana`, `dolor`, etc.) y la lista de alternativas (separadas por `|`).
```python
class NodoExpresion:
    def __init__(self, alternativas, contexto=None):
        self.contexto     = contexto      # 'manana', 'noche', etc. o None
        self.alternativas = alternativas  # lista de NodoSecuencia
```

#### `NodoSecuencia`
Una cadena de tokens unidos por `+`.
```python
class NodoSecuencia:
    def __init__(self, terminos):
        self.terminos = terminos  # lista de NodoTermino
```

#### `NodoTermino`
Un token individual con sus modificadores.
```python
class NodoTermino:
    def __init__(self, token_valor, token_tipo, negado=False,
                 urgente=False, es_modificador=False):
        self.token_valor    = token_valor    # 'mmm', 'sonrie', etc.
        self.token_tipo     = token_tipo     # 'MMM', 'SONRIE', etc.
        self.negado         = negado         # True si lleva ~ adelante
        self.urgente        = urgente        # True si lleva ! atrás
        self.es_modificador = es_modificador # True si es E6
```

#### `NodoGrupo`
Una subexpresión entre paréntesis. Permite `(mmm | uff) + sonrie`.
```python
class NodoGrupo:
    def __init__(self, expresion):
        self.expresion = expresion  # NodoExpresion interior
        self.negado    = False
        self.urgente   = False
```

### Recuperación de errores
El parser no se detiene al encontrar un error — usa `parser.errok()` para recuperarse e intentar seguir analizando el resto de la entrada.

### Errores sintácticos

| Código | Cuándo ocurre |
|---|---|
| `[SIN-001]` | Operador `+` o `\|` en posición inválida |
| `[SIN-002]` | `!` sin token previo, o `~` mal colocado |
| `[SIN-003]` | Token faltante después de `+` |
| `[SIN-004]` | `;` sin expresión válida antes o después |
| `[SIN-005]` | Contexto `[...]` fuera del inicio |
| `[SIN-006]` | Entrada terminada de forma incompleta |
| `[SIN-007]` | Se intentó negar un modificador E6 (`~rapido`) |
| `[SIN-008]` | `!` aplicado a un modificador E6 (`lento !`) |
| `[SIN-009]` | Modificador E6 usado solo sin token expresivo |
| `[SIN-010]` | Paréntesis sin cerrar o vacíos |

---

## FASE 3 — Análisis Semántico (`semantico.py`)

### ¿Qué hace?
Recibe el AST y lo interpreta: decide qué quiere comunicar la persona y genera la frase en español.

### Tabla de símbolos
Es el equivalente a la tabla de variables de un compilador convencional. En este compilador no hay variables, pero sí un **perfil de sesión** que se consulta durante la interpretación:

```python
class TablaSimbolos:
    def reset(self):
        self.contexto_activo = None   # 'manana', 'noche', etc.
        self.hay_urgencia    = False  # si algún token lleva !
```

Se reinicia con cada compilación nueva.

### Significados base (`BASE`)
Diccionario con el significado general de cada token, sin importar el contexto:

```python
BASE = {
    'mmm':          'está pensando o dudando',
    'sonrie':       'está contento',
    'palma_arriba': 'está pidiendo algo',
    'llanto':       'está muy triste o tiene dolor intenso',
    # ... 62 tokens
}
```

### Overrides por contexto (`OVERRIDE`)
Cuando hay contexto, algunos tokens cambian de significado. Ejemplo:

```python
OVERRIDE = {
    'manana': {
        'boca_abierta': 'quiere desayunar',    # (sin contexto sería "tiene hambre o sed")
        'cierra_ojos':  'aún quiere dormir más',
        'cabeza_no':    'no quiere levantarse',
    },
    'noche': {
        'boca_abierta': 'quiere cenar',
        'cierra_ojos':  'quiere dormir ya',
    },
    # ...
}
```

El proceso siempre busca primero en OVERRIDE, y si no encuentra, usa BASE.

### Detección de patrones (`detectar_patron`)
La función más importante del semántico. Analiza el conjunto de tokens activos (los que **no** están negados) y determina a cuál de los **13 patrones** pertenece la secuencia:

```python
tipos_activos = {t for t, n in zip(tipos, negados) if not n}
```

Los tokens negados con `~` se excluyen del análisis de patrones. Si dices `~sonrie`, ese token no cuenta como señal positiva.

#### Los 13 patrones (en orden de prioridad):

| Patrón | Se activa cuando | Ejemplo de frase |
|---|---|---|
| `dolor_urgente` | hay `!` + contexto dolor o tokens de dolor | *"¡Siente dolor agudo! Necesita atención urgente."* |
| `urgencia` | hay `!` o tokens urgentes (agita, levanta_brazo...) | *"¡Está llamando la atención! Es urgente."* |
| `dolor` | contexto `[dolor]` o tokens de dolor (uff, ay, frunce_ceno...) | *"Tiene dolor o malestar."* |
| `emocional_positivo` | tokens positivos (sonrie, aah, apunta_si) | *"Está contento."* |
| `hambre_ctx` | `boca_abierta` + contexto mañana/tarde/noche | *"Quiere desayunar."* |
| `hambre` | `boca_abierta` sin contexto temporal | *"Tiene hambre o sed."* |
| `emocional_negativo` | tokens negativos exclusivos (llanto, bah, mira_abajo...) | *"Está muy triste."* |
| `sueno_noche` | tokens de cansancio + contexto `[noche]` | *"Está listo para dormir."* |
| `sueno_manana` | tokens de cansancio + contexto `[manana]` | *"Aún quiere dormir, no quiere levantarse."* |
| `cansancio` | tokens de cansancio sin contexto | *"Está muy cansado."* |
| `confirmacion` | cabeza_si, cabeza_no, apunta_si, etc. | *"Está de acuerdo, dice que sí."* |
| `peticion` | palma_arriba, senala, toca, mira_objeto... | *"Está pidiendo algo."* |
| `general` | cuando no encaja en ninguno de los anteriores | Combina todos los significados |

#### Grupos de tokens por patrón:

```python
TOKENS_DOLOR    = {'UFF', 'AY', 'UUH', 'FRUNCE_CENO', 'SONIDO_AGUDO'}
TOKENS_URGENCIA = {'AGITA', 'LEVANTA_BRAZO', 'SONIDO_LARGO', 'SONIDO_REPETIDO', 'ATA'}
TOKENS_PETICION = {'PALMA_ARRIBA', 'SENALA', 'TOCA', 'MIRA_OBJETO', 'SONIDO_CORTO',
                   'PUNO', 'MUEVE_PULGARES', 'SHH'}
TOKENS_POSITIVO = {'SONRIE', 'AAH', 'APUNTA_SI'}
TOKENS_NEGATIVO = {'LLANTO', 'MIRA_ABAJO', 'BAH', 'PFF', 'ALEJA_CUERPO',
                   'MANO_DERECHA_A_IZQUIERDA'}
TOKENS_CONFIRM  = {'CABEZA_SI', 'CABEZA_NO', 'CABEZA_LADO', 'APUNTA_SI',
                   'JUNTA_DEDOS', 'MANOS_PALMAS_HACIA_ARRIBA'}
TOKENS_CANSANCIO = {'CIERRA_OJOS', 'SONIDO_GRAVE', 'MIRA_ABAJO', 'SONIDO_RONQUIDO'}
TOKENS_HAMBRE    = {'BOCA_ABIERTA'}
```

### Generación de frases (`generar_frase`)
Con el patrón detectado, construye la oración. Cada patrón tiene su propia lógica:

```python
if patron == 'dolor_urgente':
    return f'¡{base}! Necesita atención urgente ahora mismo.'

if patron == 'hambre_ctx':
    ctx_map = {'manana': 'desayunar', 'tarde': 'almorzar o merendar', 'noche': 'cenar'}
    return f'Quiere {ctx_map[contexto]}.'
```

Los modificadores E6 (`rapido`, `lento`, `doble`, `triple`) agregan una coletilla de intensidad al final de la frase.

### Advertencias semánticas

| Código | Cuándo ocurre |
|---|---|
| `[SEM-001]` | La combinación no encaja en ningún patrón |
| `[SEM-002]` | Todos los tokens están negados con `~` |
| `[SEM-003]` | `pausa` sola, sin ningún otro token |
| `[SEM-004]` | Secuencia de más de 6 tokens |

---

## Capa de IA (`interpretador_ia.py`)

### ¿Qué hace?
Es una capa **opcional** que reemplaza la generación de frases por reglas con una llamada a la **API de Claude** (Anthropic). Produce frases más naturales, empáticas y variadas que las reglas fijas.

### Relación con el semántico
`interpretador_ia.py` no sustituye a `semantico.py` — lo complementa. El semántico siempre corre primero (valida, detecta patrones, calcula significados), y al final, en lugar de generar la frase con reglas, le pasa toda esa información ya procesada a Claude para que redacte la oración final.

```
semantico.py
    ↓ detecta patrón, calcula significados
interpretador_ia.py
    ↓ si hay API key → llama a Claude
    ↓ si no hay → regresa None
semantico.py
    ↓ si None → usa generar_frase() con reglas
```

### Inicialización diferida del cliente
El cliente de la API **no se crea al importar el módulo** — se crea la primera vez que se necesita. Esto evita errores al arrancar si la clave no está configurada:

```python
_cliente_ia = None

def _obtener_cliente():
    global _cliente_ia
    if _cliente_ia is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY no está definida.")
        _cliente_ia = _anthropic_sdk.Anthropic(api_key=api_key)
    return _cliente_ia
```

### Verificación de disponibilidad
La función `ia_disponible()` es la que usa la interfaz para decidir si mostrar el motor como "IA (Claude)" o "Reglas". Intenta obtener el cliente — si falla, devuelve `False`:

```python
def ia_disponible() -> bool:
    if not _IA_DISPONIBLE:   # ¿está instalado el paquete anthropic?
        return False
    try:
        _obtener_cliente()   # ¿hay API key configurada?
        return True
    except EnvironmentError:
        return False
```

### El prompt del sistema
El corazón de la integración con IA. Es un texto largo que le explica a Claude **todo el lenguaje** antes de que interprete cualquier entrada. Incluye:
- Las 6 categorías de tokens con su significado
- Los 4 contextos temporales/situacionales
- Los operadores `~` (negación) y `!` (urgencia)
- Instrucciones de formato: tercera persona, máximo 2 oraciones, sin prefijos de contexto, sin comillas

```
"Eres un asistente especializado en comunicación aumentativa...
E1 – Sonidos vocales: mmm=duda/pensamiento | ata=llama a alguien...
E2 – Gestos de manos: palma_arriba=pide algo...
...
INSTRUCCIONES: Genera UNA SOLA ORACIÓN en español natural.
Usa tercera persona. NO incluyas prefijos como 'En la mañana:'."
```

El compilador agrega el prefijo de contexto por su cuenta, así que Claude solo redacta el contenido de la frase.

### Construcción del mensaje de usuario
Para cada compilación, `_construir_mensaje` convierte los datos del semántico en texto comprensible para Claude:

```python
# Ejemplo de lo que se le manda a Claude:
"Contexto: mañana (momento de levantarse/despertarse)
Señales: sonido_ronquido (quiere irse a dormir), junta_dedos (es poquito o quiere poco)"
```

Si algún token está negado, lo indica así: `~sonrie [NEGADO → no está contento]`
Si hay urgencia, agrega: `⚠ Hay señal de URGENCIA MÁXIMA.`

### La llamada a la API
Usa el modelo **`claude-opus-4-7`** con un máximo de 200 tokens de respuesta (suficiente para 1-2 oraciones):

```python
respuesta = cliente.messages.create(
    model="claude-opus-4-7",
    max_tokens=200,
    system=_SYSTEM_PROMPT,
    messages=[
        {"role": "user", "content": contenido}
    ],
)
frase = respuesta.content[0].text.strip()
```

### Caché — evitar llamadas repetidas
Para no gastar créditos de API con la misma entrada dos veces, guarda cada resultado en un diccionario en memoria:

```python
_cache: dict = {}
```

La clave del caché combina contexto + tokens (con sus flags) + urgencia:
```
# Ejemplo de clave:
"manana:SONIDO_RONQUIDO|JUNTA_DEDOS:False"
"dolor:~SONRIE|UFF|SONIDO_LARGO!:True"
```

Si la misma clave ya existe, devuelve el resultado guardado sin llamar a la API.

### Manejo de errores
Hay dos tipos de error manejados de forma diferente:

1. **API key no configurada** → avisa una sola vez en consola (no repite el aviso en cada compilación) y devuelve `None`
2. **Cualquier otro error** (red, límite de rate, servidor caído) → imprime el error y devuelve `None`

En ambos casos el compilador cae automáticamente al modo de reglas sin que el usuario lo note más allá del cambio en el indicador "Motor:".

### Indicador de motor en la interfaz
La función `modo_interpretacion()` en `semantico.py` devuelve una cadena que la interfaz muestra arriba de cada resultado semántico:

| Estado | Muestra |
|---|---|
| SDK instalado + API key configurada | `IA (Claude)` |
| SDK instalado pero sin API key | `Reglas (ANTHROPIC_API_KEY no configurada)` |
| SDK no instalado | `Reglas (módulo IA no disponible)` |

### Configuración de la API key

```powershell
# Solo dura mientras la terminal esté abierta (recomendado para desarrollo):
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Para que sea permanente en el sistema (requiere abrir terminal nueva después):
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-...", "User")
```

Verificar que quedó guardada:
```powershell
echo $env:ANTHROPIC_API_KEY
```

---

## Interfaz Gráfica (`interfaz.py`)

### ¿Qué hace?
Es la GUI construida con **Tkinter** (librería estándar de Python para interfaces gráficas). Es la única parte del compilador con la que interactúa el cuidador — no necesita saber nada de código.

### Estructura de la pantalla

```
┌─────────────────────────────────────────────────────────┐
│  Compilador · Lenguaje de Comunicación Personal         │
├──────────────────┬──────────────────────────────────────┤
│                  │  Contexto: [manana][tarde][noche]...  │
│  Tokens          │  Expresión: [caja de texto]           │
│  disponibles     │  Operadores: + | ! ~ ;                │
│  (botones por    │  [Borrar] [▶ Compilar]                │
│  categoría,      ├──────────────────────────────────────┤
│  con scroll)     │  TRADUCCIÓN (label amarillo) [🔊]     │
│                  ├──────────────────────────────────────┤
│                  │ [Léxico][Sintáctico][Semántico][📋]   │
│                  │  (pestañas con resultados detallados) │
└──────────────────┴──────────────────────────────────────┘
```

### Panel izquierdo — tokens disponibles
Muestra todos los tokens organizados por categoría (E1 a E6), cada una con su color y una línea de acento. Los tokens son botones: al hacer clic se insertan automáticamente en la caja de expresión con un `+` de separación si ya hay texto.

El panel tiene scroll vertical con rueda del mouse para poder ver todas las categorías.

### Panel derecho — flujo de uso

**1. Selector de contexto:** RadioButtons con colores por contexto (amarillo=mañana, naranja=tarde, azul=noche, rojo=dolor). El botón "sin contexto" lo limpia. Si el usuario ya escribió `[manana]` a mano en la caja, el compilador detecta esto y no duplica el contexto.

**2. Caja de expresión:** Campo de texto libre donde el cuidador escribe o construye la secuencia. Los botones de tokens y operadores insertan texto aquí.

**3. Botones de operadores:** `+` `|` `!` `~` `;` — cada uno se inserta inteligentemente:
- `~` va al principio del siguiente token
- `!` va al final del token actual
- `;` agrega espacio antes y después

**4. Botón Compilar:** Desencadena las 3 fases en orden. Si la entrada está vacía, muestra advertencia.

**5. Label de traducción:** Muestra la frase final en amarillo dorado, grande y prominente. Incluye el botón 🔊.

**6. Pestañas de resultados:**
- **Fase 1 · Léxico** — tabla de tokens reconocidos con TIPO, CATEGORÍA, VALOR y LÍNEA
- **Fase 2 · Sintáctico** — árbol AST en formato visual con conectores `└──` `├──`
- **Fase 3 · Semántico** — frase generada + motor usado + advertencias
- **📋 Historial** — compilaciones de la sesión con hora y frase

### Cómo funciona la compilación (`_compilar`)
Al presionar Compilar se ejecutan las 3 fases secuencialmente dentro del mismo método:

```python
def _compilar(self):
    entrada = self._construir_entrada()   # combina contexto + expresión

    # FASE 1
    lexer.input(entrada)
    toks = list(lexer)                    # tokeniza

    # FASE 2
    ast = analizar(entrada)               # construye AST

    # FASE 3
    frases = compilar(entrada)            # interpreta y genera frase

    self.lbl_frase.config(text=...)       # muestra resultado
    self._agregar_a_historial(...)        # guarda en historial
```

### Captura de stdout — por qué es necesaria
PLY imprime sus errores y advertencias directamente al stdout (la consola). Si no se capturan, aparecerían en la terminal negra y no en la interfaz. Para interceptarlos se usa `contextlib.redirect_stdout` con un `io.StringIO` (una cadena que actúa como si fuera la consola):

```python
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    toks = list(lexer)        # cualquier print() aquí va al buf
salida = buf.getvalue()       # recuperamos el texto capturado
```

Este truco se aplica por separado en cada una de las 3 fases para poder mostrar los errores en la pestaña correcta.

### Por qué los errores léxicos no se repiten en Fase 2 y 3
El léxico corre 3 veces (una por cada fase, porque cada una llama a `analizar` o `compilar` que internamente vuelve a tokenizar). Para evitar que los mismos errores léxicos aparezcan en las 3 pestañas, las fases 2 y 3 usan `ocultar_lex=True`:

```python
lineas_sint.extend(_clasificar_lineas(errores_sint, ocultar_lex=True))
```

Esto filtra todas las líneas que empiezan con `[LEX-` en las pestañas 2 y 3.

### Clasificación de líneas de error por color
La función `_clasificar_lineas` lee la salida capturada y asigna una etiqueta de color a cada línea:

| Prefijo | Etiqueta | Color | Qué significa |
|---|---|---|---|
| `[LEX-*]` | `error` | Rojo `#FF006E` | Error léxico |
| `[SIN-*]` | `error` | Rojo `#FF006E` | Error sintáctico |
| `[SEM-*]` | `advertencia` | Naranja `#FFB703` | Advertencia semántica |
| `→` | `sugerencia` | Verde `#06D6A0` itálica | Sugerencia de corrección |
| Resto | `error` | Rojo | Mensaje de error genérico |

Las líneas internas de PLY (`WARNING:`, `Generating`, `NOTE:`, `Using cached`) se filtran y nunca se muestran al usuario.

---

## Síntesis de voz

### ¿Por qué PowerShell y no pyttsx3?
La primera implementación usó `pyttsx3`, la librería estándar de Python para TTS. Funcionaba la primera vez, pero al hacer clic en 🔊 por segunda vez ya no sonaba nada. El problema: `pyttsx3` usa el motor COM de Windows internamente, y al llamar `engine.runAndWait()` varias veces en el mismo proceso ese motor queda en un estado corrupto.

Se intentó crear un engine nuevo en cada llamada, pero el estado corrupto se compartía igual porque el proceso de Python era el mismo.

**Solución final:** lanzar PowerShell como **subproceso independiente** cada vez que se necesita hablar. PowerShell crea un proceso completamente nuevo con su propio motor COM limpio, habla, y termina. No hay estado compartido.

### Detección automática de voz en español
Al arrancar la aplicación, `_detectar_voz_es` consulta las voces instaladas en el sistema y busca una en español:

```python
def _detectar_voz_es():
    r = subprocess.run(
        ['powershell', '-Command',
         'Add-Type -AssemblyName System.Speech; '
         '$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
         '$s.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name }'],
        capture_output=True, text=True, timeout=8
    )
    for nombre in r.stdout.strip().splitlines():
        if 'sabina' in nombre.lower() or 'spanish' in nombre.lower():
            return nombre.strip()
    return None
```

- Si encuentra "Microsoft Sabina Desktop" (español México), la usa.
- Si no hay ninguna voz en español, devuelve `None` y el botón 🔊 queda deshabilitado.

El nombre exacto de la voz se guarda en `_VOZ_NOMBRE` al iniciar y se reutiliza en cada llamada.

### El proceso de habla
```python
def _hablar_ps(texto):
    texto_ps = texto.replace('"', '`"')    # escapar comillas para PowerShell
    seleccion = f'$s.SelectVoice("{_VOZ_NOMBRE}"); ' if _VOZ_NOMBRE else ''
    cmd = (
        'Add-Type -AssemblyName System.Speech; '
        '$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
        f'{seleccion}'                     # seleccionar voz en español si existe
        '$s.Rate = -1; '                   # velocidad -1 (un poco más lento que normal)
        f'$s.Speak("{texto_ps}")'          # hablar el texto
    )
    subprocess.run(['powershell', '-Command', cmd], capture_output=True, timeout=30)
```

`System.Speech` es la librería nativa de Windows para síntesis de voz. `Add-Type -AssemblyName System.Speech` la carga en PowerShell.

### Threading — por qué es importante
Si la voz corriera directamente en el hilo principal de Tkinter, la interfaz se **congelaría** mientras habla (podría durar 5-10 segundos para frases largas). Para evitarlo, se lanza en un **hilo separado**:

```python
def _hablar(self):
    if not _VOZ_DISPONIBLE or not self.frase_actual:
        return
    texto = self.frase_actual
    threading.Thread(target=_hablar_ps, args=(texto,), daemon=True).start()
```

El flag `daemon=True` significa que si el usuario cierra la aplicación mientras está hablando, el hilo se termina solo sin bloquear el cierre.

### Estados del botón 🔊

| Situación | Estado del botón | Color |
|---|---|---|
| Voz en español disponible | Habilitado, clickeable | Amarillo `#FFD166` |
| Sin voz en español | Deshabilitado, gris | Gris `#555577` |
| Sin frase compilada aún | Clickeable pero no hace nada | — |

---

## Historial de compilaciones

### ¿Qué guarda?
Cada vez que una compilación termina exitosamente (con frase generada, sin error total), se agrega una entrada a `self.historial`:

```python
self.historial.append({
    "hora":    "14:32:05",              # hora exacta HH:MM:SS
    "entrada": "[manana] sonrie + ...", # expresión tal como se compiló
    "frases":  ["En la mañana: ..."],   # lista de frases (puede haber más de una con ;)
})
```

### ¿Cómo se muestra?
La pestaña 📋 Historial se redibuja completa con cada nueva compilación. Las entradas se muestran **más reciente primero** para que el cuidador vea lo último sin tener que hacer scroll.

Formato de cada entrada:
```
14:32:05  [manana] sonrie + cabeza_si
  → En la mañana: está de buen humor al despertar.
  ────────────────────────────────────────────────
```

### Limpiar historial
El botón 🗑 Limpiar vacía `self.historial` y redibuja la pestaña con el mensaje "Ninguna compilación aún." El historial **no se guarda en disco** — solo dura mientras la aplicación esté abierta.

---

## `main.py` — Punto de entrada

Archivo principal que arranca el compilador. Verifica dependencias antes de abrir la ventana:

```python
def _verificar_dependencias():
    for modulo in ("ply", "tkinter"):
        try:
            __import__(modulo)
        except ImportError:
            print(f"ERROR: Falta el módulo {modulo}")
            sys.exit(1)
```

Se ejecuta con:
```powershell
python main.py
```

---

## `tests.py` — Pruebas formales

70 pruebas organizadas en 4 bloques:

| Bloque | Pruebas | Qué verifica |
|---|---|---|
| Bloque 1 — Léxico | 21 | Tokens por categoría, operadores, contextos, errores |
| Bloque 2 — Sintáctico | 16 | Estructura del AST, flags negado/urgente, `;`, recuperación |
| Bloque 3 — Semántico | 20 | Los 13 patrones, overrides de contexto, `~`, `!`, modificadores |
| Bloque 4 — Integración | 13 | Flujo completo, entrada vacía, entrada inválida, expresiones largas |
| **Total** | **70** | **100% pasando** |

Las pruebas usan `contextlib.redirect_stdout` para silenciar la salida del compilador y solo evaluar los resultados:

```python
def _silencio(fn, *args, **kwargs):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        resultado = fn(*args, **kwargs)
    return resultado, buf.getvalue()
```

---

## Flujo completo de una compilación — ejemplo real

**Entrada:** `[manana] sonido_ronquido + junta_dedos`

### Fase 1 — Léxico
```
[manana]         → CONTEXTO = 'manana'
sonido_ronquido  → SONIDO_RONQUIDO = 'sonido_ronquido'
+                → MAS
junta_dedos      → JUNTA_DEDOS = 'junta_dedos'
```

### Fase 2 — Sintáctico (AST)
```
Programa
└── Expresion([manana], 1 alternativa)
    └── Secuencia(2 términos)
        ├── Termino(sonido_ronquido)
        └── Termino(junta_dedos)
```

### Fase 3 — Semántico
- `tipos_activos = {'SONIDO_RONQUIDO', 'JUNTA_DEDOS'}`
- `SONIDO_RONQUIDO` ∈ `TOKENS_CANSANCIO` → patrón = `sueno_manana`
- Contexto `manana` → override activo
- Frase generada: `"Aún quiere dormir, no quiere levantarse"`
- Prefijo de contexto: `"En la mañana: aún quiere dormir, no quiere levantarse"`

### Con IA activa
Claude recibe:
```
Contexto: mañana (momento de levantarse/despertarse)
Señales: sonido_ronquido (quiere irse a dormir), junta_dedos (es poquito o quiere poco)
```
Y puede devolver algo como: *"Quiere seguir durmiendo un poco más, no está listo para levantarse."*

---

## Dependencias del proyecto

```
ply        — parser LALR(1) y lexer AFD
tkinter    — interfaz gráfica (incluido en Python)
anthropic  — SDK de la API de Claude (opcional)
difflib    — sugerencias de corrección (incluido en Python)
```

Para instalar:
```powershell
pip install ply anthropic
```

---

*Documento generado el 29/05/2026 — Compilador v1.0*
