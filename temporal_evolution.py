#!/usr/bin/env python3
"""
Temporal Evolution of Airport Operations - Costa Rica
=====================================================
Serie de tiempo de operaciones totales mes a mes desde 2009,
mostrando tendencias, impacto del COVID-19 y recuperacion.
"""

import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import sys
from typing import List, Dict, Any, Tuple
from collections import defaultdict

# ============================================================
# CONFIGURACION
# ============================================================
API_URL: str = "https://datos.aresep.go.cr/ws.datosabiertos/Services/IT/Aeropuerto.svc/ObtenerHistoricoOperativoOperacion"
MONTH_ORDER: Dict[str, int] = {
    'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5,
    'Junio': 6, 'Julio': 7, 'Agosto': 8, 'Setiembre': 9, 'Octubre': 10,
    'Noviembre': 11, 'Diciembre': 12
}
REQUEST_TIMEOUT: int = 30

# Aeropuertos con sus colores (manteniendo la misma paleta)
AIRPORT_COLORS: Dict[str, str] = {
    'Aeropuerto Internacional Juan Santamaría': '#1f77b4',
    'Aeropuerto Internacional Tobías Bolaños': '#ff7f0e',
    'Aeropuerto Internacional Daniel Oduber Quirós': '#2ca02c',
    'Aeropuerto Internacional Limón': '#d62728'
}


