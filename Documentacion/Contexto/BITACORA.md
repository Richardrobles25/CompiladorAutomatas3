# Bitácora de Desarrollo
## Compilador para un Lenguaje de Comunicación Personal
**Equipo:** Nicolás · Ricardo · Rasshid
**Materia:** Lenguajes y Autómatas · Ingeniería en Sistemas Computacionales
**Periodo:** Abril – Mayo 2026

---

## Contexto del proyecto

El compilador está diseñado para asistir la comunicación de una persona con discapacidad comunicativa (hermano de Nicolás). La persona no puede articular palabras convencionales pero produce sonidos, gestos y expresiones faciales reconocibles. Un cuidador observa estas señales, las introduce como tokens en la interfaz, y el compilador las traduce a frases en español.

**Decisión de diseño clave:** el compilador no reconoce voz ni gestos automáticamente. Todo el peso de observación lo carga el acompañante humano. Esto elimina la parte técnicamente más difícil (visión por computadora, reconocimiento de voz) y permite enfocarse en las fases formales del compilador.

---

## Archivos del proyecto

| Archivo | Descripción |
|---------|-------------|
| `lexer.py` | Analizador léxico — reconoce los 57 tokens del alfabeto |
| `sintactico.py` | Analizador sintáctico — valida gramática y construye el AST |
| `semantico.py` | Analizador semántico — detecta patrones y genera frases en español |
| `interpretador_ia.py` | Módulo de interpretación con IA (Claude) — capa semántica avanzada |
| `interfaz.py` | Interfaz gráfica Tkinter para el cuidador |
| `probar_lexer.py` | Herramienta interactiva para probar el lexer en terminal |
| `MANUAL_COMPILADOR.md` | Manual interno: tokens, operadores, gramática, ejemplos |
| `COMBINACIONES.md` | Referencia completa de ~200+ combinaciones y sus frases en español |
| `BITACORA.md` | Este archivo — registro cronológico del desarrollo |
| `CONTEXTO_COMPILADOR.md` | Contexto general del proyecto (generado previamente) |
| `Documentacion/` | Propuesta, justificación, estado del arte, rúbrica, observaciones |

---

## Herramientas utilizadas

- **Python 3.14**
- **PLY (Python Lex-Yacc)** — librería para construir lexer y parser LALR
- **Tkinter** — interfaz gráfica (incluida en Python, sin instalación extra)

---

## Etapas de desarrollo

---

### ETAPA 1 — Analizador Léxico ✅
**Archivo:** `lexer.py`
**Estado:** Completo

#### ¿Qué hace?
Toma una cadena de texto como entrada y la divide en tokens. Es la primera fase del compilador — convierte texto plano en unidades que el analizador sintáctico puede procesar.

#### Tokens del alfabeto (55 tokens en 6 categorías)

| Categoría | Cantidad | Descripción |
|-----------|----------|-------------|
| E1 — Sonidos vocales | 12 | Sonidos que la persona produce: `mmm`, `ata`, `aah`, `uuh`, `oh`, `shh`, `hmm`, `uff`, `ay`, `ana`, `bah`, `pff` |
| E2 — Gestos de manos | 12 | Movimientos de manos: `senala`, `palma_arriba`, `palma_abajo`, `puno`, `mano_abierta`, `toca`, `agita`, `apunta_si`, `junta_dedos`, `separa_manos`, `pulgar_arriba`, `pulgar_abajo` |
| E3 — Vocalizaciones | 6 | Sonidos sostenidos: `sonido_largo`, `sonido_corto`, `sonido_repetido`, `sonido_agudo`, `sonido_grave`, `sonido_suave` |
| E4 — Movimientos corporales | 10 | Movimientos de cuerpo/cabeza: `cabeza_si`, `cabeza_no`, `cabeza_lado`, `inclina_cuerpo`, `acerca_cuerpo`, `aleja_cuerpo`, `senala_propio`, `senala_externo`, `encoge_hombros`, `levanta_brazo` |
| E5 — Expresiones faciales | 10 | Gestos faciales: `cierra_ojos`, `abre_ojos`, `frunce_ceno`, `sonrie`, `llanto`, `boca_abierta`, `mira_arriba`, `mira_abajo`, `mira_objeto`, `parpadeo_rapido` |
| E6 — Modificadores | 5 | Alteran intensidad: `rapido`, `lento`, `doble`, `triple`, `pausa` |

#### Operadores (5 operadores)

| Símbolo | Token | Tipo | Descripción |
|---------|-------|------|-------------|
| `+` | `MAS` | Binario | Secuencia — conecta tokens en orden |
| `\|` | `O` | Binario | Alternativa — una cosa u otra |
| `!` | `URGENTE` | Postfijo | Urgencia — marca la expresión como urgente |
| `~` | `NEG` | Prefijo | Negación — invierte el significado del token |
| `;` | `FIN_EXPR` | Separador | Nueva idea — separa dos mensajes en la misma entrada |

#### Sistema de contexto

Modificador global que precede a la expresión entre corchetes. Cambia la interpretación semántica de los tokens.

| Contexto | Sintaxis | Cuándo usarlo |
|----------|----------|---------------|
| Mañana | `[manana]` | 6am – 12pm |
| Tarde | `[tarde]` | 12pm – 7pm |
| Noche | `[noche]` | 7pm – 6am |
| Dolor | `[dolor]` | Cuando hay malestar físico |

#### Decisiones técnicas del lexer

**Una sola regex para todos los tokens:**
```python
def t_TOKEN(t):
    r'[a-z][a-z0-9_]*'
    tipo = token_map.get(t.value)
```
Se usa una sola expresión regular `[a-z][a-z0-9_]*` que captura cualquier identificador en minúsculas, luego se busca en el `token_map` para asignar el tipo correcto. Esto hace el lexer fácil de extender — para agregar un token nuevo solo se añade una entrada al diccionario.

**Comentarios ignorados:**
```python
def t_COMMENT(t):
    r'\#[^\n]*'
    pass
```
Líneas que empiezan con `#` se descartan completas. Permite al cuidador agregar notas en la entrada sin que el compilador las procese.

**Seguimiento de línea y columna:**
```python
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def _columna(t):
    ultimo_salto = t.lexer.lexdata.rfind('\n', 0, t.lexpos)
    return t.lexpos - ultimo_salto
```
Todos los errores léxicos reportan línea y columna exacta. Esto cubre el criterio 2.3 de la rúbrica.

