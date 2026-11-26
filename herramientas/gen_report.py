"""Genera las páginas y visuales PBIR del dashboard VIF Bogotá.
Uso: python gen_report.py <ruta a VIF_Bogota_Dashboard.Report> <ruta al tema json>
"""
import json, os, shutil, sys

REPORT = sys.argv[1]
THEME_SRC = sys.argv[2]
DEF = os.path.join(REPORT, "definition")
PAGES = os.path.join(DEF, "pages")
VC_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json"
PAGE_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
PAGES_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json"

TXT = "#1F2430"; GRIS_TXT = "#6B7280"; ACENTO = "#B91C1C"; GRIS = "#BDBDBD"; GRIS_HOMBRES = "#9CA3AF"

# ---------- helpers de expresiones ----------
def lit(v): return {"expr": {"Literal": {"Value": v}}}
def s(x): return "'" + x.replace("'", "''") + "'"
def n(x): return f"{x}D"
def b(x): return "true" if x else "false"
def color(hexv): return {"solid": {"color": lit(s(hexv))}}
def mref(name): return {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas"}}, "Property": name}}
def cref(ent, prop): return {"Column": {"Expression": {"SourceRef": {"Entity": ent}}, "Property": prop}}
def mcolor(name): return {"solid": {"color": {"expr": mref(name)}}}
def proj_m(name, display=None):
    p = {"field": mref(name), "queryRef": f"_Medidas.{name}", "nativeQueryRef": name}
    if display: p["displayName"] = display
    return p
def proj_c(ent, prop, active=None):
    p = {"field": cref(ent, prop), "queryRef": f"{ent}.{prop}", "nativeQueryRef": prop}
    if active is not None: p["active"] = active
    return p
def props(**kw): return [{"properties": kw}]

def container_objs(title=None, title_measure=None, title_size=11, subtitle=None, subtitle_measure=None):
    o = {
        "background": props(show=lit(b(False))),
        "border": props(show=lit(b(False))),
        "dropShadow": props(show=lit(b(False))),
        "subTitle": props(show=lit(b(False))),
    }
    if subtitle or subtitle_measure:
        st = {"show": lit(b(True)), "fontSize": lit(n(9)), "fontColor": color(GRIS_TXT),
              "alignment": lit(s("left")), "titleWrap": lit(b(True))}
        st["text"] = {"expr": mref(subtitle_measure)} if subtitle_measure else lit(s(subtitle))
        o["subTitle"] = [{"properties": st}]
    if title or title_measure:
        t = {"show": lit(b(True)), "fontSize": lit(n(title_size)), "fontColor": color(TXT),
             "alignment": lit(s("left")), "titleWrap": lit(b(True))}
        t["text"] = {"expr": mref(title_measure)} if title_measure else lit(s(title))
        o["title"] = [{"properties": t}]
    else:
        o["title"] = props(show=lit(b(False)))
    return o

def not_in_filter(name, ent, prop, value):
    return {
        "name": name, "field": cref(ent, prop), "type": "Categorical", "howCreated": "User",
        "filter": {"Version": 2, "From": [{"Name": "t", "Entity": ent, "Type": 0}],
                   "Where": [{"Condition": {"Not": {"Expression": {"In": {
                       "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": prop}}],
                       "Values": [[{"Literal": {"Value": s(value)}}]]}}}}}]},
    }

def container(name, x, y, w, h, visual, z=0, filters=None):
    vc = {"$schema": VC_SCHEMA, "name": name,
          "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
          "visual": visual}
    if filters: vc["filterConfig"] = {"filters": filters}
    return vc

# ---------- tipos de visual ----------
def textbox(name, x, y, w, h, paragraphs, z=0):
    vis = {"visualType": "textbox",
           "objects": {"general": [{"properties": {"paragraphs": paragraphs}}]},
           "visualContainerObjects": container_objs()}
    return container(name, x, y, w, h, vis, z)

def run(text, size, col=TXT, bold=False, font="Segoe UI"):
    st = {"fontSize": f"{size}pt", "color": col, "fontFamily": font}
    if bold: st["fontWeight"] = "bold"
    return {"value": text, "textStyle": st}

