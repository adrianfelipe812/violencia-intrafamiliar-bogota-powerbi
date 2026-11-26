# ETL en Power Query (M) — Violencia intrafamiliar y de género, Bogotá (SIVIM)

Fuente: Secretaría Distrital de Salud, *Violencia intrafamiliar y de género en Bogotá D.C.*, Datos Abiertos Bogotá (CC BY 4.0). Fecha del dato: 2026-07-28.
Archivo: `osb_saludmental-vintrafamiliar.csv` (UTF-8 con BOM, separador `;`). Grano: **1 fila = 1 caso notificado**. Son 492.837 casos entre 2013 y 2026; 2026 es parcial.

## Arquitectura de consultas

| Consulta | Carga | Rol |
|---|---|---|
| `pRutaCSV` | — | Parámetro con la ruta del CSV, para que el proceso sea reproducible en otro equipo |
| `pUltimoAnioCompleto` | — | Parámetro: último año con datos completos (2025) |
| `VIF_Origen` | **Deshabilitada** | Lectura cruda del CSV y tipos de dato |
| `VIF_Limpia` | **Deshabilitada** | Limpieza, normalización y llaves (la base de verdad única) |
| `Dim_Anio`, `Dim_Geografia`, `Dim_Edad`, `Dim_Sexo`, `Dim_CicloVital`, `Dim_Relacion`, `Dim_Aseguramiento`, `Dim_Perfil`, `Dim_TipoViolencia`, `Dim_Lugar` | Sí | Dimensiones |
| `Hechos_Casos` | Sí | Hecho principal: 1 fila por caso (492.837) |
| `Hechos_TipoViolencia` | Sí | Hecho secundario: 1 fila por caso y tipo de violencia (1.006.182) |

Las dos tablas de hechos comparten dimensiones conformadas (constelación de estrellas). **No se relacionan entre sí.**

## Decisiones de limpieza (con su justificación)

| # | Problema detectado al perfilar | Filas | Decisión |
|---|---|---|---|
| 1 | Espacios y caracteres de control en los textos | — | `Text.Trim` + `Text.Clean` |
| 2 | Localidad vacía (111) o "Localidad Desconocida" (43) | 154 | Se marcan como "Sin dato" y se conservan |
| 3 | Grupo de edad mal escrito: "14 - 17 años" y "De 30 - 34 años" | 3 | Se unifican con "De 14 - 17 años" y "De 27 - 44 años" |
| 4 | UPZ asignada a una localidad distinta de la suya (44 UPZ, 1–9 casos cada una) | 160 | Se conserva la localidad, que es la unidad de análisis, y la UPZ pasa a "Sin dato". No se inventa una ubicación |
| 5 | "Mujer gestante" registrada como *relación con el agresor* | 16.865 | No es una relación válida: se reclasifica como "Sin dato" |
| 6 | Hombre marcado como gestante | 1 | Se corrige a 0 |
| 7 | País escrito de varias formas (VENEZUELA / VENEZUELA (REPÚBLICA BOLIVARIANA DE), PERU/PERÚ…) | ~14.000 | Se agrupa en Nacionalidad: Colombiana, Venezolana u Otra |
| 8 | `entidadadministradora` con 279 nombres inconsistentes de EPS | — | Se excluye: no aporta a las preguntas del tablero y su limpieza no es verificable |
| 9 | 45.339 filas idénticas | 45.339 | **Se conservan.** No hay ID: son casos distintos con atributos anonimizados iguales. Borrarlas quitaría ~9 % de víctimas reales (sesgo) |
| 10 | "Sin dato" en orientación sexual, estrato, nivel educativo y estado civil | hasta 172.787 | **Se conservan como categoría.** Son faltantes legítimos de la fuente; ocultarlos sesgaría las proporciones |
| 11 | Valores atípicos | — | No hay variables numéricas continuas. El grupo "De 100 - 105 años" (24 casos) es plausible y se conserva |
| 12 | Tipo de violencia codificado en 6 columnas de lugar ("Sin dato" = ese tipo no ocurrió) | — | Se despivotan en `Hechos_TipoViolencia` y se descarta "Sin dato" |
| 13 | 2026 incompleto (fecha del dato 2026-07-28) | 25.660 | Se conserva, marcado en `Dim_Anio[Periodo]`. Las medidas interanuales lo excluyen |

---

## Consultas

### `pRutaCSV` (parámetro)
```m
"C:\ruta\a\datos\osb_saludmental-vintrafamiliar.csv" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
```

