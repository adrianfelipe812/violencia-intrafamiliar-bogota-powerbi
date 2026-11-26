# Medidas DAX — Violencia intrafamiliar y de género, Bogotá

Son **54 medidas**, todas **explícitas**:
- Las 24 analíticas descritas abajo.
- Las versiones "Año Ref" de los KPI (% Menores, % Agresor Familiar, % Mujeres, Tipos por Caso, Violencia Sexual y % Vivienda), para que la fila de KPI use un solo periodo.
- Títulos y subtítulos dinámicos: Subtítulo Localidades, Título Serie, Título Localidades, Título Relación, Título Edad, Título Tipos, Títulos KPI y Texto Periodo.
- Medidas de color y de apoyo visual: Casos Mujeres, Casos Hombres, Casos Hombres Pirámide y Posicion Edad.

Nota: `Promedio Anual 2013-2025` usa `ALL(Dim_Anio)`, y `Color Tipo Violencia` usa `ALL(Dim_TipoViolencia)`. Se usa la tabla completa porque, si solo se quita el filtro de la columna, sigue activo el de su columna de orden (sortByColumn). Todas y viven en la tabla `_Medidas`, organizadas en carpetas. El modelo tiene activada la opción *discourageImplicitMeasures*, que impide las medidas implícitas. **No hay columnas calculadas en DAX**: las columnas derivadas (Nacionalidad, N_Tipos, llaves) se crean en Power Query.

## Funciones usadas (familias de la Clase 9)

| Familia | Funciones |
|---|---|
| Agregadores | COUNTROWS, SUM, MAX |
| Iteradores | AVERAGEX, RANKX |
| CALCULATE | En casi todas las medidas comparativas |
| Modificadores de filtro | REMOVEFILTERS, ALL, ALLSELECTED, KEEPFILTERS, FILTER |
| Matemática y lógica | DIVIDE (en toda división), IF, SWITCH, COALESCE, HASONEVALUE, SELECTEDVALUE, VAR/RETURN |
| Inteligencia de tiempo | Implementada a mano sobre `Dim_Anio`, porque la fuente solo trae el año y no hay fechas diarias para SAMEPERIODLASTYEAR |

## 1. Base

| Medida | DAX | Lógica |
|---|---|---|
| **Total Casos** | `COUNTROWS ( Hechos_Casos )` | Un caso = una víctima notificada |
| **Total Hechos de Violencia** | `COUNTROWS ( Hechos_TipoViolencia )` | Caso × tipo. No sirve para contar víctimas |
| **Tipos por Caso** | `DIVIDE ( [Total Hechos de Violencia], [Total Casos] )` | Polivictimización: en promedio, 2,04 tipos por víctima |

## 2. Perfil (KPIs)

| Medida | DAX | Valor total |
|---|---|---|
| **% Víctimas Mujeres** | `DIVIDE ( CALCULATE ( [Total Casos], Dim_Sexo[Sexo] = "Mujeres" ), [Total Casos] )` | 69,9 % |
| **% Víctimas Menores de 18** | `DIVIDE ( CALCULATE ( [Total Casos], Dim_Edad[Rango_Edad] = "Menor de 18 años" ), [Total Casos] )` | 63,1 % |
| **% Agresor Familiar** | `DIVIDE ( CALCULATE ( [Total Casos], Dim_Relacion[Es_Familiar] = 1 ), [Total Casos] )` | 77,5 % |
| **% Agresor con Consumo SPA** | `DIVIDE ( SUM ( Hechos_Casos[Agresor_SPA] ), [Total Casos] )` | 5,6 % |
| **% Gestantes entre Mujeres** | `DIVIDE ( SUM ( Hechos_Casos[Gestante] ), CALCULATE ( [Total Casos], Dim_Sexo[Sexo] = "Mujeres" ) )` | 5,3 % |

`% Agresor Familiar` usa todos los casos como denominador, incluidos los "Sin dato". Es un criterio conservador: no infla el porcentaje.

## 3. Tiempo

```dax
Año Referencia =
VAR _UnAnio = IF ( HASONEVALUE ( Dim_Anio[Año] ), VALUES ( Dim_Anio[Año] ) )
VAR _UltimoCompleto = CALCULATE ( MAX ( Dim_Anio[Año] ), KEEPFILTERS ( Dim_Anio[Es_Anio_Completo] = 1 ) )
RETURN COALESCE ( _UnAnio, _UltimoCompleto )
```
Si el usuario elige un año, se usa ese. Si no, se usa el último año **completo** (2025), nunca 2026, que es parcial.

