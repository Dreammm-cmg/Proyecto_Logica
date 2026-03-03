 CHANGELOG: Suite de Validación Lógica
v2.1.1 - Hotfix (UI Grid Alignment)
[Corrección Visual] Solucionado el bug de colapso de columnas dentro del CTkScrollableFrame durante el método de Tautología. Se reescribió el motor de renderizado para asignar pesos dinámicos (grid_columnconfigure weight), otorgando un weight=5 a la columna de resultados para forzar su expansión y eliminar el espacio muerto a la derecha.

v2.1.0 - Release Candidate (Animación y UX)
[Mejora de UX/UI] Implementación de renderizado asíncrono (Efecto "VHS / Cascada"). Se reemplazó el bucle de dibujado síncrono por llamadas recursivas mediante el método UI.after() para prevenir el congelamiento de la ventana principal (Thread blocking) al renderizar matrices muy grandes.
[Navegación] Se añadió auto-scroll inteligente (yview_moveto(1.0)) acoplado a la animación de renderizado para seguir la generación de datos en tiempo real.

v2.0.0 - Refactorización de Arquitectura (Major Update)
[Arquitectura] Transición a un modelo estricto de Separación de Responsabilidades (Datos vs Vista). El motor lógico ahora devuelve matrices y arreglos puros en lugar de cadenas de texto formateadas.
[Escalabilidad] Deprecación del sistema de salida en texto plano (CTkTextbox). Implementación de un motor de renderizado de cuadrículas dinámicas capaz de instanciar celdas de forma individual.
[Mejora Visual] Colorización condicional semántica (Verde para Verdadero, Rojo para Falso, Naranja para Renglones Críticos) y diseño de filas intercaladas (fondo tipo cebra) para reducir la fatiga visual del usuario.

v1.3.0 - Integración de Herramientas de Apoyo
[Nueva Característica] Integración de un módulo de "Formulario / Leyes Lógicas" a través de una ventana flotante (CTkToplevel). Contiene Equivalencias Lógicas (De Morgan, Distribución) y Reglas de Inferencia (Modus Ponens, Tollens) accesibles en tiempo real sin salir de la app.

v1.2.0 - Parche de Seguridad y Estabilidad (Zero Trust)
[Corrección de Bug] Solución al error SympifyError que causaba el cierre abrupto del programa por inputs malformados.
[Validación] Implementación de la función validar_y_extraer_vars. Se aplica una política de Zero Trust que aísla, analizacada campo de hipótesis de forma individual usando bloques try-except antes de enviarlos al motor lógico.

v1.1.0 - Algoritmos (Actividad 2)
[Lógica Matemática] Implementación del algoritmo "Método de la Tautología". El sistema ahora es capaz de fusionar automáticamente n hipótesis en una macro-fórmula condicional unida por conjunciones y evaluarla globalmente.
v1.0.0 - Lanzamiento Inicial (GUI)
[Interfaz] Migración exitosa de aplicación de consola (CLI) a Interfaz Gráfica (GUI) utilizando la librería customtkinter.
[Características] Generación dinámica de hasta 10 campos de entrada de hipótesis, análisis mediante método del Renglón Crítico y traducción algorítmica de sintaxis humana (ej. ->, <->) a sintaxis de sympy.
