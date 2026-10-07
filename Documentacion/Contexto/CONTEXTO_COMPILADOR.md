# Compilador de Lenguaje de Comunicación Personal — Contexto Completo

**Equipo:** Nicolás · Ricardo · Rasshid  
**Materia:** Lenguajes y Autómatas — Ingeniería en Sistemas Computacionales  
**Fecha:** Abril–Mayo 2026

---

## 1. ¿Qué es el proyecto?

Un compilador para un **lenguaje formal personalizado** diseñado para personas que se comunican mediante sonidos y gestos en lugar del lenguaje hablado convencional. El compilador toma tokens de texto que representan sonidos y gestos, y los traduce a frases naturales en español.

La persona acompañante observa al usuario y teclea los tokens en la interfaz. El sistema **no reconoce voz ni visión**: todo el peso de observación lo lleva el acompañante. El compilador formaliza, valida y traduce.

### Caso de uso real
El usuario principal es el hermano de Nicolás, quien tiene discapacidad comunicativa. La familia convive diariamente con él y conoce sus patrones comunicativos, pero no existe documentación formal transferible a nuevos cuidadores.

---

## 2. Fases del compilador

| Fase | Descripción | Estado |
|------|-------------|--------|
| **1. Análisis léxico** | Reconoce tokens (sonidos/gestos) del alfabeto definido | ✅ Implementado en `src/analizador_lexico.py` |
| **2. Análisis sintáctico** | Valida secuencias de tokens según gramática BNF | ✅ Implementado en `src/analizador_sintactico.py` |
| **3. Análisis semántico** | Construye frase natural con contexto (mañana/noche/comida/dolor) | ✅ Integrado en el parser |
| **4. Generación de salida** | Produce texto en español; voz con Web Speech API | ⚠️ Solo texto; voz pendiente |

---

## 3. Alfabeto de tokens (vocabulario)

Definido en `src/vocabulario.json`. 56 tokens organizados en 6 categorías:

### Peticiones (14 tokens)
| Token | Significado |
|-------|-------------|
| `sonido_corto` | algo |
| `sonido_largo` | ayuda urgente |
| `señalar_vaso` | tomar agua |
| `señalar_comida` | comer algo |
| `señalar_puerta` | salir |
| `señalar_cama` | dormir |
| `señalar_bano` | ir al baño |
| `señalar_ropa` | cambiarme de ropa |
| `señalar_medicina` | tomar mi medicina |
| `señalar_telefono` | usar el teléfono |
| `señalar_television` | ver televisión |
| `señalar_ventana` | que abran la ventana |
| `extender_mano` | tomar algo |
| `señalar_reloj` | hacer algo en este momento |

### Emociones (10 tokens)
`manos_arriba` · `manos_abajo` · `agitar_manos` · `sonrisa` · `fruncir_ceno` · `abrazar_cuerpo` · `señalar_corazon` · `cubrir_cara` · `saltar` · `bostezar`

### Dolor (12 tokens)
`cabeza_abajo` · `señalar_cabeza` · `señalar_estomago` · `señalar_pecho` · `señalar_garganta` · `señalar_espalda` · `señalar_pierna` · `temblar` · `sudar` · `señalar_ojos` · `señalar_oidos` · `señalar_dientes`

### Social (10 tokens)
`aplaudir` · `señalar_persona` · `saludar_mano` · `despedir_mano` · `señalar_familia` · `señalar_doctor` · `señalar_enfermera` · `pulgar_arriba` · `pulgar_abajo` · `señalar_ayuda`

### Respuestas (7 tokens)
`asentir` · `negar` · `encoger_hombros` · `señalar_si` · `señalar_no` · `esperar_mano` · `repetir_gesto`

### Intensidad (3 tokens)
`muy` · `poco` · `mucho`

### Operadores especiales
| Token | Sintaxis | Descripción |
|-------|----------|-------------|
| `MAS` | `+` | Operador de secuencia entre tokens |
| `CONTEXTO` | `[manana\|noche\|comida\|dolor]` | Modificador de contexto temporal |

---

## 4. Gramática BNF

```bnf
programa     ::= contexto_opt expresion
contexto_opt ::= CONTEXTO | ε
expresion    ::= expresion MAS token_simple
              |  token_simple
token_simple ::= SONIDO_CORTO | SONIDO_LARGO | SENALAR_VASO | ...
              |  (cualquiera de los 55 tokens)
```

El parser es **LALR(1)** (generado por PLY yacc). Las secuencias son cadenas de tokens conectados con `+`, opcionalmente precedidas por un contexto entre corchetes.

### Ejemplos de entradas válidas
```
señalar_vaso
señalar_estomago + señalar_vaso
[dolor] sonido_largo + señalar_pecho
[manana] señalar_comida + manos_arriba
muy + señalar_cabeza + señalar_doctor
sonido_largo + señalar_vaso + señalar_bano
```

