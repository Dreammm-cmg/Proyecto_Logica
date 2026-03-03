"""
=============================================================================
INSTITUTO TECNOLOGICO DE ESTUDIOS SUPERIORES Y DE OCCIDENTE (ITESO)
INGENIERIA EN CIBERSEGURIDAD
MATERIA: LOGICA DISCRETA Y ESTRUCTURAS

PROYECTO INTEGRADOR: SUITE DE VALIDACION LOGICA (EFECTO VHS / DELAY + UI FIX)
AUTOR: GUSTAVO ADRIAN JOYA RODRIGUEZ, JESÚS DANIEL MARÍN TERRAZAS
FECHA: Febrero 2026
=============================================================================
"""

import customtkinter as ctk  
import sympy                 
import itertools             
from sympy.core.sympify import SympifyError 

# =============================================================================
# CONFIGURACION VISUAL GLOBAL
# =============================================================================
ctk.set_appearance_mode("Dark")       
ctk.set_default_color_theme("green")  

# =============================================================================
# MODULO 1: EL MOTOR LOGICO (BACKEND MATEMATICO)
# =============================================================================

def traducir_a_sympy(expresion):
    exp = expresion.lower() 
    if "<->" in exp:
        partes = exp.split("<->") 
        if len(partes) == 2:
            lado_a = traducir_a_sympy(partes[0].strip()) 
            lado_b = traducir_a_sympy(partes[1].strip())
            return f"({lado_a} >> {lado_b}) & ({lado_b} >> {lado_a})"
    
    exp = exp.replace("->", ">>") 
    exp = exp.replace("v", "|")   
    exp = exp.replace("^", "&")   
    return exp

def validar_y_extraer_vars(texto_caja):
    if not texto_caja: return set() 
    texto_sympy = traducir_a_sympy(texto_caja)
    try:
        expr = sympy.sympify(texto_sympy) 
        return {str(s) for s in expr.free_symbols}
    except Exception:
        raise ValueError(f"Error de Sintaxis en '{texto_caja}': Revisa operadores faltantes.")

def generar_tabla_verdad(variables):
    n = len(variables)
    return list(itertools.product([True, False], repeat=n))

def evaluar_logica_renglon_critico(hipotesis, conclusion, valores_diccionario):
    resultados_hipotesis = []
    es_critico = True 
    for h in hipotesis:
        form_h = traducir_a_sympy(h)   
        expr = sympy.sympify(form_h)   
        val = bool(expr.subs(valores_diccionario)) 
        resultados_hipotesis.append(val) 
        if not val:
            es_critico = False 
            
    form_c = traducir_a_sympy(conclusion)
    expr_c = sympy.sympify(form_c)
    val_c = bool(expr_c.subs(valores_diccionario))
    
    return resultados_hipotesis, val_c, es_critico

def evaluar_logica_tautologia(hipotesis, conclusion, variables, tabla):
    hips_traducidas = [f"({traducir_a_sympy(h)})" for h in hipotesis]
    gran_hipotesis = " & ".join(hips_traducidas)
    concl_traducida = f"({traducir_a_sympy(conclusion)})"
    
    formula_str = f"({gran_hipotesis}) >> {concl_traducida}"
    expr_final = sympy.sympify(formula_str) 
    
    matriz_resultados = [] 
    es_tautologia = True 
    
    for fila in tabla:
        vals = dict(zip(variables, fila))
        resultado = bool(expr_final.subs(vals))
        
        fila_datos = ['V' if v else 'F' for v in fila]
        
        if resultado:
            fila_datos.append("VERDADERO")
        else:
            es_tautologia = False
            fila_datos.append("FALSO (FALLA)")
            
        matriz_resultados.append(fila_datos)
        
    return formula_str, matriz_resultados, es_tautologia

# =============================================================================
# MODULO 2: LA INTERFAZ GRAFICA (FRONTEND)
# =============================================================================

