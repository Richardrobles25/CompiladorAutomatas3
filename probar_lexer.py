from lexer import lexer, tokens, CONTEXTOS_VALIDOS

print("=" * 55)
print("  Probador del Analizador Léxico")
print("=" * 55)
print(f"  Tokens disponibles: {len(tokens)}")
print(f"  Contextos válidos:  {sorted(CONTEXTOS_VALIDOS)}")
print()
print("  Ejemplos de entrada:")
print("    mmm + palma_arriba")
print("    [manana] sonrie + cabeza_si")
print("    [dolor] uff + sonido_largo + doble")
print("    # comentario del cuidador")
print()
print("  Escribe 'salir' para terminar.")
print("=" * 55)

while True:
    try:
        entrada = input("\n> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nHasta luego.")
        break

    if not entrada:
        continue
    if entrada.lower() == 'salir':
        print("Hasta luego.")
        break

    lexer.input(entrada)
    lexer.lineno = 1
    toks = list(lexer)

    if not toks:
        print("  (ningún token válido producido)")
    else:
        print(f"  {'TIPO':<22} {'VALOR':<20} LÍNEA")
        print(f"  {'-'*22} {'-'*20} -----")
        for tok in toks:
            print(f"  {tok.type:<22} {tok.value!r:<20} {tok.lineno}")
        print(f"\n  Total: {len(toks)} token(s)")
