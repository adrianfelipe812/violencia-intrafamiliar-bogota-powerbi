# Datos de origen

El CSV no está en el repositorio porque pesa unos 110 MB, más que el límite de 100 MB de GitHub. Para reproducir el ETL:

1. Entra a <https://datosabiertos.bogota.gov.co/dataset/numero-de-casos-de-violencia-intrafamiliar>.
2. Descarga el recurso CSV *Violencia intrafamiliar y de género en Bogotá D.C.* El archivo se llama `osb_saludmental-vintrafamiliar.csv`, viene en UTF-8 y usa `;` como separador.
3. Guárdalo en cualquier carpeta, por ejemplo esta.
4. En Power BI Desktop abre `powerbi/VIF_Bogota_Dashboard.pbip` y ve a *Transformar datos → Administrar parámetros*. Cambia `pRutaCSV` por la ruta completa del archivo y luego pulsa *Actualizar*.

**Cifras de control** para comprobar que la carga quedó bien: `Hechos_Casos` = 492.837 filas y `Hechos_TipoViolencia` = 1.006.182 filas. Usamos la versión publicada con fecha del dato 28/07/2026; si el portal ya publicó una versión más reciente, estas cifras cambiarán.

**Licencia de los datos:** CC BY 4.0. Fuente: Secretaría Distrital de Salud de Bogotá (SDS), SIVIM.
