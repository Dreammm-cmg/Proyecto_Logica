"""
=============================================================================
INSTITUTO TECNOLOGICO DE ESTUDIOS SUPERIORES Y DE OCCIDENTE (ITESO)
INGENIERIA EN CIBERSEGURIDAD
MATERIA: LOGICA DISCRETA Y ESTRUCTURAS
 
PROYECTO INTEGRADOR — LyED TOOLKIT
  PARTE I : Suite de Validación Lógica  
  PARTE II: Calculadora de Teoría de Conjuntos
 
AUTORES: GUSTAVO ADRIAN JOYA RODRIGUEZ, JESÚS DANIEL MARÍN TERRAZAS, SEBASTIAN CASTILLO MARTINEZ.
FECHA: Febrero-Abril 2026
=============================================================================
FIXES APLICADOS (Parte I):
  [FIX 1] OR con regex \bv\b para no romper variables llamadas 'v'.
  [FIX 2] Bicondicional <-> múltiple manejado recursivamente.
  [FIX 3] sympify con locals explícitos (e, i, n… son variables, no constantes).
  [FIX 4] Lógica muerta de columnas eliminada; peso real en tautología.
  [FIX 5] _parent_canvas envuelto en try/except para compatibilidad de versión.
 
NUEVO (Parte II — Teoría de Conjuntos):
  • Manejo dinámico de conjuntos (cantidad ilimitada → BONO +10).
  • Carga desde archivos .txt (un elemento por línea).
  • Elementos alfanuméricos y anidados a 2 niveles: {a, {b,c}}.
  • Operaciones: Unión, Intersección, Diferencia, Diferencia Simétrica, Complemento.
  • Modo guiado (dropdowns) y modo expresión libre (A | B - C ^ D).
  • Tabla de pertenencia por elemento en el resultado.
=============================================================================
"""
 
import re
import customtkinter as ctk
import sympy
import itertools
from sympy.core.sympify import SympifyError
from tkinter import filedialog, messagebox
 
# =============================================================================
# CONFIGURACION VISUAL GLOBAL
# =============================================================================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")
 
# =============================================================================
# ███████████  MODULO LOGICA PROPOSICIONAL — BACKEND  █████████████████████████
# =============================================================================
 
_LOCALS_PROPOSICIONALES = {c: sympy.Symbol(c) for c in 'abcdefghijklmnopqrstuvwxyz'}
 
 
def traducir_a_sympy(expresion):
    exp = expresion.lower()
    # FIX 2: bicondicional múltiple — recursivo sobre primera ocurrencia
    if "<->" in exp:
        idx = exp.index("<->")
        lado_a = traducir_a_sympy(exp[:idx].strip())
        lado_b = traducir_a_sympy(exp[idx + 3:].strip())
        return f"({lado_a} >> {lado_b}) & ({lado_b} >> {lado_a})"
    exp = exp.replace("->", ">>")
    # FIX 1: OR como palabra aislada, no cualquier letra 'v'
    exp = re.sub(r'\bv\b', '|', exp)
    exp = exp.replace("^", "&")
    return exp
 
 
def _sympify_seguro(texto_sympy):
    # FIX 3: locals explícitos para que e, i, n, etc. sean Variables
    return sympy.sympify(texto_sympy, locals=_LOCALS_PROPOSICIONALES)
 
 
def validar_y_extraer_vars(texto_caja):
    if not texto_caja:
        return set()
    texto_sympy = traducir_a_sympy(texto_caja)
    try:
        expr = _sympify_seguro(texto_sympy)
        return {str(s) for s in expr.free_symbols}
    except Exception:
        raise ValueError(f"Error de Sintaxis en '{texto_caja}': Revisa operadores faltantes.")
 
 
def generar_tabla_verdad(variables):
    return list(itertools.product([True, False], repeat=len(variables)))
 
 
def evaluar_logica_renglon_critico(hipotesis, conclusion, valores_diccionario):
    resultados_h = []
    es_critico = True
    for h in hipotesis:
        expr = _sympify_seguro(traducir_a_sympy(h))
        val = bool(expr.subs(valores_diccionario))
        resultados_h.append(val)
        if not val:
            es_critico = False
    expr_c = _sympify_seguro(traducir_a_sympy(conclusion))
    val_c = bool(expr_c.subs(valores_diccionario))
    return resultados_h, val_c, es_critico
 
 