def card(name, x, y, w, h, measure, title=None, title_measure=None, value_color_measure=None, size=26, z=0, title_size=9):
    labels = {"fontSize": lit(n(size)), "fontFamily": lit(s("Segoe UI Semibold")), "labelDisplayUnits": lit(n(1))}
    labels["color"] = mcolor(value_color_measure) if value_color_measure else color(TXT)
    vis = {"visualType": "card",
           "query": {"queryState": {"Values": {"projections": [proj_m(measure)]}}},
           "objects": {"labels": [{"properties": labels}],
                       "categoryLabels": props(show=lit(b(False)))},
           "visualContainerObjects": container_objs(title, title_measure, title_size=title_size)}
    # título gris pequeño para tarjetas
    vis["visualContainerObjects"]["title"][0]["properties"]["fontColor"] = color(GRIS_TXT)
    return container(name, x, y, w, h, vis, z)

def slicer(name, x, y, w, h, ent, prop, header, group, z=0):
    vis = {"visualType": "slicer",
           "query": {"queryState": {"Values": {"projections": [proj_c(ent, prop, active=True)]}}},
           "objects": {"data": props(mode=lit(s("Dropdown"))),
                       "header": props(show=lit(b(True)), text=lit(s(header)), fontColor=color(GRIS_TXT),
                                       textSize=lit(n(9))),
                       "selection": props(selectAllCheckboxEnabled=lit(b(True)))},
           "visualContainerObjects": container_objs(),
           "syncGroup": {"groupName": group, "fieldChanges": True, "filterChanges": True}}
    return container(name, x, y, w, h, vis, z)

def bar_like(vtype, name, x, y, w, h, cat, measure, title, color_measure=None, sort_field=None,
             sort_dir="Descending", tooltips=(), series=None, series_colors=None, filters=None,
             label_units=None, z=0, title_measure=None, subtitle=None, subtitle_measure=None,
             tooltip_page=None):
    qs = {"Category": {"projections": [proj_c(*cat, active=True)]},
          "Y": {"projections": [proj_m(measure)]}}
    if series: qs["Series"] = {"projections": [proj_c(*series)]}
    if tooltips: qs["Tooltips"] = {"projections": [proj_m(t) for t in tooltips]}
    query = {"queryState": qs}
    if sort_field is not None:
        query["sortDefinition"] = {"sort": [{"field": sort_field, "direction": sort_dir}], "isDefaultSort": False}
    lab = {"show": lit(b(True)), "fontSize": lit(n(9)), "color": color(GRIS_TXT)}
    if label_units: lab["labelDisplayUnits"] = lit(n(label_units))
    objects = {
        "categoryAxis": props(show=lit(b(True)), fontSize=lit(n(9)), labelColor=color(GRIS_TXT),
                              showAxisTitle=lit(b(False)), gridlineShow=lit(b(False))),
        "valueAxis": props(show=lit(b(False)), start=lit(n(0)), showAxisTitle=lit(b(False)),
                           gridlineShow=lit(b(False))),
        "labels": [{"properties": lab}],
        "legend": props(show=lit(b(bool(series))), position=lit(s("Top")), fontSize=lit(n(9)),
                        labelColor=color(GRIS_TXT), showTitle=lit(b(False))),
    }
    dp = []
    if color_measure:
        dp.append({"properties": {"fill": mcolor(color_measure)},
                   "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}})
    if series_colors:
        ent, prop = series
        for val, hexv in series_colors.items():
            dp.append({"properties": {"fill": color(hexv)},
                       "selector": {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0,
                                    "Left": cref(ent, prop), "Right": {"Literal": {"Value": s(val)}}}}}]}})
    if not dp:
        dp.append({"properties": {"fill": color(GRIS)}})
    objects["dataPoint"] = dp
    vco = container_objs(title, title_measure, title_size=12, subtitle=subtitle, subtitle_measure=subtitle_measure)
    if tooltip_page:
        vco["visualTooltip"] = props(show=lit(b(True)), type=lit(s("Canvas")), section=lit(s(tooltip_page)))
    vis = {"visualType": vtype, "query": query, "objects": objects,
           "visualContainerObjects": vco, "drillFilterOtherVisuals": True}
    return container(name, x, y, w, h, vis, z, filters)

