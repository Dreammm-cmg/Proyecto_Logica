# Changelog — LyED Toolkit
**ITESO · Ingeniería en Ciberseguridad · Lógica Discreta y Estructuras**  
Autores: Gustavo Adrián Joya Rodriguéz · Sebastián Castillo Martínez · Jesus Daniel Marín Terrazas

---

## [3.0.0] — Parte II: Teoría de Conjuntos *(2026-04)*

### 🧮 Nueva funcionalidad: Módulo de Teoría de Conjuntos

- **Tab integrado `∪  Teoría de Conjuntos`** — La aplicación ahora es un toolkit de dos módulos dentro de una ventana tabbed (`CTkTabview`). El módulo de Lógica Proposicional queda en el tab `⊢  Lógica Proposicional` sin cambios.

- **Gestión dinámica de conjuntos (BONO +10)**
  - Conjuntos base protegidos: **U, A, B, C** (no eliminables).
  - Botón `➕ Agregar conjunto` — asigna automáticamente el siguiente nombre disponible en el alfabeto (D, E, F…).
  - Botón `🗑 Eliminar último` — elimina el último conjunto agregado que no sea base.
  - Los dropdowns del modo guiado se refrescan automáticamente al agregar o eliminar conjuntos.

- **Tarjetas de conjuntos**
  - Cada conjunto tiene una tarjeta visual con `CTkTextbox` editable.
  - Botón `✅ Aplicar texto` — parsea el contenido multilínea del textbox y construye el conjunto.
  - Botón `📂 Cargar archivo` — abre un explorador de archivos para importar un `.txt` (un elemento por línea).
  - El label de cada tarjeta muestra la cardinalidad en tiempo real: `A  |3|`.

- **Soporte de elementos anidados**
  - Elementos simples: strings arbitrarios (`manzana`, `42`, `x`).
  - Subconjuntos anidados a 2 niveles: `{a,b}` se almacena como `frozenset`.
  - Líneas que comienzan con `#` son ignoradas (comentarios).

- **Modo Guiado (dropdowns)**
  - Tres ComboBoxes: Conjunto A, Operación, Conjunto B.
  - Operaciones disponibles: Unión (∪), Intersección (∩), Diferencia (−), Diferencia Simétrica (△).

- **Modo Expresión Libre**
  - Campo de texto libre con evaluación segura via `eval()` con namespace controlado (`__builtins__: {}`).
  - Operadores soportados: `|` (union), `&` (inter), `-` (diff), `^` (symdiff).
  - Alias de palabras clave: `union`, `inter`, `diff`, `symdiff`.
  - Complemento: `~X` → traducido automáticamente a `(U - X)`.
  - Expresiones encadenadas: `(A | B) - C & D`.

- **Renderizado de resultados**
  - Muestra el conjunto resultante formateado con notación matemática (`∅` para conjunto vacío).
  - Muestra la **cardinalidad**: `|resultado| = N`.
  - **Tabla de pertenencia por elemento**: columnas Elemento / ¿En resultado?, colorizada en verde (✔ SÍ) y rojo (✘ NO).
  - Usa el universo `U` como referencia para construir la tabla de pertenencia.

### 🏗 Cambios arquitectónicos

- Renombrado: título de ventana actualizado a **`LyED ToolKit — ITESO Ciberseguridad`**.
- Agregado bloque `MÓDULO TEORÍA DE CONJUNTOS — BACKEND` con funciones puras libres de estado.
- Funciones de backend nuevas: `parse_elemento`, `cargar_conjunto_desde_texto`, `formatear_elemento`, `formatear_conjunto`, `evaluar_expresion_conjuntos`, `operacion_guiada`.
- Métodos de frontend nuevos en `SuiteLogica`: `_construir_tab_conjuntos`, `_agregar_tarjeta`, `_agregar_conjunto`, `_eliminar_ultimo_conjunto`, `_construir_modo_guiado`, `_construir_modo_expresion`, `_calcular_conjuntos`, `_mostrar_resultado_conjuntos`, `_mostrar_error_conj`, `_limpiar_resultado_conj`, `_cargar_archivo`, `_aplicar_texto`, `_actualizar_lbl_conjunto`, `_refrescar_combos`.