**Contexto con validación:**
```python
def t_CONTEXTO(t):
    r'\[[a-z]+\]'
    valor = t.value[1:-1]
    if valor not in CONTEXTOS_VALIDOS:
        print(f"Error léxico — línea {t.lineno}: contexto '[{valor}]' no reconocido.")
        return None
    t.value = valor
    return t
```
Si el contexto no está en `{'manana', 'noche', 'tarde', 'dolor'}`, se reporta el error y se lista cuáles son válidos.

#### Ejemplos de entradas válidas para el lexer

```
[manana] mmm + palma_arriba + sonido_largo
[noche] sonrie + cabeza_si
[dolor] uff + sonido_largo + encoge_hombros !
~cabeza_no + sonrie
palma_arriba | mira_objeto
[manana] sonrie + cabeza_si ; [dolor] ay + senala_propio
# comentario del cuidador — ignorado por el compilador
```

#### Criterios de la rúbrica cubiertos

| Criterio | Estado |
|----------|--------|
| 1.1 Correctitud en identificación de tokens | ✅ 55 tokens reconocidos correctamente |
| 1.2 Manejo de errores léxicos | ✅ Errores con línea y columna |
| 1.3 Eficiencia | ✅ Sin backtracking — una regex + lookup en diccionario |
| 1.4 Manejo de comentarios y espacios | ✅ `#` y espacios ignorados |
| 1.5 Uso de expresiones regulares | ✅ Regex por categoría de símbolo |
| 1.6 Flexibilidad y modularidad | ✅ Agregar token = una línea en `token_map` |

---

### ETAPA 2 — Interfaz Gráfica (Tkinter) ✅
**Archivo:** `interfaz.py`
**Estado:** Completa para Etapa 2 (conectada al lexer)

#### ¿Qué hace en esta etapa?
Proporciona una interfaz visual para el cuidador. Permite construir expresiones clickeando botones de tokens y muestra el resultado del análisis léxico. En etapas posteriores se conectará al parser y al semántico para mostrar la frase traducida.

#### Componentes de la interfaz

**Panel izquierdo — Tokens disponibles:**
- Los 55 tokens organizados por categoría (E1 a E6)
- Cada categoría tiene su propio color identificador
- Scroll vertical para navegar todas las categorías
- Al clickear un token se agrega automáticamente a la expresión con `+`

**Panel derecho — Entrada y análisis:**
- Selector de contexto con radio buttons (`manana`, `tarde`, `noche`, `dolor`)
- Caja de texto donde se construye la expresión (también editable a mano)
- Botones de operadores (`+`, `|`, `!`, `~`, `;`) con descripción de cada uno
- Botón **Analizar léxico** — ejecuta el lexer y muestra tabla de tokens
- Botón **Borrar todo**
- Área de resultado con colores: verde = tokens válidos, rojo = errores léxicos

#### Nota sobre el botón principal
En esta etapa el botón dice **"Analizar léxico"**. En la Etapa 5 (integración final) pasará a llamarse **"Compilar"** y mostrará la frase en español generada por el semántico.

#### Para ejecutar la interfaz
```
cd C:\CompiladorAutomatas3
python interfaz.py
```

---

### ETAPA 3 — Analizador Sintáctico ✅
**Archivo:** `sintactico.py`
**Estado:** Completo

#### ¿Qué hace?
Recibe la secuencia de tokens del lexer y verifica que formen una estructura gramaticalmente válida. Si la entrada es válida, construye el **AST (Árbol de Sintaxis Abstracta)** que el analizador semántico usará para generar la frase.

#### Tipo de parser
**LALR(1)** — generado por PLY yacc. Se eligió LALR(1) porque:
- La gramática del lenguaje es libre de contexto y no ambigua con las reglas de precedencia definidas
- Es más eficiente que LL(1) para gramáticas con operadores y recursión izquierda
- PLY yacc genera parsers LALR de forma automática a partir de las reglas BNF

#### Gramática BNF implementada

```bnf
programa     ::= expresion
               | programa FIN_EXPR expresion

expresion    ::= secuencia
               | CONTEXTO secuencia
               | expresion O secuencia

secuencia    ::= termino
               | secuencia MAS termino

termino      ::= token_base
               | NEG termino
               | termino URGENTE

token_base   ::= MMM | ATA | AAH | ... (los 55 tokens)
```

#### Precedencia de operadores

| Nivel | Operador | Tipo | Prioridad |
|-------|----------|------|-----------|
| 1 | `\|` (O) | Binario | Menor |
| 2 | `+` (MAS) | Binario | Media-baja |
| 3 | `!` (URGENTE) | Postfijo | Media-alta |
| 4 | `~` (NEG) | Prefijo | Mayor |

#### Nodos del AST

```python
NodoPrograma(expresiones)
    └── NodoExpresion(alternativas, contexto)
            └── NodoSecuencia(terminos)
                    └── NodoTermino(token_valor, token_tipo, negado, urgente)
```

**NodoPrograma:** raíz del árbol. Contiene una lista de expresiones (separadas por `;`).

**NodoExpresion:** una expresión completa. Puede tener contexto (`manana`, `noche`, etc.) y una o varias alternativas unidas por `|`.

**NodoSecuencia:** lista de términos unidos por `+` en orden.

**NodoTermino:** un token individual con sus modificadores. Atributos:
- `token_valor` — el texto del token (ej. `'mmm'`)
- `token_tipo` — el tipo PLY (ej. `'MMM'`)
- `negado` — `True` si fue precedido por `~`
- `urgente` — `True` si fue seguido por `!`

#### Recuperación de errores

El parser no se detiene ante el primer error. Implementa recuperación en dos niveles:

1. **En secuencia:** si hay un token inválido después de `+`, reporta el error y continúa con el token siguiente válido.
2. **En `p_error`:** para cualquier token inesperado, reporta con línea y tipo, luego llama `parser.errok()` para reanudar el análisis.

#### Ejemplo de AST generado

Entrada: `[dolor] ~sonrie + uff + sonido_largo !`

```
Programa(1 expresion(es))
└── Expresion([dolor] 1 alternativa(s))
    └── Secuencia(3 termino(s))
        ├── Termino(~sonrie)       ← negado=True
        ├── Termino(uff)
        └── Termino(!sonido_largo) ← urgente=True
```

Entrada con `;`: `[manana] sonrie + cabeza_si ; [dolor] ay + senala_propio`