def in_filter(name, ent, prop, value):
    return {
        "name": name, "field": cref(ent, prop), "type": "Categorical", "howCreated": "User",
        "filter": {"Version": 2, "From": [{"Name": "t", "Entity": ent, "Type": 0}],
                   "Where": [{"Condition": {"In": {
                       "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": prop}}],
                       "Values": [[{"Literal": {"Value": s(value)}}]]}}}]},
    }

def line_chart(name, x, y, w, h, title_measure, subtitle, z=0, show_avg=True, title=None, compact=False):
    """Línea de casos por año (solo años completos) con el promedio 2013-2025 como referencia punteada."""
    ys = [proj_m("Total Casos", "Casos notificados")]
    if show_avg: ys.append(proj_m("Promedio Anual 2013-2025", "Promedio 2013–2025"))
    qs = {"Category": {"projections": [proj_c(*ANIO, active=True)]}, "Y": {"projections": ys},
          "Tooltips": {"projections": [proj_m("Variación % Interanual"), proj_m("Variación % vs Promedio")]}}
    query = {"queryState": qs,
             "sortDefinition": {"sort": [{"field": cref(*ANIO), "direction": "Ascending"}], "isDefaultSort": False}}
    avg = "_Medidas.Promedio Anual 2013-2025"; casos = "_Medidas.Total Casos"
    objects = {
        "categoryAxis": props(show=lit(b(True)), fontSize=lit(n(7 if compact else 9)), labelColor=color(GRIS_TXT),
                              showAxisTitle=lit(b(False)), gridlineShow=lit(b(False)),
                              axisType=lit(s("Categorical"))),
        "valueAxis": props(show=lit(b(False)), showAxisTitle=lit(b(False)), gridlineShow=lit(b(False))),
        "labels": [{"properties": {"show": lit(b(not compact)), "fontSize": lit(n(8)), "color": color(GRIS_TXT),
                                   "labelDisplayUnits": lit(n(1)), "labelPosition": lit(s("Above")),
                                   "enableBackground": lit(b(True)), "backgroundColor": color("#FFFFFF"), "backgroundTransparency": lit(n(0))}},
                   {"properties": {"show": lit(b(False))}, "selector": {"metadata": avg}}],
        "legend": props(show=lit(b(show_avg and not compact)), position=lit(s("Bottom")), fontSize=lit(n(9)),
                        labelColor=color(GRIS_TXT), showTitle=lit(b(False))),
        "dataPoint": [{"properties": {"fill": color(ACENTO)}, "selector": {"metadata": casos}},
                      {"properties": {"fill": color(GRIS_HOMBRES)}, "selector": {"metadata": avg}}],
        "lineStyles": [{"properties": {"lineChartType": lit(s("linear"))}},
                       {"properties": {"lineChartType": lit(s("linear")), "strokeWidth": lit(n(3)), "showMarker": lit(b(True)),
                                       "markerSize": lit(n(4))}, "selector": {"metadata": casos}},
                       {"properties": {"lineChartType": lit(s("linear")), "strokeWidth": lit(n(2)), "lineStyle": lit(s("dashed")),
                                       "showMarker": lit(b(False))}, "selector": {"metadata": avg}}],
    }
    vis = {"visualType": "lineChart", "query": query, "objects": objects,
           "visualContainerObjects": container_objs(title, title_measure, title_size=9 if compact else 12, subtitle=subtitle),
           "drillFilterOtherVisuals": True}
    return container(name, x, y, w, h, vis, z, [in_filter(f"f{name}Completo", "Dim_Anio", "Periodo", "Año completo")])