```dax
Casos Año Referencia =
VAR _Anio = [Año Referencia]
RETURN CALCULATE ( [Total Casos], REMOVEFILTERS ( Dim_Anio ), Dim_Anio[Año] = _Anio )

Casos Año Anterior =
VAR _Anio = [Año Referencia]
RETURN CALCULATE ( [Total Casos], REMOVEFILTERS ( Dim_Anio ), Dim_Anio[Año] = _Anio - 1 )

Variación % Interanual =
VAR _Anio = [Año Referencia]
VAR _EsCompleto = CALCULATE ( MAX ( Dim_Anio[Es_Anio_Completo] ), REMOVEFILTERS ( Dim_Anio ), Dim_Anio[Año] = _Anio )
VAR _Actual = [Casos Año Referencia]
VAR _Previo = [Casos Año Anterior]
RETURN IF ( _EsCompleto = 1, DIVIDE ( _Actual - _Previo, _Previo ) )
```
**Decisión ética:** si el año es parcial, la variación devuelve BLANK. Comparar el primer semestre de 2026 contra todo 2025 mostraría una caída falsa de −51 %.

```dax
Promedio Anual 2013-2025 =
AVERAGEX (
    FILTER ( ALL ( Dim_Anio[Año], Dim_Anio[Es_Anio_Completo] ), Dim_Anio[Es_Anio_Completo] = 1 ),
    [Total Casos]
)

Variación % vs Promedio =
VAR _Anio = [Año Referencia]
VAR _EsCompleto = CALCULATE ( MAX ( Dim_Anio[Es_Anio_Completo] ), REMOVEFILTERS ( Dim_Anio ), Dim_Anio[Año] = _Anio )
VAR _Promedio = [Promedio Anual 2013-2025]
RETURN IF ( _EsCompleto = 1, DIVIDE ( [Casos Año Referencia] - _Promedio, _Promedio ) )
```

| Año | Casos | Variación interanual | vs. promedio 2013–2025 |
|---|---|---|---|
| 2019 | 32.877 | +7,1 % | −8,5 % |
| 2020 | 23.649 | −28,1 % | −34,2 % |
| 2021 | 30.340 | +28,3 % | −15,6 % |
| 2022 | 41.318 | +36,2 % | +15,0 % |
| 2023 | 45.879 | +11,0 % | +27,7 % |
| 2024 | 51.070 | +11,3 % | +42,1 % |
| **2025** | **52.493** | **+2,8 %** | **+46,1 %** |
| 2026* | 25.660 | — (parcial) | — (parcial) |

Promedio anual 2013–2025: 35.937 casos.

## 4. Participación y ranking

| Medida | DAX | Diferencia |
|---|---|---|
| **% del Total Visible** | `DIVIDE ( [Total Casos], CALCULATE ( [Total Casos], ALLSELECTED () ) )` | Respeta los segmentadores: es un % sobre lo que el usuario ve |
| **% del Total Bogotá** | `DIVIDE ( [Total Casos], CALCULATE ( [Total Casos], REMOVEFILTERS ( Dim_Geografia ) ) )` | Ignora solo la geografía: es un % sobre la ciudad |
| **Ranking Localidad** | `IF ( HASONEVALUE ( Dim_Geografia[Localidad] ), RANKX ( ALLSELECTED ( Dim_Geografia[Localidad] ), [Total Casos], , DESC, DENSE ) )` | 1 = localidad con más casos |

Top 3 localidades en todo el periodo: Ciudad Bolívar (65.414; 13,3 %), Bosa (63.450; 12,9 %) y Kennedy (61.096; 12,4 %).

## 5. Tipo y lugar

| Medida | DAX |
|---|---|
| **% de Casos con este Tipo** | `DIVIDE ( [Total Hechos de Violencia], [Total Casos] )`. En un gráfico por tipo, da el % de víctimas que sufrieron ese tipo. No suma 100 % porque un caso puede tener varios tipos |
| **Casos con Violencia Sexual** | `CALCULATE ( [Total Hechos de Violencia], Dim_TipoViolencia[Tipo_Violencia] = "Sexual" )` |
| **Casos con Violencia Física** | `CALCULATE ( [Total Hechos de Violencia], Dim_TipoViolencia[Tipo_Violencia] = "Física" )` |
| **% Hechos en la Vivienda** | `DIVIDE ( CALCULATE ( [Total Hechos de Violencia], Dim_Lugar[Lugar] = "Vivienda" ), [Total Hechos de Violencia] )` |

| Tipo | Víctimas | % de víctimas |
|---|---|---|
| Emocional | 491.299 | 99,7 % |
| Negligencia | 185.596 | 37,7 % |
| Física | 152.543 | 31,0 % |
| Sexual | 134.058 | 27,2 % |
| Abandono | 21.941 | 4,5 % |
| Económica | 20.745 | 4,2 % |

El 86,6 % de los hechos ocurre en la vivienda.

## 6. Formato (colores para el formato condicional)

| Medida | Uso |
|---|---|
| **Color Variación** | Rojo `#B91C1C` si los casos suben; gris `#6B7280` si bajan; gris claro si no hay comparación |
| **Color Top 3 Localidades** | Rojo para las 3 localidades con más casos; gris `#BDBDBD` para el resto |
| **Color Año Referencia** | Rojo para el último año completo; gris claro `#E5E7EB` para 2026 parcial; gris para el resto |

Se aplican en *Formato → Colores → fx → Valor del campo*. Son atributos preatentivos: un solo color de acento sobre gris, como propone la Clase 10.
