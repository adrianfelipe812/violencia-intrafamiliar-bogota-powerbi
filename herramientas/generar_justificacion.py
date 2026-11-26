"""Genera el PDF de justificación del proyecto integrador (máx. 4 páginas, APA 7.ª ed.).

Uso: python generar_justificacion.py <carpeta con modelo.png, pagina1.png, pagina2.png> <pdf de salida>
"""
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, Paragraph as _P, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

IMG = Path(sys.argv[1]); SALIDA = Path(sys.argv[2])

def Paragraph(texto, estilo):
    """Espacio no separable antes de % para que número y signo no se partan."""
    return _P(texto.replace(" %", "\u00a0%").replace("s. f.", "s.\u00a0f."), estilo)

pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-B", "C:/Windows/Fonts/arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Arial-I", "C:/Windows/Fonts/ariali.ttf"))
pdfmetrics.registerFont(TTFont("Arial-BI", "C:/Windows/Fonts/arialbi.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-B", italic="Arial-I", boldItalic="Arial-BI")

ACENTO = colors.HexColor("#B91C1C"); GRIS = colors.HexColor("#4B5563"); OSCURO = colors.HexColor("#1F2430")
S_TIT = ParagraphStyle("tit", fontName="Arial-B", fontSize=13.2, leading=16.5, spaceAfter=3)
S_AUT = ParagraphStyle("aut", fontName="Arial", fontSize=8.8, leading=11.5, textColor=GRIS, spaceAfter=6)
S_H = ParagraphStyle("h", fontName="Arial-B", fontSize=10.4, leading=13, spaceBefore=6, spaceAfter=2.5, textColor=ACENTO, keepWithNext=1)
S_P = ParagraphStyle("p", fontName="Arial", fontSize=9.1, leading=11.7, alignment=TA_JUSTIFY, spaceAfter=3.5)
S_GI = ParagraphStyle("gi", parent=S_P, fontName="Arial-B", fontSize=9.8, leading=13, backColor=colors.HexColor("#FDECEC"),
                      borderPadding=(5, 7, 5, 7), spaceBefore=3, spaceAfter=8, leftIndent=7, rightIndent=7)
S_FIG = ParagraphStyle("fig", fontName="Arial-B", fontSize=8.8, leading=11, spaceBefore=4)
S_FIGT = ParagraphStyle("figt", fontName="Arial-I", fontSize=8.8, leading=11, spaceAfter=2)
S_NOTA = ParagraphStyle("nota", fontName="Arial", fontSize=7.6, leading=9.6, textColor=GRIS, spaceAfter=5,
                        alignment=TA_JUSTIFY)
S_T = ParagraphStyle("t", fontName="Arial", fontSize=7.6, leading=9.4)
S_TB = ParagraphStyle("tb", parent=S_T, fontName="Arial-B", textColor=colors.white)
S_TC = ParagraphStyle("tc", parent=S_T, fontName="Courier", fontSize=7.0, leading=8.8)
S_REF = ParagraphStyle("ref", fontName="Arial", fontSize=8.1, leading=10.0, leftIndent=18, firstLineIndent=-18,
                       spaceAfter=1.5)

ANCHO = LETTER[0] - 2 * 2.0 * cm

def tabla(filas, anchos, mono_col=None):
    data = []
    for i, f in enumerate(filas):
        fila = []
        for j, c in enumerate(f):
            est = S_TB if i == 0 else (S_TC if (mono_col is not None and j == mono_col) else S_T)
            fila.append(Paragraph(c, est))
        data.append(fila)
    t = Table(data, colWidths=[a * ANCHO for a in anchos], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), OSCURO),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#D1D5DB")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.5), ("RIGHTPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    return t

def figura(num, titulo, ruta, ancho_cm, nota):
    from PIL import Image as PI
    w, h = PI.open(ruta).size
    img = Image(str(ruta), width=ancho_cm * cm, height=ancho_cm * cm * h / w)
    return KeepTogether([Paragraph(f"Figura {num}", S_FIG), Paragraph(titulo, S_FIGT), img,
                         Paragraph(f"<i>Nota.</i> {nota}", S_NOTA)])