```
Programa(2 expresion(es))
├── Expresion([manana] 1 alternativa(s))
│   └── Secuencia(2 termino(s))
│       ├── Termino(sonrie)
│       └── Termino(cabeza_si)
└── Expresion([dolor] 1 alternativa(s))
    └── Secuencia(2 termino(s))
        ├── Termino(ay)
        └── Termino(senala_propio)
```

#### Errores que detecta el parser (que el lexer no detecta)

```
+ mmm              → Error: token inesperado '+' al inicio
mmm + + palma      → Error: dos operadores seguidos
! sonido_largo     → Error: '!' sin token previo
[dolor]            → Error: contexto sin expresión
```

#### Criterios de la rúbrica cubiertos

| Criterio | Estado |
|----------|--------|
| 2.1 Correctitud en construcción del AST | ✅ AST con clases de nodos jerárquicos |
| 2.2 Elección del tipo de parser | ✅ LALR(1) con justificación |
| 2.3 Manejo de errores sintácticos | ✅ Mensajes con línea y tipo de token |
| 2.4 Generación del AST | ✅ Árbol refleja jerarquía del lenguaje |
| 2.5 Modularidad y mantenibilidad | ✅ Una función por regla gramatical |
| 2.6 Recuperación de errores | ✅ Continúa el análisis después de errores |

---

### ETAPA 4 — Analizador Semántico ✅
**Archivo:** `semantico.py`
**Estado:** Completo

#### ¿Qué hace?
Recorre el AST generado por el analizador sintáctico y produce una frase en español. Para cada expresión del programa:
1. Recorre los `NodoTermino` del AST y resuelve el significado de cada token considerando el contexto activo y la negación (`negado=True`)
2. Detecta el patrón dominante de la secuencia (dolor, urgencia, petición, etc.)
3. Genera una frase en español apropiada al patrón, con prefijo de contexto si aplica

#### Tabla de símbolos contextual

No almacena variables como en un compilador convencional. Almacena el perfil de interpretación de la sesión:

```python
class TablaSimbolos:
    contexto_activo  # 'manana' | 'noche' | 'tarde' | 'dolor' | None
    hay_urgencia     # True si algún término tiene urgente=True
```

#### Base de datos de significados

| Estructura | Contenido |
|-----------|-----------|
| `BASE` | Diccionario con el significado base de los 55 tokens (ej. `'sonrie': 'está sonriendo'`) |
| `OVERRIDE` | Significados alternativos por contexto (ej. `'manana' → {'boca_abierta': 'quiere desayunar'}`) — 43 overrides en 4 contextos |
| `CATEGORIA` | Mapea cada tipo de token a su categoría E1–E6 |

#### Los 13 patrones semánticos implementados

El analizador detecta el patrón según prioridad descendente:

| Prioridad | Patrón | Activado por |
|-----------|--------|-------------|
| 1 | `dolor_urgente` | Tokens de dolor + urgencia (`!`) o contexto `[dolor]` + `!` |
| 2 | `urgencia` | Operador `!`, `agita`, `levanta_brazo`, `sonido_largo`, `ata` |
| 3 | `dolor` | `uff`, `ay`, `uuh`, `frunce_ceno`, `sonido_agudo`, contexto `[dolor]` |
| 4 | `emocional_positivo` | `sonrie`, `aah`, `pulgar_arriba`, `apunta_si` |
| 5 | `hambre_ctx` | `boca_abierta` con contexto `[manana]`, `[tarde]` o `[noche]` |
| 6 | `hambre` | `boca_abierta` sin contexto |
| 7 | `emocional_negativo` (strong) | `llanto`, `bah`, `pff`, `pulgar_abajo`, `aleja_cuerpo` |
| 8 | `sueno_noche` | `cierra_ojos`, `sonido_grave`, `mira_abajo` + contexto `[noche]` |
| 9 | `sueno_manana` | `cierra_ojos`, `sonido_grave`, `mira_abajo` + contexto `[manana]` |
| 10 | `cansancio` | `cierra_ojos`, `sonido_grave`, `mira_abajo` sin contexto especial |
| 11 | `confirmacion` | `cabeza_si`, `cabeza_no`, `cabeza_lado`, `junta_dedos` |
| 12 | `emocional_negativo` | `mira_abajo` u otros negativos restantes |
| 13 | `peticion` | `palma_arriba`, `senala`, `toca`, `mira_objeto`, etc. |
| — | `general` | Cualquier secuencia que no encaje en otro patrón |

#### Efecto de los modificadores semánticos

| Operador | Efecto en la frase |
|----------|--------------------|
| `~` (NEG) | Invierte la frase: "no quiere levantarse" → "quiere levantarse" |
| `!` (URGENTE) | Añade "¡" al inicio y "es urgente" al final; activa patrón urgencia/dolor_urgente |
| `\|` (O) | Genera dos frases alternativas: "o bien ... o bien ..." |
| `;` (FIN_EXPR) | Produce una frase por cada expresión separada |

#### Decisión de diseño: separación de tokens compartidos

Problema encontrado: `mira_abajo` pertenece a `TOKENS_CANSANCIO` y a `TOKENS_NEGATIVO`. Con `llanto + mira_abajo`, el patrón cansancio se activaba antes que el negativo (por estar más arriba en la prioridad).

Solución: antes del chequeo de cansancio, se verifica si hay tokens "exclusivamente negativos" (`TOKENS_NEGATIVO - TOKENS_CANSANCIO`). Si están presentes, se retorna `emocional_negativo` de inmediato. `mira_abajo` solo activa cansancio cuando va solo o con otros tokens de cansancio.

#### Ejemplos de salida semántica

| Entrada | Frase generada |
|---------|---------------|
| `[dolor] uff + sonido_largo !` | `Con señales de dolor: ¡Está sufriendo! Necesita atención urgente ahora mismo.` |
| `[manana] boca_abierta + palma_arriba` | `En la mañana: quiere desayunar.` |
| `sonrie + cabeza_si` | `Está contento y de acuerdo` |
| `llanto + mira_abajo` | `Está muy triste y decaído` |
| `~cabeza_no + aah` | `Está de acuerdo y hace sonido de satisfacción` |
| `palma_arriba \| mira_objeto` | `Quiere algo — o lo está indicando` |

#### Criterios de la rúbrica cubiertos

| Criterio | Estado |
|----------|--------|
| 3.1 Análisis semántico con tabla de símbolos | ✅ `TablaSimbolos` con contexto y urgencia |
| 3.2 Validación semántica | ✅ Resolución de 13 patrones con 200+ combinaciones |
| 3.3 Coherencia contextual | ✅ Sistema de overrides por contexto (43 entradas) |
| 3.4 Gestión de ambigüedades | ✅ Prioridad de patrones explícita y documentada |