def evaluar_logica_tautologia(hipotesis, conclusion, variables, tabla):
    gran_hip = " & ".join(f"({traducir_a_sympy(h)})" for h in hipotesis)
    concl = f"({traducir_a_sympy(conclusion)})"
    formula_str = f"({gran_hip}) >> {concl}"
    expr_final = _sympify_seguro(formula_str)
    matriz = []
    es_tautologia = True
    for fila in tabla:
        vals = dict(zip(variables, fila))
        resultado = bool(expr_final.subs(vals))
        fila_datos = ['V' if v else 'F' for v in fila]
        fila_datos.append("VERDADERO" if resultado else "FALSO (FALLA)")
        if not resultado:
            es_tautologia = False
        matriz.append(fila_datos)
    return formula_str, matriz, es_tautologia
 
 
# =============================================================================
# ███████████  MODULO TEORIA DE CONJUNTOS — BACKEND  ██████████████████████████
# =============================================================================
 
def parse_elemento(s: str):
    """Convierte una línea de texto en elemento: str o frozenset (anidado a 2 niveles)."""
    s = s.strip()
    if s.startswith('{') and s.endswith('}'):
        interior = s[1:-1]
        partes = [p.strip() for p in interior.split(',') if p.strip()]
        return frozenset(partes)
    return s
 
 
def cargar_conjunto_desde_texto(texto: str) -> set:
    """Parsea texto multilínea en un set Python con soporte de anidamiento."""
    resultado = set()
    for linea in texto.strip().splitlines():
        linea = linea.strip()
        if linea and not linea.startswith('#'):
            resultado.add(parse_elemento(linea))
    return resultado
 
 
def formatear_elemento(e) -> str:
    """Representación legible de un elemento (frozenset → {a, b})."""
    if isinstance(e, frozenset):
        return '{' + ', '.join(sorted(str(x) for x in e)) + '}'
    return str(e)
 
 
def formatear_conjunto(s: set) -> str:
    """Representación legible de un conjunto completo."""
    if not s:
        return '∅'
    return '{' + ', '.join(sorted(formatear_elemento(e) for e in s)) + '}'
 
 
def evaluar_expresion_conjuntos(expr_str: str, conjuntos: dict) -> set:
    """
    Evalúa una expresión de conjuntos de forma segura.
    Operadores soportados:
      | / union       → Unión
      & / inter       → Intersección
      -  / diff       → Diferencia
      ^  / symdiff    → Diferencia simétrica
      ~X              → Complemento (U - X)
    """
    expr = expr_str.strip()
    expr = re.sub(r'\bunion\b',   '|', expr, flags=re.IGNORECASE)
    expr = re.sub(r'\binter\b',   '&', expr, flags=re.IGNORECASE)
    expr = re.sub(r'\bsymdiff\b', '^', expr, flags=re.IGNORECASE)
    expr = re.sub(r'\bdiff\b',    '-', expr, flags=re.IGNORECASE)
    # Complemento: ~X  →  (U-X)
    expr = re.sub(r'~(\w+)', lambda m: f'(U-{m.group(1)})', expr)
 
    namespace = {nombre: valor for nombre, valor in conjuntos.items()}
    try:
        resultado = eval(expr, {"__builtins__": {}}, namespace)  # noqa: S307
    except KeyError as e:
        raise ValueError(f"Conjunto no definido: {e}")
    except SyntaxError:
        raise ValueError("Sintaxis inválida en la expresión.")
    except Exception as e:
        raise ValueError(f"Error evaluando expresión: {e}")
 
    if not isinstance(resultado, (set, frozenset)):
        raise ValueError("La expresión no produjo un conjunto válido.")
    return set(resultado)
 
 
def operacion_guiada(conj_a: set, conj_b: set, operacion: str) -> tuple:
    """Ejecuta operación binaria y devuelve (resultado, símbolo)."""
    ops = {
        "Unión (A ∪ B)":                (conj_a | conj_b, "∪"),
        "Intersección (A ∩ B)":         (conj_a & conj_b, "∩"),
        "Diferencia (A − B)":           (conj_a - conj_b, "−"),
        "Diferencia Simétrica (A △ B)": (conj_a ^ conj_b, "△"),
    }
    if operacion not in ops:
        raise ValueError(f"Operación desconocida: {operacion}")
    return ops[operacion]
 
 
# =============================================================================
# ████████████████████  INTERFAZ GRÁFICA — LyED TOOLKIT  ██████████████████████
# =============================================================================
 
