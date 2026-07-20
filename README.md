# Visualización de Operaciones Aeroportuarias - Costa Rica

Este proyecto tiene como objetivo visualizar las operaciones mensuales en los aeropuertos internacionales de Costa Rica a partir de datos abiertos de [ARESEP](https://datos.aresep.go.cr/).

---

## Visualizaciones Disponibles

### 1. Incremento Porcentual por Aeropuerto (`operations_growth.py`)

Grafico interactivo que muestra la evolucion mensual de las operaciones como **porcentaje de incremento** respecto al primer mes del periodo (desde 2020).

- Cada año se representa con una linea de color distinto
- Un subplot independiente por cada aeropuerto
- **Interactivo:** Pasa el mouse sobre los puntos para ver valores exactos
- **Autoguardado:** Genera `operations_growth_airports.html`

```bash
python3 operations_growth.py
```

### 2. Heatmap de Estacionalidad (`airport_heatmap.py`)

Heatmap interactivo que muestra:

- **Panel superior:** Volumen promedio de operaciones por aeropuerto y mes
- **Panel inferior:** Distribucion porcentual del trafico anual de cada aeropuerto
- **Interactivo:** Pasa el mouse sobre las celdas para ver detalles, zoom, exportar como PNG
- **Autoguardado:** Genera `estacionalidad_aeropuertos.html`

```bash
python3 airport_heatmap.py
```

### 3. Evolucion Temporal (`temporal_evolution.py`)

Serie de tiempo interactiva de operaciones totales mes a mes desde 2009 hasta la actualidad.

- Muestra la tendencia general del trafico aereo en Costa Rica
- Incluye todos los aeropuertos combinados y por separado
- Visualiza el impacto del COVID-19 y la recuperacion posterior
- **Autoguardado:** Genera `temporal_evolution_airports.html`

```bash
python3 temporal_evolution.py
```

### 4. Perfil de Estacionalidad (`seasonality_profile.py`)

Grafico interactivo del patron mensual promedio de cada aeropuerto.

- Compara perfiles estacionales entre aeropuertos
- Identifica meses pico y valle por aeropuerto
- Revela diferencias entre aeropuertos turisticos y de negocios
- **Autoguardado:** Genera `seasonality_profile_airports.html`

```bash
python3 seasonality_profile.py
```

---

## Requisitos e Instalacion

### Python 3.x + entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Dependencias incluidas

| Paquete | Uso |
|---------|-----|
| `requests` | Llamadas a la API de ARESEP |
| `plotly` | Todas las visualizaciones (interactivas) |
| `pandas` | Procesamiento de datos tabulares |
| `numpy` | Operaciones numericas |

---

## API de ARESEP

**Endpoint:**
```
https://datos.aresep.go.cr/ws.datosabiertos/Services/IT/Aeropuerto.svc/ObtenerHistoricoOperativoOperacion
```

**Datos disponibles:**
- **4 aeropuertos:** Juan Santamaria, Daniel Oduber Quiros, Tobias Bolanos, Limon
- **Periodo:** 2009 - 2026
- **Campos:** `id_Registro`, `id_Aeropuerto`, `aeropuerto`, `id_Mes`, `mes`, `anho`, `totalOperaciones`

> Nota: La API no acepta parametros de filtro; se descargan todos los datos y se procesan localmente.

---