---

### ETAPA 5 — Integración final ✅
**Archivo:** `interfaz.py` (actualización completa)
**Estado:** Completo

#### ¿Qué hace?
Conecta el pipeline completo `lexer → sintáctico → semántico` y lo expone a través de la interfaz gráfica. El cuidador construye la expresión con clics y obtiene la traducción en español de inmediato.

#### Componentes añadidos en esta etapa

**Label de traducción (prominente):**
- Texto en `#FFD166` (amarillo dorado) sobre fondo `#0F3460` (azul oscuro)
- Actualizado en tiempo real al compilar
- Muestra la frase generada por el semántico con wraplength para textos largos

**Panel de fases (Notebook con 3 tabs):**

| Tab | Color | Contenido |
|-----|-------|-----------|
| `Fase 1 · Léxico` | verde `#00FF9F` | Tabla de tokens: tipo, valor, línea |
| `Fase 2 · Sintáctico` | azul `#4CC9F0` | AST impreso con `imprimir_ast()` |
| `Fase 3 · Semántico` | dorado `#FFD166` | Frases generadas por expresión |

**Captura de output PLY con `contextlib.redirect_stdout`:**
```python
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    ast = analizar(entrada)
errores_sint = buf.getvalue()
```
Los mensajes de diagnóstico de PLY (tablas LALR, errores) se capturan en el buffer en lugar de salir por la consola, y se muestran en el tab correspondiente.

#### Para ejecutar
```
cd C:\CompiladorAutomatas3
python interfaz.py
```

#### Criterios de la rúbrica cubiertos

| Criterio | Estado |
|----------|--------|
| 4.1 Interfaz funcional | ✅ Tkinter completo con las 3 fases visibles |
| 4.2 Visualización del AST | ✅ Tab "Fase 2 · Sintáctico" muestra el árbol |
| 4.3 Tabla de tokens | ✅ Tab "Fase 1 · Léxico" muestra tipo, valor, línea |
| 4.4 Frase traducida | ✅ Label prominente + Tab "Fase 3 · Semántico" |
| 4.5 Experiencia del usuario | ✅ Botones de tokens, operadores, contexto con colores |

---

### ETAPA 6 — Pruebas formales ✅
**Archivo:** `tests.py`
**Estado:** Completo

#### ¿Qué hace?
Suite de pruebas automatizadas que verifica el funcionamiento correcto de las tres fases del compilador sin intervención manual. Cubre los criterios 3.2 (Pruebas de Integración) y 3.4 (Pruebas de Casos de Error) de la rúbrica.

#### Estructura

| Bloque | Pruebas | Qué verifica |
|--------|---------|-------------|
| 1 · Léxico | 21 | Tokens de las 6 categorías, operadores, contextos válidos e inválidos, comentarios, mayúsculas |
| 2 · Sintáctico | 16 | AST construido correctamente, estructura de nodos, flags `negado`/`urgente`, separador `;`, errores |
| 3 · Semántico | 20 | 13 patrones, overrides de contexto, operadores `~` y `!`, modificadores E6 |
| 4 · Integración | 13 | Pipeline completo end-to-end, entrada vacía, entrada inválida, expresión larga, todos los contextos |
| **Total** | **70** | **100% pasadas** |

#### Técnica utilizada
Todas las pruebas usan `contextlib.redirect_stdout` para capturar el output de PLY sin que interfiera con el reporte de resultados. Cada prueba valida comportamiento real del compilador — no simulaciones.

```
python tests.py   →  70/70 ✅  Cobertura: 100%
```

---

### ETAPA 7 — Síntesis de voz ✅
**Archivo:** `interfaz.py` (añadido botón 🔊)
**Estado:** Completo

#### ¿Qué hace?
Permite escuchar la frase traducida en voz alta usando la voz **Microsoft Sabina Desktop (español México)** disponible en el sistema.

#### Implementación

- **Librería:** `pyttsx3`
- **Voz detectada:** `TTS_MS_ES-MX_SABINA_11.0` — español de México
- **Detección:** se usa `v.languages` (ej. `['es-MX']`) en lugar del path del registro, que contiene `"voices"` con `"es"` y causaba selección incorrecta de la voz en inglés
- **Hilo separado:** `threading.Thread(daemon=True)` — la interfaz no se congela mientras habla
- **Motor fresco por clic:** se llama `pyttsx3.init()` cada vez para evitar el bug de "solo habla una vez" que ocurre cuando `runAndWait()` deja el motor en estado inconsistente
- **Botón 🔊:** aparece junto a la etiqueta TRADUCCIÓN; deshabilitado automáticamente si `pyttsx3` no está disponible

---

### ETAPA 8 — Sistema de errores tipificados y sugerencias ✅
**Archivos:** `lexer.py`, `sintactico.py`, `semantico.py`, `interfaz.py`
**Estado:** Completo

#### ¿Qué hace?
Clasifica todos los errores del compilador con códigos únicos y agrega sugerencias de corrección para cada uno, igual a como lo hacen compiladores modernos (GCC, Python, Rust).

#### Tabla de códigos de error

| Código | Fase | Archivo | Cuándo aparece |
|--------|------|---------|----------------|
| `[LEX-001]` | Léxico | `lexer.py` → `t_TOKEN()` | Token no reconocido |
| `[LEX-002]` | Léxico | `lexer.py` → `t_CONTEXTO()` | Contexto inválido |
| `[LEX-003]` | Léxico | `lexer.py` → `t_error()` | Carácter no permitido |
| `[SIN-001]` | Sintáctico | `sintactico.py` → `p_error()` | Operador `+` o `\|` mal ubicado, token inesperado |
| `[SIN-002]` | Sintáctico | `sintactico.py` → `p_error()` | `!` sin token previo, `~` en posición inválida |
| `[SIN-003]` | Sintáctico | `sintactico.py` → `p_secuencia_error_mas()` | Token faltante después de `+` |
| `[SIN-004]` | Sintáctico | `sintactico.py` → `p_error()` | `;` sin expresión válida |
| `[SIN-005]` | Sintáctico | `sintactico.py` → `p_error()` | Contexto `[x]` fuera de lugar |
| `[SIN-006]` | Sintáctico | `sintactico.py` → `p_error()` | Entrada incompleta |
| `[SEM-001]` | Semántico | `semantico.py` → `interpretar_secuencia()` | Combinación sin patrón reconocido |
| `[SEM-002]` | Semántico | `semantico.py` → `interpretar_secuencia()` | Todos los tokens negados con `~` |
| `[SEM-003]` | Semántico | `semantico.py` → `interpretar_secuencia()` | `pausa` sola |
| `[SEM-004]` | Semántico | `semantico.py` → `interpretar_secuencia()` | Secuencia de más de 6 tokens |