h = []
h.append(Paragraph("Violencia intrafamiliar y de género en Bogotá: arquitectura, análisis y diseño ético de un "
                   "dashboard corporativo en Power BI", S_TIT))
h.append(Paragraph("Adrian Felipe Grateron Ramirez, Jhonatan Smith Doncel y Jorge Emmanuel Marin<br/>"
                   "Maestría en Ciencia de Datos, Universidad Santo Tomás · Visualización de Datos · "
                   "Docente: Diana Angélica Pulido López · 26 de noviembre de 2026", S_AUT))

# 1 ------------------------------------------------------------------
h.append(Paragraph("1. Propósito y Gran Idea", S_H))
h.append(Paragraph("En 2025 se notificaron 52.493 casos de violencia intrafamiliar en Bogotá, la cifra más alta de la "
                   "serie y un 46 % más que el promedio 2013–2025. La violencia ocurre en casa, la ejerce la propia "
                   "familia y recae sobre todo en niñas, niños y mujeres.", S_GI))
h.append(Paragraph(
    "Pensamos el tablero para los equipos de la Secretaría Distrital de Salud y de la Secretaría de la Mujer, que toman "
    "decisiones sin ser especialistas en datos. La historia avanza en tres actos (Nussbaumer Knaflic, 2015): qué está "
    "pasando (tendencia e indicadores), quién agrede y dónde (relación con el agresor y localidades) y a quién afecta y "
    "dónde actuar (pirámide de edad y sexo, tipos de violencia y propuestas). Sobre ese arco aplicamos el Bing-Bang-Bongo, "
    "que consiste en repetir el mensaje central tres veces (Pulido López, 2026b): lo anunciamos en el título de la página 1, "
    "lo demostramos con los títulos de los gráficos y lo repetimos en el recuadro «¿Dónde actuar?», ya convertido en "
    "decisiones.", S_P))

# 2 ------------------------------------------------------------------
h.append(Paragraph("2. Datos y proceso ETL en Power Query (lenguaje M)", S_H))
h.append(Paragraph(
    "Trabajamos con datos abiertos y oficiales. Usamos el conjunto <i>Violencia intrafamiliar y de género en Bogotá "
    "D.C.</i>, que publica la Secretaría Distrital de Salud [SDS] (2026) a partir del Subsistema de Vigilancia "
    "Epidemiológica de la Violencia Intrafamiliar y de Género (SIVIM), con licencia CC BY 4.0. Cada fila es un caso "
    "notificado: son 492.837 registros y 23 columnas entre 2013 y 2026, aunque de 2026 solo está el primer semestre. "
    "Antes de transformar nada revisamos el perfil de todas las filas (no solo las 1.000 que Power BI toma por defecto) "
    "y anotamos cifras de control para comprobar después que la carga no perdiera ni duplicara casos.", S_P))
h.append(Paragraph(
    "Organizamos el proceso en capas para que se pueda seguir y repetir (Microsoft, s. f.-c). Dos parámetros guardan la "
    "ruta del archivo y el último año completo, así que basta cambiarlos para correr todo en otro equipo. La consulta "
    "<i>VIF_Origen</i> solo lee el CSV y asigna tipos de dato, y <i>VIF_Limpia</i> reúne toda la depuración. Las dos son "
    "consultas de apoyo con la carga deshabilitada y de ellas salen las 12 tablas del modelo. Al limpiar seguimos una "
    "regla simple: corregir el error y conservar el dato incómodo pero real (Pulido López, 2026a). La Tabla 1 resume cada "
    "decisión.", S_P))