---

## 5. AST actual

El AST se construye como una **lista de tuplas** `(valor_token, tipo_semántico)`:

```python
# Ejemplo: señalar_estomago + señalar_vaso
[("señalar_estomago", "dolor"), ("señalar_vaso", "peticion")]
```

La función `construir_frase()` en `analizador_sintactico.py` recorre el AST y selecciona la plantilla adecuada según las combinaciones presentes (dolor+petición, emoción+social, urgencia, etc.).

---

## 6. Sistema de contexto semántico

El contexto (`manana`, `noche`, `comida`, `dolor`) sobreescribe el significado base del token:

| Token | Base | En `[manana]` | En `[noche]` | En `[comida]` |
|-------|------|---------------|--------------|---------------|
| `señalar_comida` | comer algo | Quiero desayunar | Quiero cenar | — |
| `señalar_cama` | dormir | Aún quiero dormir un poco más | Ya es hora de dormir | — |
| `manos_arriba` | estoy feliz | — | — | Está delicioso, me encanta |
| `sonido_largo` | ayuda urgente | — | — | — | Tengo mucho dolor, necesito ayuda urgente |

---

## 7. Plantillas de frases

Definidas en `vocabulario.json` → `"plantillas"`:

| Combinación | Plantilla |
|-------------|-----------|
| Petición sola | `Me gustaría {peticion}, por favor.` |
| Emoción + petición | `{emocion_cap} y me gustaría {peticion}, por favor.` |
| Dolor solo | `{dolor_cap}. Necesito ayuda.` |
| Dolor + petición | `{dolor_cap}. Por eso me gustaría {peticion}, por favor.` |
| Social sola | `{social_cap}.` |
| Social + emoción | `{emocion_cap}. {social_cap}.` |
| Saludo | `{social_cap}. ¿Cómo están?` |
| Despedida | `{social_cap}. Fue un gusto.` |
| Urgencia | `¡{peticion_cap}! Es urgente, por favor ayúdenme.` |
| Confirmación | `{respuesta_cap}.` |

---

## 8. Arquitectura del código

```
CompiladorAutomatas2/
├── src/
│   ├── analizador_lexico.py      ← Lexer principal (PLY lex, 55 tokens)
│   ├── analizador_sintactico.py  ← Parser + semántica (PLY yacc, LALR(1))
│   ├── vocabulario.json          ← Vocabulario, contextos y plantillas
│   └── ply/                      ← Librería PLY local
├── lexer.py                      ← Lexer antiguo (versión inicial, tokens MMM/ATA)
├── main.py                       ← Entry point antigua (usa lexer.py viejo)
├── tests/
│   ├── lexico.py                 ← Test de calculadora (PLY demo, no del proyecto)
│   ├── sintx.py                  ← Test de calculadora (PLY demo, no del proyecto)
│   └── [resto = tests de PLY]    ← Tests de la librería PLY, no del compilador
├── example/                      ← Ejemplos de PLY (BASIC, ANSI C, etc.)
└── doc/                          ← Documentación de PLY
```

**Herramientas:** Python 3.14 · PLY (Python Lex-Yacc) · JSON para vocabulario

---

## 9. Observaciones de la maestra

La maestra indicó que el documento formal del proyecto debe tener esta estructura mínima:

1. Introducción
2. Problemática
3. Objetivos
4. Descripción del DSL
5. Tabla de Tokens
6. Expresiones Regulares
7. Gramática BNF/EBNF
8. Tipo de Parser
9. AST esperado
10. Manejo de errores
11. Casos de prueba
12. Herramientas a usar
13. Arquitectura lexer-parser
14. Resultados esperados

Análisis por fase que proporcionó:
- **Fase 1 (Léxico):** La más sencilla. La entrada ya es texto, el lexer solo necesita reconocer identificadores de un catálogo. No hay reconocimiento de voz/visión.
- **Fase 2 (Sintáctico):** Primer reto real. La gramática debe capturar que los gestos no se combinan arbitrariamente. Requiere trabajo previo con el usuario para documentar patrones reales. Una CFG en BNF con parser recursivo descendente es suficiente.
- **Fase 3 (Semántico):** El corazón del proyecto. La semántica es personal y contextual — la solución es una tabla de símbolos por usuario. El compilador no infiere significados, los consulta.
- **Fase 4 (Generación):** La más directa. Plantillas + Web Speech API del navegador para síntesis de voz en español.

**Riesgo principal:** El compilador solo funciona si el lenguaje ya está formalizado. Antes del código, debe documentarse el vocabulario real del usuario con sus cuidadores.

---

## 10. Rúbrica de evaluación (100 puntos)

### 10.1 Analizador Léxico — 30 puntos (6 criterios × 5 pts)

