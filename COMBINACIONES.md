# Combinaciones del Lenguaje de Comunicación Personal
## Referencia completa para el Analizador Semántico
**Compilador · Lenguajes y Autómatas 2026**

---

## Cómo leer este documento

Cada token tiene:
- **Significado base** — lo que produce sin ningún contexto ni modificador
- **Override por contexto** — cómo cambia el significado según `[manana]`, `[tarde]`, `[noche]` o `[dolor]`

Las combinaciones de tokens producen frases distintas según los patrones definidos al final del documento.

---

## Significados base de los 55 tokens

### E1 — Sonidos vocales

| Token | Significado base |
|-------|-----------------|
| `mmm` | Está pensando o dudando |
| `ata` | Llama la atención de alguien cercano |
| `aah` | Siente alivio o satisfacción |
| `uuh` | Siente incomodidad o molestia leve |
| `oh` | Está sorprendido por algo |
| `shh` | Pide silencio o quiere esperar |
| `hmm` | Está indeciso entre opciones |
| `uff` | Está cansado o frustrado |
| `ay` | Siente dolor agudo o se asustó |
| `ana` | Llama a una persona específica cercana |
| `bah` | Rechaza algo o a alguien |
| `pff` | No le importa o está en desacuerdo |

### E2 — Gestos de manos

| Token | Significado base |
|-------|-----------------|
| `senala` | Quiere algo en esa dirección |
| `palma_arriba` | Está pidiendo algo |
| `palma_abajo` | Pide calma o que paren |
| `puno` | Quiere algo con mucha determinación |
| `mano_abierta` | Pide que esperen o se detengan |
| `toca` | Quiere ese objeto o quiere contacto con esa persona |
| `agita` | Llama la atención de forma urgente |
| `apunta_si` | Confirma que eso es correcto |
| `junta_dedos` | Es exactamente eso, preciso |
| `separa_manos` | No sabe o no tiene idea |
| `pulgar_arriba` | Está de acuerdo o se siente bien |
| `pulgar_abajo` | No está de acuerdo o algo está mal |

### E3 — Vocalizaciones

| Token | Significado base |
|-------|-----------------|
| `sonido_largo` | Necesita atención, algo importante |
| `sonido_corto` | Hace una petición simple |
| `sonido_repetido` | Insiste, no ha sido atendido todavía |
| `sonido_agudo` | Alerta o dolor agudo intenso |
| `sonido_grave` | Está cansado o somnoliento |
| `sonido_suave` | Está tranquilo y bien |

### E4 — Movimientos corporales

| Token | Significado base |
|-------|-----------------|
| `cabeza_si` | Afirma, está de acuerdo |
| `cabeza_no` | Niega, no quiere |
| `cabeza_lado` | Está indeciso o no está seguro |
| `inclina_cuerpo` | Muestra interés en algo |
| `acerca_cuerpo` | Quiere acercarse a algo o alguien |
| `aleja_cuerpo` | Quiere alejarse, no quiere estar cerca |
| `senala_propio` | Es para él, le afecta a él mismo |
| `senala_externo` | Es para otro, está afuera |
| `encoge_hombros` | No sabe, no le importa |
| `levanta_brazo` | Pide ayuda o atención directa |

### E5 — Expresiones faciales

| Token | Significado base |
|-------|-----------------|
| `cierra_ojos` | Está cansado o no quiere ver algo |
| `abre_ojos` | Está sorprendido o asustado |
| `frunce_ceno` | Siente dolor, disgusto o confusión |
| `sonrie` | Está contento o de acuerdo |
| `llanto` | Está muy triste o tiene dolor intenso |
| `boca_abierta` | Tiene hambre o sed |
| `mira_arriba` | Está recordando o pensando algo |
| `mira_abajo` | Está triste, avergonzado o cansado |
| `mira_objeto` | Quiere ese objeto que está mirando |
| `parpadeo_rapido` | Siente incomodidad en los ojos |

### E6 — Modificadores

