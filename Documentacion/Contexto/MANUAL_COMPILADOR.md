# Manual Interno del Compilador
## Lenguaje de Comunicación Personal — Lenguajes y Autómatas 2026
**Equipo:** Nicolás · Ricardo · Rasshid

---

## ¿Qué es este compilador?

Un compilador que toma secuencias de tokens — cada uno representando un sonido, gesto o expresión que produce una persona con discapacidad comunicativa — y las traduce a frases en español natural.

El cuidador o familiar observa a la persona y escribe los tokens en la interfaz. El compilador valida la secuencia, la interpreta según el contexto y genera la frase correspondiente.

**Lo que el compilador NO hace:** reconocer voz ni gestos automáticamente. Todo el peso de observación lo carga el acompañante humano. El compilador formaliza, valida y traduce.

---

## Arquitectura del compilador

```
Entrada de texto
      ↓
┌─────────────┐
│   LÉXICO    │  Reconoce tokens individuales
└──────┬──────┘
       ↓
┌─────────────┐
│ SINTÁCTICO  │  Valida combinaciones según gramática BNF
└──────┬──────┘
       ↓
┌─────────────┐
│  SEMÁNTICO  │  Interpreta significado según contexto
└──────┬──────┘
       ↓
┌─────────────┐
│ GENERACIÓN  │  Produce frase en español (texto + voz)
└─────────────┘
```

**Archivos del proyecto:**
- `lexer.py` — Analizador léxico (PLY lex)
- `parser.py` — Analizador sintáctico (PLY yacc, LALR)
- `semantico.py` — Tabla de símbolos + generación de frases
- `main.py` — Entry point
- `probar_lexer.py` — Herramienta interactiva de prueba

---

## Categorías de tokens

El alfabeto del lenguaje tiene **55 tokens** organizados en 6 categorías. Cada token representa una acción física que la persona **puede realizar** dadas sus capacidades.

### E1 — Sonidos vocales (12 tokens)

Sonidos que la persona produce con la voz sin articular palabras.

| Token | Descripción | Interpretación base |
|-------|-------------|---------------------|
| `mmm` | Sonido nasal cerrado | Duda, pensando, atención |
| `ata` | Vocalización corta "ata" | Llama a su hermano |
| `aah` | Sonido abierto prolongado | Alivio, satisfacción |
| `uuh` | Sonido grave de queja | Molestia, incomodidad |
| `oh` | Sonido de sorpresa | Sorpresa, descubrimiento |
| `shh` | Sonido sibilante | ganas de hacer del baño |
| `uff` | Sonido de esfuerzo/cansancio | Dolor, cansancio, frustración |
| `ay` | Exclamación de dolor | Dolor agudo o susto |
| `ana` | Vocalización repetitiva | Llamado a persona cercana |
| `bah` | Rechazo vocal | Rechazo, no querer algo |
| `pff` | Sonido de burla/indiferencia | Desacuerdo, no importa |

---

### E2 — Gestos de manos (12 tokens)

Movimientos que la persona puede hacer con las manos o brazos.

| Token | Descripción | Interpretación base |
|-------|-------------|---------------------|
| `senala` | Señala en dirección general | Quiere algo en esa dirección |
| `palma_arriba` | Palma de la mano hacia arriba | Pedir, recibir, ¿qué? |
| `palma_abajo` | Palma hacia abajo | Calma, parar, suficiente |
| `puno` | Mano cerrada en puño | Fuerza, determinación, querer fuertemente |
| `mano_abierta` | Mano extendida abierta | Alto, espera, detente |
| `toca` | Toca algo o a alguien | Quiere ese objeto o persona |
| `agita` | Agita la mano o brazo | Llamar atención, urgencia |
| `apunta_si` | Apunta con el dedo afirmativamente | Confirmar, eso es, sí |
| `junta_dedos` | Junta los dedos (gesto italiano) | poquito |
| `separa_manos` | Separa las manos | No sé, no tengo idea |
| `dedoindice_boca` | dedo indice sobre la boca | Guardar silencio |
| `mueve_pulgares`  |  mueve pulgares simulando control | Quiere jugar videojuegos |
| `mano_derecha_a_izquierda` | mueve la mano de derecha a izquierda rapidamemente | indica que algo lo acabo todo |
| `manos_palmas_hacia_arriba` | manos arriba con palmas hacia arriba | quiere que le digan que tiene razon |

---

### E3 — Vocalizaciones (6 tokens)

Sonidos sostenidos o patrones vocales con características específicas.

