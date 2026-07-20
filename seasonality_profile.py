#!/usr/bin/env python3
"""
Seasonality Profile of Airport Operations - Costa Rica
=====================================================
Compara el patron mensual promedio de operaciones entre
los distintos aeropuertos, identificando temporada alta,
baja y diferencias estacionales.
"""

import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import sys
from typing import List, Dict, Any, Tuple
from collections import defaultdict

# ============================================================
# CONFIGURACION
# ============================================================
API_URL: str = "https://datos.aresep.go.cr/ws.datosabiertos/Services/IT/Aeropuerto.svc/ObtenerHistoricoOperativoOperacion"
MONTH_ORDER: List[str] = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre'
]
MONTH_SHORT: List[str] = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                           'Jul', 'Ago', 'Set', 'Oct', 'Nov', 'Dic']
REQUEST_TIMEOUT: int = 30
YEAR_FROM: int = 2020

# Aeropuertos con colores y marcadores (misma paleta)
AIRPORT_STYLE: Dict[str, Dict[str, Any]] = {
    'Aeropuerto Internacional Juan Santamaría': {
        'color': '#1f77b4', 'symbol': 'circle', 'dash': 'solid'
    },
    'Aeropuerto Internacional Tobías Bolaños': {
        'color': '#ff7f0e', 'symbol': 'square', 'dash': 'dash'
    },
    'Aeropuerto Internacional Daniel Oduber Quirós': {
        'color': '#2ca02c', 'symbol': 'triangle-up', 'dash': 'dot'
    },
    'Aeropuerto Internacional Limón': {
        'color': '#d62728', 'symbol': 'diamond', 'dash': 'longdash'
    }
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


def compute_seasonality(items: List[Dict[str, Any]],
                        year_from: int = YEAR_FROM) -> Dict[str, Any]:
    """
    Calcula perfiles estacionales promedio por aeropuerto.

    Args:
        items: Datos de la API.
        year_from: Anio desde el cual considerar datos.

    Returns:
        Diccionario con promedios mensuales por aeropuerto y metadatos.
    """
    filtered = [it for it in items if it['anho'] >= year_from]

    # Agrupar por aeropuerto y mes
    monthly: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))

    for item in filtered:
        monthly[item['aeropuerto']][item['mes']].append(item['totalOperaciones'])

    # Calcular promedios
    profiles: Dict[str, List[float]] = {}
    for airport in AIRPORT_STYLE.keys():
        if airport in monthly:
            profiles[airport] = [
                float(np.mean(monthly[airport].get(m, [0]))) for m in MONTH_ORDER
            ]
        else:
            profiles[airport] = [0.0] * 12

    # Calcular total promedio por mes (todos los aeropuertos)
    total_monthly: List[float] = [
        sum(profiles[a][i] for a in profiles) for i in range(12)
    ]

    # Determinar temporada alta y baja
    month_labels: List[str] = []
    for i, val in enumerate(total_monthly):
        if val >= float(np.percentile(total_monthly, 66)):
            month_labels.append('Alta')
        elif val <= float(np.percentile(total_monthly, 33)):
            month_labels.append('Baja')
        else:
            month_labels.append('Media')

    # Encontrar pico y valle de cada aeropuerto
    peaks: Dict[str, Tuple[str, float]] = {}
    valleys: Dict[str, Tuple[str, float]] = {}
    for airport, profile in profiles.items():
        label = airport.replace('Aeropuerto Internacional ', '')
        max_idx = int(np.argmax(profile))
        min_idx = int(np.argmin(profile))
        peaks[label] = (MONTH_ORDER[max_idx], profile[max_idx])
        valleys[label] = (MONTH_ORDER[min_idx], profile[min_idx])

    return {
        'profiles': profiles,
        'total_monthly': total_monthly,
        'month_labels': month_labels,
        'peaks': peaks,
        'valleys': valleys
    }