| Token | Efecto sobre el mensaje |
|-------|------------------------|
| `rapido` | Aumenta la urgencia del mensaje |
| `lento` | Suaviza la intensidad del mensaje |
| `doble` | Refuerza el mensaje (énfasis x2) |
| `triple` | Énfasis máximo (x3) |
| `pausa` | Separa dos ideas dentro de la misma secuencia |

---

## Overrides por contexto

Cuando se activa un contexto, ciertos tokens cambian su significado base por el override.

### Contexto `[manana]`

| Token | Significado base | Override [manana] |
|-------|-----------------|-------------------|
| `boca_abierta` | Tiene hambre o sed | Quiere desayunar |
| `cierra_ojos` | Está cansado | Aún quiere dormir más |
| `sonrie` | Está contento | Está de buen humor al despertar |
| `uff` | Está frustrado | No quiere levantarse todavía |
| `levanta_brazo` | Pide ayuda | Necesita ayuda para levantarse |
| `sonido_largo` | Necesita atención | No quiere despertarse aún |
| `palma_arriba` | Pide algo | Quiere que le den el desayuno |
| `mira_objeto` | Quiere ese objeto | Quiere algo del desayuno |
| `sonido_grave` | Está somnoliento | Sigue con sueño, no quiere levantarse |
| `cabeza_no` | No quiere | No quiere levantarse |
| `agita` | Urgencia | Necesita algo urgente antes de levantarse |

### Contexto `[tarde]`

| Token | Significado base | Override [tarde] |
|-------|-----------------|------------------|
| `boca_abierta` | Tiene hambre o sed | Quiere almorzar o merendar |
| `senala_externo` | Apunta afuera | Quiere salir a pasear |
| `sonrie` | Está contento | Está disfrutando la tarde |
| `cierra_ojos` | Está cansado | Quiere descansar un rato |
| `agita` | Urgencia | Quiere actividad o entretenimiento |
| `inclina_cuerpo` | Muestra interés | Quiere participar en algo |
| `palma_arriba` | Pide algo | Quiere algo para la tarde |
| `mira_objeto` | Quiere ese objeto | Quiere ese objeto para entretenerse |
| `acerca_cuerpo` | Quiere acercarse | Quiere compañía o actividad compartida |

### Contexto `[noche]`

| Token | Significado base | Override [noche] |
|-------|-----------------|------------------|
| `cierra_ojos` | Está cansado | Quiere dormir ya |
| `boca_abierta` | Tiene hambre o sed | Quiere cenar |
| `sonido_grave` | Somnoliento | Está listo para dormir |
| `uff` | Frustrado | Está muy cansado del día |
| `levanta_brazo` | Pide ayuda | Necesita ayuda para acostarse |
| `sonido_largo` | Necesita atención | No puede dormir, necesita ayuda |
| `palma_abajo` | Pide calma | Quiere que bajen la voz o apaguen la luz |
| `mira_abajo` | Está triste | Está cansado y listo para descansar |
| `sonido_suave` | Está tranquilo | Está bien, listo para dormir |
| `palma_arriba` | Pide algo | Quiere algo antes de dormir |

### Contexto `[dolor]`

| Token | Significado base | Override [dolor] |
|-------|-----------------|------------------|
| `uff` | Está frustrado | Está sufriendo |
| `ay` | Dolor agudo | Siente un dolor muy intenso |
| `sonido_largo` | Necesita atención | Tiene mucho dolor, necesita ayuda urgente |
| `frunce_ceno` | Dolor o disgusto | El dolor es intenso |
| `llanto` | Muy triste | El dolor es insoportable |
| `senala_propio` | Es para él | Le duele algo en su cuerpo |
| `levanta_brazo` | Pide ayuda | Necesita atención o medicina |
| `sonido_agudo` | Alerta | Dolor agudo muy intenso |
| `agita` | Urgencia | El dolor es urgente, necesita ayuda ya |
| `uuh` | Incomodidad | Siente malestar físico constante |
| `encoge_hombros` | No sabe | No sabe cómo describir el dolor |
| `mira_abajo` | Tristeza | Está abatido por el dolor |
| `abre_ojos` | Sorpresa | El dolor lo asustó |

---

## Patrones de combinación

Cuando se combinan tokens de distintas categorías, el semántico identifica el patrón dominante y genera la frase correspondiente.