| Token | Descripción | Interpretación base |
|-------|-------------|---------------------|
| `sonido_largo` | Vocalización sostenida larga | Urgencia |
| `sonido_corto` | Vocalización breve | Petición simple, aviso |
| `sonido_repetido` | Vocalización que se repite | Insistencia, no ha sido atendido |
| `sonido_agudo` | Vocalización en tono alto | Dolor agudo, susto, alerta |
| `sonido_grave` | Vocalización en tono bajo | Cansancio, somnolencia |
| `sonido_suave` | Vocalización muy tenue | Bienestar, tranquilidad |
| `sonido_ronquido` | Simulacion de ronquido | irse a dormir |

---

### E4 — Movimientos corporales (10 tokens)

Movimientos del cuerpo, cabeza o postura.

| Token | Descripción | Interpretación base |
|-------|-------------|---------------------|
| `cabeza_si` | Movimiento afirmativo de cabeza | Sí, correcto, quiero eso |
| `cabeza_no` | Movimiento negativo de cabeza | No, incorrecto, no quiero |
| `cabeza_lado` | Cabeza hacia un lado | Tal vez, no estoy seguro |
| `inclina_cuerpo` | Inclina el cuerpo hacia adelante | Interés, querer acercarse |
| `acerca_cuerpo` | Se acerca hacia algo/alguien | Quiero estar cerca, quiero eso |
| `aleja_cuerpo` | Se aleja de algo/alguien | No quiero, aléjate, molesta |
| `senala_propio` | Señala hacia sí mismo | Es para mí, yo lo quiero, me duele a mí |
| `senala_externo` | Señala hacia afuera/otro | Es para otro, allá afuera |
| `encoge_hombros` | Encoge los hombros | No sé, no importa |
| `levanta_brazo` | Levanta el brazo | Necesito ayuda, atención |

---

### E5 — Expresiones faciales (10 tokens)

Gestos y expresiones del rostro.

| Token | Descripción | Interpretación base |
|-------|-------------|---------------------|
| `cierra_ojos` | Cierra los ojos | Cansancio, quiere dormir, no quiere ver |
| `abre_ojos` | Abre los ojos muy grandes | Sorpresa, miedo, alerta |
| `frunce_ceno` | Frunce el ceño | Enojo |
| `sonrie` | Sonrisa | Bienestar, felicidad, de acuerdo |
| `llanto` | Llora o hace ademán de llorar | Tristeza, dolor intenso, miedo |
| `boca_abierta` | Abre la boca | Hambre, sed, quiere hablar |
| `mira_arriba` | Dirige la vista hacia arriba | Recuerda algo, pensando |
| `mira_abajo` | Dirige la vista hacia abajo | Tristeza, vergüenza, cansancio |
| `mira_objeto` | Mira fijamente un objeto | Quiere ese objeto |
| `parpadeo_rapido` | Parpadea rápido | Incomodidad ocular, molestia |

---

### E6 — Modificadores (5 tokens)

Alteran la intensidad o duración de lo que se está comunicando. Siempre acompañan a otro token.

| Token | Descripción | Efecto |
|-------|-------------|--------|
| `rapido` | Acción rápida o urgente | Aumenta urgencia |
| `lento` | Acción lenta o suave | Disminuye intensidad |
| `doble` | Dos veces | Refuerzo del mensaje |
| `triple` | Tres veces | Énfasis máximo |
| `pausa` | Pausa deliberada | Separación entre ideas |

---

## Sistema de contexto

El contexto es un modificador global que precede a toda la expresión entre corchetes. Le dice al compilador en qué situación ocurre la comunicación, lo que cambia cómo se interpretan los tokens.

**Sintaxis:** `[contexto] expresion`

### Contextos disponibles

| Contexto | Cuándo usarlo | Efecto semántico |
|----------|--------------|-----------------|
| `[manana]` | Mañana (aprox. 6am–12pm) | Peticiones orientadas al inicio del día: levantarse, desayunar, rutina |
| `[tarde]` | Tarde (aprox. 12pm–7pm) | Actividades del día: pasear, televisión, visitas |
| `[noche]` | Noche (aprox. 7pm–6am) | Orientado al descanso: cenar, dormir, tranquilidad |
| `[dolor]` | Cuando hay malestar físico | Prioriza interpretación de dolor sobre otras lecturas |

### Ejemplo de cómo cambia el significado

```
sonido_largo + senala_propio
```
- Sin contexto → *"Necesita atención"*
- `[manana]` → *"Ya quiere levantarse"*
- `[noche]` → *"No puede dormir, necesita ayuda"*
- `[dolor]` → *"Tiene mucho dolor, necesita ayuda urgente"*

---

## Operadores

Los operadores conectan tokens y expresiones para construir mensajes más complejos.

### `+` — Secuencia (MAS)