---

## [2.1.1] — Hotfix: UI Grid Alignment

### 🐛 Corrección Visual

- **[FIX]** Solucionado el bug de colapso de columnas dentro del `CTkScrollableFrame` durante el método de Tautología.
- Se reescribió el motor de renderizado para asignar pesos dinámicos (`grid_columnconfigure weight`), otorgando un `weight=5` a la columna de resultados para forzar su expansión y eliminar el espacio muerto a la derecha.

---

## [2.1.0] — Release Candidate: Animación y UX

### ✨ Mejoras de UX/UI

- **[Efecto VHS / Cascada]** Implementación de renderizado asíncrono.
  - Se reemplazó el bucle de dibujado síncrono por llamadas recursivas mediante `UI.after()`.
  - Previene el congelamiento de la ventana principal (Thread blocking) al renderizar matrices muy grandes.
- **[Navegación]** Añadido auto-scroll inteligente (`yview_moveto(1.0)`) acoplado a la animación de renderizado para seguir la generación de datos en tiempo real.

---

## [2.0.0] — Major Update: Refactorización de Arquitectura

### 🏗 Cambios arquitectónicos

- **[Arquitectura]** Transición a un modelo estricto de Separación de Responsabilidades (Datos vs Vista).  
  El motor lógico ahora devuelve matrices y arreglos puros en lugar de cadenas de texto formateadas.
- **[Escalabilidad]** Deprecación del sistema de salida en texto plano (`CTkTextbox`).  
  Implementación de un motor de renderizado de cuadrículas dinámicas capaz de instanciar celdas de forma individual.

### ✨ Mejoras visuales

- **[Colorización semántica]** Verde para Verdadero, Rojo para Falso, Naranja para Renglones Críticos.
- **[Diseño zebra]** Filas intercaladas con fondo alternado para reducir la fatiga visual del usuario.

---

## [1.3.0] — Integración de Herramientas de Apoyo

### ✨ Nueva característica

- **[Formulario / Leyes]** Integración de un módulo de apoyo accesible via `CTkToplevel`.
  - Contiene Equivalencias Lógicas (De Morgan, Distribución, Asociatividad, Conmutatividad).
  - Contiene Reglas de Inferencia (Modus Ponens, Modus Tollens, Silogismo Hipotético, Silogismo Disyuntivo).
  - Accesible en tiempo real sin salir de la aplicación.

---

## [1.2.0] — Parche de Seguridad y Estabilidad (Zero Trust)

### 🔒 Correcciones de seguridad y estabilidad

- **[FIX]** Solución al error `SympifyError` que causaba el cierre abrupto del programa por inputs malformados.
- **[Validación]** Implementación de `validar_y_extraer_vars()` con política Zero Trust.
  - Aísla y analiza cada campo de hipótesis individualmente.
  - Usa bloques `try-except` antes de enviar al motor lógico.

---

## [1.1.0] — Algoritmos: Método de la Tautología

### ✨ Lógica matemática

- **[Tautología]** Implementación del algoritmo de Verificación por Tautología.
  - Fusiona automáticamente `n` hipótesis en una macro-fórmula condicional unida por conjunciones.
  - Evalúa la fórmula `(H1 & H2 & ... & Hn) >> C` en toda la tabla de verdad.
  - Verifica si es una tautología absoluta (VERDADERO en todos los renglones).

---

## [1.0.0] — Lanzamiento Inicial (GUI)

### 🚀 Primera versión

- **[Interfaz]** Migración exitosa de aplicación de consola (CLI) a Interfaz Gráfica (GUI) utilizando la librería `customtkinter`. Tema Dark/Green.
- **[Características]**
  - Generación dinámica de hasta **10 campos** de entrada de hipótesis.
  - Análisis mediante **Método del Renglón Crítico**.
  - Traducción algorítmica de sintaxis humana (`->`, `<->`, `v`, `^`) a sintaxis de `sympy`.
  - Tabla de verdad en texto plano con indicador de Renglón Crítico.
  - Botón Limpiar Todo.

---

> 📦 **Repositorio:** [github.com/Dreammm-cmg/Proyecto_Logica](https://github.com/Dreammm-cmg/Proyecto_Logica)