def create_plot(seasonality: Dict[str, Any]) -> None:
    """
    Genera el grafico de perfil estacional con Plotly.

    Args:
        seasonality: Datos de estacionalidad calculados.
    """
    profiles = seasonality['profiles']
    total_monthly = seasonality['total_monthly']
    month_labels = seasonality['month_labels']

    x = list(range(len(MONTH_ORDER)))

    # Crear figura con 2 paneles
    fig = make_subplots(
        rows=2, cols=1,
        specs=[[{}], [{"secondary_y": True}]],
        vertical_spacing=0.12,
        row_heights=[0.55, 0.45],
        subplot_titles=(
            '<b>Perfil de Estacionalidad por Aeropuerto</b>',
            '<b>Distribucion del Trafico Mensual por Aeropuerto</b>'
        )
    )

    # ---- Panel superior: Perfiles por aeropuerto ----
    # Agregar bandas de temporada como rectangulos
    for i in range(12):
        if month_labels[i] == 'Alta':
            color = 'rgba(0, 180, 0, 0.08)'
            label = 'Temporada Alta'
        elif month_labels[i] == 'Baja':
            color = 'rgba(220, 0, 0, 0.08)'
            label = 'Temporada Baja'
        else:
            continue

        fig.add_vrect(
            x0=i - 0.45,
            x1=i + 0.45,
            fillcolor=color,
            layer='below',
            line_width=0,
            row=1, col=1
        )

    # Lineas de perfil por aeropuerto
    for airport, style in AIRPORT_STYLE.items():
        if airport in profiles:
            label = airport.replace('Aeropuerto Internacional ', '')
            fig.add_trace(
                go.Scatter(
                    x=MONTH_SHORT,
                    y=profiles[airport],
                    mode='lines+markers',
                    name=label,
                    legendgroup=label,
                    line=dict(color=style['color'], width=2.5, dash=style['dash']),
                    marker=dict(
                        symbol=style['symbol'],
                        size=8,
                        color=style['color'],
                        line=dict(width=1, color='white')
                    ),
                    hovertemplate=(
                        f'<b>{label}</b><br>'
                        '%{x}<br>'
                        '<b>%{y:,.0f}</b> operaciones promedio<extra></extra>'
                    )
                ),
                row=1, col=1
            )

    # Anotar picos
    for label, (month, value) in seasonality['peaks'].items():
        month_idx = MONTH_ORDER.index(month)
        airport_full = [a for a in AIRPORT_STYLE.keys()
                        if a.replace('Aeropuerto Internacional ', '') == label][0]
        color = AIRPORT_STYLE[airport_full]['color']
        fig.add_annotation(
            x=MONTH_SHORT[month_idx],
            y=value,
            text=f'{label}<br>{month}',
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowcolor=color,
            ax=0,
            ay=-25,
            font=dict(size=9, color=color),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor=color,
            borderwidth=1,
            borderpad=3,
            row=1, col=1
        )

    # ---- Panel inferior: Distribucion porcentual apilada ----
    # Barra apilada de porcentajes
    bottom = np.zeros(12)
    for airport, style in AIRPORT_STYLE.items():
        if airport in profiles:
            label = airport.replace('Aeropuerto Internacional ', '')
            values = np.array(profiles[airport])
            # Convertir a porcentaje del total mensual
            with np.errstate(divide='ignore', invalid='ignore'):
                pcts = np.where(
                    np.array(total_monthly) > 0,
                    values / np.array(total_monthly) * 100,
                    0
                )

            fig.add_trace(
                go.Bar(
                    x=MONTH_SHORT,
                    y=pcts,
                    name=label,
                    legendgroup=label,
                    marker=dict(color=style['color'], line=dict(width=0.5, color='white')),
                    hovertemplate=(
                        f'<b>{label}</b><br>'
                        '%{x}<br>'
                        '<b>%{y:.1f}%</b> del trafico mensual<extra></extra>'
                    ),
                    showlegend=False,
                    offsetgroup=0,
                ),
                row=2, col=1
            )
            bottom += pcts

    # Linea de total en el segundo panel (usando eje secundario)
    fig.add_trace(
        go.Scatter(
            x=MONTH_SHORT,
            y=total_monthly,
            mode='lines+markers',
            name='Total promedio',
            line=dict(color='gray', width=2, dash='dot'),
            marker=dict(symbol='diamond', size=6, color='gray'),
            hovertemplate=(
                '%{x}<br>'
                '<b>%{y:,.0f}</b> operaciones totales<extra></extra>'
            )
        ),
        row=2, col=1,
        secondary_y=True
    )

    # Layout general
    fig.update_layout(
        title=dict(
            text=(
                "<b>Perfil de Estacionalidad Aeroportuaria</b><br>"
                f"<sup>Promedio mensual desde {YEAR_FROM} | "
                "Fuente: <a href='https://datos.aresep.go.cr/'>ARESEP</a></sup>"
            ),
            font=dict(size=20, family='Arial Black, sans-serif'),
            x=0.5,
            xanchor='center',
            y=0.98,
        ),
        height=800,
        width=1050,
        template='plotly_white',
        hovermode='x unified',
        font=dict(family='Segoe UI, Arial, sans-serif', size=12),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(size=11)
        ),
        hoverlabel=dict(
            bgcolor='white',
            font_size=11,
            font_family='Segoe UI, Arial, sans-serif'
        ),
        margin=dict(t=120, b=50, l=70, r=70),
        barmode='stack',
    )

    # Ejes panel superior
    fig.update_xaxes(
        title='',
        tickfont=dict(size=11),
        showgrid=True,
        gridcolor='#eee',
        row=1, col=1
    )
    fig.update_yaxes(
        title=dict(text='<b>Operaciones Promedio por Mes</b>', font=dict(size=11)),
        tickfont=dict(size=10),
        showgrid=True,
        gridcolor='#eee',
        tickformat=',',
        row=1, col=1
    )

    # Ejes panel inferior
    fig.update_xaxes(
        title=dict(text='<b>Mes</b>', font=dict(size=12)),
        tickfont=dict(size=11),
        showgrid=True,
        gridcolor='#eee',
        row=2, col=1
    )
    fig.update_yaxes(
        title=dict(text='<b>Porcentaje del Total Mensual (%)</b>', font=dict(size=11)),
        tickfont=dict(size=10),
        showgrid=True,
        gridcolor='#eee',
        range=[0, 105],
        row=2, col=1
    )

    # Eje secundario para la linea de total
    fig.update_yaxes(
        title=dict(text='<b>Operaciones Totales</b>', font=dict(size=10, color='gray')),
        tickfont=dict(size=9, color='gray'),
        tickformat=',',
        row=2, col=1,
        secondary_y=True
    )

    # Guardar y mostrar
    output_file = "seasonality_profile_airports.html"
    fig.write_html(output_file)
    print(f"Grafico guardado como '{output_file}'")
    fig.show()


def main() -> None:
    """Funcion principal."""
    print("=" * 60)
    print("  PERFIL DE ESTACIONALIDAD AEROPORTUARIA")
    print("  Costa Rica - Fuente: ARESEP")
    print("=" * 60)

    try:
        raw_data = fetch_data()
        seasonality = compute_seasonality(raw_data)

        # Mostrar resumen en consola
        print("\nResumen de Estacionalidad:")
        print("-" * 40)
        for label, (peak_month, peak_val) in seasonality['peaks'].items():
            valley_month, valley_val = seasonality['valleys'][label]
            ratio = peak_val / valley_val if valley_val > 0 else float('inf')
            print(f"  {label}:")
            print(f"    Pico en {peak_month} ({peak_val:,.0f} ops)")
            print(f"    Valle en {valley_month} ({valley_val:,.0f} ops)")
            print(f"    Relacion pico/valle: {ratio:.1f}x\n")

        create_plot(seasonality)
        print("Grafico generado exitosamente.")
    except KeyboardInterrupt:
        print("Proceso interrumpido por el usuario.")
        sys.exit(0)


if __name__ == "__main__":
    main()
