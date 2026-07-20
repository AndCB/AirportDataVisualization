#!/usr/bin/env python3
"""
Heatmap de Estacionalidad Aeroportuaria - Costa Rica
=====================================================
Visualiza la intensidad de operaciones mensuales por aeropuerto
para identificar patrones estacionales, temporada alta/baja,
y distribucion del trafico aereo.
"""

import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from typing import List, Dict, Any

# ============================================================
# CONFIGURACION
# ============================================================
API_URL: str = "https://datos.aresep.go.cr/ws.datosabiertos/Services/IT/Aeropuerto.svc/ObtenerHistoricoOperativoOperacion"
MONTH_ORDER: List[str] = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre'
]
COLORS_VOLUME: str = 'YlOrRd'
COLORS_PCT: str = 'Viridis'
YEAR_FROM: int = 2020
REQUEST_TIMEOUT: int = 30


# ============================================================
# FUNCIONES
# ============================================================
def fetch_data() -> List[Dict[str, Any]]:
    """
    Obtiene datos desde la API de ARESEP con manejo de errores.

    Returns:
        Lista de registros obtenidos de la API.
    """
    print("Conectando con API de ARESEP...")
    try:
        response = requests.get(API_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        sys.exit(f"Error: La API no respondio tras {REQUEST_TIMEOUT}s")
    except requests.exceptions.ConnectionError:
        sys.exit("Error: No se pudo conectar con la API")
    except requests.exceptions.HTTPError as e:
        sys.exit(f"Error HTTP: {e.response.status_code}")
    except ValueError:
        sys.exit("Error: Respuesta no es JSON valido")

    items = data.get('value', [])
    if not items:
        sys.exit("Error: La API devolvio datos vacios")

    print(f"Datos: {len(items)} registros obtenidos")
    return items


def validate_data(items: List[Dict[str, Any]]) -> None:
    """Valida que todos los items tengan los campos requeridos."""
    required = {'aeropuerto', 'mes', 'anho', 'totalOperaciones'}
    for i, item in enumerate(items):
        missing = required - set(item.keys())
        if missing:
            sys.exit(f"Registro {i}: faltan campos {missing}")


def create_heatmap(items: List[Dict[str, Any]], year_from: int = YEAR_FROM) -> go.Figure:
    """
    Crea un panel con dos heatmaps:
      1. Volumen promedio absoluto de operaciones
      2. Distribucion porcentual del total anual

    Args:
        items: Datos de la API.
        year_from: Anio desde el cual filtrar.

    Returns:
        Figura de Plotly con los heatmaps.
    """
    filtered = [it for it in items if it['anho'] >= year_from]
    if not filtered:
        sys.exit(f"No hay datos desde el anio {year_from}")

    df = pd.DataFrame(filtered)

    # Heatmap 1: Volumen promedio absoluto
    pivot_avg = df.pivot_table(
        values='totalOperaciones',
        index='aeropuerto',
        columns='mes',
        aggfunc='mean',
        fill_value=0
    )
    pivot_avg = pivot_avg[[m for m in MONTH_ORDER if m in pivot_avg.columns]]

    # Heatmap 2: Distribucion porcentual anual
    pivot_pct = pivot_avg.div(pivot_avg.sum(axis=1), axis=0) * 100

    # Construir figura
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=[
            f'<b>Volumen Promedio de Operaciones</b><br><sup>Operaciones/mes (promedio desde {year_from})</sup>',
            f'<b>Distribucion Porcentual del Total Anual</b><br><sup>% de operaciones del anio que ocurren en cada mes (desde {year_from})</sup>'
        ],
        vertical_spacing=0.18,
        row_heights=[0.48, 0.48]
    )

    # Heatmap 1: Volumen
    hm1 = go.Heatmap(
        z=pivot_avg.values,
        x=list(pivot_avg.columns),
        y=list(pivot_avg.index),
        colorscale=COLORS_VOLUME,
        text=np.round(pivot_avg.values, 0).astype(int),
        texttemplate='%{text}',
        textfont=dict(size=10, color='black'),
        hovertemplate=(
            '<b>%{y}</b><br>'
            '%{x}<br>'
            '<b>%{z:.0f}</b> operaciones/mes (prom.)<br>'
            '<extra></extra>'
        ),
        colorbar=dict(
            title=dict(text="Ops. promedio", side="right"),
            len=0.4, y=0.75, x=1.02
        ),
        zmin=0,
        zmax=pivot_avg.values.max()
    )

    # Heatmap 2: Porcentaje
    hm2 = go.Heatmap(
        z=pivot_pct.values,
        x=list(pivot_pct.columns),
        y=list(pivot_pct.index),
        colorscale=COLORS_PCT,
        text=np.round(pivot_pct.values, 1),
        texttemplate='%{text}%',
        textfont=dict(size=10, color='black'),
        hovertemplate=(
            '<b>%{y}</b><br>'
            '%{x}<br>'
            '<b>%{z:.1f}%</b> del trafico anual<br>'
            '<extra></extra>'
        ),
        colorbar=dict(
            title=dict(text="% anual", side="right"),
            len=0.4, y=0.25, x=1.02
        ),
        zmin=0,
        zmax=pivot_pct.values.max()
    )

    fig.add_trace(hm1, row=1, col=1)
    fig.add_trace(hm2, row=2, col=1)

    # Anotaciones informativas
    annotations = []

    # Encontrar el aeropuerto con la estacionalidad mas marcada
    if not pivot_pct.empty:
        seasonality_std = pivot_pct.std(axis=1)
        most_seasonal_airport = seasonality_std.idxmax()
        peak_month = pivot_pct.loc[most_seasonal_airport].idxmax()
        peak_val = pivot_pct.loc[most_seasonal_airport].max()
        valley_month = pivot_pct.loc[most_seasonal_airport].idxmin()
        valley_val = pivot_pct.loc[most_seasonal_airport].min()

        # Nombre corto del aeropuerto
        airport_short = most_seasonal_airport.replace(
            'Aeropuerto Internacional ', ''
        )

        annotations.append(dict(
            x=1.0, y=1.16,
            xref='paper', yref='paper',
            text=(
                f'Estacionalidad mas marcada: {airport_short}'
                f'<br>Pico en <b>{peak_month}</b> ({peak_val:.1f}% del trafico anual)'
                f'<br>Valle en <b>{valley_month}</b> ({valley_val:.1f}%)'
            ),
            showarrow=False,
            font=dict(size=11),
            align='left',
            bordercolor='#ddd',
            borderwidth=1,
            borderpad=6,
            bgcolor='rgba(255,255,255,0.9)'
        ))

    # Layout
    fig.update_layout(
        title=dict(
            text=(
                '<b>Heatmap de Estacionalidad Aeroportuaria</b><br>'
                f'<sup>Operaciones mensuales promedio desde {year_from} | '
                "Fuente: <a href='https://datos.aresep.go.cr/'>ARESEP</a></sup>"
            ),
            font=dict(size=22, family='Arial Black, sans-serif'),
            x=0.5,
            xanchor='center',
            y=0.98
        ),
        height=850,
        width=1050,
        template='plotly_white',
        hovermode='closest',
        font=dict(family='Segoe UI, Arial, sans-serif', size=12),
        margin=dict(t=140, b=60, l=100, r=120),
        annotations=annotations
    )

    # Ejes
    fig.update_xaxes(
        title_text='', row=1, col=1,
        tickangle=45, tickfont=dict(size=11)
    )
    fig.update_xaxes(
        title_text='<b>Mes</b>', row=2, col=1,
        tickangle=45, tickfont=dict(size=11)
    )
    fig.update_yaxes(
        title_text='<b>Aeropuerto</b>', row=1, col=1,
        tickfont=dict(size=11)
    )
    fig.update_yaxes(
        title_text='<b>Aeropuerto</b>', row=2, col=1,
        tickfont=dict(size=11)
    )

    return fig


def main() -> None:
    """Funcion principal."""
    print("=" * 65)
    print("  HEATMAP DE ESTACIONALIDAD AEROPORTUARIA")
    print("  Costa Rica - Fuente: ARESEP")
    print("=" * 65)

    try:
        raw_data = fetch_data()
        validate_data(raw_data)

        airports = sorted(set(it['aeropuerto'] for it in raw_data))
        years = sorted(set(it['anho'] for it in raw_data))
        print(f"{len(airports)} aeropuertos: {', '.join(airports)}")
        print(f"Datos disponibles: {years[0]} - {years[-1]}")

        print(f"Filtrando desde {YEAR_FROM}...")
        fig = create_heatmap(raw_data, year_from=YEAR_FROM)

        output_file = "estacionalidad_aeropuertos.html"
        fig.write_html(output_file)
        print(f"Grafico guardado como '{output_file}'")

        print("Abriendo en el navegador...")
        fig.show()

        print("Heatmap generado exitosamente.")
        print(f"Archivo: {output_file}")

    except KeyboardInterrupt:
        print("Proceso interrumpido por el usuario.")
        sys.exit(0)


if __name__ == "__main__":
    main()