### `pUltimoAnioCompleto` (parámetro)
```m
2025 meta [IsParameterQuery = true, Type = "Number", IsParameterQueryRequired = true]
```

### `VIF_Origen` (carga deshabilitada)
```m
let
    Origen = Csv.Document(File.Contents(pRutaCSV), [Delimiter = ";", Columns = 23, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Encabezados, {
        {"ano", Int64.Type}, {"grupoedad", type text}, {"sexo", type text}, {"NOMBRE_LOCALIDAD", type text},
        {"NOMBREUPZ", type text}, {"tipoaseguramiento", type text}, {"entidadadministradora", type text},
        {"relacion_agresor", type text}, {"orientacion_sexual", type text}, {"gestante", Int64.Type},
        {"estrato", type text}, {"pais_procedencia", type text}, {"ciclo_vital", type text},
        {"estado_civil", type text}, {"nivel_educativo", type text}, {"agresor_consumospa", Int64.Type},
        {"victima_consumospa", Int64.Type}, {"lugocurrenciaemocional", type text}, {"lugocurrenciafisica", type text},
        {"lugocurrenciasexual", type text}, {"lugocurrenciaeconomica", type text},
        {"lugocurrencianegligencia", type text}, {"lugocurrenciaabandono", type text}})
in
    Tipos
```