#### Sugerencias con difflib
Para `[LEX-001]` y `[LEX-002]` se usa `difflib.get_close_matches()` con umbral `cutoff=0.6` para proponer el token o contexto más parecido al que escribió el usuario:

```
[LEX-001] Error léxico: token 'sonie' no reconocido.
  → ¿Quisiste decir: sonrie?
```

#### Visualización en la interfaz
Los mensajes en los tabs usan colores diferenciados:
- 🔴 `[LEX-*]` y `[SIN-*]` → errores reales (rojo `#FF006E`)
- 🟡 `[SEM-*]` → advertencias semánticas (amarillo `#FFB703`)
- 🟢 Líneas `→ ...` → sugerencias de corrección (verde `#06D6A0`)

Los tabs de Fase 2 y Fase 3 filtran los `[LEX-*]` para no duplicar mensajes que ya aparecen en Fase 1.

---

## Decisiones de diseño registradas

| Decisión | Alternativa descartada | Razón |
|----------|----------------------|-------|
| Tokens abstractos (`mmm`, `senala`) en lugar de semánticos (`señalar_vaso`) | Tokens descriptivos tipo `señalar_vaso` | La persona no puede señalar objetos específicos — los tokens representan capacidades físicas reales |
| Tkinter para la interfaz | Web (HTML+JS) o Flask | Proyecto académico en etapa inicial — Tkinter viene incluido en Python, sin dependencias extra |
| LALR(1) con PLY yacc | Parser recursivo descendente manual | PLY yacc genera tablas LALR automáticamente y permite definir la gramática en BNF directamente |
| Clases de nodos para el AST (`NodoPrograma`, etc.) | Listas de tuplas | Las clases reflejan mejor la jerarquía del lenguaje y son más evaluables según la rúbrica |
| Semántica por tabla de símbolos contextual | Inferencia automática de significado | El compilador consulta significados, no los infiere — esto lo hace predecible y correcto para el usuario real |

---

---

### ETAPA 9 — Actualización del alfabeto de tokens ✅
**Archivos:** `lexer.py`, `sintactico.py`, `semantico.py`, `interfaz.py`
**Estado:** Completo
**Fecha:** Mayo 2026

#### ¿Por qué se hizo?
Al revisar el `MANUAL_COMPILADOR.md` se detectó que el alfabeto de tokens había evolucionado respecto al código. Se eliminaron 3 tokens obsoletos y se agregaron 5 tokens nuevos para reflejar mejor las señales reales de comunicación de la persona.

#### Tokens eliminados

| Token eliminado | Categoría | Razón |
|----------------|-----------|-------|
| `hmm` | E1 — Sonidos vocales | Redundante con `mmm` — la persona no produce este sonido distintamente |
| `pulgar_arriba` | E2 — Gestos de manos | La persona no realiza este gesto — se reemplazó por `apunta_si` |
| `pulgar_abajo` | E2 — Gestos de manos | La persona no realiza este gesto — el rechazo se expresa con `cabeza_no` o `bah` |

#### Tokens agregados

| Token nuevo | Categoría | Significado base |
|-------------|-----------|-----------------|
| `dedoindice_boca` | E2 — Gestos de manos | Pide silencio |
| `mueve_pulgares` | E2 — Gestos de manos | Quiere jugar videojuegos |
| `mano_derecha_a_izquierda` | E2 — Gestos de manos | Indica que algo se acabó |
| `manos_palmas_hacia_arriba` | E2 — Gestos de manos | Quiere que le den la razón |
| `sonido_ronquido` | E3 — Vocalizaciones | Quiere irse a dormir |

El total pasó de **55 tokens** a **57 tokens** (3 eliminados + 5 agregados = +2 netos).

#### Cambios en `lexer.py`

**Tuple `tokens` — sección E1 y E2:**
```python
# ANTES (E1 tenía 12, E2 tenía 12):
'MMM', 'ATA', 'AAH', 'UUH', 'OH', 'SHH',
'UFF', 'AY', 'ANA', 'BAH', 'PFF', 'HMM',  # ← HMM eliminado

'SENALA', 'PALMA_ARRIBA', 'PALMA_ABAJO', 'PUNO',
'MANO_ABIERTA', 'TOCA', 'AGITA', 'APUNTA_SI',
'JUNTA_DEDOS', 'SEPARA_MANOS',
'PULGAR_ARRIBA', 'PULGAR_ABAJO',            # ← estos dos eliminados

# AHORA (E1 tiene 11, E2 tiene 14, E3 tiene 7):
'MMM', 'ATA', 'AAH', 'UUH', 'OH', 'SHH',
'UFF', 'AY', 'ANA', 'BAH', 'PFF',

'SENALA', 'PALMA_ARRIBA', 'PALMA_ABAJO', 'PUNO',
'MANO_ABIERTA', 'TOCA', 'AGITA', 'APUNTA_SI',
'JUNTA_DEDOS', 'SEPARA_MANOS',
'DEDOINDICE_BOCA', 'MUEVE_PULGARES',        # ← nuevos
'MANO_DERECHA_A_IZQUIERDA', 'MANOS_PALMAS_HACIA_ARRIBA',  # ← nuevos

'SONIDO_LARGO', 'SONIDO_CORTO', 'SONIDO_REPETIDO',
'SONIDO_AGUDO', 'SONIDO_GRAVE', 'SONIDO_SUAVE',
'SONIDO_RONQUIDO',                          # ← nuevo
```

**Diccionario `token_map`:**
```python
# Entradas eliminadas:
'hmm': 'HMM',
'pulgar_arriba': 'PULGAR_ARRIBA',
'pulgar_abajo': 'PULGAR_ABAJO',

# Entradas agregadas:
'dedoindice_boca':           'DEDOINDICE_BOCA',
'mueve_pulgares':            'MUEVE_PULGARES',
'mano_derecha_a_izquierda':  'MANO_DERECHA_A_IZQUIERDA',
'manos_palmas_hacia_arriba': 'MANOS_PALMAS_HACIA_ARRIBA',
'sonido_ronquido':           'SONIDO_RONQUIDO',
```