h.append(Paragraph("Tabla 1", S_FIG)); h.append(Paragraph("Decisiones de depuración en Power Query", S_FIGT))
h.append(tabla([
    ["Lo que encontramos al perfilar", "Filas", "Qué hicimos y por qué"],
    ["Espacios, vacíos y «Localidad Desconocida»", "154", "Limpiamos el texto (<i>Text.Trim</i>, <i>Text.Clean</i>) y los marcamos como «Sin dato»."],
    ["Grupos de edad mal escritos («14 - 17 años», «De 30 - 34 años»)", "3", "Los unimos con el grupo oficial que les corresponde."],
    ["UPZ asignada a una localidad que no es la suya", "160", "Dejamos la localidad, que es nuestra unidad de análisis, y pasamos la UPZ a «Sin dato» para no inventar una ubicación."],
    ["«Mujer gestante» registrada como relación con el agresor", "16.865", "No es una relación posible, así que la reclasificamos como «Sin dato»."],
    ["Hombre marcado como gestante", "1", "Lo corregimos a 0 porque contradice la columna de sexo."],
    ["El mismo país escrito de varias formas", "≈14.000", "Lo agrupamos en nacionalidad colombiana, venezolana u otra."],
    ["EPS con 279 nombres inconsistentes", "—", "La dejamos fuera: no responde ninguna pregunta del tablero y no podíamos verificar su limpieza."],
    ["Filas idénticas", "45.339", "Las conservamos. Sin un identificador son víctimas distintas con los mismos datos anonimizados; borrarlas quitaría cerca del 9 % de los casos."],
    ["«Sin dato» en orientación, estrato, educación y estado civil", "≤172.787", "Los conservamos como una categoría más, porque ocultarlos cambiaría las proporciones."],
    ["Tipo de violencia repartido en seis columnas de lugar", "—", "Las despivotamos (<i>Table.Unpivot</i>) en una segunda tabla de hechos; «Sin dato» significa que ese tipo no ocurrió."],
], [0.37, 0.09, 0.54]))
h.append(Paragraph(
    "<i>Nota.</i> El conjunto no tiene variables numéricas continuas, así que no había atípicos que quitar; los 24 casos de "
    "100 a 105 años son posibles y los dejamos. Después de cargar, todas las tablas coincidieron con las cifras de control.",
    S_NOTA))

# 3 ------------------------------------------------------------------
h.append(Paragraph("3. Arquitectura del modelo: esquema en estrella", S_H))
h.append(Paragraph(
    "La idea del modelo es separar lo que medimos de aquello por lo que filtramos (Kimball y Ross, 2013). Un mismo caso "
    "puede sufrir varios tipos de violencia, y por eso usamos dos tablas de hechos con niveles de detalle distintos: "
    "<i>Hechos_Casos</i> tiene una fila por víctima y <i>Hechos_TipoViolencia</i> una fila por cada tipo que sufrió cada "
    "caso (1.006.182 filas). Si contáramos víctimas en la segunda tabla, la cifra saldría casi al doble, así que cada medida "
    "usa la tabla que le corresponde. Las dos comparten ocho dimensiones y forman una constelación de estrellas (Figura 1).",
    S_P))
h.append(Paragraph(
    "Las 18 relaciones son de uno a muchos y el filtro viaja en una sola dirección, de la dimensión hacia los hechos. No "
    "usamos relaciones bidireccionales ni de muchos a muchos, y las dos tablas de hechos no se conectan entre sí. Cada "
    "llave de dimensión es única (en Geografía y Perfil combinamos dos o más campos) y una consulta en DAX confirmó que no "
    "quedó ninguna fila sin pareja. Dejamos localidad y UPZ en la misma dimensión para no formar un copo de nieve, y "
    "agrupamos en <i>Dim_Perfil</i> cinco atributos socioeconómicos de la víctima. Como la fuente solo trae el año, la "
    "dimensión de tiempo es anual y marca 2026 como parcial. También desactivamos la fecha y hora automática y las "
    "medidas implícitas (<i>discourageImplicitMeasures</i>).", S_P))
h.append(figura(1, "Modelo semántico: dos tablas de hechos y diez dimensiones", IMG / "modelo.png", 11.8,
                "Las flechas indican la dirección del filtro, de la dimensión a los hechos. Elaboración propia."))

