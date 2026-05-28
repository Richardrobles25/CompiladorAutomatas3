import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from lexer import lexer, CONTEXTOS_VALIDOS

# ── Datos de tokens por categoría ──────────────────────────────────────────

CATEGORIAS = [
    ("E1 · Sonidos vocales", "#3A86FF",
     ["mmm", "ata", "aah", "uuh", "oh", "shh",
      "hmm", "uff", "ay", "ana", "bah", "pff"]),

    ("E2 · Gestos de manos", "#8338EC",
     ["senala", "palma_arriba", "palma_abajo", "puno",
      "mano_abierta", "toca", "agita", "apunta_si",
      "junta_dedos", "separa_manos", "pulgar_arriba", "pulgar_abajo"]),

    ("E3 · Vocalizaciones", "#06D6A0",
     ["sonido_largo", "sonido_corto", "sonido_repetido",
      "sonido_agudo", "sonido_grave", "sonido_suave"]),

    ("E4 · Movimientos corporales", "#FB5607",
     ["cabeza_si", "cabeza_no", "cabeza_lado", "inclina_cuerpo",
      "acerca_cuerpo", "aleja_cuerpo", "senala_propio",
      "senala_externo", "encoge_hombros", "levanta_brazo"]),

    ("E5 · Expresiones faciales", "#FF006E",
     ["cierra_ojos", "abre_ojos", "frunce_ceno", "sonrie",
      "llanto", "boca_abierta", "mira_arriba", "mira_abajo",
      "mira_objeto", "parpadeo_rapido"]),

    ("E6 · Modificadores", "#6D6875",
     ["rapido", "lento", "doble", "triple", "pausa"]),
]

CONTEXTOS = ["manana", "tarde", "noche", "dolor"]

OPERADORES = [
    ("+",  "MAS     · secuencia",   "#3A86FF"),
    ("|",  "O       · alternativa", "#8338EC"),
    ("!",  "URGENTE · urgencia",    "#FF006E"),
    ("~",  "NEG     · negación",    "#FB5607"),
    (";",  "FIN     · nueva idea",  "#06D6A0"),
]

# ── Clase principal ─────────────────────────────────────────────────────────