**Mensaje de error actualizado:**
```python
# ANTES:
print(f"  → Usa uno de los 55 tokens del alfabeto ...")
# AHORA:
print(f"  → Usa uno de los 57 tokens del alfabeto ...")
```

#### Cambios en `sintactico.py`

La regla `p_token_base` lista explícitamente todos los tokens válidos. Se actualizó para reflejar el nuevo alfabeto:

```python
def p_token_base(p):
    '''token_base : MMM
                  | ...
                  | DEDOINDICE_BOCA        ← agregado
                  | MUEVE_PULGARES         ← agregado
                  | MANO_DERECHA_A_IZQUIERDA  ← agregado
                  | MANOS_PALMAS_HACIA_ARRIBA ← agregado
                  | SONIDO_RONQUIDO        ← agregado
                  | ...'''
    # (también se eliminaron HMM, PULGAR_ARRIBA, PULGAR_ABAJO)
```

#### Cambios en `semantico.py`

**Diccionario `CATEGORIA`** — mapeo token → categoría E1-E6:
```python
# Eliminados:
'HMM':'E1', 'PULGAR_ARRIBA':'E2', 'PULGAR_ABAJO':'E2'

# Agregados:
'DEDOINDICE_BOCA':'E2',
'MUEVE_PULGARES':'E2',
'MANO_DERECHA_A_IZQUIERDA':'E2',
'MANOS_PALMAS_HACIA_ARRIBA':'E2',
'SONIDO_RONQUIDO':'E3',
```

**Diccionario `BASE`** — significados base de cada token:
```python
# Eliminados:
'hmm': 'está pensando en silencio',
'pulgar_arriba': 'está de acuerdo o satisfecho',
'pulgar_abajo': 'no está de acuerdo o rechaza',

# Modificado (cambio de significado):
# ANTES: 'shh': 'pide silencio o quiere esperar'
# AHORA: 'shh': 'tiene ganas de ir al baño'
# (la persona usa este sonido específicamente para indicar necesidad de baño)

# Agregados:
'dedoindice_boca':           'pide silencio',
'mueve_pulgares':            'quiere jugar videojuegos',
'mano_derecha_a_izquierda':  'indica que algo se acabó',
'manos_palmas_hacia_arriba': 'quiere que le den la razón',
'sonido_ronquido':           'quiere irse a dormir',
```

**Grupos de patrones actualizados:**
```python
# TOKENS_PETICION: se agregaron MUEVE_PULGARES y SHH
TOKENS_PETICION = {'PALMA_ARRIBA','SENALA','TOCA','MIRA_OBJETO',
                   'SONIDO_CORTO','PUNO','MUEVE_PULGARES','SHH'}

# TOKENS_POSITIVO: PULGAR_ARRIBA reemplazado por APUNTA_SI
TOKENS_POSITIVO = {'SONRIE','AAH','APUNTA_SI'}

# TOKENS_NEGATIVO: se agregó MANO_DERECHA_A_IZQUIERDA
TOKENS_NEGATIVO = {'LLANTO','MIRA_ABAJO','BAH','PFF',
                   'ALEJA_CUERPO','MANO_DERECHA_A_IZQUIERDA'}

# TOKENS_CONFIRM: se agregó MANOS_PALMAS_HACIA_ARRIBA
TOKENS_CONFIRM = {'CABEZA_SI','CABEZA_NO','CABEZA_LADO',
                  'APUNTA_SI','JUNTA_DEDOS','MANOS_PALMAS_HACIA_ARRIBA'}

# TOKENS_CANSANCIO: se agregó SONIDO_RONQUIDO
TOKENS_CANSANCIO = {'CIERRA_OJOS','SONIDO_GRAVE','MIRA_ABAJO','SONIDO_RONQUIDO'}
```

**Función `_frase_confirmacion` actualizada** — se reemplazaron referencias a `PULGAR_ARRIBA` y `HMM`:
```python
def _frase_confirmacion(infos):
    tipos = [i['tipo'] for i in infos]
    if 'CABEZA_SI' in tipos:
        if 'APUNTA_SI' in tipos:
            return 'Confirma que sí, eso es exactamente lo correcto'
        if 'MANOS_PALMAS_HACIA_ARRIBA' in tipos:   # ← nuevo caso
            return 'Confirma que sí y quiere que le den la razón'
        return 'Está de acuerdo, dice que sí'
    ...
```

#### Cambios en `interfaz.py`

**Diccionario `CATEGORIA_TOKEN`** — mismas 3 eliminaciones y 5 adiciones que en el semántico.

**Lista `CATEGORIAS`** — actualizada la sublista de E1, E2 y E3:
```python
("E2 · Gestos de manos", "#8338EC",
 ["senala", "palma_arriba", "palma_abajo", "puno",
  "mano_abierta", "toca", "agita", "apunta_si",
  "junta_dedos", "separa_manos",
  "dedoindice_boca", "mueve_pulgares",          # ← nuevos
  "mano_derecha_a_izquierda",                   # ← nuevo
  "manos_palmas_hacia_arriba"]),                 # ← nuevo

("E3 · Vocalizaciones", "#06D6A0",
 ["sonido_largo", "sonido_corto", "sonido_repetido",
  "sonido_agudo", "sonido_grave", "sonido_suave",
  "sonido_ronquido"]),                           # ← nuevo
```

---

### ETAPA 10 — Intérprete semántico con IA (Claude) ✅
**Archivo nuevo:** `interpretador_ia.py`
**Archivos modificados:** `semantico.py`, `interfaz.py`
**Estado:** Completo
**Fecha:** Mayo 2026

#### ¿Por qué se hizo?
El analizador semántico basado en reglas cubre ~200 combinaciones predefinidas, pero tiene limitaciones:
- Combinaciones nuevas o poco comunes caen en el patrón `general` sin frase específica
- La frase generada es mecánica ("Pide silencio. Pide calma o que paren.")

Al integrar un modelo de lenguaje grande (Claude de Anthropic), el compilador puede generar frases en español natural para **cualquier combinación posible de tokens**, adaptadas al contexto, la negación y la urgencia. El sistema de reglas se conserva como respaldo.

#### Arquitectura de la integración

```
Entrada de texto
      │
      ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────────────────┐
│  lexer.py   │────▶│ sintactico.py│────▶│      semantico.py        │
│ (55 tokens) │     │    (AST)     │     │                          │
└─────────────┘     └──────────────┘     │  ┌─────────────────────┐ │
                                         │  │ interpretador_ia.py │ │
                                         │  │  (Claude API)       │ │
                                         │  └────────┬────────────┘ │
                                         │           │              │
                                         │   IA disponible?         │
                                         │   ┌───YES─┘  NO─┐        │
                                         │   ▼              ▼        │
                                         │ Frase IA    Sistema de   │
                                         │ (natural)   Reglas       │
                                         └──────────────────────────┘
                                                      │
                                                      ▼
                                               Frase en español
```