def pyramid_chart(name, x, y, w, h, title_measure, subtitle_measure, z=0):
    """Pirámide: hombres a la izquierda (valores negativos con formato positivo), mujeres a la derecha."""
    qs = {"Category": {"projections": [proj_c(*EDAD, active=True)]},
          "Y": {"projections": [proj_m("Casos Hombres Pirámide", "Hombres"), proj_m("Casos Mujeres", "Mujeres")]},
          "Tooltips": {"projections": [proj_m("Posicion Edad")]}}
    query = {"queryState": qs,
             "sortDefinition": {"sort": [{"field": mref("Posicion Edad"), "direction": "Descending"}], "isDefaultSort": False}}
    objects = {
        "categoryAxis": props(show=lit(b(True)), fontSize=lit(n(9)), labelColor=color(GRIS_TXT),
                              showAxisTitle=lit(b(False)), gridlineShow=lit(b(False))),
        "valueAxis": props(show=lit(b(True)), fontSize=lit(n(8)), labelColor=color(GRIS_TXT), showAxisTitle=lit(b(False)),
                           gridlineShow=lit(b(False)), labelDisplayUnits=lit(n(1000))),
        "labels": props(show=lit(b(True)), fontSize=lit(n(8)), color=color("#FFFFFF"), bold=lit(b(True)), labelDensity=lit(n(100)),
                        labelDisplayUnits=lit(n(1)), labelPosition=lit(s("InsideCenter")), labelOverflow=lit(b(True))),
        "legend": props(show=lit(b(True)), position=lit(s("Top")), fontSize=lit(n(9)), labelColor=color(GRIS_TXT),
                        showTitle=lit(b(False))),
        "layout": props(ribbonGapSize=lit(n(0))),
        "dataPoint": [
            {"properties": {"fill": color(GRIS_HOMBRES)}, "selector": {"metadata": "_Medidas.Casos Hombres Pirámide"}},
            {"properties": {"fill": color(ACENTO)}, "selector": {"metadata": "_Medidas.Casos Mujeres"}},
        ],
    }
    vis = {"visualType": "barChart", "query": query, "objects": objects,
           "visualContainerObjects": container_objs(None, title_measure, title_size=12, subtitle_measure=subtitle_measure),
           "drillFilterOtherVisuals": True}
    return container(name, x, y, w, h, vis, z)

def page_navigator(name, x, y, w, h, z=0):
    vis = {"visualType": "pageNavigator",
           "objects": {"pages": props(showHiddenPages=lit(b(False)), showTooltipPages=lit(b(False)))},
           "visualContainerObjects": {"title": props(show=lit(b(False))),
                                      "background": props(show=lit(b(False))),
                                      "border": props(show=lit(b(False)))}}
    return container(name, x, y, w, h, vis, z)

def back_button(name, x, y, w, h, z=0):
    default = {"id": "default"}
    vis = {"visualType": "actionButton",
           "objects": {"icon": [{"properties": {"show": lit(b(True)), "shapeType": lit(s("back")),
                                                "lineColor": color(GRIS_TXT), "lineWeight": lit(n(2))},
                                 "selector": default}],
                       "fill": [{"properties": {"show": lit(b(False))}, "selector": default}],
                       "outline": [{"properties": {"show": lit(b(True)), "lineColor": color("#D1D5DB")},
                                    "selector": default}],
                       "text": [{"properties": {"show": lit(b(True)), "text": lit(s("Volver")),
                                                "fontColor": color(GRIS_TXT), "fontSize": lit(n(10))},
                                 "selector": default}]},
           "visualContainerObjects": {"visualLink": props(show=lit(b(True)), type=lit(s("Back"))),
                                      "title": props(show=lit(b(False)))}}
    return container(name, x, y, w, h, vis, z)

# ---------- campos ----------
ANIO = ("Dim_Anio", "Año_Etiqueta"); LOC = ("Dim_Geografia", "Localidad"); UPZ = ("Dim_Geografia", "UPZ")
REL = ("Dim_Relacion", "Grupo_Relacion"); EDAD = ("Dim_Edad", "Grupo_Edad"); SEXO = ("Dim_Sexo", "Sexo")
TIPO = ("Dim_TipoViolencia", "Tipo_Violencia")

SUB = ("Casos notificados al SIVIM, 2013–2026*. *2026 incluye solo el primer semestre. "
       "Son casos notificados, no tasas: parte del aumento puede reflejar mayor notificación.")

FUENTE = ("Fuente: Secretaría Distrital de Salud de Bogotá (SDS) – SIVIM, «Violencia intrafamiliar y de género en Bogotá D.C.», "
          "Datos Abiertos Bogotá (CC BY 4.0), dato al 28/07/2026. Elaboración propia.")