### `VIF_Limpia` (carga deshabilitada)
```m
let
    Fuente = VIF_Origen,
    // Llave sustituta del caso (la fuente no trae ID)
    ConID = Table.AddIndexColumn(Fuente, "ID_Caso", 1, 1, Int64.Type),
    // 8. Se excluye la EPS (279 nombres inconsistentes)
    SinEntidad = Table.RemoveColumns(ConID, {"entidadadministradora"}),
    Renombrado = Table.RenameColumns(SinEntidad, {
        {"ano", "Año"}, {"grupoedad", "Grupo_Edad"}, {"sexo", "Sexo"}, {"NOMBRE_LOCALIDAD", "Localidad"},
        {"NOMBREUPZ", "UPZ"}, {"tipoaseguramiento", "Tipo_Aseguramiento"}, {"relacion_agresor", "Relacion_Agresor"},
        {"orientacion_sexual", "Orientacion_Sexual"}, {"gestante", "Gestante"}, {"estrato", "Estrato"},
        {"pais_procedencia", "Pais"}, {"ciclo_vital", "Ciclo_Vital"}, {"estado_civil", "Estado_Civil"},
        {"nivel_educativo", "Nivel_Educativo"}, {"agresor_consumospa", "Agresor_SPA"},
        {"victima_consumospa", "Victima_SPA"}, {"lugocurrenciaemocional", "Lugar_Emocional"},
        {"lugocurrenciafisica", "Lugar_Fisica"}, {"lugocurrenciasexual", "Lugar_Sexual"},
        {"lugocurrenciaeconomica", "Lugar_Economica"}, {"lugocurrencianegligencia", "Lugar_Negligencia"},
        {"lugocurrenciaabandono", "Lugar_Abandono"}}),
    // Lista explícita de columnas de texto (reproducible y auditable)
    ColsTexto = {"Grupo_Edad", "Sexo", "Localidad", "UPZ", "Tipo_Aseguramiento", "Relacion_Agresor",
        "Orientacion_Sexual", "Estrato", "Pais", "Ciclo_Vital", "Estado_Civil", "Nivel_Educativo",
        "Lugar_Emocional", "Lugar_Fisica", "Lugar_Sexual", "Lugar_Economica", "Lugar_Negligencia", "Lugar_Abandono"},
    // 1. Recorte y limpieza de caracteres (los nulos pasan a texto vacío)
    Recortado = Table.TransformColumns(Renombrado, List.Transform(ColsTexto, (c) => {c, each if _ = null then "" else Text.Clean(Text.Trim(_)), type text})),
    // 2. Vacíos y localidad desconocida -> "Sin dato"
    VaciosSinDato = Table.ReplaceValue(Recortado, "", "Sin dato", Replacer.ReplaceValue, ColsTexto),
    LocalidadDesconocida = Table.ReplaceValue(VaciosSinDato, "Localidad Desconocida", "Sin dato", Replacer.ReplaceValue, {"Localidad"}),
    // 3. Etiquetas de edad inconsistentes
    Edad1 = Table.ReplaceValue(LocalidadDesconocida, "14 - 17 años", "De 14 - 17 años", Replacer.ReplaceValue, {"Grupo_Edad"}),
    Edad2 = Table.ReplaceValue(Edad1, "De 30 - 34 años", "De 27 - 44 años", Replacer.ReplaceValue, {"Grupo_Edad"}),
    // 4. UPZ asignada a otra localidad: se conserva la localidad y la UPZ pasa a "Sin dato"
    UPZValidas = Table.SelectRows(Edad2, each [UPZ] <> "Sin dato"),
    ConteoUPZ = Table.Group(UPZValidas, {"UPZ", "Localidad"}, {{"n", each Table.RowCount(_), Int64.Type}}),
    LocalidadModal = Table.Group(ConteoUPZ, {"UPZ"}, {{"Localidad_Modal", each Table.Max(_, "n")[Localidad], type text}}),
    ConModal = Table.NestedJoin(Edad2, {"UPZ"}, LocalidadModal, {"UPZ"}, "M", JoinKind.LeftOuter),
    ExpModal = Table.ExpandTableColumn(ConModal, "M", {"Localidad_Modal"}),
    UPZCorregida = Table.ReplaceValue(ExpModal, each [UPZ],
        each if [UPZ] <> "Sin dato" and [Localidad_Modal] <> [Localidad] then "Sin dato" else [UPZ],
        Replacer.ReplaceValue, {"UPZ"}),
    SinModal = Table.RemoveColumns(UPZCorregida, {"Localidad_Modal"}),
    // 5. "Mujer gestante" no es una relación con el agresor
    Relacion = Table.ReplaceValue(SinModal, "Mujer gestante", "Sin dato", Replacer.ReplaceValue, {"Relacion_Agresor"}),
    // 6. Gestante incoherente con el sexo
    Gestante = Table.ReplaceValue(Relacion, each [Gestante], each if [Sexo] = "Hombres" then 0 else [Gestante], Replacer.ReplaceValue, {"Gestante"}),
    // 7. Nacionalidad agrupada
    Nacionalidad = Table.AddColumn(Gestante, "Nacionalidad", each
        if [Pais] = "COLOMBIA" then "Colombiana"
        else if Text.StartsWith([Pais], "VENEZUELA") then "Venezolana"
        else if [Pais] = "Sin dato" then "Sin dato"
        else "Otra", type text),
    SinPais = Table.RemoveColumns(Nacionalidad, {"Pais"}),
    // Número de tipos de violencia por caso
    NTipos = Table.AddColumn(SinPais, "N_Tipos", each List.Count(List.Select(
        {[Lugar_Emocional], [Lugar_Fisica], [Lugar_Sexual], [Lugar_Economica], [Lugar_Negligencia], [Lugar_Abandono]},
        each _ <> "Sin dato")), Int64.Type),
    // Llaves naturales compuestas para las dimensiones de varias columnas
    ClaveGeo = Table.AddColumn(NTipos, "Clave_Geo", each [Localidad] & " | " & [UPZ], type text),
    ClavePerfil = Table.AddColumn(ClaveGeo, "Clave_Perfil", each Text.Combine(
        {[Orientacion_Sexual], [Estrato], [Estado_Civil], [Nivel_Educativo], [Nacionalidad]}, " | "), type text)
in
    ClavePerfil
```

### `Hechos_Casos`
```m
let
    Fuente = VIF_Limpia,
    Columnas = Table.SelectColumns(Fuente, {"ID_Caso", "Año", "Clave_Geo", "Grupo_Edad", "Sexo", "Ciclo_Vital",
        "Relacion_Agresor", "Tipo_Aseguramiento", "Clave_Perfil", "Gestante", "Agresor_SPA", "Victima_SPA", "N_Tipos"})
in
    Columnas
```