| # | Criterio | Descripción |
|---|----------|-------------|
| 1.1 | Correctitud en identificación de tokens | ¿El lexer identifica correctamente todos los tokens? |
| 1.2 | Manejo de errores léxicos | ¿Detecta caracteres no válidos o secuencias erróneas? |
| 1.3 | Eficiencia | ¿Evita retrocesos innecesarios con grandes entradas? |
| 1.4 | Manejo de espacios/comentarios | ¿Ignora espacios y comentarios correctamente? |
| 1.5 | Uso de expresiones regulares | ¿Usa regex eficientes y claras para describir tokens? |
| 1.6 | Flexibilidad y modularidad | ¿Es fácil agregar nuevos tokens sin refactorizar? |

### 10.2 Analizador Sintáctico — 30 puntos (6 criterios × 5 pts)

| # | Criterio | Descripción |
|---|----------|-------------|
| 2.1 | Correctitud en construcción del AST | ¿El parser construye correctamente el AST? |
| 2.2 | Elección del tipo de parser | ¿LL(1), LR, LALR es adecuado para la gramática? |
| 2.3 | Manejo de errores sintácticos | ¿Mensajes de error claros con posición? |
| 2.4 | Generación del AST | ¿El árbol refleja la jerarquía del lenguaje? |
| 2.5 | Modularidad y mantenibilidad | ¿Fácil de extender con nuevas reglas? |
| 2.6 | Recuperación de errores | ¿Puede continuar analizando tras un error? |

### 10.3 Integración Lexer + Parser — 20 puntos (4 criterios × 5 pts)

| # | Criterio | Descripción |
|---|----------|-------------|
| 3.1 | Integración lexer-parser | ¿El flujo de trabajo entre ambos es claro y eficiente? |
| 3.2 | Pruebas de integración | ¿Hay tests que verifican que el lexer genera tokens que el parser consume? |
| 3.3 | Manejo de casos complejos | ¿Funciona con tokens múltiples y estructuras anidadas? |
| 3.4 | Pruebas de casos de error | ¿Se valida el comportamiento ante errores léxicos y sintácticos? |

### 10.4 Evaluación General — 10 puntos (2 criterios × 5 pts)

| # | Criterio | Descripción |
|---|----------|-------------|
| 4.1 | Innovación y creatividad | ¿El proyecto presenta enfoques creativos? |
| 4.2 | Escalabilidad | ¿El sistema escala si el lenguaje se expande? |

### 10.5 Presentación y Exposición — 10 puntos

---

## 11. Lo que ya está hecho ✅

| Componente | Estado | Archivo |
|------------|--------|---------|
| Propuesta del compilador | ✅ Completo | ZIP: PropuestaCompilador.docx |
| Justificación del proyecto | ✅ Completo | ZIP: JustificacionHatersMU.docx |
| Estado del arte | ✅ Completo | ZIP: EstadoDelArte.docx |
| Presentación PPT | ✅ Existe | ZIP: CompiladorLenguajesyAutomatas.pptx |
| Léxico (55 tokens, 6 categorías) | ✅ Funcional | `src/analizador_lexico.py` |
| Manejo de errores léxicos (`t_error`) | ✅ Básico | `src/analizador_lexico.py:135` |
| Ignorar espacios y saltos de línea | ✅ Hecho | `src/analizador_lexico.py:129` |
| Vocabulario en JSON (extensible) | ✅ Completo | `src/vocabulario.json` |
| Parser LALR(1) con PLY yacc | ✅ Funcional | `src/analizador_sintactico.py` |
| Gramática BNF para secuencias | ✅ Implementada | `src/analizador_sintactico.py:148` |
| Análisis semántico con contexto | ✅ Funcional | `src/analizador_sintactico.py:24` |
| Sistema de plantillas de frases | ✅ Completo | `src/vocabulario.json` → plantillas |
| Tabla de símbolos contextual | ✅ Implementada | `src/vocabulario.json` → contexto |
| Pipeline léxico+sintáctico+semántico | ✅ Integrado | `src/analizador_sintactico.py:265` |
| Manejo de errores sintácticos (`p_error`) | ✅ Básico | `src/analizador_sintactico.py:252` |

---

## 12. Lo que FALTA por hacer ❌

### Prioridad ALTA (afecta directamente la calificación)