class SuiteLogica(ctk.CTk):
    def __init__(self):
        super().__init__() 
        self.title("Sistema Validador - Proyecto Integrador") 
        self.geometry("1100x750") 

        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        # Variables de control para la animacion
        self.animacion_activa = False
        self.id_animacion = None

        # === PANEL IZQUIERDO ===
        self.panel_input = ctk.CTkFrame(self, width=320)
        self.panel_input.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.panel_input, text="HIPOTESIS (Max 10)", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.inputs_h = []
        for i in range(10):
            entry = ctk.CTkEntry(self.panel_input, placeholder_text=f"Hipotesis {i+1} (Ej: p -> q)", width=280)
            entry.pack(pady=3)
            self.inputs_h.append(entry)

        ctk.CTkLabel(self.panel_input, text="CONCLUSION", font=("Arial", 14, "bold")).pack(pady=10)
        self.input_c = ctk.CTkEntry(self.panel_input, width=280, placeholder_text="Ej: r")
        self.input_c.pack()
        
        self.btn_rc = ctk.CTkButton(self.panel_input, text="Validar por Renglon Critico", command=self.ejecutar_rc)
        self.btn_rc.pack(pady=(20, 5))
        
        self.btn_tau = ctk.CTkButton(self.panel_input, text="Validar por Tautologia", 
                                     fg_color="orange", hover_color="#cc8400", command=self.ejecutar_tau)
        self.btn_tau.pack(pady=5)
        
        self.btn_form = ctk.CTkButton(self.panel_input, text="📘 Ver Formulario / Leyes", 
                                      fg_color="#3B8ED0", hover_color="#36719F", command=self.abrir_formulario)
        self.btn_form.pack(pady=20)

        self.btn_cls = ctk.CTkButton(self.panel_input, text="Limpiar Todo", 
                                     fg_color="gray", hover_color="#444", command=self.limpiar)
        self.btn_cls.pack(pady=5)

        # === PANEL DERECHO ===
        self.panel_res = ctk.CTkFrame(self)
        self.panel_res.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.panel_res.grid_rowconfigure(1, weight=1)
        self.panel_res.grid_columnconfigure(0, weight=1)

        self.lbl_titulo_tabla = ctk.CTkLabel(self.panel_res, text="TABLA DE VERDAD Y ANALISIS", font=("Arial", 16, "bold"))
        self.lbl_titulo_tabla.grid(row=0, column=0, pady=5)

        self.frame_tabla = ctk.CTkScrollableFrame(self.panel_res, fg_color="#1E1E1E")
        self.frame_tabla.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.lbl_veredicto = ctk.CTkLabel(self.panel_res, text="ESPERANDO DATOS...", font=("Arial", 20, "bold"))
        self.lbl_veredicto.grid(row=2, column=0, pady=20)

    # --- MOTOR DE RENDERIZADO CON EFECTO VHS (DELAY) ---
    def cancelar_animacion(self):
        if self.id_animacion is not None:
            self.after_cancel(self.id_animacion)
            self.animacion_activa = False

    def iniciar_renderizado_vhs(self, encabezados, matriz_datos, veredicto_texto, veredicto_color):
        self.cancelar_animacion()
        self.animacion_activa = True
        self.set_veredicto("CALCULANDO...", "gray") 
        
        # Limpiar tabla
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()

        # LOGICA CORREGIDA: PESOS DINAMICOS PARA RELLENAR ESPACIOS
        es_tautologia = "RESULTADO SUPER-FORMULA" in encabezados
        for i in range(len(encabezados)):
            if es_tautologia:
                if i == len(encabezados) - 1:
                    # Peso masivo (5) para obligar a la columna de resultado a expandirse a tope
                    self.frame_tabla.grid_columnconfigure(i, weight=10)
                else:
                    # Peso 1 para las variables, asegurando que el frame interior se estire completo
                    self.frame_tabla.grid_columnconfigure(i, weight=1)
            else:
                # Comportamiento normal en renglon critico
                self.frame_tabla.grid_columnconfigure(i, weight=1)

        # Dibujar Encabezados 
        for col_idx, texto in enumerate(encabezados):
            lbl = ctk.CTkLabel(self.frame_tabla, text=texto, font=("Arial", 14, "bold"), 
                               fg_color="#333333", corner_radius=5, pady=5)
            lbl.grid(row=0, column=col_idx, padx=2, pady=2, sticky="nsew")

        # Arrancar efecto VHS
        self.dibujar_fila_con_delay(matriz_datos, 0, veredicto_texto, veredicto_color)

    def dibujar_fila_con_delay(self, matriz_datos, row_idx, veredicto_texto, veredicto_color):
        if not self.animacion_activa: return 
        
        if row_idx >= len(matriz_datos):
            self.animacion_activa = False
            self.set_veredicto(veredicto_texto, veredicto_color) 
            return

        fila = matriz_datos[row_idx]
        bg_color = "#252525" if row_idx % 2 == 0 else "#2A2A2A"

        for col_idx, valor in enumerate(fila):
            valor_str = str(valor)
            color_texto = "white"
            if valor_str == 'V' or valor_str == 'VERDADERO': color_texto = "#2CC985" 
            elif valor_str == 'F' or "FALSO" in valor_str: color_texto = "#FF5555"   
            elif "CRITICO" in valor_str: color_texto = "#F39C12"                     
            
            lbl = ctk.CTkLabel(self.frame_tabla, text=valor_str, text_color=color_texto, 
                               font=("Consolas", 14, "bold"), fg_color=bg_color, corner_radius=3)
            lbl.grid(row=row_idx+1, column=col_idx, padx=2, pady=2, sticky="nsew")
        
        self.frame_tabla._parent_canvas.yview_moveto(1.0)
        velocidad_ms = 100 
        self.id_animacion = self.after(velocidad_ms, self.dibujar_fila_con_delay, matriz_datos, row_idx + 1, veredicto_texto, veredicto_color)

    # --- LOGICA DE CONTROL ---
    def abrir_formulario(self):
        ventana_form = ctk.CTkToplevel(self) 
        ventana_form.title("Formulario de Logica Proposicional")
        ventana_form.geometry("600x700")
        
        texto_leyes = """
=== 1. EQUIVALENCIAS LOGICAS (Teorema 2.1.1) ===
Simbolos App:  ~ (Negacion), v (OR), ^ (AND), -> (Implica), <-> (Si y solo si)

1. Leyes Conmutativas:
   p ^ q  ≡  q ^ p
   p v q  ≡  q v p

2. Leyes Asociativas:
   (p ^ q) ^ r  ≡  p ^ (q ^ r)
   (p v q) v r  ≡  p v (q v r)

3. Leyes Distributivas:
   p ^ (q v r)  ≡  (p ^ q) v (p ^ r)
   p v (q ^ r)  ≡  (p v q) ^ (p v r)

4. Leyes de De Morgan:
   ~(p ^ q)  ≡  ~p v ~q
   ~(p v q)  ≡  ~p ^ ~q

5. Doble Negacion:
   ~(~p)  ≡  p

6. Implicacion y Bicondicional:
   p -> q   ≡  ~p v q
   p <-> q  ≡  (p -> q) ^ (q -> p)

=== 2. REGLAS DE INFERENCIA ===
1. Modus Ponens:
   H1: p -> q
   H2: p
   -------
   C:  q

2. Modus Tollens:
   H1: p -> q
   H2: ~q
   -------
   C:  ~p
"""
        txt_form = ctk.CTkTextbox(ventana_form, font=("Consolas", 14))
        txt_form.pack(fill="both", expand=True, padx=10, pady=10)
        txt_form.insert("0.0", texto_leyes)
        txt_form.configure(state="disabled") 

    def obtener_datos_seguro(self):
        raw_hipotesis = [entry.get().strip() for entry in self.inputs_h if entry.get().strip()]
        raw_conclusion = self.input_c.get().strip()
        
        if not raw_hipotesis:
            self.mostrar_error("Error: Escribe al menos una hipotesis.")
            return None, None, None
        if not raw_conclusion:
            self.mostrar_error("Error: Falta la conclusion.")
            return None, None, None

        variables_totales = set() 
        
        try:
            for h in raw_hipotesis:
                vars_h = validar_y_extraer_vars(h)
                variables_totales.update(vars_h) 
            
            vars_c = validar_y_extraer_vars(raw_conclusion)
            variables_totales.update(vars_c)
            
        except ValueError as e:
            self.mostrar_error(str(e))
            return None, None, None
            
        if not variables_totales:
            self.mostrar_error("Error: No encontré variables (letras).")
            return None, None, None
            
        return raw_hipotesis, raw_conclusion, sorted(list(variables_totales))

    def ejecutar_rc(self):
        h, c, v = self.obtener_datos_seguro()
        if not h: return 

        try:
            tabla = generar_tabla_verdad(v)
            
            encabezados = v + h + [c, "ESTADO"]
            matriz_filas = []
            valido = True       
            hay_critico = False 
            
            for fila in tabla:
                valores = dict(zip(v, fila))
                res_h, res_c, es_critico = evaluar_logica_renglon_critico(h, c, valores)
                
                datos_fila = ['V' if x else 'F' for x in fila]
                datos_fila.extend(['V' if x else 'F' for x in res_h])
                datos_fila.append('V' if res_c else 'F') 
                
                if es_critico:
                    hay_critico = True
                    if not res_c:
                        valido = False
                        datos_fila.append("CRITICO (FALLA)")
                    else:
                        datos_fila.append("CRITICO")
                else:
                    datos_fila.append("-")
                
                matriz_filas.append(datos_fila)

            veredicto_txt = ""
            veredicto_col = ""
            if not hay_critico:
                veredicto_txt, veredicto_col = "INVALIDO (VACUO)", "orange"
            elif valido:
                veredicto_txt, veredicto_col = "ARGUMENTO VALIDO", "#2CC985"
            else:
                veredicto_txt, veredicto_col = "ARGUMENTO INVALIDO", "#FF5555"

            self.lbl_titulo_tabla.configure(text="METODO: RENGLON CRITICO")
            self.iniciar_renderizado_vhs(encabezados, matriz_filas, veredicto_txt, veredicto_col)
                
        except Exception as e:
            self.mostrar_error(f"Error grave: {e}")

    def ejecutar_tau(self):
        h, c, v = self.obtener_datos_seguro()
        if not h: return

        try:
            tabla = generar_tabla_verdad(v)
            formula, matriz_datos, es_tau = evaluar_logica_tautologia(h, c, v, tabla)
            encabezados = v + ["RESULTADO SUPER-FORMULA"]
            
            veredicto_txt = "ES TAUTOLOGIA (VALIDO)" if es_tau else "NO ES TAUTOLOGIA (INVALIDO)"
            veredicto_col = "#2CC985" if es_tau else "#FF5555"

            self.lbl_titulo_tabla.configure(text=f"TAUTOLOGIA: {formula}")
            self.iniciar_renderizado_vhs(encabezados, matriz_datos, veredicto_txt, veredicto_col)
                
        except Exception as e:
            self.mostrar_error(f"Error grave: {e}")

    def limpiar(self):
        self.cancelar_animacion() 
        for entry in self.inputs_h:
            entry.delete(0, "end")
        self.input_c.delete(0, "end")
        self.lbl_titulo_tabla.configure(text="TABLA DE VERDAD Y ANALISIS")
        for widget in self.frame_tabla.winfo_children():
            widget.destroy() 
        self.set_veredicto("ESPERANDO DATOS...", "gray")

    def mostrar_error(self, msg):
        self.cancelar_animacion()
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()
        
        lbl_err = ctk.CTkLabel(self.frame_tabla, text=f"❌ {msg}", text_color="#FF5555", font=("Arial", 16, "bold"))
        lbl_err.grid(row=0, column=0, pady=20, padx=20)
        self.set_veredicto("ERROR DE ENTRADA", "orange")

    def set_veredicto(self, texto, color):
        self.lbl_veredicto.configure(text=texto, text_color=color)

if __name__ == "__main__":
    app = SuiteLogica() 
    app.mainloop()