def footer(prefix, z=90):
    return textbox(f"{prefix}Fuente", 24, 696, 1232, 22,
                   [{"textRuns": [run(FUENTE, 7.5, GRIS_TXT)]}], z=z)

def header_block(prefix, title, z0=0):
    return [
        textbox(f"{prefix}Titulo", 24, 10, 830, 84,
                [{"textRuns": [run(title, 18, TXT, True, "Segoe UI Semibold")]},
                 {"textRuns": [run(SUB, 9, GRIS_TXT)]}], z=z0),
        slicer(f"{prefix}SlAnio", 870, 4, 180, 52, *ANIO, "Año", "SyncAnio", z=z0 + 1),
        slicer(f"{prefix}SlLoc", 1070, 4, 186, 52, *LOC, "Localidad", "SyncLocalidad", z=z0 + 2),
        page_navigator(f"{prefix}Nav", 870, 60, 386, 34, z=z0 + 3),
    ]

def kpi_row(prefix, specs, y=100, z0=10):
    out = []
    for i, sp in enumerate(specs):
        out.append(card(f"{prefix}Kpi{i+1}", 24 + i * 212, y, 200, 112, z=z0 + i, **sp))
    return out

TOOLTIP_PAGE = "TooltipLocalidad"

# ---------- página 1: Panorama (Bing + Bang) ----------
p1 = "Panorama"
v1 = header_block("p1", "La violencia intrafamiliar notificada en Bogotá llegó a su máximo en 2025")
v1 += kpi_row("p1", [
    dict(measure="Casos Año Referencia", title_measure="Título Casos Año"),
    dict(measure="Variación % vs Promedio", title_measure="Título KPI Variación", value_color_measure="Color vs Promedio"),
    dict(measure="Variación % Interanual", title="FRENTE AL AÑO ANTERIOR", value_color_measure="Color Variación"),
    dict(measure="% Menores de 18 Año Ref", title_measure="Título KPI Menores"),
])
v1.append(line_chart("p1Serie", 24, 216, 830, 212, "Título Serie",
                     "Desde 2021 los casos suben cada año. La caída de 2020 coincide con la pandemia (posible subregistro). "
                     "2026* se excluye de la serie por estar incompleto.", z=20))
v1.append(bar_like("clusteredBarChart", "p1Rel", 24, 432, 830, 262, REL, "% del Total Visible", None,
                   title_measure="Título Relación", subtitle_measure="Texto Periodo",
                   color_measure="Color Relación Familiar", sort_field=mref("% del Total Visible"),
                   tooltips=("Total Casos",), z=21))
v1.append(bar_like("clusteredBarChart", "p1Loc", 870, 100, 386, 566, LOC, "Total Casos", None,
                   title_measure="Título Localidades", subtitle_measure="Subtítulo Localidades",
                   color_measure="Color Top 3 Localidades", sort_field=mref("Total Casos"),
                   tooltips=("% del Total Bogotá", "Ranking Localidad"), label_units=1,
                   filters=[not_in_filter("fLocSinDato", *LOC, "Sin dato")], tooltip_page=TOOLTIP_PAGE, z=22))
v1.append(textbox("p1NotaLoc", 870, 666, 386, 30,
                  [{"textRuns": [run("Pasa el mouse para ver la tendencia de cada localidad; clic derecho → Obtener detalles. "
                                     "Se excluyen 154 casos sin localidad.", 8, GRIS_TXT)]}], z=23))
v1.append(footer("p1"))
i1 = []
charts1 = ["p1Serie", "p1Rel", "p1Loc"]
targets1 = charts1 + [f"p1Kpi{i}" for i in range(1, 5)]
for src in charts1:
    for tgt in targets1:
        if src != tgt: i1.append({"source": src, "target": tgt, "type": "DataFilter"})