### Patrón 1 — Dolor

Activado cuando hay tokens de **E5 facial de dolor** (`frunce_ceno`, `llanto`) o **E1 de queja** (`uff`, `ay`, `uuh`) o cuando el contexto es `[dolor]`.

| Combinación | Frase generada |
|-------------|----------------|
| `frunce_ceno + sonido_largo` | Tiene dolor y necesita ayuda |
| `ay + senala_propio` | Le duele algo en su cuerpo |
| `uff + encoge_hombros` | Está sufriendo y no sabe cómo explicarlo |
| `llanto + levanta_brazo` | Tiene mucho dolor y pide ayuda |
| `sonido_agudo + frunce_ceno` | Siente un dolor agudo e intenso |
| `uuh + cabeza_lado` | Siente malestar pero no sabe bien qué es |
| `[dolor] uff + sonido_largo` | Está sufriendo mucho y necesita atención urgente |
| `[dolor] ay + senala_propio + levanta_brazo` | Le duele algo, necesita ayuda ahora |
| `[dolor] llanto + agita` | Tiene dolor insoportable, necesita ayuda urgente |
| `[dolor] sonido_agudo + frunce_ceno !` | ¡Dolor muy intenso, emergencia! |

### Patrón 2 — Petición simple

Activado cuando hay tokens de **E2 de petición** (`palma_arriba`, `senala`, `toca`, `mira_objeto`) o **E3 de aviso** (`sonido_corto`, `sonido_largo`).

| Combinación | Frase generada |
|-------------|----------------|
| `palma_arriba + mira_objeto` | Quiere ese objeto |
| `mmm + palma_arriba` | Está pidiendo algo, no está seguro qué |
| `senala + apunta_si` | Quiere exactamente eso que señala |
| `toca + cabeza_si` | Quiere ese objeto o ese contacto |
| `sonido_corto + senala` | Pide algo en esa dirección |
| `mira_objeto + agita` | Quiere ese objeto urgentemente |
| `palma_arriba + sonido_repetido` | Lleva rato pidiendo algo y no ha sido atendido |
| `[manana] palma_arriba + boca_abierta` | Quiere su desayuno |
| `[tarde] senala_externo + agita` | Quiere salir, está insistiendo |
| `[noche] palma_arriba + boca_abierta` | Quiere cenar antes de dormir |

### Patrón 3 — Estado emocional positivo

Activado cuando hay tokens de **E5 positivos** (`sonrie`, `abre_ojos`) o **E2 de afirmación** (`pulgar_arriba`, `apunta_si`, `cabeza_si`).

| Combinación | Frase generada |
|-------------|----------------|
| `sonrie + cabeza_si` | Está contento y de acuerdo |
| `aah + pulgar_arriba` | Se siente bien y está satisfecho |
| `sonrie + pulgar_arriba` | Está muy bien y feliz |
| `aah + sonrie` | Siente alivio y está contento |
| `cabeza_si + pulgar_arriba` | Confirma que sí, está de acuerdo |
| `sonrie + apunta_si` | Está feliz y confirma que eso es correcto |
| `[manana] sonrie + cabeza_si` | Está de buen humor esta mañana |
| `[tarde] aah + sonrie` | Está disfrutando y se siente bien |

### Patrón 4 — Estado emocional negativo

Activado cuando hay tokens de **E5 negativos** (`llanto`, `frunce_ceno`, `mira_abajo`) o **E1 de rechazo** (`bah`, `pff`, `uuh`).

| Combinación | Frase generada |
|-------------|----------------|
| `llanto + mira_abajo` | Está muy triste |
| `bah + aleja_cuerpo` | Rechaza algo y no quiere estar cerca |
| `frunce_ceno + cabeza_no` | Está disgustado y no quiere |
| `pff + palma_abajo` | No le importa y pide que paren |
| `mira_abajo + encoge_hombros` | Está decaído y no sabe qué decir |
| `uuh + aleja_cuerpo` | Siente malestar y quiere alejarse |
| `llanto + senala_propio` | Está triste por algo que le pasó a él |
| `[noche] mira_abajo + cierra_ojos` | Está cansado y triste, quiere descansar |