# 4 ------------------------------------------------------------------
h.append(Paragraph("4. Cálculos analíticos en DAX", S_H))
h.append(Paragraph(
    "Todas las cifras del tablero salen de fórmulas escritas por nosotros, no de sumas automáticas. Son 54 medidas "
    "explícitas reunidas en la tabla <i>_Medidas</i> (Microsoft, s. f.-b). No creamos columnas calculadas en DAX: lo que "
    "había que derivar se hizo en Power Query. En toda división usamos <i>DIVIDE</i>, que devuelve un vacío en lugar de un "
    "error que deforme el gráfico, y en las medidas largas usamos <i>VAR/RETURN</i> para que se puedan leer. La Tabla 2 "
    "muestra las principales.", S_P))
h.append(Paragraph("Tabla 2", S_FIG)); h.append(Paragraph("Indicadores principales y su lógica", S_FIGT))
h.append(tabla([
    ["Medida", "Expresión (núcleo)", "Qué hace y por qué"],
    ["% Agresor Familiar", "DIVIDE(CALCULATE([Total Casos], Dim_Relacion[Es_Familiar]=1), [Total Casos])",
     "CALCULATE cambia el contexto de filtro. El denominador incluye los «Sin dato» para no inflar el porcentaje."],
    ["Casos Año Referencia", "VAR _A=[Año Referencia] RETURN CALCULATE([Total Casos], REMOVEFILTERS(Dim_Anio), Dim_Anio[Año]=_A)",
     "Toma el año elegido o, si no hay uno, el último año completo. Nunca usa 2026 por defecto."],
    ["Variación % vs Promedio", "AVERAGEX(FILTER(ALL(Dim_Anio), [Es_Anio_Completo]=1), [Total Casos])",
     "Recorre los años completos (transición de contexto). Si el año es parcial queda vacía, para no mostrar una falsa caída del 51 %."],
    ["Ranking Localidad", "RANKX(ALLSELECTED(Dim_Geografia[Localidad]), [Total Casos],, DESC, DENSE)",
     "Ordena las localidades según lo filtrado y decide cuáles tres van en rojo."],
    ["% del Total Visible / Bogotá", "DIVIDE([Total Casos], CALCULATE([Total Casos], ALLSELECTED()))",
     "Con ALLSELECTED da el % de lo que se está viendo; con REMOVEFILTERS(Dim_Geografia), el % de toda la ciudad."],
    ["% de Casos con este Tipo", "DIVIDE([Total Hechos de Violencia], [Total Casos])",
     "Cruza las dos tablas de hechos por las dimensiones compartidas. No suma 100 % porque un caso puede tener varios tipos."],
], [0.2, 0.43, 0.37], mono_col=1))
h.append(Paragraph(
    "<i>Nota.</i> Al revisar los resultados encontramos un error de contexto: el promedio anual salía igual al valor de cada "
    "año, porque <i>ALL(columna)</i> no quitaba el filtro de su columna de orden (<i>sortByColumn</i>). Lo corregimos con "
    "<i>ALL(tabla)</i> y volvimos a comparar con las cifras de control.", S_NOTA))

# 5 ------------------------------------------------------------------
h.append(Paragraph("5. Diseño visual: Gestalt, color y atributos preatentivos", S_H))
h.append(figura(2, "Página 1 · Panorama (planteamiento y conflicto)", IMG / "pagina1.png", 16.2,
                "Exportación del tablero con los filtros por defecto. Fuente: SDS (2026). Elaboración propia."))
h.append(Paragraph(
    "<b>Cada gráfico responde a una tarea.</b> Escogimos la forma según lo que el lector necesita hacer (Munzner, 2014). "
    "Para comparar categorías usamos barras horizontales ordenadas, porque el ojo compara mejor longitudes sobre una "
    "misma escala que ángulos o áreas (Cleveland y McGill, 1984). La serie anual es una línea recta entre punto y punto: "
    "una línea suavizada inventaría valores entre un año y otro (Tufte, 2001). Su eje no arranca en cero porque lo que "
    "importa es la pendiente, mientras que las barras siempre empiezan en cero (Few, 2012). Para comparar hombres y "
    "mujeres por edad usamos una pirámide. No hay tortas ni gráficos 3D; en los tipos de violencia una torta sería "
    "incluso incorrecta, porque los porcentajes no suman 100 %.", S_P))