# ---------- página 2: Víctimas y violencias (Bongo) ----------
p2 = "Victimas"
v2 = header_block("p2", "Víctimas: sobre todo niñas y niños, y desde la adolescencia, mujeres")
v2 += kpi_row("p2", [
    dict(measure="% Mujeres Año Ref", title_measure="Título KPI Mujeres"),
    dict(measure="% Agresor Familiar Año Ref", title_measure="Título KPI Familiar"),
    dict(measure="Violencia Sexual Año Ref", title_measure="Título KPI Sexual"),
    dict(measure="% Vivienda Año Ref", title_measure="Título KPI Vivienda"),
])
v2.append(pyramid_chart("p2Edad", 24, 222, 620, 472, "Título Edad", "Texto Periodo", z=20))
v2.append(bar_like("clusteredBarChart", "p2Tipo", 664, 222, 592, 252, TIPO, "% de Casos con este Tipo", None,
                   title_measure="Título Tipos", subtitle_measure="Texto Periodo",
                   color_measure="Color Tipo Violencia", sort_field=mref("% de Casos con este Tipo"),
                   tooltips=("Total Hechos de Violencia",), z=21))
v2.append(textbox("p2NotaTipo", 664, 474, 592, 22,
                  [{"textRuns": [run("Un caso puede tener varios tipos (no suma 100 %). La emocional figura en casi todos por la codificación del SIVIM.", 8, GRIS_TXT)]}], z=22))
v2.append(textbox("p2Accion", 664, 498, 592, 196, [
    {"textRuns": [run("¿Dónde actuar? Propuesta para 2027", 12, ACENTO, True, "Segoe UI Semibold")]},
    {"textRuns": [run("En 2025, el 77 % de los agresores fue un familiar y el 79 % de los hechos ocurrió en la vivienda.", 9, TXT)]},
    {"textRuns": [run("1. Hogar · Integración Social y SDS: ", 9, TXT, True),
                  run("piloto de 6 meses de acompañamiento a familias con niñas y niños notificados; meta: seguimiento a todos los casos de menores en las UPZ piloto.", 9, TXT)]},
    {"textRuns": [run("2. Escuela · Secretaría de Educación: ", 9, TXT, True),
                  run("activar la ruta de violencia sexual en los colegios, donde ocurrió el 29 % de la violencia sexual de 2025; plazo: año escolar 2027.", 9, TXT)]},
    {"textRuns": [run("3. Mujeres de 18 a 44 años · Secretaría de la Mujer: ", 9, TXT, True),
                  run("son casi 9 de cada 10 víctimas de esa edad; meta: contacto y seguimiento de cada caso notificado en los 30 días siguientes.", 9, TXT)]},
    {"textRuns": [run("4. Territorio · SDS: ", 9, TXT, True),
                  run("calcular tasas con las proyecciones del DANE antes de priorizar por riesgo; hoy Ciudad Bolívar, Bosa y Kennedy concentran casi 4 de cada 10 casos por volumen.", 9, TXT)]},
], z=23))
v2.append(footer("p2"))
i2 = [{"source": "p2Edad", "target": t, "type": "DataFilter"} for t in ["p2Tipo"] + [f"p2Kpi{i}" for i in range(1, 5)]]
i2 += [{"source": "p2Tipo", "target": t, "type": "NoFilter"} for t in ["p2Edad"] + [f"p2Kpi{i}" for i in range(1, 5)]]

# ---------- página 3: Detalle localidad (drill-through) ----------
p3 = "DetalleLocalidad"
v3 = [
    card("p3Titulo", 24, 10, 1100, 64, "Título Detalle Localidad", size=20, z=0),
    back_button("p3Volver", 1150, 20, 106, 40, z=1),
]
v3 += kpi_row("p3", [
    dict(measure="Variación % vs Promedio", title_measure="Título KPI Variación", value_color_measure="Color vs Promedio"),
    dict(measure="% Mujeres Año Ref", title_measure="Título KPI Mujeres"),
    dict(measure="% Menores de 18 Año Ref", title_measure="Título KPI Menores"),
    dict(measure="% Agresor Familiar Año Ref", title_measure="Título KPI Familiar"),
], y=90)
v3.append(line_chart("p3Serie", 24, 222, 600, 470, None,
                     "Casos notificados por año (años completos) frente al promedio 2013–2025 de la localidad.",
                     z=20, title="Evolución de los casos en la localidad"))