# ============================================================
# FUNCIONES
# ============================================================
def fetch_data() -> List[Dict[str, Any]]:
    """
    Obtiene datos desde la API de ARESEP.

    Returns:
        Lista de registros de la API.
    """
    print("Conectando con ARESEP...")
    try:
        response = requests.get(API_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        sys.exit(f"Error de conexion: {e}")
    except ValueError:
        sys.exit("Error: Respuesta no es JSON valido")

    items = data.get('value', [])
    if not items:
        sys.exit("Error: La API devolvio datos vacios")

    print(f"{len(items)} registros obtenidos")
    return items


def build_time_series(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Construye series de tiempo a partir de los datos.

    Args:
        items: Registros de la API.

    Returns:
        Diccionario con fechas, totales por mes y por aeropuerto.
    """
    # Agrupar por (anio, mes)
    monthly_total: Dict[Tuple[int, str], int] = defaultdict(int)
    monthly_by_airport: Dict[Tuple[int, str], Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for item in items:
        key = (item['anho'], item['mes'])
        monthly_total[key] += item['totalOperaciones']
        monthly_by_airport[key][item['aeropuerto']] += item['totalOperaciones']

    # Ordenar cronologicamente
    sorted_keys = sorted(monthly_total.keys(), key=lambda x: (x[0], MONTH_ORDER[x[1]]))

    dates: List[datetime] = []
    totals: List[int] = []
    airport_series: Dict[str, List[int]] = {a: [] for a in AIRPORT_COLORS.keys()}

    for year, month in sorted_keys:
        month_num = MONTH_ORDER[month]
        dates.append(datetime(year, month_num, 1))
        totals.append(monthly_total[(year, month)])

        for airport in AIRPORT_COLORS.keys():
            airport_series[airport].append(
                monthly_by_airport[(year, month)].get(airport, 0)
            )

    return {
        'dates': dates,
        'totals': totals,
        'airport_series': airport_series
    }


def create_plot(ts: Dict[str, Any]) -> None:
    """
    Genera el grafico de evolucion temporal con Plotly.

    Args:
        ts: Diccionario con series de tiempo.
    """
    dates = ts['dates']
    totals = ts['totals']

    # Crear figura con 2 paneles verticales
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.65, 0.35],
        subplot_titles=(
            '<b>Evolucion de Operaciones Aeroportuarias en Costa Rica (2009-2026)</b>',
            '<b>Desglose por Aeropuerto</b>'
        )
    )

    # ---- Panel superior: Total general ----
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=totals,
            mode='lines+markers',
            name='Total operaciones',
            line=dict(color='#1f77b4', width=2.5),
            marker=dict(size=4, color='#1f77b4'),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.15)',
            hovertemplate='%{x|%b %Y}<br><b>%{y:,}</b> operaciones<extra></extra>'
        ),
        row=1, col=1
    )

    # Linea vertical para COVID-19
    covid_start = datetime(2020, 3, 1)
    fig.add_vline(
        x=covid_start,
        line=dict(color='red', width=2, dash='dash'),
        annotation_text='Inicio pandemia COVID-19',
        annotation_position='top left',
        annotation_font=dict(size=10, color='red'),
        row=1, col=1
    )

    # Resaltar periodo critico (mar-jun 2020)
    fig.add_vrect(
        x0=datetime(2020, 3, 1),
        x1=datetime(2020, 6, 1),
        fillcolor='red',
        opacity=0.06,
        layer='below',
        line_width=0,
        row=1, col=1
    )

    # Anotacion: punto maximo
    max_idx = totals.index(max(totals))
    fig.add_annotation(
        x=dates[max_idx],
        y=totals[max_idx],
        text=f'Maximo: {totals[max_idx]:,}<br>{dates[max_idx].strftime("%b %Y")}',
        showarrow=True,
        arrowhead=2,
        arrowsize=1.2,
        arrowcolor='#1f77b4',
        ax=40,
        ay=-30,
        font=dict(size=10, color='#1f77b4'),
        bgcolor='rgba(255,255,255,0.85)',
        bordercolor='#1f77b4',
        borderwidth=1,
        borderpad=4,
        row=1, col=1
    )

    # Anotacion: punto minimo post-2020
    post_covid = [(d, t) for d, t in zip(dates, totals) if d >= datetime(2020, 3, 1)]
    if post_covid:
        min_val = min(post_covid, key=lambda x: x[1])
        fig.add_annotation(
            x=min_val[0],
            y=min_val[1],
            text=f'Minimo: {min_val[1]:,}<br>{min_val[0].strftime("%b %Y")}',
            showarrow=True,
            arrowhead=2,
            arrowsize=1.2,
            arrowcolor='red',
            ax=30,
            ay=-40,
            font=dict(size=10, color='red'),
            bgcolor='rgba(255,255,255,0.85)',
            bordercolor='red',
            borderwidth=1,
            borderpad=4,
            row=1, col=1
        )

    # ---- Panel inferior: Desglose por aeropuerto ----
    for airport, color in AIRPORT_COLORS.items():
        series = ts['airport_series'][airport]
        label = airport.replace('Aeropuerto Internacional ', '')
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=series,
                mode='lines',
                name=label,
                line=dict(color=color, width=2),
                opacity=0.85,
                hovertemplate=(
                    f'<b>{label}</b><br>'
                    '%{x|%b %Y}<br>'
                    '<b>%{y:,}</b> operaciones<extra></extra>'
                )
            ),
            row=2, col=1
        )

    # Layout general
    fig.update_layout(
        title=dict(
            text=(
                "<b>Evolucion de Operaciones Aeroportuarias en Costa Rica</b><br>"
                "<sup>Serie temporal 2009-2026 | "
                "Fuente: <a href='https://datos.aresep.go.cr/'>ARESEP</a></sup>"
            ),
            font=dict(size=20, family='Arial Black, sans-serif'),
            x=0.5,
            xanchor='center',
            y=0.98,
        ),
        height=800,
        template='plotly_white',
        hovermode='x unified',
        font=dict(family='Segoe UI, Arial, sans-serif', size=12),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.0,
            xanchor='center',
            x=0.5,
            font=dict(size=11)
        ),
        hoverlabel=dict(
            bgcolor='white',
            font_size=11,
            font_family='Segoe UI, Arial, sans-serif'
        ),
        margin=dict(t=120, b=40, l=60, r=30),
    )

    # Configuracion de ejes
    fig.update_xaxes(
        title=dict(text='<b>Anio</b>', font=dict(size=12)),
        showgrid=True,
        gridcolor='#eee',
        dtick='M12',
        tickformat='%Y',
        row=2, col=1
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor='#eee',
        dtick='M12',
        tickformat='%Y',
        row=1, col=1
    )
    fig.update_yaxes(
        title=dict(text='<b>Operaciones Mensuales</b>', font=dict(size=12)),
        showgrid=True,
        gridcolor='#eee',
        tickformat=',',
        row=1, col=1
    )
    fig.update_yaxes(
        title=dict(text='<b>Operaciones Mensuales</b>', font=dict(size=12)),
        showgrid=True,
        gridcolor='#eee',
        tickformat=',',
        row=2, col=1
    )

    # Ajustar rangeslider para zoom en el panel inferior
    fig.update_xaxes(rangeslider_visible=False, row=2, col=1)

    # Guardar y mostrar
    output_file = "temporal_evolution_airports.html"
    fig.write_html(output_file)
    print(f"Grafico guardado como '{output_file}'")
    fig.show()


def main() -> None:
    """Funcion principal."""
    print("=" * 60)
    print("  EVOLUCION TEMPORAL DE OPERACIONES AEROPORTUARIAS")
    print("  Costa Rica - Fuente: ARESEP")
    print("=" * 60)

    try:
        raw_data = fetch_data()
        ts = build_time_series(raw_data)
        create_plot(ts)
        print("Grafico generado exitosamente.")
    except KeyboardInterrupt:
        print("Proceso interrumpido por el usuario.")
        sys.exit(0)


if __name__ == "__main__":
    main()
