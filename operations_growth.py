#!/usr/bin/env python3
"""
Operations Growth by Airport - Costa Rica
==========================================
Incremento porcentual en operaciones mensuales por aeropuerto,
tomando como base el primer mes del periodo.
Fuente: ARESEP - https://datos.aresep.go.cr/
"""

import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import math
from typing import List, Dict, Any

# ============================================================
# CONFIGURACION
# ============================================================
API_URL: str = "https://datos.aresep.go.cr/ws.datosabiertos/Services/IT/Aeropuerto.svc/ObtenerHistoricoOperativoOperacion"
MONTH_ORDER: Dict[str, int] = {
    'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5,
    'Junio': 6, 'Julio': 7, 'Agosto': 8, 'Setiembre': 9, 'Octubre': 10,
    'Noviembre': 11, 'Diciembre': 12
}
YEAR_FROM: int = 2020
REQUEST_TIMEOUT: int = 30

# Paleta de colores para los anios
COLORS = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#17becf'
]


# ============================================================
# FUNCIONES
# ============================================================
def fetch_data() -> List[Dict[str, Any]]:
    """
    Obtiene datos historicos de operaciones aeroportuarias desde la API de ARESEP.

    Returns:
        Lista de diccionarios con los datos.

    Raises:
        SystemExit: Si hay error de conexion, timeout, o formato inesperado.
    """
    print("Conectando con ARESEP...")
    try:
        response = requests.get(API_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        sys.exit(f"Error: La API no respondio despues de {REQUEST_TIMEOUT} segundos.")
    except requests.exceptions.ConnectionError:
        sys.exit("Error: No se pudo conectar con la API. Verifica tu conexion a internet.")
    except requests.exceptions.HTTPError as e:
        sys.exit(f"Error HTTP: {e.response.status_code} - {e.response.reason}")
    except requests.exceptions.RequestException as e:
        sys.exit(f"Error inesperado de red: {e}")

    try:
        data: Dict[str, Any] = response.json()
    except ValueError:
        sys.exit("Error: La respuesta de la API no es un JSON valido.")

    items: List[Dict[str, Any]] = data.get('value', [])
    if not items:
        sys.exit("Error: La API devolvio una lista vacia.")

    return items


def validate_data(items: List[Dict[str, Any]]) -> None:
    """
    Valida que todos los items tengan los campos requeridos con tipos correctos.

    Args:
        items: Lista de registros de la API.

    Raises:
        SystemExit: Si algun campo requerido falta o tiene tipo incorrecto.
    """
    required_keys: Dict[str, type] = {
        'aeropuerto': str,
        'mes': str,
        'anho': (int, float),
        'totalOperaciones': (int, float)
    }

    for i, item in enumerate(items):
        for key, expected_type in required_keys.items():
            if key not in item:
                sys.exit(f"Error: El registro {i} no contiene el campo '{key}'.")
            if not isinstance(item[key], expected_type):
                sys.exit(
                    f"Error: El campo '{key}' en el registro {i} deberia ser "
                    f"{expected_type.__name__}, pero es {type(item[key]).__name__}."
                )


def process_data(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filtra datos desde YEAR_FROM y ordena por anio y mes.

    Args:
        items: Lista de registros de la API.

    Returns:
        Lista filtrada y ordenada.
    """
    filtered: List[Dict[str, Any]] = [
        item for item in items if item['anho'] >= YEAR_FROM
    ]

    if not filtered:
        sys.exit(f"No hay datos disponibles desde el anio {YEAR_FROM}.")

    filtered.sort(key=lambda x: (x['anho'], MONTH_ORDER.get(x['mes'], 99)))

    print(f"Datos filtrados: {len(filtered)} registros desde {YEAR_FROM}")
    return filtered


def create_plots(items: List[Dict[str, Any]]) -> None:
    """
    Genera los subplots de incremento porcentual por aeropuerto usando Plotly.

    Args:
        items: Lista de registros procesados.
    """
    airports: List[str] = sorted(set(item['aeropuerto'] for item in items))
    n_airports: int = len(airports)
    n_cols: int = int(math.ceil(n_airports ** 0.5))
    n_rows: int = int(math.ceil(n_airports / n_cols))

    print(f"Aeropuertos ({n_airports}): {', '.join(airports)}")

    # Crear nombres cortos para titulos
    airport_short_names: Dict[str, str] = {}
    for ap in airports:
        short = ap.replace('Aeropuerto Internacional ', '')
        airport_short_names[ap] = short

    # Construir subplots
    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=[airport_short_names[ap] for ap in airports],
        horizontal_spacing=0.08,
        vertical_spacing=0.12,
    )

    # Agregar trazados
    for idx, airport in enumerate(airports):
        row = (idx // n_cols) + 1
        col = (idx % n_cols) + 1

        airport_data: List[Dict[str, Any]] = [
            item for item in items if item['aeropuerto'] == airport
        ]

        if not airport_data:
            continue

        years: List[int] = sorted(set(item['anho'] for item in airport_data))
        first_month_ops: int = airport_data[0]['totalOperaciones']

        for y_idx, year in enumerate(years):
            year_data: List[Dict[str, Any]] = [
                item for item in airport_data if item['anho'] == year
            ]
            months: List[str] = [item['mes'] for item in year_data]
            total_ops: List[int] = [item['totalOperaciones'] for item in year_data]

            # Calcular incremento porcentual real
            percent_increase: List[float] = [
                ((ops - first_month_ops) / first_month_ops) * 100
                for ops in total_ops
            ]

            fig.add_trace(
                go.Scatter(
                    x=months,
                    y=percent_increase,
                    mode='lines+markers',
                    name=str(year),
                    legendgroup=str(year),
                    showlegend=(idx == 0),
                    line=dict(color=COLORS[y_idx % len(COLORS)], width=2),
                    marker=dict(size=6),
                    hovertemplate=(
                        f'<b>{airport_short_names[airport]}</b><br>'
                        '%{x}<br>'
                        f'Anio {year}<br>'
                        '<b>%{y:.1f}%</b> de incremento<br>'
                        '<extra></extra>'
                    ),
                ),
                row=row, col=col
            )

        # Linea de referencia en y=0
        fig.add_hline(
            y=0, line=dict(color='gray', width=0.5, dash='dot'),
            row=row, col=col
        )

    # Ocultar subplots vacios
    total_cells = n_rows * n_cols
    for i in range(n_airports, total_cells):
        row = (i // n_cols) + 1
        col = (i % n_cols) + 1
        fig.update_xaxes(visible=False, row=row, col=col)
        fig.update_yaxes(visible=False, row=row, col=col)

    # Layout general
    fig.update_layout(
        title=dict(
            text=(
                '<b>Incremento Porcentual en Operaciones Mensuales por Aeropuerto</b><br>'
                f'<sup>Base = primer mes del periodo, desde {YEAR_FROM} | '
                "Fuente: <a href='https://datos.aresep.go.cr/'>ARESEP</a></sup>"
            ),
            font=dict(size=18, family='Arial Black, sans-serif'),
            x=0.5,
            xanchor='center',
        ),
        height=300 * n_rows,
        width=350 * n_cols,
        template='plotly_white',
        hovermode='closest',
        font=dict(family='Segoe UI, Arial, sans-serif', size=11),
        legend=dict(
            title=dict(text='<b>Anio</b>'),
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(size=11)
        ),
        margin=dict(t=100, b=40, l=50, r=30),
    )

    # Configurar ejes
    fig.update_xaxes(
        tickangle=45,
        tickfont=dict(size=9),
        showgrid=True,
        gridcolor='#eee',
    )
    fig.update_yaxes(
        title=dict(text='Incremento (%)', font=dict(size=10)),
        tickfont=dict(size=9),
        showgrid=True,
        gridcolor='#eee',
        zeroline=False,
    )

    # Guardar y mostrar
    output_file = "operations_growth_airports.html"
    fig.write_html(output_file)
    print(f"Grafico guardado como '{output_file}'")
    fig.show()


def main() -> None:
    """Funcion principal del script."""
    print("=" * 60)
    print("  CRECIMIENTO DE OPERACIONES POR AEROPUERTO")
    print("  Costa Rica - Fuente: ARESEP (https://datos.aresep.go.cr/)")
    print("=" * 60)

    try:
        raw_data = fetch_data()
        validate_data(raw_data)
        processed_data = process_data(raw_data)
        create_plots(processed_data)
        print("\nVisualizacion generada exitosamente.")
    except KeyboardInterrupt:
        print("\nProceso interrumpido por el usuario.")
        sys.exit(0)


if __name__ == "__main__":
    main()