Conecta dos tokens en orden. Es el operador principal del lenguaje.

```
mmm + palma_arriba
uff + sonido_largo + encoge_hombros
[manana] sonrie + cabeza_si + boca_abierta
```

**Precedencia:** la más baja de los operadores unarios. Asociativo por la izquierda.

---

### `|` — Alternativa (O)

Indica que la persona comunicó una cosa u otra, o que el cuidador no está seguro entre dos opciones. El compilador genera una frase que contempla ambas posibilidades.

```
sonrie | cabeza_si
palma_arriba | senala_externo
[tarde] boca_abierta | mira_objeto
```
→ *"Parece que quiere algo, quizás agua o salir"*

**Precedencia:** menor que `+`. Es decir, `a + b | c + d` se lee como `(a + b) | (c + d)`.

---

### `!` — Urgencia (URGENTE, postfijo)

Marca toda la expresión como urgente. Va al final de la secuencia. Activa un nivel de alerta en la salida.

```
sonido_largo + encoge_hombros !
uff !
[dolor] sonido_agudo + frunce_ceno !
```
→ *"¡Es urgente! Necesita atención inmediata."*

**Precedencia:** la más alta. Solo aplica a la expresión inmediatamente a su izquierda.

---

### `~` — Negación (NEG, prefijo)

Niega o invierte el significado del token que le sigue. Útil cuando la persona hace un gesto pero en sentido negativo.

```
~cabeza_si
~sonrie
~palma_arriba
```
→ *"No quiere eso"*, *"No está bien"*, *"No pide nada"*

**Precedencia:** la más alta entre los operadores. Se aplica primero que `+` y `|`.

---

### `;` — Nueva idea (FIN_EXPR)

Separa dos mensajes completamente distintos dentro de una misma entrada. El parser los analiza como expresiones independientes y genera una frase por cada una.

```
[manana] mmm + boca_abierta ; [dolor] uff + senala_propio
```
→ Frase 1: *"Quiere desayunar"*
→ Frase 2: *"Le duele algo"*

---

## Tabla de precedencia de operadores

De mayor a menor prioridad:

| Nivel | Operador | Tipo | Ejemplo |
|-------|----------|------|---------|
| 1 (mayor) | `~` | Prefijo unario | `~sonrie` |
| 2 | `!` | Postfijo unario | `uff !` |
| 3 | `+` | Binario, izq→der | `mmm + palma_arriba` |
| 4 (menor) | `\|` | Binario, izq→der | `sonrie \| cabeza_si` |

El `;` no tiene precedencia con los otros — simplemente separa expresiones completas.

---

## Ejemplos de entradas válidas

```
# Petición simple
mmm + palma_arriba

# Con contexto de mañana
[manana] boca_abierta + senala_propio

# Urgente
[dolor] sonido_largo + frunce_ceno !

# Negación
~cabeza_no + sonrie

# Alternativa
palma_arriba | mira_objeto

# Complejo: negación + secuencia + urgencia
[dolor] ~sonrie + uff + sonido_largo !

# Dos mensajes en una entrada
[manana] sonrie + cabeza_si ; [dolor] ay + senala_propio

# Comentario del cuidador (ignorado por el compilador)
# el paciente se despertó agitado
[noche] agita + sonido_largo !
```

---

## Ejemplos de errores que detecta el lexer

```
token_inventado          → Error léxico: token no reconocido
[contexto_malo] mmm      → Error léxico: contexto no reconocido
mmm @ palma_arriba       → Error léxico: carácter '@' no válido
```

---

## Tabla de símbolos contextual (semántica)

La tabla de símbolos no almacena variables como en un compilador convencional — almacena el **perfil de interpretación** del usuario. Se consulta durante el análisis semántico para resolver ambigüedades.

| Clave | Contenido |
|-------|-----------|
| `contexto_activo` | El contexto de la sesión actual (`manana`, `noche`, etc.) |
| `sesion_previa` | Últimos tokens emitidos (para resolver patrones repetidos) |
| `nivel_urgencia` | `normal` o `urgente` según presencia de `!` |
| `negacion_activa` | Si el token fue precedido por `~` |

---

## Gramática BNF (borrador)

```bnf
programa     ::= expresion (';' expresion)*

expresion    ::= contexto_opt secuencia ('|' secuencia)*

contexto_opt ::= '[' CONTEXTO ']'
              |  ε

secuencia    ::= termino ('+' termino)*

termino      ::= termino '!'
              |  '~' termino
              |  token_base

token_base   ::= E1 | E2 | E3 | E4 | E5 | E6
```

---

*Este manual se actualiza a medida que avanza el desarrollo del compilador.*
