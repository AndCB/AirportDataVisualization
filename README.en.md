> 🌐 **Language:** **[Español](README.md)** | [English](README.en.md)

# Airport Operations Visualization - Costa Rica

This project aims to visualize monthly operations at Costa Rica's international airports using open data from [ARESEP](https://datos.aresep.go.cr/).

---

## Available Visualizations

### 1. Percentage Growth by Airport (`operations_growth.py`)

Interactive chart showing monthly operations as a **percentage increase** relative to the first month of the period (since 2020).

- Each year is represented by a different colored line
- An independent subplot for each airport
- **Interactive:** Hover over data points to see exact values
- **Auto-save:** Generates `operations_growth_airports.html`

```bash
python3 operations_growth.py
```

### 2. Seasonality Heatmap (`airport_heatmap.py`)

Interactive heatmap showing:

- **Top panel:** Average volume of operations by airport and month
- **Bottom panel:** Percentage distribution of each airport's annual traffic
- **Interactive:** Hover over cells for details, zoom, export as PNG
- **Auto-save:** Generates `estacionalidad_aeropuertos.html`

```bash
python3 airport_heatmap.py
```

### 3. Temporal Evolution (`temporal_evolution.py`)

Interactive time series of total month-by-month operations from 2009 to the present.

- Shows the overall trend of air traffic in Costa Rica
- Includes all airports combined and individually
- Visualizes the impact of COVID-19 and subsequent recovery
- **Auto-save:** Generates `temporal_evolution_airports.html`

```bash
python3 temporal_evolution.py
```

### 4. Seasonality Profile (`seasonality_profile.py`)

Interactive chart of the average monthly pattern for each airport.

- Compares seasonal profiles across airports
- Identifies peak and valley months per airport
- Reveals differences between tourist and business airports
- **Auto-save:** Generates `seasonality_profile_airports.html`

```bash
python3 seasonality_profile.py
```

---

## Requirements and Installation

### Python 3.x + virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Included Dependencies

| Package | Usage |
|---------|-------|
| `requests` | ARESEP API calls |
| `plotly` | All visualizations (interactive) |
| `pandas` | Tabular data processing |
| `numpy` | Numerical operations |

---

## ARESEP API

**Endpoint:**
```
https://datos.aresep.go.cr/ws.datosabiertos/Services/IT/Aeropuerto.svc/ObtenerHistoricoOperativoOperacion
```

**Available Data:**
- **4 airports:** Juan Santamaria, Daniel Oduber Quiros, Tobias Bolanos, Limon
- **Period:** 2009 - 2026
- **Fields:** `id_Registro`, `id_Aeropuerto`, `aeropuerto`, `id_Mes`, `mes`, `anho`, `totalOperaciones`

> Note: The API does not accept filter parameters; all data is downloaded and processed locally.

---
