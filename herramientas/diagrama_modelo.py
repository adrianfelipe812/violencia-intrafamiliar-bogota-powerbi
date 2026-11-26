"""Diagrama del modelo en estrella (constelación) para el PDF."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

out = sys.argv[1]
ACENTO = "#B91C1C"; GRIS = "#6B7280"; GRIS_CLARO = "#E5E7EB"; TXT = "#1F2430"
fig, ax = plt.subplots(figsize=(10, 4.9), dpi=220)
ax.set_xlim(0, 100); ax.set_ylim(-3, 46); ax.axis("off")

def caja(x, y, w, h, titulo, lineas, hecho=False):
    fc = "#FDECEC" if hecho else "#F9FAFB"; ec = ACENTO if hecho else "#9CA3AF"
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=0.8",
                                fc=fc, ec=ec, lw=1.6 if hecho else 1))
    ax.text(x + w / 2, y + h - 1.6, titulo, ha="center", va="top", fontsize=8.6, fontweight="bold",
            color=ACENTO if hecho else TXT)
    for i, l in enumerate(lineas):
        ax.text(x + w / 2, y + h - 4.4 - i * 2.3, l, ha="center", va="top", fontsize=6.6, color=GRIS)
    return (x + w / 2, y + h / 2)

# hechos en el centro
hc = caja(37, 25, 26, 12, "Hechos_Casos", ["1 fila = 1 caso (492.837)", "Gestante · Agresor_SPA · N_Tipos",
                                          "8 llaves a dimensiones"], hecho=True)
ht = caja(37, 6, 26, 12, "Hechos_TipoViolencia", ["1 fila = caso × tipo (1.006.182)",
                                                 "Tipo_Violencia · Lugar", "10 llaves a dimensiones"], hecho=True)
# dimensiones conformadas (izquierda y derecha)
izq = [("Dim_Anio", "Año · Periodo (2026* parcial)"), ("Dim_Geografia", "Localidad · UPZ (134)"),
       ("Dim_Edad", "Grupo · Orden · Rango"), ("Dim_Sexo", "Sexo")]
der = [("Dim_CicloVital", "Ciclo vital · Orden"), ("Dim_Relacion", "Relación · Grupo · Es_Familiar"),
       ("Dim_Aseguramiento", "Régimen de salud"), ("Dim_Perfil", "Orientación · Estrato · Educación…")]
ys = [37, 27, 17, 7]
for (t, d), y in zip(izq, ys):
    c = caja(2, y, 22, 6.5, t, [d])
    for tgt in (hc, ht):
        ax.annotate("", xy=(37, tgt[1]), xytext=(24.6, y + 3.25),
                    arrowprops=dict(arrowstyle="-|>", color="#9CA3AF", lw=0.7, shrinkA=0, shrinkB=0))
for (t, d), y in zip(der, ys):
    c = caja(76, y, 22, 6.5, t, [d])
    for tgt in (hc, ht):
        ax.annotate("", xy=(63, tgt[1]), xytext=(75.4, y + 3.25),
                    arrowprops=dict(arrowstyle="-|>", color="#9CA3AF", lw=0.7, shrinkA=0, shrinkB=0))
# dimensiones exclusivas del hecho por tipo (abajo)
for x, t, d in [(30, "Dim_TipoViolencia", "6 tipos · Orden"), (52, "Dim_Lugar", "12 lugares")]:
    caja(x, -2, 18, 6, t, [d])
    ax.annotate("", xy=(x + 9, 6), xytext=(x + 9, 4.3),
                arrowprops=dict(arrowstyle="-|>", color="#9CA3AF", lw=0.8))
ax.text(50, 44.6, "Relaciones 1:*  ·  filtro de dirección única (dimensión → hecho)  ·  sin relación entre hechos",
        ha="center", fontsize=7.4, color=GRIS)
plt.savefig(out, bbox_inches="tight", facecolor="white")
print("ok", out)