### `Hechos_TipoViolencia`
```m
let
    Fuente = VIF_Limpia,
    Columnas = Table.SelectColumns(Fuente, {"ID_Caso", "Año", "Clave_Geo", "Grupo_Edad", "Sexo", "Ciclo_Vital",
        "Relacion_Agresor", "Tipo_Aseguramiento", "Clave_Perfil", "Lugar_Emocional", "Lugar_Fisica", "Lugar_Sexual",
        "Lugar_Economica", "Lugar_Negligencia", "Lugar_Abandono"}),
    Despivotado = Table.Unpivot(Columnas, {"Lugar_Emocional", "Lugar_Fisica", "Lugar_Sexual", "Lugar_Economica",
        "Lugar_Negligencia", "Lugar_Abandono"}, "Columna", "Lugar"),
    // "Sin dato" en la columna de lugar = ese tipo de violencia no ocurrió en el caso
    SoloOcurridos = Table.SelectRows(Despivotado, each [Lugar] <> "Sin dato"),
    Tipo = Table.AddColumn(SoloOcurridos, "Tipo_Violencia", each Record.Field(
        [Lugar_Emocional = "Emocional", Lugar_Fisica = "Física", Lugar_Sexual = "Sexual",
         Lugar_Economica = "Económica", Lugar_Negligencia = "Negligencia", Lugar_Abandono = "Abandono"], [Columna]), type text),
    Final = Table.RemoveColumns(Tipo, {"Columna"})
in
    Final
```

### `Dim_Anio`
```m
let
    Anios = Table.Distinct(Table.SelectColumns(VIF_Limpia, {"Año"})),
    Orden = Table.Sort(Anios, {{"Año", Order.Ascending}}),
    Periodo = Table.AddColumn(Orden, "Periodo", each if [Año] <= pUltimoAnioCompleto then "Año completo" else "Parcial (1.er semestre)", type text),
    Completo = Table.AddColumn(Periodo, "Es_Anio_Completo", each if [Año] <= pUltimoAnioCompleto then 1 else 0, Int64.Type),
    Etiqueta = Table.AddColumn(Completo, "Año_Etiqueta", each if [Año] <= pUltimoAnioCompleto then Text.From([Año]) else Text.From([Año]) & "*", type text)
in
    Etiqueta
```

### `Dim_Geografia`
```m
let
    Geo = Table.Distinct(Table.SelectColumns(VIF_Limpia, {"Clave_Geo", "Localidad", "UPZ"})),
    Orden = Table.Sort(Geo, {{"Localidad", Order.Ascending}, {"UPZ", Order.Ascending}})
in
    Orden
```

### `Dim_Edad`
```m
let
    Tabla = #table(type table [Grupo_Edad = text, Orden_Edad = Int64.Type, Rango_Edad = text], {
        {"Menor 1 año", 1, "Menor de 18 años"}, {"De 1 - 5 años", 2, "Menor de 18 años"},
        {"De 6 - 13 años", 3, "Menor de 18 años"}, {"De 14 - 17 años", 4, "Menor de 18 años"},
        {"De 18 - 26 años", 5, "18 años o más"}, {"De 27 - 44 años", 6, "18 años o más"},
        {"De 45 - 59 años", 7, "18 años o más"}, {"De 60 - 69 años", 8, "18 años o más"},
        {"De 70 - 79 años", 9, "18 años o más"}, {"De 80 - 99 años", 10, "18 años o más"},
        {"De 100 - 105 años", 11, "18 años o más"}})
in
    Tabla
```

### `Dim_Sexo`
```m
let
    Sexo = Table.Distinct(Table.SelectColumns(VIF_Limpia, {"Sexo"}))
in
    Sexo
```

### `Dim_CicloVital`
```m
let
    Tabla = #table(type table [Ciclo_Vital = text, Orden_Ciclo = Int64.Type], {
        {"Primera Infancia", 1}, {"Infancia", 2}, {"Adolescencia", 3}, {"Juventud", 4}, {"Adultez", 5}, {"Vejez", 6}})
in
    Tabla
```

