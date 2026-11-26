# Validación del storytelling — criterio 3 de la rúbrica (nivel Estratégico)

## 1. La historia (tres actos + Bing-Bang-Bongo)

**Bing-Bang-Bongo = repetir el mensaje central tres veces** (Pulido López, 2026b): se anuncia en el título de la página 1, se demuestra en los títulos de los gráficos y se repite en el recuadro «¿Dónde actuar?». Los tres actos (planteamiento, conflicto, resolución) son el arco narrativo (Nussbaumer Knaflic, 2015).

**Gran Idea:** *La violencia intrafamiliar notificada en Bogotá llegó en 2025 a su máximo (46 % sobre el promedio 2013–2025). Ocurre en casa, la ejerce la familia y recae sobre niñas, niños y mujeres. Hay cuatro frentes concretos donde actuar.*

| Acto | Pregunta | Dónde | Evidencia (cifras de 2025, salvo que se indique otro periodo) |
|---|---|---|---|
| **Bing** · planteamiento | ¿Qué está pasando? | P1: KPI + línea anual | 52.493 casos, +46 % frente al promedio; suben desde 2021 |
| **Bang** · conflicto | ¿Quién agrede y dónde? | P1: agresor + localidades (+ tooltip y drill-through) | 77 % de agresores familiares; Ciudad Bolívar, Bosa y Kennedy concentran el 39 % |
| **Bongo** · resolución | ¿A quién afecta y qué hacer? | P2: pirámide, tipos, KPI, "¿Dónde actuar?" | 65 % de víctimas menores de 18; 87 % de mujeres entre los 18 y 44 años; 79 % de los hechos en la vivienda; 29 % de la violencia sexual ocurre en la escuela |

Orden de lectura en Z: título → KPI → tendencia → agresor; luego, la columna derecha con el territorio. El cierre está en la página 2 con el llamado a la acción, que tiene cuatro prioridades, cada una respaldada por una cifra.

## 2. Problemas detectados en la revisión y cómo se corrigieron

| # | Problema | Por qué afectaba el nivel Estratégico | Corrección |
|---|---|---|---|
| 1 | La fila de KPI mezclaba periodos: casos de 2025 junto a porcentajes de 2013–2026 | Falta de rigor: el lector compara cifras que no son comparables | Todos los KPI se calculan sobre el **año de referencia** (por defecto 2025), y el título lo dice ("· 2025") |
| 2 | Títulos fijos que dejan de ser ciertos al filtrar (en 2025 el orden de los tipos cambia: física 36 %, sexual 34 %, negligencia 28 %) | Un título que miente con otro filtro rompe la veracidad | **Títulos dinámicos en DAX**: siempre describen lo que el usuario está viendo |
| 3 | Los gráficos no decían su periodo | Ambigüedad temporal | Subtítulo dinámico "Periodo seleccionado: …" |
| 4 | Línea **suavizada** | La interpolación curva inventa valores entre años y sugiere picos que no existen | Línea **recta** entre puntos anuales |
| 5 | La línea de promedio coincidía con la de casos | Error de contexto: la medida no quitaba el filtro de `Año_Etiqueta` | `ALL(Dim_Anio)` en la medida del promedio |
| 6 | Todas las barras de tipos salían en rojo | `ALL` sobre una columna con orden (`Orden_Tipo`) no quita ese filtro | `ALL(Dim_TipoViolencia)` sobre la tabla completa |
| 7 | 2026 parcial dibujado en la serie | Mostraba una caída falsa del 51 % | 2026\* se excluye de la línea y se dice en el subtítulo; las variaciones devuelven BLANK si el año es parcial |
| 8 | Edad × sexo en barras agrupadas | Costaba comparar dos barras pequeñas por fila | **Pirámide**: la asimetría se ve de un vistazo |
| 9 | Llamado a la acción genérico | Sin evidencia, no es accionable | Cuatro prioridades, cada una con su cifra |

## 3. Decisiones de diseño y su justificación teórica (para el PDF)

- **Elección de gráficos según la tarea** (Munzner, 2014; Cleveland y McGill, 1984):
  - Barras para comparar categorías: posición y longitud sobre una escala común.
  - Línea para una serie temporal continua.
  - Pirámide para comparar dos distribuciones simétricas.
  - Ninguna torta ni 3D. En tipos de violencia, una torta sería un error, porque los porcentajes no suman 100 %.
- **Línea recta, no suavizada:** solo hay datos anuales y unir con curvas inventa información (Tufte, 2001: integridad gráfica).
- **Eje de la línea sin forzar a cero:** la línea codifica pendiente y no longitud (Few, 2012). Las barras sí empiezan siempre en cero.
- **Gris + un acento (#B91C1C):** el color es un **atributo preatentivo** (Ware, 2012). El ojo encuentra el foco antes de leer:
  - 2025 en la línea,
  - el top 3 de localidades,
  - los agresores familiares,
  - el tipo más frecuente,
  - las mujeres en la pirámide.
- **Gestalt:**
  - **Semejanza:** todo lo rojo es "foco" y todo lo gris es "contexto".
  - **Proximidad:** los KPI agrupados en una fila; título y subtítulo juntos.
  - **Figura-fondo:** el promedio en gris punteado y la emocional en gris claro quedan como fondo.
  - **Continuidad:** la línea anual.
  - **Cierre:** las tarjetas sin bordes se perciben como unidades.
- **Datos-tinta** (Tufte, 2001; Few, 2012): sin bordes, fondos, sombras ni cuadrículas, y sin eje Y cuando hay etiquetas de datos.
- **Shneiderman (1996):** visión general (P1), filtro (segmentadores sincronizados), detalles bajo demanda (**tooltip de página** al pasar el mouse y **drill-through** por localidad).
- **Interacciones:** filtrado cruzado entre los gráficos de casos. El gráfico de tipos va en "Ninguno", porque su dimensión no filtra la tabla de casos y un clic engañaría al usuario.
- **Ética:**
  - Se habla de "casos notificados", no de tasas.
  - La caída de 2020 se anota como posible subregistro.
  - 2026 se marca como parcial.
  - Se conservan las filas duplicadas y los "Sin dato".

## 4. Checklist del nivel Estratégico

- [x] Se eliminó todo el caos visual: tema propio, sin bordes, fondos ni cuadrículas.
- [x] Atributos preatentivos que guían la atención: un acento, formato condicional por medidas.
- [x] Interacciones editadas con criterio: filtrado cruzado y "Ninguno" justificado.
- [x] Historia en tres actos con un llamado a la acción respaldado por datos.
- [x] Títulos que concluyen y que siguen siendo verdaderos con cualquier filtro.
- [x] Kit de storytelling de la Clase 10: navegador de páginas, drill-through, tooltip de página, segmentadores sincronizados.
- [ ] Opcional: marcadores Bing/Bang/Bongo con el navegador de marcadores. No es obligatorio en la rúbrica.
- [ ] PDF APA con esta justificación (pendiente).
