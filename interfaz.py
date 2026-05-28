import tkinter as tk
from tkinter import ttk, scrolledtext
import sys, os, io, contextlib

sys.path.insert(0, os.path.dirname(__file__))
sys.stdout.reconfigure(encoding='utf-8')

from lexer    import lexer, CONTEXTOS_VALIDOS
from sintactico import analizar, imprimir_ast
from semantico  import compilar

# ── Datos de tokens por categoría ───────────────────────────────────────────

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
    ("+", "MAS · secuencia",   "#3A86FF"),
    ("|", "O · alternativa",   "#8338EC"),
    ("!", "URGENTE · urgencia","#FF006E"),
    ("~", "NEG · negación",    "#FB5607"),
    (";", "FIN · nueva idea",  "#06D6A0"),
]

# ── Clase principal ──────────────────────────────────────────────────────────

class Interfaz:
    def __init__(self, root):
        self.root = root
        self.root.title("Compilador · Lenguaje de Comunicación Personal")
        self.root.configure(bg="#1A1A2E")
        self.root.resizable(True, True)
        self.contexto_activo = tk.StringVar(value="")
        self._construir_ui()
        self.root.update_idletasks()
        # Ajustar al 90% de la pantalla disponible, sin sobrepasar
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w  = min(1100, int(sw * 0.90))
        h  = min(720,  int(sh * 0.90))
        x  = (sw - w) // 2
        y  = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(700, 500)

    # ── UI ───────────────────────────────────────────────────────────────────

    def _construir_ui(self):
        tk.Label(self.root,
                 text="Compilador · Lenguaje de Comunicación Personal",
                 font=("Segoe UI", 11, "bold"), bg="#1A1A2E", fg="#E0E0FF"
                 ).pack(pady=(6, 1))
        tk.Label(self.root,
                 text="El cuidador observa · escribe los tokens · el compilador traduce",
                 font=("Segoe UI", 8), bg="#1A1A2E", fg="#888AAA"
                 ).pack(pady=(0, 4))

        cuerpo = tk.Frame(self.root, bg="#1A1A2E")
        cuerpo.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        cuerpo.columnconfigure(0, weight=3)
        cuerpo.columnconfigure(1, weight=4)
        cuerpo.rowconfigure(0, weight=1)

        self._panel_tokens(cuerpo)
        self._panel_derecho(cuerpo)

    # ── Panel izquierdo: tokens ──────────────────────────────────────────────

    def _panel_tokens(self, parent):
        marco = tk.Frame(parent, bg="#16213E")
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        tk.Label(marco, text="Tokens disponibles",
                 font=("Segoe UI", 9, "bold"), bg="#16213E", fg="#A0A8D0"
                 ).pack(anchor="w", padx=8, pady=(6, 4))

        canvas = tk.Canvas(marco, bg="#16213E", highlightthickness=0)
        scroll = ttk.Scrollbar(marco, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        interior = tk.Frame(canvas, bg="#16213E")
        win_id = canvas.create_window((0, 0), window=interior, anchor="nw")

        interior.bind("<Configure>", lambda e: (
            canvas.configure(scrollregion=canvas.bbox("all")),
            canvas.itemconfig(win_id, width=e.width)
        ))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        for nombre, color, tokens in CATEGORIAS:
            self._seccion_tokens(interior, nombre, color, tokens)

    def _seccion_tokens(self, parent, nombre, color, tokens):
        marco = tk.Frame(parent, bg="#16213E")
        marco.pack(fill="x", padx=6, pady=(5, 1))
        tk.Frame(marco, bg=color, height=2).pack(fill="x")
        tk.Label(marco, text=nombre, font=("Segoe UI", 8, "bold"),
                 bg="#16213E", fg=color).pack(anchor="w", pady=(2, 2))
        grilla = tk.Frame(marco, bg="#16213E")
        grilla.pack(fill="x")
        col, max_col = 0, 4
        for token in tokens:
            tk.Button(grilla, text=token, font=("Consolas", 7),
                      bg="#0F3460", fg="#E0E0FF",
                      activebackground=color, activeforeground="white",
                      relief="flat", bd=0, padx=4, pady=2, cursor="hand2",
                      command=lambda t=token: self._agregar_token(t)
                      ).grid(row=col//max_col, column=col%max_col,
                             padx=1, pady=1, sticky="ew")
            grilla.columnconfigure(col % max_col, weight=1)
            col += 1

    # ── Panel derecho: entrada + resultados ──────────────────────────────────

    def _panel_derecho(self, parent):
        marco = tk.Frame(parent, bg="#16213E")
        marco.grid(row=0, column=1, sticky="nsew")
        marco.rowconfigure(3, weight=1)
        marco.columnconfigure(0, weight=1)

        # Contexto
        tk.Label(marco, text="Contexto de la sesión",
                 font=("Segoe UI", 8, "bold"), bg="#16213E", fg="#A0A8D0"
                 ).grid(row=0, column=0, sticky="w", padx=8, pady=(6, 2))
        f_ctx = tk.Frame(marco, bg="#16213E")
        f_ctx.grid(row=1, column=0, sticky="w", padx=8)
        colores_ctx = {"manana":"#FFB703","tarde":"#FB8500","noche":"#4CC9F0","dolor":"#D62828"}
        for ctx in CONTEXTOS:
            tk.Radiobutton(f_ctx, text=ctx, value=ctx,
                           variable=self.contexto_activo,
                           font=("Segoe UI", 8, "bold"),
                           bg="#16213E", fg=colores_ctx[ctx],
                           selectcolor="#0F3460", activebackground="#16213E",
                           cursor="hand2"
                           ).pack(side="left", padx=(0, 6))
        tk.Button(f_ctx, text="sin contexto",
                  font=("Segoe UI", 7), bg="#16213E", fg="#555577",
                  relief="flat", cursor="hand2",
                  command=lambda: self.contexto_activo.set("")
                  ).pack(side="left")

        # Expresión + operadores + botones en un subframe
        f_entrada = tk.Frame(marco, bg="#16213E")
        f_entrada.grid(row=2, column=0, sticky="ew", padx=8, pady=(6, 0))
        f_entrada.columnconfigure(0, weight=1)

        tk.Label(f_entrada, text="Expresión",
                 font=("Segoe UI", 8, "bold"), bg="#16213E", fg="#A0A8D0"
                 ).grid(row=0, column=0, sticky="w")
        self.txt_expresion = tk.Text(f_entrada, height=2,
                                     font=("Consolas", 10),
                                     bg="#0F3460", fg="#E0E0FF",
                                     insertbackground="white",
                                     relief="flat", padx=6, pady=4, wrap="word")
        self.txt_expresion.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        # Operadores
        f_ops = tk.Frame(f_entrada, bg="#16213E")
        f_ops.grid(row=2, column=0, sticky="w", pady=(5, 0))
        for simbolo, desc, color in OPERADORES:
            f = tk.Frame(f_ops, bg="#16213E")
            f.pack(side="left", padx=(0, 4))
            tk.Button(f, text=simbolo, font=("Consolas", 11, "bold"),
                      bg="#0F3460", fg=color,
                      activebackground=color, activeforeground="white",
                      relief="flat", width=3, pady=2, cursor="hand2",
                      command=lambda s=simbolo: self._agregar_operador(s)
                      ).pack()
            tk.Label(f, text=desc, font=("Segoe UI", 6),
                     bg="#16213E", fg="#555577").pack()

        # Botones compilar / borrar
        f_acc = tk.Frame(f_entrada, bg="#16213E")
        f_acc.grid(row=3, column=0, sticky="w", pady=(6, 0))
        tk.Button(f_acc, text="  Borrar todo",
                  font=("Segoe UI", 8), bg="#2D2D44", fg="#AAAACC",
                  relief="flat", padx=8, pady=4, cursor="hand2",
                  command=self._borrar
                  ).pack(side="left", padx=(0, 6))
        tk.Button(f_acc, text="▶  Compilar",
                  font=("Segoe UI", 9, "bold"), bg="#3A86FF", fg="white",
                  relief="flat", padx=12, pady=4, cursor="hand2",
                  command=self._compilar
                  ).pack(side="left")

        # ── Frase traducida (prominente) ──────────────────────────
        f_frase = tk.Frame(marco, bg="#0F3460", pady=5)
        f_frase.grid(row=3, column=0, sticky="ew", padx=8, pady=(8, 0))
        f_frase.columnconfigure(0, weight=1)
        tk.Label(f_frase, text="TRADUCCIÓN",
                 font=("Segoe UI", 7, "bold"), bg="#0F3460", fg="#A0A8D0"
                 ).grid(row=0, column=0, sticky="w", padx=8)
        self.lbl_frase = tk.Label(f_frase, text="— escribe una expresión y presiona Compilar —",
                                  font=("Segoe UI", 10), bg="#0F3460", fg="#FFD166",
                                  wraplength=480, justify="left")
        self.lbl_frase.grid(row=1, column=0, sticky="ew", padx=8, pady=(1, 4))

        # ── Área de fases (tabs) ──────────────────────────────────
        notebook = ttk.Notebook(marco)
        notebook.grid(row=4, column=0, sticky="nsew", padx=8, pady=(6, 8))
        marco.rowconfigure(4, weight=1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook",        background="#16213E", borderwidth=0)
        style.configure("TNotebook.Tab",    background="#0F3460", foreground="#A0A8D0",
                         font=("Segoe UI", 9), padding=[10, 4])
        style.map("TNotebook.Tab",
                  background=[("selected", "#3A86FF")],
                  foreground=[("selected", "white")])

        def _tab(etiqueta, fg):
            f = tk.Frame(notebook, bg="#0A0A1A")
            t = scrolledtext.ScrolledText(f, font=("Consolas", 9),
                                          bg="#0A0A1A", fg=fg,
                                          relief="flat", padx=8, pady=6,
                                          state="disabled")
            t.pack(fill="both", expand=True)
            t.tag_config("titulo",    foreground="#A0A8D0", font=("Segoe UI", 9, "bold"))
            t.tag_config("error",     foreground="#FF006E")
            t.tag_config("ok",        foreground=fg)
            t.tag_config("dim",       foreground="#555577")
            t.tag_config("frase_tab", foreground="#FFD166",
                          font=("Segoe UI", 10, "bold"))
            notebook.add(f, text=etiqueta)
            return t

        self.tab_lexico    = _tab("  Fase 1 · Léxico  ",    "#00FF9F")
        self.tab_sintactico = _tab("  Fase 2 · Sintáctico  ", "#4CC9F0")
        self.tab_semantico  = _tab("  Fase 3 · Semántico  ",  "#FFD166")

    # ── Lógica ───────────────────────────────────────────────────────────────

    def _agregar_token(self, token):
        actual = self.txt_expresion.get("1.0", "end-1c").strip()
        if actual and not actual.endswith(("+", "|", "~", ";")):
            self.txt_expresion.insert("end", " + ")
        self.txt_expresion.insert("end", token)

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

    def _borrar(self):
        self.txt_expresion.delete("1.0", "end")
        self.contexto_activo.set("")
        self.lbl_frase.config(text="— escribe una expresión y presiona Compilar —")
        for tab in (self.tab_lexico, self.tab_sintactico, self.tab_semantico):
            self._escribir(tab, [("Borrado.\n", "dim")])

    def _construir_entrada(self):
        expr = self.txt_expresion.get("1.0", "end-1c").strip()
        ctx  = self.contexto_activo.get()
        if ctx:
            return f"[{ctx}] {expr}" if expr else f"[{ctx}]"
        return expr

    def _compilar(self):
        entrada = self._construir_entrada()
        if not entrada:
            self.lbl_frase.config(text="⚠ No hay nada que compilar.")
            return

        buf = io.StringIO()

        # ── FASE 1: Léxico ────────────────────────────────────────
        with contextlib.redirect_stdout(buf):
            lexer.input(entrada)
            lexer.lineno = 1
            toks = list(lexer)
        errores_lexico = buf.getvalue(); buf.truncate(0); buf.seek(0)

        lineas_lex = []
        lineas_lex.append((f"Entrada: {entrada}\n", "titulo"))
        lineas_lex.append(("─" * 48 + "\n", "dim"))
        if errores_lexico.strip():
            for e in errores_lexico.strip().splitlines():
                lineas_lex.append((e + "\n", "error"))
            lineas_lex.append(("─" * 48 + "\n", "dim"))
        if toks:
            lineas_lex.append((f"{'TIPO':<24} {'VALOR':<18} LÍNEA\n", "dim"))
            lineas_lex.append(("─"*24 + " " + "─"*18 + " ─────\n", "dim"))
            for tok in toks:
                lineas_lex.append((f"{tok.type:<24} {repr(tok.value):<18} {tok.lineno}\n", "ok"))
            lineas_lex.append(("─" * 48 + "\n", "dim"))
            lineas_lex.append((f"Total: {len(toks)} token(s)\n", "titulo"))
        else:
            lineas_lex.append(("No se produjeron tokens válidos.\n", "error"))
        self._escribir(self.tab_lexico, lineas_lex)

        # ── FASE 2: Sintáctico ────────────────────────────────────
        with contextlib.redirect_stdout(buf):
            ast = analizar(entrada)
        errores_sint = buf.getvalue(); buf.truncate(0); buf.seek(0)

        lineas_sint = []
        lineas_sint.append((f"Entrada: {entrada}\n", "titulo"))
        lineas_sint.append(("─" * 48 + "\n", "dim"))
        if errores_sint.strip():
            for e in errores_sint.strip().splitlines():
                lineas_sint.append((e + "\n", "error"))
            lineas_sint.append(("─" * 48 + "\n", "dim"))
        if ast:
            lineas_sint.append(("AST (Árbol de Sintaxis Abstracta):\n", "titulo"))
            lineas_sint.append(("\n", "dim"))
            buf_ast = io.StringIO()
            with contextlib.redirect_stdout(buf_ast):
                imprimir_ast(ast)
            for linea in buf_ast.getvalue().splitlines():
                lineas_sint.append((linea + "\n", "ok"))
        else:
            lineas_sint.append(("No se pudo construir el AST.\n", "error"))
        self._escribir(self.tab_sintactico, lineas_sint)

        # ── FASE 3: Semántico ─────────────────────────────────────
        with contextlib.redirect_stdout(buf):
            frases = compilar(entrada)
        errores_sem = buf.getvalue()

        lineas_sem = []
        lineas_sem.append((f"Entrada: {entrada}\n", "titulo"))
        lineas_sem.append(("─" * 48 + "\n", "dim"))
        if errores_sem.strip():
            for e in errores_sem.strip().splitlines():
                lineas_sem.append((e + "\n", "error"))
            lineas_sem.append(("─" * 48 + "\n", "dim"))

        if frases and frases[0] != 'Error: no se pudo analizar la entrada.':
            for i, f in enumerate(frases, 1):
                if len(frases) > 1:
                    lineas_sem.append((f"Expresión {i}:\n", "dim"))
                lineas_sem.append((f"{f}\n", "frase_tab"))
            # Actualizar label prominente
            texto_label = "\n".join(frases)
            self.lbl_frase.config(text=texto_label)
        else:
            lineas_sem.append(("No se pudo generar la frase.\n", "error"))
            self.lbl_frase.config(text="⚠ Error al generar la traducción.")

        self._escribir(self.tab_semantico, lineas_sem)

    def _escribir(self, widget, lineas):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        for texto, tag in lineas:
            widget.insert("end", texto, tag)
        widget.configure(state="disabled")


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = Interfaz(root)
    root.mainloop()