### Patrón 5 — Urgencia / llamado de atención

Activado cuando hay `agita`, `levanta_brazo`, `sonido_repetido`, `sonido_largo` o el operador `!`.

| Combinación | Frase generada |
|-------------|----------------|
| `agita + sonido_largo` | Necesita atención urgente |
| `levanta_brazo + sonido_largo` | Pide ayuda urgentemente |
| `sonido_repetido + agita` | Lleva tiempo sin ser atendido, es urgente |
| `ata + levanta_brazo` | Llama a alguien y pide ayuda |
| `agita + ata` | Llama urgentemente a alguien específico |
| `sonido_largo !` | ¡Necesita atención ahora mismo! |
| `levanta_brazo !` | ¡Pide ayuda urgente! |
| `[dolor] agita + sonido_largo !` | ¡Emergencia, tiene dolor y necesita ayuda ya! |

### Patrón 6 — Confirmación / respuesta

Activado cuando hay tokens de **E4 de afirmación/negación** (`cabeza_si`, `cabeza_no`) o **E2 de respuesta** (`pulgar_arriba`, `pulgar_abajo`, `apunta_si`).

| Combinación | Frase generada |
|-------------|----------------|
| `cabeza_si + pulgar_arriba` | Sí, está completamente de acuerdo |
| `cabeza_no + palma_abajo` | No quiere y pide que paren |
| `cabeza_lado + encoge_hombros` | No está seguro, le da igual |
| `pulgar_abajo + bah` | No quiere eso para nada |
| `apunta_si + cabeza_si` | Confirma que sí, eso es exactamente |
| `cabeza_no + aleja_cuerpo` | No quiere y se aleja |
| `pulgar_arriba + sonrie` | Está bien y feliz |
| `cabeza_lado + hmm` | Está dudando, no tiene claro |

### Patrón 7 — Cansancio / sueño

Activado cuando hay `cierra_ojos`, `sonido_grave`, `mira_abajo` o contexto `[noche]`.

| Combinación | Frase generada |
|-------------|----------------|
| `cierra_ojos + sonido_grave` | Tiene mucho sueño |
| `sonido_grave + mira_abajo` | Está muy cansado y decaído |
| `cierra_ojos + cabeza_lado` | Tiene sueño pero no está seguro de querer dormir |
| `[noche] cierra_ojos + sonido_grave` | Está listo para dormir |
| `[manana] cierra_ojos + cabeza_no` | No quiere levantarse todavía |
| `cierra_ojos + palma_abajo` | Quiere dormir y que lo dejen descansar |
| `sonido_grave + encoge_hombros` | Está cansado pero no sabe qué necesita |

### Patrón 8 — Hambre / sed

Activado cuando hay `boca_abierta`, `mira_objeto` en contexto de comida, o `palma_arriba` con contexto `[manana]` o `[noche]`.

| Combinación | Frase generada |
|-------------|----------------|
| `boca_abierta + senala` | Tiene hambre o sed y señala lo que quiere |
| `boca_abierta + mira_objeto` | Quiere comer o tomar lo que está mirando |
| `boca_abierta + palma_arriba` | Pide comida o bebida |
| `[manana] boca_abierta + palma_arriba` | Quiere su desayuno |
| `[tarde] boca_abierta + senala` | Quiere almorzar o merendar algo específico |
| `[noche] boca_abierta + mira_objeto` | Quiere cenar eso que está mirando |
| `boca_abierta + sonido_repetido` | Tiene mucha hambre o sed, lleva rato esperando |
| `boca_abierta + agita` | Tiene mucha hambre o sed y es urgente |

---

## Efectos de los operadores

### Operador `~` (negación)

Invierte el significado base o el override del token que le sigue.

| Expresión | Significado base del token | Con ~ |
|-----------|--------------------------|-------|
| `~sonrie` | Está contento | No está contento |
| `~cabeza_si` | Está de acuerdo | No está de acuerdo |
| `~palma_arriba` | Pide algo | No pide nada |
| `~pulgar_arriba` | Está bien | No está bien |
| `~cabeza_no` | No quiere | Sí quiere (doble negación) |
| `~sonido_suave` | Está tranquilo | No está tranquilo |