#### Archivo nuevo: `interpretador_ia.py`

Este archivo es el puente entre el compilador y la API de Anthropic. Sus responsabilidades son:

1. **Cargar el SDK de Anthropic** de forma segura — si no está instalado, el módulo funciona igual pero todas las funciones devuelven `None` (no lanza excepciones)
2. **Construir el prompt del sistema** — describe el lenguaje completo al modelo para que entienda el contexto
3. **Transformar los datos internos** en texto comprensible para Claude
4. **Cachear las respuestas** — misma combinación de tokens no llama la API dos veces
5. **Manejar errores de red o de clave** sin detener el compilador

**Estructura del módulo:**
```python
# ── Importación segura del SDK ───────────────────────────────────────────────
try:
    import anthropic as _anthropic_sdk
    _IA_DISPONIBLE = True
except ImportError:
    _IA_DISPONIBLE = False   # el compilador sigue funcionando sin IA

# ── Caché para no llamar la API dos veces con la misma entrada ───────────────
_cache: dict = {}

# ── Cliente con inicialización diferida ──────────────────────────────────────
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

**El prompt del sistema** — le dice a Claude quién es la persona y qué significa cada token:

```python
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
  ...  (todos los 57 tokens con su significado)

Contextos temporales:
  [manana] = momento del despertar
  [tarde]  = hora de la tarde
  [noche]  = hora de dormir
  [dolor]  = la persona está experimentando dolor físico

Operadores:
  ~ antes de un token = NEGACIÓN
  ! después de un token = URGENCIA MÁXIMA