class Interfaz:
    def __init__(self, root):
        self.root = root
        self.root.title("Compilador · Lenguaje de Comunicación Personal")
        self.root.configure(bg="#1A1A2E")
        self.root.resizable(True, True)

        self.contexto_activo = tk.StringVar(value="")
        self.expresion = []  # lista de strings que forman la entrada

        self._construir_ui()
        self.root.update_idletasks()
        self.root.minsize(1000, 680)

    # ── Construcción de la UI ───────────────────────────────────────────────

    def _construir_ui(self):
        # Título
        tk.Label(
            self.root, text="Compilador · Lenguaje de Comunicación Personal",
            font=("Segoe UI", 14, "bold"), bg="#1A1A2E", fg="#E0E0FF"
        ).pack(pady=(12, 4))
        tk.Label(
            self.root,
            text="El cuidador observa los gestos y sonidos · escribe los tokens · el compilador traduce",
            font=("Segoe UI", 9), bg="#1A1A2E", fg="#888AAA"
        ).pack(pady=(0, 10))

        # Cuerpo principal (izquierda + derecha)
        cuerpo = tk.Frame(self.root, bg="#1A1A2E")
        cuerpo.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        cuerpo.columnconfigure(0, weight=3)
        cuerpo.columnconfigure(1, weight=2)
        cuerpo.rowconfigure(0, weight=1)

        self._panel_tokens(cuerpo)
        self._panel_entrada(cuerpo)

    def _panel_tokens(self, parent):
        marco = tk.Frame(parent, bg="#16213E", bd=0)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(
            marco, text="Tokens disponibles",
            font=("Segoe UI", 10, "bold"), bg="#16213E", fg="#A0A8D0"
        ).pack(anchor="w", padx=12, pady=(10, 6))

        # Canvas + scrollbar para scroll vertical
        canvas = tk.Canvas(marco, bg="#16213E", highlightthickness=0)
        scroll = ttk.Scrollbar(marco, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        interior = tk.Frame(canvas, bg="#16213E")
        win_id = canvas.create_window((0, 0), window=interior, anchor="nw")

        def _ajustar(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win_id, width=e.width)

        interior.bind("<Configure>", _ajustar)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        for nombre, color, tokens in CATEGORIAS:
            self._seccion_tokens(interior, nombre, color, tokens)

    def _seccion_tokens(self, parent, nombre, color, tokens):
        marco = tk.Frame(parent, bg="#16213E")
        marco.pack(fill="x", padx=10, pady=(8, 2))

        # Encabezado de categoría
        tk.Frame(marco, bg=color, height=2).pack(fill="x")
        tk.Label(
            marco, text=nombre,
            font=("Segoe UI", 9, "bold"), bg="#16213E", fg=color
        ).pack(anchor="w", pady=(4, 4))

        # Botones en grilla
        grilla = tk.Frame(marco, bg="#16213E")
        grilla.pack(fill="x")
        col, max_col = 0, 4
        for token in tokens:
            tk.Button(
                grilla, text=token,
                font=("Consolas", 8),
                bg="#0F3460", fg="#E0E0FF",
                activebackground=color, activeforeground="white",
                relief="flat", bd=0, padx=6, pady=4,
                cursor="hand2",
                command=lambda t=token: self._agregar_token(t)
            ).grid(row=col // max_col, column=col % max_col,
                   padx=2, pady=2, sticky="ew")
            grilla.columnconfigure(col % max_col, weight=1)
            col += 1

    def _panel_entrada(self, parent):
        marco = tk.Frame(parent, bg="#16213E")
        marco.grid(row=0, column=1, sticky="nsew")

        # ── Sección contexto ──────────────────────────────────────
        tk.Label(marco, text="Contexto de la sesión",
                 font=("Segoe UI", 9, "bold"), bg="#16213E", fg="#A0A8D0"
                 ).pack(anchor="w", padx=12, pady=(10, 4))

        f_ctx = tk.Frame(marco, bg="#16213E")
        f_ctx.pack(fill="x", padx=12)
        colores_ctx = {"manana": "#FFB703", "tarde": "#FB8500",
                       "noche": "#023E8A", "dolor": "#D62828"}
        for ctx in CONTEXTOS:
            tk.Radiobutton(
                f_ctx, text=ctx, value=ctx,
                variable=self.contexto_activo,
                font=("Segoe UI", 9, "bold"),
                bg="#16213E", fg=colores_ctx[ctx],
                selectcolor="#0F3460",
                activebackground="#16213E",
                cursor="hand2",
            ).pack(side="left", padx=(0, 8))
        tk.Button(
            f_ctx, text="sin contexto",
            font=("Segoe UI", 8), bg="#16213E", fg="#555577",
            relief="flat", cursor="hand2",
            command=lambda: self.contexto_activo.set("")
        ).pack(side="left")

        # ── Expresión construida ──────────────────────────────────
        tk.Label(marco, text="Expresión",
                 font=("Segoe UI", 9, "bold"), bg="#16213E", fg="#A0A8D0"
                 ).pack(anchor="w", padx=12, pady=(14, 4))

        self.txt_expresion = tk.Text(
            marco, height=3,
            font=("Consolas", 11),
            bg="#0F3460", fg="#E0E0FF",
            insertbackground="white",
            relief="flat", padx=8, pady=6,
            wrap="word"
        )
        self.txt_expresion.pack(fill="x", padx=12)
        self.txt_expresion.bind("<KeyRelease>", self._sync_desde_texto)

        # ── Operadores ────────────────────────────────────────────
        tk.Label(marco, text="Operadores",
                 font=("Segoe UI", 9, "bold"), bg="#16213E", fg="#A0A8D0"
                 ).pack(anchor="w", padx=12, pady=(14, 4))

        f_ops = tk.Frame(marco, bg="#16213E")
        f_ops.pack(fill="x", padx=12)
        for simbolo, desc, color in OPERADORES:
            f = tk.Frame(f_ops, bg="#16213E")
            f.pack(side="left", padx=(0, 6))
            tk.Button(
                f, text=simbolo,
                font=("Consolas", 14, "bold"),
                bg="#0F3460", fg=color,
                activebackground=color, activeforeground="white",
                relief="flat", width=3, pady=4,
                cursor="hand2",
                command=lambda s=simbolo: self._agregar_operador(s)
            ).pack()
            tk.Label(f, text=desc, font=("Segoe UI", 7),
                     bg="#16213E", fg="#555577").pack()

        # ── Botones de acción ─────────────────────────────────────
        f_acc = tk.Frame(marco, bg="#16213E")
        f_acc.pack(fill="x", padx=12, pady=(14, 0))
        tk.Button(
            f_acc, text="⬛  Borrar todo",
            font=("Segoe UI", 9), bg="#2D2D44", fg="#AAAACC",
            relief="flat", padx=10, pady=6, cursor="hand2",
            command=self._borrar
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            f_acc, text="▶  Analizar léxico",
            font=("Segoe UI", 9, "bold"), bg="#3A86FF", fg="white",
            relief="flat", padx=14, pady=6, cursor="hand2",
            command=self._analizar
        ).pack(side="left")

        # ── Área de resultado ─────────────────────────────────────
        tk.Label(marco, text="Resultado del análisis léxico",
                 font=("Segoe UI", 9, "bold"), bg="#16213E", fg="#A0A8D0"
                 ).pack(anchor="w", padx=12, pady=(18, 4))

        self.txt_resultado = scrolledtext.ScrolledText(
            marco, height=10,
            font=("Consolas", 9),
            bg="#0A0A1A", fg="#00FF9F",
            insertbackground="white",
            relief="flat", padx=8, pady=6,
            state="disabled"
        )
        self.txt_resultado.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Tags para colorear la salida
        self.txt_resultado.tag_config("encabezado", foreground="#A0A8D0")
        self.txt_resultado.tag_config("error",      foreground="#FF006E")
        self.txt_resultado.tag_config("ok",         foreground="#00FF9F")
        self.txt_resultado.tag_config("dim",        foreground="#555577")

    # ── Lógica ──────────────────────────────────────────────────────────────

    def _agregar_token(self, token):
        actual = self.txt_expresion.get("1.0", "end-1c").strip()
        if actual and not actual.endswith(("+", "|", "~", ";")):
            self.txt_expresion.insert("end", " + ")
        self.txt_expresion.insert("end", token)
        self._sync_desde_texto()

    def _agregar_operador(self, simbolo):
        actual = self.txt_expresion.get("1.0", "end-1c").rstrip()
        if simbolo == "~":
            self.txt_expresion.delete("1.0", "end")
            self.txt_expresion.insert("end", actual + " ~" if actual else "~")
        elif simbolo == "!":
            self.txt_expresion.delete("1.0", "end")
            self.txt_expresion.insert("end", actual + " !" if actual else "")
        elif simbolo == ";":
            self.txt_expresion.insert("end", " ; ")
        else:
            self.txt_expresion.insert("end", f" {simbolo} ")
        self._sync_desde_texto()

    def _sync_desde_texto(self, _event=None):
        pass  # reservado para cuando el parser valide en tiempo real

    def _borrar(self):
        self.txt_expresion.delete("1.0", "end")
        self.contexto_activo.set("")
        self._escribir_resultado([("Expresión borrada.\n", "dim")])

    def _construir_entrada(self):
        expr = self.txt_expresion.get("1.0", "end-1c").strip()
        ctx  = self.contexto_activo.get()
        if ctx:
            return f"[{ctx}] {expr}" if expr else f"[{ctx}]"
        return expr

    def _analizar(self):
        entrada = self._construir_entrada()
        if not entrada:
            self._escribir_resultado([("No hay nada que analizar.\n", "error")])
            return

        errores = []
        _print_orig = __builtins__["print"] if isinstance(__builtins__, dict) else print

        # Captura los mensajes de error del lexer
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            lexer.input(entrada)
            lexer.lineno = 1
            toks = list(lexer)
        salida_lexer = buf.getvalue()

        lineas = []
        lineas.append((f"Entrada:  {entrada}\n", "encabezado"))
        lineas.append(("-" * 42 + "\n", "dim"))

        if salida_lexer.strip():
            for err in salida_lexer.strip().splitlines():
                lineas.append((err + "\n", "error"))
            lineas.append(("-" * 42 + "\n", "dim"))

        if toks:
            lineas.append((f"{'TIPO':<22} {'VALOR':<18} LÍNEA\n", "dim"))
            lineas.append((f"{'─'*22} {'─'*18} ─────\n", "dim"))
            for tok in toks:
                linea = f"{tok.type:<22} {repr(tok.value):<18} {tok.lineno}\n"
                lineas.append((linea, "ok"))
            lineas.append(("-" * 42 + "\n", "dim"))
            lineas.append((f"Total: {len(toks)} token(s)\n", "encabezado"))
        else:
            lineas.append(("No se produjeron tokens válidos.\n", "error"))

        lineas.append(("\n⚙ Parser y semántico: pendiente (Etapa 3)\n", "dim"))
        self._escribir_resultado(lineas)

    def _escribir_resultado(self, lineas):
        self.txt_resultado.configure(state="normal")
        self.txt_resultado.delete("1.0", "end")
        for texto, tag in lineas:
            self.txt_resultado.insert("end", texto, tag)
        self.txt_resultado.configure(state="disabled")


# ── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = Interfaz(root)
    root.mainloop()