### Operador `!` (urgencia)

Agrega urgencia a toda la expresión. Cambia el tono de la frase generada.

| Expresión | Sin `!` | Con `!` |
|-----------|---------|---------|
| `sonido_largo` | Necesita atención | ¡Necesita atención ahora mismo! |
| `levanta_brazo` | Pide ayuda | ¡Pide ayuda urgente! |
| `[dolor] uff + frunce_ceno` | Está sufriendo con dolor | ¡Está sufriendo mucho, es urgente! |
| `agita + sonido_largo` | Necesita atención urgente | ¡Emergencia, atención inmediata! |
| `palma_arriba` | Pide algo | ¡Necesita algo ahora! |

### Operador `|` (alternativa)

El cuidador no está seguro entre dos gestos o la persona ofrece dos opciones.

| Expresión | Frase generada |
|-----------|----------------|
| `palma_arriba \| mira_objeto` | Parece que quiere algo, quizás ese objeto |
| `sonrie \| cabeza_si` | Parece que está de acuerdo o contento |
| `boca_abierta \| senala` | Parece que tiene hambre o quiere algo en esa dirección |
| `uff \| frunce_ceno` | Parece que está cansado o con dolor |
| `cierra_ojos \| sonido_grave` | Parece que tiene sueño |

### Modificadores E6 con tokens

| Expresión | Frase generada |
|-----------|----------------|
| `uff + doble` | Está muy cansado o frustrado |
| `sonido_largo + doble` | Necesita mucha atención, es importante |
| `llanto + triple` | Está llorando mucho, tristeza intensa |
| `uff + triple` | Está extremadamente cansado o sufriendo |
| `agita + rapido` | Urgencia extrema, necesita atención ya |
| `sonrie + lento` | Está un poco contento, tranquilo |
| `sonido_largo + rapido` | Necesita atención inmediata y rápida |
| `cabeza_si + doble` | Confirma con mucho énfasis que sí |
| `cabeza_no + doble` | Niega con mucho énfasis |

---

## Combinaciones complejas (múltiples patrones)

Expresiones que combinan varios patrones a la vez.

| Expresión completa | Frase generada |
|-------------------|----------------|
| `[dolor] ~sonrie + uff + sonido_largo !` | No está bien, está sufriendo mucho. ¡Necesita atención urgente! |
| `[manana] cierra_ojos + cabeza_no + uff` | No quiere levantarse, sigue con sueño y está molesto |
| `[noche] boca_abierta + mira_objeto + palma_arriba` | Quiere cenar eso que está mirando |
| `[dolor] ay + senala_propio + levanta_brazo !` | Le duele algo en su cuerpo. ¡Necesita ayuda ahora! |
| `sonrie + cabeza_si + pulgar_arriba` | Está muy contento y totalmente de acuerdo |
| `llanto + levanta_brazo + sonido_largo !` | Tiene dolor o tristeza intensa. ¡Pide ayuda urgente! |
| `agita + ata + sonido_largo` | Llama urgentemente a alguien, necesita atención |
| `[tarde] sonrie + acerca_cuerpo + apunta_si` | Está contento y quiere acercarse a eso, confirma que sí |
| `~sonrie + frunce_ceno + cabeza_no` | No está bien, tiene dolor o disgusto y rechaza algo |
| `boca_abierta + mira_objeto + agita + rapido` | Quiere urgentemente eso que está mirando |

---

## Resumen de cantidad de combinaciones cubiertas

| Tipo | Combinaciones documentadas |
|------|--------------------------|
| Significados base | 55 (uno por token) |
| Overrides por contexto | 43 (distribuidos en 4 contextos) |
| Patrones de combinación | 8 patrones · 68 combinaciones específicas |
| Efectos de operadores | 28 combinaciones con `~`, `!`, `\|`, modificadores E6 |
| Combinaciones complejas | 10 ejemplos multi-patrón |
| **Total documentado** | **~200+ frases distintas posibles** |

---

*Este documento es la base de datos del analizador semántico (`semantico.py`).*
*Cada combinación aquí documentada se implementa como una regla en el semántico.*