INSTRUCCIONES: Genera UNA SOLA ORACIÓN en español natural.
- Tercera persona ("Quiere...", "Está...", "Siente...")
- NO incluyas prefijos de contexto como "En la mañana:" (el sistema los agrega)
- Máximo 2 oraciones cortas
- Solo la oración, sin explicaciones ni comillas
"""
```

**Función principal `interpretar_con_ia`:**

```python
def interpretar_con_ia(infos: list, contexto, hay_urgente: bool):
    """
    Parámetros:
        infos       – lista de dicts: {valor, tipo, significado, negado, urgente}
        contexto    – 'manana' | 'tarde' | 'noche' | 'dolor' | None
        hay_urgente – True si algún token lleva '!'

    Retorna:
        str  – frase interpretada en español natural
        None – si la IA no está disponible (usar sistema de reglas como respaldo)
    """
    if not _IA_DISPONIBLE:
        return None

    # 1. Revisar caché primero
    clave = _clave_cache(infos, contexto, hay_urgente)
    if clave in _cache:
        return _cache[clave]

    # 2. Construir el mensaje para Claude
    mensaje = _construir_mensaje(infos, contexto, hay_urgente)

    # 3. Llamar a la API
    try:
        cliente = _obtener_cliente()
        respuesta = cliente.messages.create(
            model="claude-opus-4-7",
            max_tokens=200,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": mensaje}],
        )
        frase = respuesta.content[0].text.strip()
        _cache[clave] = frase   # guardar en caché
        return frase

    except EnvironmentError as e:
        # Avisar una sola vez si no hay API key
        print(f"\n[IA] {e}")
        print("[IA] Usando interpretación basada en reglas.\n")
        return None

    except Exception as e:
        # Cualquier error de red, rate limit, etc. → respaldo a reglas
        print(f"[IA] Error al contactar Claude → {e}")
        return None
```

**Construcción del mensaje para Claude** — convierte los datos internos del compilador a texto legible:

```python
def _construir_mensaje(infos, contexto, hay_urgente):
    partes = []

    # Agregar contexto si existe
    if contexto:
        desc_ctx = {
            'manana': 'mañana (momento de levantarse)',
            'tarde':  'tarde (actividades diurnas)',
            'noche':  'noche (hora de dormir)',
            'dolor':  'dolor (la persona está sufriendo)',
        }
        partes.append(f"Contexto: {desc_ctx[contexto]}")

    # Describir cada token con su significado y modificadores
    tokens_desc = []
    for info in infos:
        desc = info['valor']
        if info['negado']:
            desc = f"~{desc} (NEGADO: {info['significado']})"
        else:
            desc = f"{desc} ({info['significado']})"
        if info['urgente']:
            desc += " [¡URGENTE!]"
        tokens_desc.append(desc)

    partes.append("Señales: " + ", ".join(tokens_desc))

    if hay_urgente:
        partes.append("⚠ Hay señal de URGENCIA MÁXIMA.")

    return "\n".join(partes)
```

**Ejemplo de mensaje enviado a Claude:**
```
Contexto: dolor (la persona está sufriendo)
Señales: ay (siente un dolor muy intenso), senala_propio (le duele algo en su cuerpo) [¡URGENTE!]
⚠ Hay señal de URGENCIA MÁXIMA.
```

**Respuesta de Claude:**
```
Siente un dolor intenso en alguna parte de su cuerpo y necesita atención urgente ahora mismo.
```

#### Cambios en `semantico.py`

**Nueva importación al inicio del archivo** (con fallback si el módulo no existe):

```python
# ── Importar intérprete de IA (opcional: funciona sin él) ───────────────────
try:
    from interpretador_ia import interpretar_con_ia, ia_disponible
    _IA_IMPORTADA = True
except ImportError:
    _IA_IMPORTADA = False
    def interpretar_con_ia(*args, **kwargs): return None
    def ia_disponible(): return False
```

**Función `interpretar_secuencia` modificada** — se agregan dos líneas al final que intentan la IA antes de las reglas:

```python
def interpretar_secuencia(secuencia, contexto):
    # ... (mismo código que antes: construir infos, detectar patrón, advertencias)

    # ── Intentar interpretación con IA ──────────────────────────────────────
    frase_ia = interpretar_con_ia(infos, contexto, hay_urgente)
    if frase_ia:
        return frase_ia          # ← IA tuvo éxito, usar su frase

    # ── Interpretación basada en reglas (respaldo) ───────────────────────────
    return generar_frase(infos, patron, contexto, hay_urgente)
```

**Nueva función `modo_interpretacion`** — reporta el motor activo para mostrarlo en la interfaz:

```python
def modo_interpretacion() -> str:
    if _IA_IMPORTADA and ia_disponible():
        return "IA (Claude)"
    if _IA_IMPORTADA:
        return "Reglas (ANTHROPIC_API_KEY no configurada)"
    return "Reglas (módulo IA no disponible)"
```

#### Cambios en `interfaz.py`

**Nueva importación:**
```python
from semantico import compilar, modo_interpretacion
```

**Indicador de modo en la interfaz** — pequeña etiqueta junto al encabezado TRADUCCIÓN:
```python
_modo = modo_interpretacion()
_ia_activa = "IA" in _modo and "no" not in _modo.lower()
_modo_color = "#06D6A0" if _ia_activa else "#888AAA"  # verde si IA, gris si reglas
_modo_icono = "✦ IA" if _ia_activa else "⚙ Reglas"

self.lbl_modo_ia = tk.Label(
    f_frase_hdr, text=_modo_icono,
    font=("Segoe UI", 7, "bold"), bg="#0F3460", fg=_modo_color
)
```

**Compilación en hilo separado** — la Fase 3 (semántica) puede tardar 1-3 segundos cuando usa la IA. Para que la interfaz no se congele, se refactorizó `_compilar` para correr la fase 3 en un hilo:

```python
def _compilar(self):
    entrada = self._construir_entrada()

    # Fases 1 y 2 (léxico y sintáctico) — síncronas, muy rápidas
    # ... (código igual que antes)

    # Fase 3: semántica — puede llamar a la IA, corre en hilo
    self.btn_compilar.configure(state="disabled", text="⏳ Interpretando...")
    self.lbl_frase.config(text="⏳ Interpretando señales...")

    def _fase3_hilo():
        buf3 = io.StringIO()
        with contextlib.redirect_stdout(buf3):
            frases = compilar(entrada)      # ← aquí puede llamar a Claude
        errores_sem = buf3.getvalue()
        # Regresar al hilo principal para actualizar la UI
        self.root.after(0, lambda: self._mostrar_semantico(entrada, frases, errores_sem))

    threading.Thread(target=_fase3_hilo, daemon=True).start()


def _mostrar_semantico(self, entrada, frases, errores_sem):
    """Actualiza la UI con el resultado de la fase semántica."""
    self.btn_compilar.configure(state="normal", text="▶  Compilar")
    # ... muestra frases en el tab semántico y en el label prominente
```

> **¿Por qué `root.after(0, ...)`?**  
> Tkinter no es thread-safe — si un hilo que no es el principal intenta modificar widgets, la aplicación crashea. `root.after(0, callback)` agenda el callback para que corra en el próximo ciclo del hilo principal de Tkinter, haciendo la actualización segura.

#### Instalación requerida

```bash
pip install anthropic
```

#### Activación de la IA

```bash
# Configurar la clave de API (una sola vez en cada sesión de terminal)
export ANTHROPIC_API_KEY='sk-ant-...'

# Iniciar la aplicación
python3 interfaz.py
```

Para hacerla permanente (no tener que escribirla cada vez):
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zshrc
source ~/.zshrc
```

#### Comportamiento según disponibilidad

| Situación | Comportamiento | Indicador en UI |
|-----------|---------------|-----------------|
| SDK instalado + API key configurada | Usa Claude para todas las frases | **✦ IA** (verde) |
| SDK instalado + sin API key | Avisa una vez en consola, usa reglas | **⚙ Reglas** (gris) |
| SDK no instalado | Usa reglas silenciosamente | **⚙ Reglas** (gris) |
| Error de red o rate limit | Avisa en consola, usa reglas para esa frase | **⚙ Reglas** (gris) |

#### Comparación de resultados: Reglas vs IA

| Entrada | Sistema de Reglas | Claude (IA) |
|---------|------------------|-------------|
| `mueve_pulgares + agita` | `¡Quiere jugar videojuegos y llama la atención urgentemente! Es urgente.` | `Está agitado y llama la atención porque quiere que lo dejen jugar videojuegos.` |
| `[tarde] manos_palmas_hacia_arriba + cabeza_si` | `En la tarde: confirma que sí y quiere que le den la razón` | `En la tarde confirma que sí tiene razón y quiere que se lo reconozcan.` |
| `dedoindice_boca + palma_abajo` | `Pide silencio. Pide calma o que paren.` | `Pide que hagan silencio y se calmen.` |
| `[dolor] ~sonrie + sonido_agudo !` | `Con señales de dolor: ¡siente un dolor agudo e intenso! Necesita atención urgente ahora mismo.` | `Con señales de dolor: no está bien y siente un dolor agudo muy intenso, necesita ayuda urgente.` |

#### Decisión de diseño: IA como capa sobre el compilador, no en lugar de él

La IA **no reemplaza** el analizador léxico ni el sintáctico. El pipeline `lexer → parser → semántico` corre completo antes de que la IA entre en juego. Esto es intencional:

- El **lexer** garantiza que solo tokens válidos del alfabeto lleguen al semántico
- El **parser** garantiza que la estructura gramatical es correcta (precedencia, operadores)
- El **semántico** detecta el patrón, calcula los significados individuales con los overrides de contexto, y detecta las advertencias `[SEM-*]`
- La **IA** recibe los datos ya procesados y listos — no texto crudo — lo que hace su tarea más precisa y predecible

Esto también cumple completamente con los criterios de la rúbrica: las tres fases formales del compilador existen y funcionan independientemente de si la IA está disponible o no.

---

## Estado actual del proyecto

| Componente | Estado | Archivo |
|------------|--------|---------|
| Analizador léxico (57 tokens) | ✅ Completo | `lexer.py` |
| Analizador sintáctico | ✅ Completo | `sintactico.py` |
| Analizador semántico | ✅ Completo | `semantico.py` |
| Intérprete IA (Claude) | ✅ Completo | `interpretador_ia.py` |
| Interfaz gráfica integrada | ✅ Completo | `interfaz.py` |
| Suite de pruebas formales | ✅ Completo | `tests.py` |
| Síntesis de voz (español) | ✅ Completo | `interfaz.py` |
| Sistema de errores tipificados | ✅ Completo | `lexer.py`, `sintactico.py`, `semantico.py` |
| Manual interno | ✅ Completo | `MANUAL_COMPILADOR.md` |
| Referencia de combinaciones | ✅ Completo | `COMBINACIONES.md` |
| Documento formal (14 secciones) | 🔜 Pendiente | — |

---

*Bitácora actualizada al terminar la Etapa 10 — Intérprete semántico con IA (Claude).*