h.append(Paragraph(
    "<b>El color señala lo importante.</b> Todo está en gris salvo un solo rojo (#B91C1C), que funciona como atributo "
    "preatentivo: el ojo lo encuentra antes de empezar a leer (Ware, 2012). Ese rojo lo asignan medidas de DAX por formato "
    "condicional y marca 2025 en la línea, las tres localidades con más casos, los agresores familiares, el tipo de "
    "violencia más frecuente y las mujeres en la pirámide. También aplicamos principios de la Gestalt (Ware, 2012). Por semejanza, el "
    "rojo se lee como foco y el gris como contexto. Por proximidad, los indicadores forman una fila y el título va pegado a "
    "su subtítulo. Por figura-fondo, el promedio (gris punteado) y la violencia emocional (gris claro, porque el SIVIM la "
    "registra en casi todos los casos) quedan atrás. Por continuidad, la línea guía la lectura en el tiempo, y por cierre, las tarjetas "
    "se perciben como bloques aunque no tengan bordes. Para cuidar la proporción datos-tinta creamos un tema sin bordes, "
    "fondos, sombras ni cuadrículas, y ocultamos el eje cuando las barras ya tienen sus etiquetas (Tufte, 2001).", S_P))
h.append(Paragraph(
    "<b>La historia y la interacción.</b> Los títulos dicen la conclusión y se calculan en DAX, así que siguen siendo "
    "ciertos aunque el usuario cambie los filtros. Los subtítulos indican el periodo. Los indicadores de arriba usan el "
    "año de referencia y ninguno repite una cifra que ya muestre un gráfico, para que el lector no vea dos valores para lo "
    "mismo. Seguimos la idea de Shneiderman (1996): primero la visión general (página 1), luego el "
    "filtro (segmentadores de año y localidad sincronizados y un navegador de páginas) y por último el detalle cuando se "
    "pide. Ese detalle está en dos páginas ocultas que se abren desde el gráfico de localidades: un tooltip con la tendencia "
    "de cada una y una página de obtención de detalles por UPZ. En <i>Editar interacciones</i> elegimos el filtrado cruzado "
    "en lugar del resaltado, porque recalcula los gráficos en vez de dejar barras a medio pintar. El gráfico de tipos quedó "
    "en «Ninguno», porque su dimensión no filtra la tabla de casos y un clic ahí haría creer que se filtró algo que no "
    "cambió (Microsoft, s. f.-a). En el recuadro de acción cada prioridad tiene un responsable y un plazo o una meta; son "
    "propuestas del equipo, no compromisos de las entidades.", S_P))
h.append(figura(3, "Página 2 · Víctimas y violencias (resolución)", IMG / "pagina2.png", 16.2,
                "Los indicadores corresponden al año de referencia (2025) y los gráficos al periodo seleccionado. Fuente: SDS (2026). "
                "Elaboración propia."))
h.append(Paragraph(
    "<b>Ética y límites.</b> Hablamos de casos notificados y no de tasas: sin la población de cada localidad no podemos "
    "calcular incidencia, y parte del aumento puede deberse a que hoy se notifica más. La caída de 2020 la señalamos como "
    "un posible subregistro durante la pandemia. Las tres localidades con más casos están entre las más pobladas, así que "
    "en el tablero aclaramos que los conteos muestran volumen de atención y no riesgo, y proponemos calcular tasas antes de "
    "priorizar territorios: presentar conteos como riesgo puede estigmatizar a quienes viven allí (Cairo, 2019). La fuente no trae mes ni semestre, así que 2026 (primer semestre) no se "
    "compara en volumen con años completos; anualizarlo exigiría suponer un comportamiento por temporadas que no podemos "
    "verificar. De 2026 solo analizamos su composición: porcentajes por edad, agresor, tipo y localidad. La fuente aparece "
    "en el pie de página del tablero, y para actualizar los datos basta con cambiar el parámetro <i>pRutaCSV</i>.", S_P))