| # | Qué falta | Criterio de rúbrica afectado | Puntos en riesgo |
|---|-----------|------------------------------|------------------|
| A1 | **Recuperación de errores en el parser** — el parser debe poder continuar analizando después de un error, no detenerse | 2.6 Recuperación de errores | 5 pts |
| A2 | **Tests de integración del proyecto** — `tests/lexico.py` y `tests/sintx.py` son demos de calculadora, no del compilador. Falta un archivo de tests sistemáticos que prueben el pipeline real | 3.2 Pruebas de integración | 5 pts |
| A3 | **Tests de casos de error** — verificar que entradas inválidas producen los mensajes de error correctos, tanto léxicos como sintácticos | 3.4 Pruebas de errores | 5 pts |
| A4 | **Documento formal con la estructura mínima requerida** — la maestra pidió explícitamente: Introducción, Problemática, Objetivos, Descripción del DSL, Tabla de Tokens, Expresiones Regulares, Gramática BNF/EBNF, Tipo de Parser, AST esperado, Manejo de errores, Casos de prueba, Herramientas, Arquitectura, Resultados esperados | Presentación y documentación | hasta 10 pts |
| A5 | **Manejo de comentarios en el lexer** — el criterio 1.4 pide que también se ignoren comentarios, no solo espacios | 1.4 Espacios y comentarios | hasta 5 pts |

### Prioridad MEDIA (mejora la calificación)

| # | Qué falta | Criterio afectado |
|---|-----------|-------------------|
| B1 | **AST formal con clases de nodos** — actualmente el AST es una lista de tuplas. La maestra evalúa si el AST refleja la jerarquía; una estructura de clases (`NodoSecuencia`, `NodoToken`, etc.) sería más puntuable | 2.4 Generación del AST |
| B2 | **Documentar explícitamente que el parser es LALR(1)** y justificar por qué es adecuado para la gramática del lenguaje | 2.2 Elección del parser |
| B3 | **Conectar `main.py` con el pipeline real** — actualmente `main.py` usa el lexer viejo (`lexer.py`), no el compilador completo en `src/` | 3.1 Integración |
| B4 | **Casos de prueba complejos documentados** — secuencias con contexto, múltiples dolores, intensidad + dolor + social, casos límite | 3.3 Casos complejos |
| B5 | **Mensajes de error con número de línea/columna** — el error léxico actual muestra columna pero no línea; el error sintáctico no muestra posición | 2.3 Manejo de errores |

### Prioridad BAJA (mejoras adicionales)

| # | Qué falta | Criterio afectado |
|---|-----------|-------------------|
| C1 | **Generación de voz** con Web Speech API del navegador o pyttsx3 — la maestra lo mencionó en observaciones | 4.1 Innovación |
| C2 | **Interfaz gráfica** (GUI o web) para el acompañante — la propuesta menciona "interfaz simple" | 4.1 Innovación |
| C3 | **Mecanismo de extensión del vocabulario** desde la interfaz — agregar tokens sin editar JSON manualmente | 4.2 Escalabilidad |

---

## 13. Problemas técnicos detectados en el código actual

### `main.py` desconectado del compilador real
```python
# main.py línea 1 — usa el lexer viejo
from lexer import lexer  # ← debería importar desde src/
```
`main.py` importa el `lexer.py` de la raíz (versión antigua con tokens `MMM`, `ATA`, etc.), no el compilador completo en `src/`. Esto significa que ejecutar `main.py` no muestra el pipeline real.

### Dos versiones del lexer coexistiendo
- `lexer.py` (raíz): versión inicial, tokens de sonidos vocales (`MMM`, `ATA`, `AAH`...) y gestos (`SENALA`, `PALMA_ARRIBA`...)
- `src/analizador_lexico.py`: versión final, tokens de gestos descriptivos (`señalar_vaso`, `sonrisa`...)

Ambos están activos pero son incompatibles. El código de producción es el de `src/`.

### Tests en `tests/` no son del proyecto
`tests/lexico.py` y `tests/sintx.py` son tests de una calculadora aritmética (demo de PLY), no del compilador del lenguaje de comunicación personal.

---

## 14. Casos de prueba existentes (en `analizador_sintactico.py`)

Solo hay 1 caso de prueba hardcodeado (incompleto, la descripción no coincide con la entrada):
```python
("señalar_vaso + señalar_television + sonrisa", None, "Múltiples dolores + petición")
```

La descripción dice "múltiples dolores + petición" pero la entrada tiene una petición, otra petición y una emoción.

---

## 15. Resumen: puntuación estimada con el estado actual

| Sección | Puntaje máximo | Estimado actual | Qué sube la nota |
|---------|---------------|-----------------|------------------|
| Analizador Léxico | 30 | ~22–25 | Agregar manejo de comentarios (A5), más casos de prueba |
| Analizador Sintáctico | 30 | ~20–23 | Agregar recuperación de errores (A1), AST formal (B1) |
| Integración | 20 | ~12–15 | Tests de integración (A2, A3), conectar main.py (B3) |
| Evaluación General | 10 | ~7–8 | Voz/GUI (C1, C2) |
| Presentación | 10 | TBD | Documento con estructura mínima (A4) |
| **Total estimado** | **100** | **~61–71** | |

Con las mejoras de prioridad ALTA implementadas el estimado sube a **~80–88**.
