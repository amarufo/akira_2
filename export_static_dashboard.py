import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Cargar data
db_path = "db.xlsx"
poblaciones = pd.read_excel(db_path, sheet_name="poblaciones")
brechas = pd.read_excel(db_path, sheet_name="brecha")

# Gráfico 1: Población total
fig1 = go.Figure(go.Bar(
    x=poblaciones["AÑO"],
    y=poblaciones["POB_TOTAL"],
    text=[f"{v:,.0f}" for v in poblaciones["POB_TOTAL"]],
    textposition="inside",
    marker=dict(color=poblaciones["POB_TOTAL"], colorscale="Turbo")
))
fig1.update_layout(title="Población Total", plot_bgcolor="white")
fig1.write_html("docs/grafico_poblacion_total.html", include_plotlyjs="cdn")

# Gráfico 2: Brechas
fig_brecha = go.Figure()
fig_brecha.add_trace(go.Bar(x=brechas["AÑO"], y=brechas["OFERTA_O"], name="Oferta optimizada", marker_color="#005bbc"))
fig_brecha.add_trace(go.Bar(x=brechas["AÑO"], y=brechas["DEMANDA_CP"], name="Demanda", marker_color="#ffd600"))
fig_brecha.add_trace(go.Scatter(x=brechas["AÑO"], y=-1*brechas["BRECHA"], mode="lines+markers", name="Brecha", line=dict(color="green")))
fig_brecha.update_layout(title="Brecha de cobertura", barmode="group", plot_bgcolor="white")
fig_brecha.write_html("docs/grafico_brecha.html", include_plotlyjs="cdn")

# Puedes hacer lo mismo para el gráfico Monte Carlo (usa fig_montecarlo)
