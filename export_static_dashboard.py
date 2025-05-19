# export_static_dashboard.py
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ────────────────────────── RUTAS Y CARPETAS ───────────────────────────
DB_PATH = "db.xlsx"
OUT_DIR  = os.path.join("docs", "plots")
os.makedirs(OUT_DIR, exist_ok=True)

# ────────────────────────── DATOS POBLACION ────────────────────────────
poblaciones = pd.read_excel(DB_PATH, sheet_name="poblaciones")
columnas    = [c for c in poblaciones.columns if c != "AÑO"]
fases_horiz = [
    dict(type="rect", xref="x", yref="paper", x0=2019, x1=2024.9, y0=0, y1=1, fillcolor="#d4b40e",
         opacity=0.89, layer="below", line_width=0),
    dict(type="rect", xref="x", yref="paper", x0=2025, x1=2026.9, y0=0, y1=1, fillcolor="#bcbcac",
         opacity=0.89, layer="below", line_width=0),
    dict(type="rect", xref="x", yref="paper", x0=2027, x1=2028.9, y0=0, y1=1, fillcolor="#d4b40e",
         opacity=0.89, layer="below", line_width=0),
    dict(type="rect", xref="x", yref="paper", x0=2029, x1=2038.9, y0=0, y1=1, fillcolor="#efe30e",
         opacity=0.89, layer="below", line_width=0),
]

def export_fig(fig: go.Figure, filename: str):
    """Guarda la figura como HTML en docs/plots/"""
    fullpath = os.path.join(OUT_DIR, filename)
    fig.write_html(fullpath, include_plotlyjs="cdn")

# ───────────── 1. GRÁFICOS DE POBLACIÓN ─────────────
for col in columnas:
    y     = poblaciones[col]
    fig   = go.Figure(go.Bar(
        x=poblaciones["AÑO"],
        y=y,
        text=[f"{v:,.0f}" for v in y],
        textposition="inside",
        marker=dict(color=y, colorscale="Turbo")
    ))
    y_min = y.min()*0.79
    y_max = y.max()*1.03
    fig.update_layout(yaxis=dict(range=[y_min, y_max], tickformat=","), xaxis=dict(dtick=1),
                      margin=dict(l=0, r=0, t=30, b=0), bargap=0.1, plot_bgcolor="white",
                      title=f"Evolución de {col}")
    fig.update_layout(shapes=fases_horiz)
    export_fig(fig, f"poblacion_{col.lower()}.html")

# ───────────── 2. DONAS (capacidad de diseño/actual/óptima/final) ─────
donuts_info = [
    ("donut_diseno.html",  "Capacidad de diseño = 3×30×2", 180, 1200, "#00ff9f"),
    ("donut_actual.html",  "Capacidad actual  = 3×30×2",   180, 1200, "#00b8ff"),
    ("donut_optimo.html",  "Capacidad óptima  = 3×30×2",   180, 1200, "#001eff"),
    ("donut_final.html",   "Capacidad final   = 20×30×2", 1200, 1200, "red"),
]

for fname, titulo, valor, total, color in donuts_info:
    fig = go.Figure(go.Pie(values=[valor, total-valor],
                           hole=0.6,
                           marker=dict(colors=[color, "#f0f0f0"]),
                           textinfo="none",
                           showlegend=False))
    fig.update_layout(annotations=[dict(text=str(valor), x=0.5, y=0.5, font_size=18, showarrow=False)],
                      title=titulo,
                      margin=dict(t=40, b=0, l=0, r=0))
    export_fig(fig, fname)

# ───────────── 3. GRÁFICO DE BRECHA ─────────────
brechas = pd.read_excel(DB_PATH, sheet_name="brecha")
fig_brecha = go.Figure()
fig_brecha.add_trace(go.Bar(x=brechas["AÑO"], y=brechas["OFERTA_O"],
                            name="Oferta optimizada", marker_color="#005bbc"))
fig_brecha.add_trace(go.Bar(x=brechas["AÑO"], y=brechas["DEMANDA_CP"],
                            name="Demanda con proyecto", marker_color="#ffd600"))
fig_brecha.add_trace(go.Scatter(x=brechas["AÑO"], y=-1*brechas["BRECHA"],
                                name="Brecha", mode="lines+markers", line_color="#2ca02c"))
fig_brecha.update_layout(title="Evolución de la brecha",
                         barmode="group",
                         plot_bgcolor="white",
                         xaxis=dict(dtick=1),
                         legend=dict(orientation="h", yanchor="bottom", y=1.02))
export_fig(fig_brecha, "brecha.html")

# ───────────── 4. SIMULACIÓN MONTECARLO ─────────────
valores_m = np.array([
    598.00, 623.00, 695.00, 719.00, 733.00, 671.00, 605.66, 585.04,
    571.26, 576.67, 712.82, 821.95, 904.02, 952.04, 963.23, 974.54,
    985.97, 997.63, 1009.40, 1021.30])
años_hist = np.arange(2019, 2019 + len(valores_m))
rend      = np.log(valores_m[1:] / valores_m[:-1])
mu, sigma = rend.mean(), rend.std(ddof=1)

start_year = 2026
end_year   = 2038
f_years    = end_year - start_year
initial_value = valores_m[np.where(años_hist == start_year)[0][0]]

np.random.seed(42)
n_sim, n_show = 5000, 200
sims = np.zeros((f_years+1, n_sim)); sims[0] = initial_value
for t in range(1, f_years+1):
    sims[t] = sims[t-1] * np.exp(np.random.normal(mu, sigma, n_sim))

años_sim  = np.arange(start_year, end_year+1)
max_m     = sims.max(axis=1)
min_m     = sims.min(axis=1)

fig_mc = go.Figure()
for i in range(n_show):
    fig_mc.add_trace(go.Scatter(x=años_sim, y=sims[:, i], mode="lines",
                                line=dict(width=1), opacity=0.15, showlegend=False))
fig_mc.add_trace(go.Scatter(x=años_sim, y=max_m, name="Máximo",
                            mode="lines+markers", line=dict(dash="dash")))
fig_mc.add_trace(go.Scatter(x=años_sim, y=min_m, name="Mínimo",
                            mode="lines+markers", line=dict(dash="dash")))
fig_mc.add_trace(go.Scatter(x=[start_year], y=[initial_value], mode="markers",
                            name=f"Valor {start_year}", marker_size=8))
fig_mc.update_layout(title=f"Simulación Monte Carlo ({n_sim} corridas)",
                     xaxis_title="Año", yaxis_title="Valor", hovermode="x unified")
export_fig(fig_mc, "montecarlo.html")

print(f"✔ Archivos HTML exportados en {OUT_DIR}")