v3.append(bar_like("clusteredBarChart", "p3Upz", 644, 222, 612, 470, UPZ, "Total Casos",
                   "Casos por UPZ de residencia", sort_field=mref("Total Casos"), subtitle_measure="Texto Periodo",
                   tooltips=("% del Total Visible",), label_units=1,
                   filters=[not_in_filter("fUpzSinDato", *UPZ, "Sin dato")], z=21))
v3.append(footer("p3"))
i3 = [{"source": "p3Serie", "target": "p3Upz", "type": "DataFilter"},
      {"source": "p3Upz", "target": "p3Serie", "type": "DataFilter"}]
drill_filter = {"name": "fDrillLocalidad", "field": cref(*LOC), "type": "Categorical", "howCreated": "Drillthrough"}

# ---------- página 4: tooltip de localidad ----------
p4 = TOOLTIP_PAGE
v4 = [
    card("p4Casos", 8, 2, 148, 80, "Casos Año Referencia", title_measure="Título Casos Año", size=16, z=0, title_size=7),
    card("p4Var", 164, 2, 148, 80, "Variación % vs Promedio", title="VS. PROMEDIO 2013–2025",
         value_color_measure="Color vs Promedio", size=16, z=1, title_size=7),
    line_chart("p4Serie", 4, 86, 312, 150, None, None, z=2, show_avg=True,
               title="Casos por año (línea gris: promedio 2013–2025)", compact=True),
]

pages = [
    (p1, "1 · Panorama", v1, i1, None),
    (p2, "2 · Víctimas y violencias", v2, i2, None),
    (p3, "Detalle localidad", v3, i3, "drill"),
    (p4, "Tooltip localidad", v4, [], "tooltip"),
]

# ---------- escribir ----------
def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

for d in os.listdir(PAGES):
    full = os.path.join(PAGES, d)
    if os.path.isdir(full):
        shutil.rmtree(full)

for pname, display, visuals, inter, kind in pages:
    page = {"$schema": PAGE_SCHEMA, "name": pname, "displayName": display, "displayOption": "FitToPage",
            "height": 720, "width": 1280, "visualInteractions": inter}
    if kind == "tooltip":
        page.update({"height": 240, "width": 320, "type": "Tooltip", "visibility": "HiddenInViewMode",
                     "pageBinding": {"name": "pbTooltipLocalidad", "type": "Tooltip"}})
    if kind == "drill":
        page["filterConfig"] = {"filters": [drill_filter]}
        page["pageBinding"] = {"name": "pbDrillLocalidad", "type": "Drillthrough", "acceptsFilterContext": "Default",
                               "parameters": [{"name": "prmLocalidad", "boundFilter": "fDrillLocalidad",
                                               "fieldExpr": cref(*LOC)}]}
        page["visibility"] = "HiddenInViewMode"
    dump(os.path.join(PAGES, pname, "page.json"), page)
    names = set()
    for v in visuals:
        assert v["name"] not in names, v["name"]; names.add(v["name"])
        dump(os.path.join(PAGES, pname, "visuals", v["name"], "visual.json"), v)

dump(os.path.join(PAGES, "pages.json"), {"$schema": PAGES_SCHEMA, "pageOrder": [p[0] for p in pages],
                                          "activePageName": p1})

# ---------- tema personalizado ----------
rep_path = os.path.join(DEF, "report.json")
rep = json.load(open(rep_path, encoding="utf-8"))
theme_name = "Tema_VIF_Bogota.json"
dst = os.path.join(REPORT, "StaticResources", "RegisteredResources", theme_name)
os.makedirs(os.path.dirname(dst), exist_ok=True)
shutil.copyfile(THEME_SRC, dst)
rep["themeCollection"]["customTheme"] = {
    "name": theme_name, "reportVersionAtImport": rep["themeCollection"]["baseTheme"]["reportVersionAtImport"],
    "type": "RegisteredResources"}
rep["resourcePackages"] = [p for p in rep["resourcePackages"] if p["name"] != "RegisteredResources"]
rep["resourcePackages"].append({"name": "RegisteredResources", "type": "RegisteredResources",
                                "items": [{"name": theme_name, "path": theme_name, "type": "CustomTheme"}]})
dump(rep_path, rep)
print("Páginas:", [p[0] for p in pages], "visuales:", sum(len(p[2]) for p in pages))