### `Dim_Relacion`
```m
let
    Mapa = #table(type table [Relacion_Agresor = text, Grupo_Relacion = text, Es_Familiar = Int64.Type], {
        {"Madre", "Padres y cuidadores", 1}, {"Padre", "Padres y cuidadores", 1},
        {"Padrastro", "Padres y cuidadores", 1}, {"Madrastra", "Padres y cuidadores", 1},
        {"Abuelo(a)", "Otros familiares", 1}, {"Hermano(a)", "Otros familiares", 1},
        {"Hijo(a)", "Otros familiares", 1}, {"Otro familiar", "Otros familiares", 1},
        {"Pareja", "Pareja o expareja", 1}, {"Expareja", "Pareja o expareja", 1},
        {"Estudiantes", "Comunidad educativa", 0}, {"Docentes", "Comunidad educativa", 0},
        {"Administrativos", "Comunidad educativa", 0},
        {"Conocido", "Conocidos y otros", 0}, {"Amigo(a)", "Conocidos y otros", 0}, {"Vecino", "Conocidos y otros", 0},
        {"Jefe", "Conocidos y otros", 0}, {"Compañero(a) de trabajo", "Conocidos y otros", 0},
        {"Servidor Público", "Conocidos y otros", 0}, {"Sacerdote", "Conocidos y otros", 0},
        {"Desconocido", "Desconocido", 0}, {"Sin dato", "Sin dato", 0}}),
    // Robustez: cualquier valor nuevo de la fuente entra como "Sin clasificar"
    Valores = Table.Distinct(Table.SelectColumns(VIF_Limpia, {"Relacion_Agresor"})),
    Union = Table.NestedJoin(Valores, {"Relacion_Agresor"}, Mapa, {"Relacion_Agresor"}, "M", JoinKind.LeftOuter),
    Exp = Table.ExpandTableColumn(Union, "M", {"Grupo_Relacion", "Es_Familiar"}),
    SinNulos = Table.ReplaceValue(Table.ReplaceValue(Exp, null, "Sin clasificar", Replacer.ReplaceValue, {"Grupo_Relacion"}), null, 0, Replacer.ReplaceValue, {"Es_Familiar"}),
    Tipos = Table.TransformColumnTypes(SinNulos, {{"Grupo_Relacion", type text}, {"Es_Familiar", Int64.Type}})
in
    Tipos
```

### `Dim_Aseguramiento`
```m
let
    Aseg = Table.Distinct(Table.SelectColumns(VIF_Limpia, {"Tipo_Aseguramiento"}))
in
    Aseg
```

### `Dim_Perfil` (dimensión de atributos socioeconómicos de la víctima)
```m
let
    Perfil = Table.Distinct(Table.SelectColumns(VIF_Limpia, {"Clave_Perfil", "Orientacion_Sexual", "Estrato", "Estado_Civil", "Nivel_Educativo", "Nacionalidad"}))
in
    Perfil
```

### `Dim_TipoViolencia`
```m
let
    Tabla = #table(type table [Tipo_Violencia = text, Orden_Tipo = Int64.Type], {
        {"Emocional", 1}, {"Física", 2}, {"Sexual", 3}, {"Negligencia", 4}, {"Económica", 5}, {"Abandono", 6}})
in
    Tabla
```

### `Dim_Lugar`
```m
let
    Lugar = Table.Distinct(Table.SelectColumns(Hechos_TipoViolencia, {"Lugar"})),
    Orden = Table.Sort(Lugar, {{"Lugar", Order.Ascending}})
in
    Orden
```

## Relaciones del modelo

18 relaciones **muchos a uno (\*:1)**, dirección de filtro **única** (de la dimensión hacia los hechos) y todas activas. No hay relaciones bidireccionales ni muchos a muchos.

| Dimensión (lado 1) | Llave | Hechos_Casos | Hechos_TipoViolencia |
|---|---|---|---|
| Dim_Anio | Año | ✓ | ✓ |
| Dim_Geografia | Clave_Geo | ✓ | ✓ |
| Dim_Edad | Grupo_Edad | ✓ | ✓ |
| Dim_Sexo | Sexo | ✓ | ✓ |
| Dim_CicloVital | Ciclo_Vital | ✓ | ✓ |
| Dim_Relacion | Relacion_Agresor | ✓ | ✓ |
| Dim_Aseguramiento | Tipo_Aseguramiento | ✓ | ✓ |
| Dim_Perfil | Clave_Perfil | ✓ | ✓ |
| Dim_TipoViolencia | Tipo_Violencia | — | ✓ |
| Dim_Lugar | Lugar | — | ✓ |

Integridad referencial verificada con DAX: **0 filas huérfanas** en todas las relaciones. Se activó la opción del modelo *discourageImplicitMeasures*, que impide las medidas implícitas, y la fecha/hora automática está desactivada.

## Cifras de control esperadas (validadas con Python sobre el CSV y verificadas en Power BI tras la carga)

| Tabla | Filas |
|---|---|
| Hechos_Casos | 492.837 |
| Hechos_TipoViolencia | 1.006.182 |
| Dim_Anio | 14 |
| Dim_Geografia | 134 |
| Dim_Perfil | 1.525 |
| Dim_Relacion | 22 |
| Dim_Aseguramiento | 8 |
| Dim_Edad | 11 |
| Dim_CicloVital | 6 |
| Dim_TipoViolencia | 6 |
| Dim_Lugar | 12 |
| Dim_Sexo | 2 |