# Referencias ---------------------------------------------------------
h.append(Paragraph("Referencias", S_H))
refs = [
    "Cairo, A. (2019). <i>How charts lie: Getting smarter about visual information</i>. W. W. Norton &amp; Company.",
    "Cleveland, W. S., & McGill, R. (1984). Graphical perception: Theory, experimentation, and application to the "
    "development of graphical methods. <i>Journal of the American Statistical Association, 79</i>(387), 531–554. "
    "https://doi.org/10.1080/01621459.1984.10478080",
    "Few, S. (2012). <i>Show me the numbers: Designing tables and graphs to enlighten</i> (2.ª ed.). Analytics Press.",
    "Kimball, R., & Ross, M. (2013). <i>The data warehouse toolkit: The definitive guide to dimensional modeling</i> "
    "(3.ª ed.). Wiley.",
    "Microsoft. (s. f.-a). <i>Documentación de Power BI: guías, tutoriales y referencias</i>. Microsoft Learn. "
    "https://learn.microsoft.com/es-es/power-bi/",
    "Microsoft. (s. f.-b). <i>Referencia de Data Analysis Expressions (DAX)</i>. Microsoft Learn. "
    "https://learn.microsoft.com/es-es/dax/",
    "Microsoft. (s. f.-c). <i>Documentación de Power Query: transformación y preparación de datos</i>. Microsoft Learn. "
    "https://learn.microsoft.com/es-es/power-query/",
    "Munzner, T. (2014). <i>Visualization analysis and design</i>. CRC Press.",
    "Nussbaumer Knaflic, C. (2015). <i>Storytelling with data: A data visualization guide for business professionals</i>. Wiley.",
    "Pulido López, D. A. (2026a). <i>Sesión 7. Power BI: BI de autoservicio + Power Query</i> [Presentación de clase]. "
    "Universidad Santo Tomás.",
    "Pulido López, D. A. (2026b, 14 de mayo). <i>Video de profundización Sección 3: Storytelling con datos en Power BI</i> "
    "[Video]. YouTube. https://www.youtube.com/watch?v=aW1obeVA6Uc",
    "Secretaría Distrital de Salud. (2026). <i>Violencia intrafamiliar y de género en Bogotá D.C.</i> [Conjunto de datos]. "
    "Datos Abiertos Bogotá. Recuperado el 25 de noviembre de 2026, de "
    "https://datosabiertos.bogota.gov.co/dataset/numero-de-casos-de-violencia-intrafamiliar",
    "Shneiderman, B. (1996). The eyes have it: A task by data type taxonomy for information visualizations. En "
    "<i>Proceedings 1996 IEEE Symposium on Visual Languages</i> (pp. 336–343). IEEE. https://doi.org/10.1109/VL.1996.545307",
    "Tufte, E. R. (2001). <i>The visual display of quantitative information</i> (2.ª ed.). Graphics Press.",
    "Ware, C. (2012). <i>Information visualization: Perception for design</i> (3.ª ed.). Morgan Kaufmann.",
]
h += [Paragraph(r, S_REF) for r in refs]

def pie(canvas, doc):
    canvas.saveState(); canvas.setFont("Arial", 7.5); canvas.setFillColor(GRIS)
    canvas.drawRightString(LETTER[0] - 2.0 * cm, 1.1 * cm, str(doc.page)); canvas.restoreState()

doc = SimpleDocTemplate(str(SALIDA), pagesize=LETTER, leftMargin=2.0 * cm, rightMargin=2.0 * cm,
                        topMargin=1.6 * cm, bottomMargin=1.6 * cm,
                        title="Justificación del dashboard de violencia intrafamiliar en Bogotá",
                        author="Grateron, Doncel y Marin")
doc.build(h, onFirstPage=pie, onLaterPages=pie)
from pypdf import PdfReader
print("páginas:", len(PdfReader(str(SALIDA)).pages))