class SuiteLogica(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LyED ToolKit — ITESO Ciberseguridad")
        self.geometry("1200x820")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
 
        # Estado animación (lógica proposicional)
        self.animacion_activa = False
        self.id_animacion = None
 
        # ── TABS PRINCIPALES ──────────────────────────────────────────────────
        self.tabs = ctk.CTkTabview(self, anchor="nw")
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
 
        self.tab_logica    = self.tabs.add("⊢  Lógica Proposicional")
        self.tab_conjuntos = self.tabs.add("∪  Teoría de Conjuntos")
 
        self._construir_tab_logica()
        self._construir_tab_conjuntos()
 
    # =========================================================================
    #  TAB 1 — LÓGICA PROPOSICIONAL
    # =========================================================================
 
    def _construir_tab_logica(self):
        tab = self.tab_logica
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)
 
        # Panel izquierdo — entradas
        self.panel_input = ctk.CTkFrame(tab, width=320)
        self.panel_input.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
 
        ctk.CTkLabel(self.panel_input, text="HIPOTESIS (Max 10)",
                     font=("Arial", 16, "bold")).pack(pady=10)
        self.inputs_h = []
        for i in range(10):
            e = ctk.CTkEntry(self.panel_input,
                             placeholder_text=f"Hipotesis {i+1} (Ej: p -> q)", width=280)
            e.pack(pady=3)
            self.inputs_h.append(e)
 
        ctk.CTkLabel(self.panel_input, text="CONCLUSION",
                     font=("Arial", 14, "bold")).pack(pady=10)
        self.input_c = ctk.CTkEntry(self.panel_input, width=280, placeholder_text="Ej: r")
        self.input_c.pack()
 
        ctk.CTkButton(self.panel_input, text="Validar por Renglon Critico",
                      command=self.ejecutar_rc).pack(pady=(20, 5))
        ctk.CTkButton(self.panel_input, text="Validar por Tautologia",
                      fg_color="orange", hover_color="#cc8400",
                      command=self.ejecutar_tau).pack(pady=5)
        ctk.CTkButton(self.panel_input, text="📘 Ver Formulario / Leyes",
                      fg_color="#3B8ED0", hover_color="#36719F",
                      command=self.abrir_formulario).pack(pady=20)
        ctk.CTkButton(self.panel_input, text="Limpiar Todo",
                      fg_color="gray", hover_color="#444",
                      command=self.limpiar).pack(pady=5)
 
        # Panel derecho — resultados
        self.panel_res = ctk.CTkFrame(tab)
        self.panel_res.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.panel_res.grid_rowconfigure(1, weight=1)
        self.panel_res.grid_columnconfigure(0, weight=1)
 
        self.lbl_titulo_tabla = ctk.CTkLabel(
            self.panel_res, text="TABLA DE VERDAD Y ANALISIS", font=("Arial", 16, "bold"))
        self.lbl_titulo_tabla.grid(row=0, column=0, pady=5)
 
        self.frame_tabla = ctk.CTkScrollableFrame(self.panel_res, fg_color="#1E1E1E")
        self.frame_tabla.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
 
        self.lbl_veredicto = ctk.CTkLabel(
            self.panel_res, text="ESPERANDO DATOS...", font=("Arial", 20, "bold"))
        self.lbl_veredicto.grid(row=2, column=0, pady=20)
 
    # ── MOTOR VHS ─────────────────────────────────────────────────────────────
 
    def cancelar_animacion(self):
        if self.id_animacion is not None:
            self.after_cancel(self.id_animacion)
            self.animacion_activa = False
 
    def iniciar_renderizado_vhs(self, encabezados, matriz_datos, veredicto_texto, veredicto_color):
        self.cancelar_animacion()
        self.animacion_activa = True
        self.set_veredicto("CALCULANDO...", "gray")
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()
 
        # FIX 4: peso real en última columna de tautología
        es_tautologia = "RESULTADO SUPER-FORMULA" in encabezados
        for i in range(len(encabezados)):
            w = 5 if (es_tautologia and i == len(encabezados) - 1) else 1
            self.frame_tabla.grid_columnconfigure(i, weight=w)
 
        for col_idx, texto in enumerate(encabezados):
            lbl = ctk.CTkLabel(self.frame_tabla, text=texto, font=("Arial", 14, "bold"),
                               fg_color="#333333", corner_radius=5, pady=5)
            lbl.grid(row=0, column=col_idx, padx=2, pady=2, sticky="nsew")
 
        self.dibujar_fila_con_delay(matriz_datos, 0, veredicto_texto, veredicto_color)
 
    def dibujar_fila_con_delay(self, matriz_datos, row_idx, veredicto_texto, veredicto_color):
        if not self.animacion_activa:
            return
        if row_idx >= len(matriz_datos):
            self.animacion_activa = False
            self.set_veredicto(veredicto_texto, veredicto_color)
            return
 
        fila = matriz_datos[row_idx]
        bg_color = "#252525" if row_idx % 2 == 0 else "#2A2A2A"
 
        for col_idx, valor in enumerate(fila):
            valor_str = str(valor)
            color_texto = "white"
            if valor_str in ('V', 'VERDADERO'):          color_texto = "#2CC985"
            elif valor_str == 'F' or "FALSO" in valor_str: color_texto = "#FF5555"
            elif "CRITICO" in valor_str:                  color_texto = "#F39C12"
 
            lbl = ctk.CTkLabel(self.frame_tabla, text=valor_str, text_color=color_texto,
                               font=("Consolas", 14, "bold"), fg_color=bg_color, corner_radius=3)
            lbl.grid(row=row_idx + 1, column=col_idx, padx=2, pady=2, sticky="nsew")
 
        # FIX 5: _parent_canvas protegido con try/except
        try:
            self.frame_tabla._parent_canvas.yview_moveto(1.0)
        except AttributeError:
            pass
 
        self.id_animacion = self.after(
            100, self.dibujar_fila_con_delay,
            matriz_datos, row_idx + 1, veredicto_texto, veredicto_color)
 
    # ── LÓGICA DE CONTROL (Tab 1) ─────────────────────────────────────────────
 
    def abrir_formulario(self):
        win = ctk.CTkToplevel(self)
        win.title("Formulario de Logica Proposicional")
        win.geometry("600x700")
        leyes = """
=== 1. EQUIVALENCIAS LOGICAS (Teorema 2.1.1) ===
Simbolos App:  ~ (Negacion), v (OR), ^ (AND), -> (Implica), <-> (Si y solo si)
 
NOTA: La 'v' como OR debe estar separada por espacios: "p v q".
      Gracias al parser regex, 'v' como variable también es válida.
 
1. Conmutativas:   p ^ q ≡ q ^ p  |  p v q ≡ q v p
2. Asociativas:    (p^q)^r ≡ p^(q^r)  |  (pvq)vr ≡ pv(qvr)
3. Distributivas:  p^(qvr) ≡ (p^q)v(p^r)
4. De Morgan:      ~(p^q) ≡ ~pv~q  |  ~(pvq) ≡ ~p^~q
5. Doble Negacion: ~(~p) ≡ p
6. Implicacion:    p->q ≡ ~pvq
7. Bicondicional:  p<->q ≡ (p->q)^(q->p)
 
=== 2. REGLAS DE INFERENCIA ===
Modus Ponens:   H1: p->q  H2: p   ⊢  q
Modus Tollens:  H1: p->q  H2: ~q  ⊢  ~p
Silogismo Hip.: H1: p->q  H2: q->r ⊢ p->r
"""
        txt = ctk.CTkTextbox(win, font=("Consolas", 14))
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        txt.insert("0.0", leyes)
        txt.configure(state="disabled")
 
    def obtener_datos_seguro(self):
        raw_h = [e.get().strip() for e in self.inputs_h if e.get().strip()]
        raw_c = self.input_c.get().strip()
        if not raw_h:
            self.mostrar_error("Error: Escribe al menos una hipotesis.")
            return None, None, None
        if not raw_c:
            self.mostrar_error("Error: Falta la conclusion.")
            return None, None, None
        vars_tot = set()
        try:
            for h in raw_h:
                vars_tot.update(validar_y_extraer_vars(h))
            vars_tot.update(validar_y_extraer_vars(raw_c))
        except ValueError as e:
            self.mostrar_error(str(e))
            return None, None, None
        if not vars_tot:
            self.mostrar_error("Error: No encontré variables.")
            return None, None, None
        return raw_h, raw_c, sorted(vars_tot)
 
    def ejecutar_rc(self):
        h, c, v = self.obtener_datos_seguro()
        if not h:
            return
        try:
            tabla = generar_tabla_verdad(v)
            encabezados = v + h + [c, "ESTADO"]
            matriz_filas = []
            valido = True
            hay_critico = False
            for fila in tabla:
                valores = dict(zip(v, fila))
                res_h, res_c, es_critico = evaluar_logica_renglon_critico(h, c, valores)
                datos = ['V' if x else 'F' for x in fila]
                datos.extend(['V' if x else 'F' for x in res_h])
                datos.append('V' if res_c else 'F')
                if es_critico:
                    hay_critico = True
                    if not res_c:
                        valido = False
                        datos.append("CRITICO (FALLA)")
                    else:
                        datos.append("CRITICO")
                else:
                    datos.append("-")
                matriz_filas.append(datos)
 
            if not hay_critico:
                vt, vc = "INVALIDO (VACUO)", "orange"
            elif valido:
                vt, vc = "ARGUMENTO VALIDO", "#2CC985"
            else:
                vt, vc = "ARGUMENTO INVALIDO", "#FF5555"
 
            self.lbl_titulo_tabla.configure(text="METODO: RENGLON CRITICO")
            self.iniciar_renderizado_vhs(encabezados, matriz_filas, vt, vc)
        except Exception as e:
            self.mostrar_error(f"Error grave: {e}")
 
    def ejecutar_tau(self):
        h, c, v = self.obtener_datos_seguro()
        if not h:
            return
        try:
            tabla = generar_tabla_verdad(v)
            formula, matriz, es_tau = evaluar_logica_tautologia(h, c, v, tabla)
            encabezados = v + ["RESULTADO SUPER-FORMULA"]
            vt = "ES TAUTOLOGIA (VALIDO)" if es_tau else "NO ES TAUTOLOGIA (INVALIDO)"
            vc = "#2CC985" if es_tau else "#FF5555"
            self.lbl_titulo_tabla.configure(text=f"TAUTOLOGIA: {formula}")
            self.iniciar_renderizado_vhs(encabezados, matriz, vt, vc)
        except Exception as e:
            self.mostrar_error(f"Error grave: {e}")
 
    def limpiar(self):
        self.cancelar_animacion()
        for e in self.inputs_h:
            e.delete(0, "end")
        self.input_c.delete(0, "end")
        self.lbl_titulo_tabla.configure(text="TABLA DE VERDAD Y ANALISIS")
        for w in self.frame_tabla.winfo_children():
            w.destroy()
        self.set_veredicto("ESPERANDO DATOS...", "gray")
 
    def mostrar_error(self, msg):
        self.cancelar_animacion()
        for w in self.frame_tabla.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.frame_tabla, text=f"❌ {msg}",
                     text_color="#FF5555", font=("Arial", 16, "bold")
                     ).grid(row=0, column=0, pady=20, padx=20)
        self.set_veredicto("ERROR DE ENTRADA", "orange")
 
    def set_veredicto(self, texto, color):
        self.lbl_veredicto.configure(text=texto, text_color=color)
 
    # =========================================================================
    #  TAB 2 — TEORÍA DE CONJUNTOS
    # =========================================================================
 
    def _construir_tab_conjuntos(self):
        tab = self.tab_conjuntos
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=2)
        tab.grid_rowconfigure(0, weight=1)
 
        # Almacén interno: nombre → Python set
        self._conjuntos: dict = {"U": set(), "A": set(), "B": set(), "C": set()}
        self._tarjetas_conj: dict = {}
 
        # ── PANEL IZQUIERDO: gestión de conjuntos ─────────────────────────────
        self._panel_conj = ctk.CTkFrame(tab, width=370)
        self._panel_conj.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self._panel_conj.grid_rowconfigure(1, weight=1)
        self._panel_conj.grid_columnconfigure(0, weight=1)
 
        ctk.CTkLabel(self._panel_conj, text="CONJUNTOS DEFINIDOS",
                     font=("Arial", 15, "bold")).grid(row=0, column=0, pady=8)
 
        self._scroll_conj = ctk.CTkScrollableFrame(self._panel_conj, fg_color="#1A1A2E")
        self._scroll_conj.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self._scroll_conj.grid_columnconfigure(0, weight=1)
 
        btn_frame = ctk.CTkFrame(self._panel_conj, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=6)
        ctk.CTkButton(btn_frame, text="➕ Agregar conjunto", width=165,
                      command=self._agregar_conjunto).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="🗑 Eliminar último", width=165,
                      fg_color="#6B2737", hover_color="#8B0000",
                      command=self._eliminar_ultimo_conjunto).pack(side="left", padx=4)
 
        for nombre in ["U", "A", "B", "C"]:
            self._agregar_tarjeta(nombre)
 
        # ── PANEL DERECHO: operaciones y resultados ───────────────────────────
        self._panel_ops = ctk.CTkFrame(tab)
        self._panel_ops.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self._panel_ops.grid_rowconfigure(3, weight=1)
        self._panel_ops.grid_columnconfigure(0, weight=1)
 
        ctk.CTkLabel(self._panel_ops, text="OPERACIONES",
                     font=("Arial", 15, "bold")).grid(row=0, column=0, pady=8)
 
        # Sub-tabs modo guiado / expresión libre
        self._op_tabs = ctk.CTkTabview(self._panel_ops, height=170)
        self._op_tabs.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        self._tab_guiado = self._op_tabs.add("🔘 Guiado")
        self._tab_expr   = self._op_tabs.add("✏️  Expresión Libre")
        self._construir_modo_guiado()
        self._construir_modo_expresion()
 
        btn_ej = ctk.CTkFrame(self._panel_ops, fg_color="transparent")
        btn_ej.grid(row=2, column=0, pady=6)
        ctk.CTkButton(btn_ej, text="▶  Calcular", width=160,
                      command=self._calcular_conjuntos).pack(side="left", padx=6)
        ctk.CTkButton(btn_ej, text="🧹 Limpiar resultado", width=160,
                      fg_color="gray", hover_color="#444",
                      command=self._limpiar_resultado_conj).pack(side="left", padx=6)
 
        self._frame_res_conj = ctk.CTkScrollableFrame(self._panel_ops, fg_color="#1E1E1E")
        self._frame_res_conj.grid(row=3, column=0, sticky="nsew", padx=8, pady=6)
        self._frame_res_conj.grid_columnconfigure(0, weight=1)
 
        self._lbl_res_conj = ctk.CTkLabel(
            self._panel_ops, text="ESPERANDO OPERACIÓN...",
            font=("Arial", 18, "bold"), text_color="gray")
        self._lbl_res_conj.grid(row=4, column=0, pady=10)
 
    # ── TARJETAS DE CONJUNTOS ─────────────────────────────────────────────────
 
    def _agregar_tarjeta(self, nombre: str):
        fila_idx = len(self._tarjetas_conj)
        frame = ctk.CTkFrame(self._scroll_conj, fg_color="#16213E", corner_radius=8)
        frame.grid(row=fila_idx, column=0, sticky="ew", padx=4, pady=4)
        frame.grid_columnconfigure(1, weight=1)
 
        lbl_nombre = ctk.CTkLabel(frame, text=nombre, font=("Arial", 16, "bold"),
                                  text_color="#2CC985", width=40)
        lbl_nombre.grid(row=0, column=0, padx=8, pady=(6, 2), sticky="nw")
 
        txt = ctk.CTkTextbox(frame, height=72, font=("Consolas", 12), fg_color="#0F0F23")
        txt.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        txt.insert("0.0", "# Un elemento por línea\n# Ej: {a,b} para anidado")
 
        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.grid(row=1, column=0, columnspan=2, pady=(0, 4))
 
        ctk.CTkButton(btn_row, text="📂 Cargar archivo", width=140,
                      command=lambda n=nombre: self._cargar_archivo(n)).pack(side="left", padx=4)
        ctk.CTkButton(btn_row, text="✅ Aplicar texto", width=140,
                      fg_color="#1E5631", hover_color="#145A32",
                      command=lambda n=nombre: self._aplicar_texto(n)).pack(side="left", padx=4)
 
        self._tarjetas_conj[nombre] = {"frame": frame, "txt": txt, "lbl": lbl_nombre}
 
    def _agregar_conjunto(self):
        """Agrega un nuevo conjunto con nombre automático — BONO conjuntos ilimitados."""
        usados = set(self._conjuntos.keys())
        candidatos = list("DEFGHIJKLMNOPQRSTVWXYZ") + [str(i) for i in range(1, 100)]
        for letra in candidatos:
            if letra not in usados:
                self._conjuntos[letra] = set()
                self._agregar_tarjeta(letra)
                return
        messagebox.showinfo("Límite", "No hay más nombres disponibles.")
 
    def _eliminar_ultimo_conjunto(self):
        protegidos = {"U", "A", "B", "C"}
        eliminables = [n for n in self._tarjetas_conj if n not in protegidos]
        if not eliminables:
            messagebox.showinfo("Info", "Los conjuntos U, A, B y C son obligatorios.")
            return
        ultimo = eliminables[-1]
        self._tarjetas_conj[ultimo]["frame"].destroy()
        del self._tarjetas_conj[ultimo]
        del self._conjuntos[ultimo]
 
    def _cargar_archivo(self, nombre: str):
        ruta = filedialog.askopenfilename(
            title=f"Cargar Conjunto {nombre}",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos", "*.*")])
        if not ruta:
            return
        try:
            with open(ruta, encoding="utf-8") as f:
                contenido = f.read()
            txt_w = self._tarjetas_conj[nombre]["txt"]
            txt_w.delete("0.0", "end")
            txt_w.insert("0.0", contenido)
            self._conjuntos[nombre] = cargar_conjunto_desde_texto(contenido)
            self._actualizar_lbl_conjunto(nombre)
            messagebox.showinfo("✅ Cargado",
                                f"Conjunto {nombre} cargado:\n"
                                f"{formatear_conjunto(self._conjuntos[nombre])}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")
 
    def _aplicar_texto(self, nombre: str):
        contenido = self._tarjetas_conj[nombre]["txt"].get("0.0", "end")
        try:
            self._conjuntos[nombre] = cargar_conjunto_desde_texto(contenido)
            self._actualizar_lbl_conjunto(nombre)
            messagebox.showinfo("✅ Aplicado",
                                f"Conjunto {nombre} = "
                                f"{formatear_conjunto(self._conjuntos[nombre])}")
        except Exception as e:
            messagebox.showerror("Error de parseo", str(e))
 
    def _actualizar_lbl_conjunto(self, nombre: str):
        n = len(self._conjuntos[nombre])
        self._tarjetas_conj[nombre]["lbl"].configure(text=f"{nombre}  |{n}|")
 
    # ── MODO GUIADO ───────────────────────────────────────────────────────────
 
    def _construir_modo_guiado(self):
        tab = self._tab_guiado
        tab.grid_columnconfigure((0, 1, 2), weight=1)
 
        ctk.CTkLabel(tab, text="Conjunto A:").grid(row=0, column=0, padx=4, pady=6)
        self._cmb_a = ctk.CTkComboBox(tab, values=list(self._conjuntos.keys()), width=80)
        self._cmb_a.grid(row=1, column=0, padx=4)
        self._cmb_a.set("A")
 
        ctk.CTkLabel(tab, text="Operación:").grid(row=0, column=1, padx=4)
        self._cmb_op = ctk.CTkComboBox(tab, width=230, values=[
            "Unión (A ∪ B)",
            "Intersección (A ∩ B)",
            "Diferencia (A − B)",
            "Diferencia Simétrica (A △ B)",
        ])
        self._cmb_op.grid(row=1, column=1, padx=4)
        self._cmb_op.set("Unión (A ∪ B)")
 
        ctk.CTkLabel(tab, text="Conjunto B:").grid(row=0, column=2, padx=4)
        self._cmb_b = ctk.CTkComboBox(tab, values=list(self._conjuntos.keys()), width=80)
        self._cmb_b.grid(row=1, column=2, padx=4)
        self._cmb_b.set("B")
 
        ctk.CTkLabel(tab,
                     text="Tip: también puedes encadenar operaciones en el tab 'Expresión Libre'",
                     font=("Arial", 11), text_color="gray"
                     ).grid(row=2, column=0, columnspan=3, pady=(8, 0))
 
    def _refrescar_combos(self):
        nombres = list(self._conjuntos.keys())
        self._cmb_a.configure(values=nombres)
        self._cmb_b.configure(values=nombres)
 
    # ── MODO EXPRESIÓN LIBRE ──────────────────────────────────────────────────
 
    def _construir_modo_expresion(self):
        tab = self._tab_expr
        tab.grid_columnconfigure(0, weight=1)
 
        ctk.CTkLabel(tab,
                     text="Escribe una expresión  (ej: (A | B) - C  ó  A union B inter ~C)",
                     font=("Arial", 12)).grid(row=0, column=0, pady=(8, 2), padx=8, sticky="w")
 
        self._entry_expr = ctk.CTkEntry(tab, placeholder_text="(A | B) - C",
                                        width=420, font=("Consolas", 13))
        self._entry_expr.grid(row=1, column=0, padx=8, pady=4, sticky="ew")
 
        ctk.CTkLabel(tab,
                     text="| union    & inter    - diff    ^ symdiff    ~X complemento",
                     font=("Consolas", 11), text_color="gray"
                     ).grid(row=2, column=0, pady=4)
 
    # ── CALCULAR ──────────────────────────────────────────────────────────────
 
    def _calcular_conjuntos(self):
        self._refrescar_combos()
        self._limpiar_resultado_conj()
        modo = self._op_tabs.get()
 
        try:
            if "Guiado" in modo:
                na = self._cmb_a.get()
                nb = self._cmb_b.get()
                op = self._cmb_op.get()
                if na not in self._conjuntos:
                    raise ValueError(f"Conjunto '{na}' no definido.")
                if nb not in self._conjuntos:
                    raise ValueError(f"Conjunto '{nb}' no definido.")
                resultado, simbolo = operacion_guiada(self._conjuntos[na],
                                                      self._conjuntos[nb], op)
                expr_str = f"{na} {simbolo} {nb}"
            else:
                expr_str = self._entry_expr.get().strip()
                if not expr_str:
                    raise ValueError("Escribe una expresión antes de calcular.")
                resultado = evaluar_expresion_conjuntos(expr_str, self._conjuntos)
 
            self._mostrar_resultado_conjuntos(expr_str, resultado)
 
        except ValueError as e:
            self._mostrar_error_conj(str(e))
        except Exception as e:
            self._mostrar_error_conj(f"Error inesperado: {e}")
 
    # ── RENDERIZADO DE RESULTADO ──────────────────────────────────────────────
 
    def _mostrar_resultado_conjuntos(self, expresion: str, resultado: set):
        frame = self._frame_res_conj
        for w in frame.winfo_children():
            w.destroy()
 
        # Encabezado
        ctk.CTkLabel(frame, text=f"  {expresion}  ",
                     font=("Arial", 14, "bold"), fg_color="#2C3E50",
                     corner_radius=6, pady=6
                     ).grid(row=0, column=0, sticky="ew", padx=6, pady=6)
 
        # Resultado y cardinalidad
        ctk.CTkLabel(frame, text=formatear_conjunto(resultado),
                     font=("Consolas", 15, "bold"), text_color="#2CC985",
                     wraplength=560, justify="left"
                     ).grid(row=1, column=0, sticky="w", padx=14, pady=4)
 
        ctk.CTkLabel(frame, text=f"Cardinalidad: |resultado| = {len(resultado)}",
                     font=("Consolas", 13), text_color="#F39C12"
                     ).grid(row=2, column=0, sticky="w", padx=14, pady=2)
 
        # Tabla de pertenencia usando el universo U
        universo = self._conjuntos.get("U", set())
        todos = universo | resultado
        if todos:
            ctk.CTkFrame(frame, height=2, fg_color="#333333"
                         ).grid(row=3, column=0, sticky="ew", padx=6, pady=8)
 
            ctk.CTkLabel(frame, text="Tabla de pertenencia al resultado:",
                         font=("Arial", 12, "bold"), text_color="gray"
                         ).grid(row=4, column=0, sticky="w", padx=14)
 
            sub = ctk.CTkFrame(frame, fg_color="#252525")
            sub.grid(row=5, column=0, sticky="ew", padx=6, pady=4)
            sub.grid_columnconfigure((0, 1), weight=1)
 
            for ci, titulo in enumerate(["Elemento", "¿En resultado?"]):
                ctk.CTkLabel(sub, text=titulo, font=("Arial", 12, "bold"),
                             fg_color="#333333", corner_radius=4, pady=4
                             ).grid(row=0, column=ci, padx=3, pady=3, sticky="ew")
 
            for ri, elem_str in enumerate(sorted(formatear_elemento(e) for e in todos), 1):
                parsed = parse_elemento(elem_str)
                pertenece = parsed in resultado or elem_str in resultado
                color = "#2CC985" if pertenece else "#FF5555"
                marca = "✔ SÍ" if pertenece else "✘ NO"
 
                ctk.CTkLabel(sub, text=elem_str, font=("Consolas", 12),
                             fg_color="#2A2A2A", corner_radius=3
                             ).grid(row=ri, column=0, padx=3, pady=2, sticky="ew")
                ctk.CTkLabel(sub, text=marca, font=("Consolas", 12, "bold"),
                             text_color=color, fg_color="#2A2A2A", corner_radius=3
                             ).grid(row=ri, column=1, padx=3, pady=2, sticky="ew")
 
        self._lbl_res_conj.configure(
            text=f"RESULTADO: {len(resultado)} elemento(s)", text_color="#2CC985")
 
    def _mostrar_error_conj(self, msg: str):
        for w in self._frame_res_conj.winfo_children():
            w.destroy()
        ctk.CTkLabel(self._frame_res_conj, text=f"❌ {msg}",
                     text_color="#FF5555", font=("Arial", 14, "bold")
                     ).grid(row=0, column=0, pady=20, padx=12)
        self._lbl_res_conj.configure(text="ERROR EN LA OPERACIÓN", text_color="orange")
 
    def _limpiar_resultado_conj(self):
        for w in self._frame_res_conj.winfo_children():
            w.destroy()
        self._lbl_res_conj.configure(text="ESPERANDO OPERACIÓN...", text_color="gray")
 
 
# =============================================================================
# ENTRY POINT
# =============================================================================
 
if __name__ == "__main__":
    app = SuiteLogica()
    app.mainloop()