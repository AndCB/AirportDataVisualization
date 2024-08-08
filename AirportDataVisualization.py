import requests
import matplotlib.pyplot as plt
import sys
import math

# URL of the API
url = "https://datos.aresep.go.cr/ws.datosabiertos/Services/IT/Aeropuerto.svc/ObtenerHistoricoOperativoOperacion"

response = requests.get(url)

if(response.status_code != 200):
    sys.exit('Failed to retrieve data')
    
# for filtering the data by month
month_order = {'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5,
               'Junio': 6, 'Julio': 7, 'Agosto': 8, 'Setiembre': 9, 'Octubre': 10,
               'Noviembre': 11, 'Diciembre': 12}

res = response.json()
data = res.get('value', [])
filtered_values = [item for item in data if item['anho'] >= 2020] # filter everything after 2020 out
filtered_values.sort(key=lambda x: (x['anho'], month_order[x['mes']]))

airports = sorted(set(item['aeropuerto'] for item in filtered_values))

n_airports = len(airports)
n_cols = int(math.ceil(n_airports ** 0.5))
n_rows = int(math.ceil(n_airports/n_cols))

# create plot
fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(10, 6 * n_rows), layout='constrained')
fig.subplots_adjust(hspace=0.5, wspace=0.4)
fig.suptitle("Incremento porcentual en operaciones mensuales por aeropuerto")

axes = axes.flatten()
    
for ax, airport in zip(axes, airports):
    airport_data = [item for item in filtered_values if (item['aeropuerto'] == airport)]
    
    years = sorted(set(item['anho'] for item in airport_data))
    
    first_year_data = airport_data[0] if airport_data else None
    if(first_year_data):
        first_total_ops = first_year_data['totalOperaciones']
    else:
        first_total_ops = None

    for year in years:
        year_data = [item for item in airport_data if item['anho'] == year]
            
        months = [item['mes'] for item in year_data]
        total_ops = [item['totalOperaciones'] for item in year_data]
        
        if first_total_ops is not None:
            percent_increase = [(ops / first_total_ops) for ops in total_ops]
        else:
            percent_increase = [0] * len(total_ops)

        ax.plot(months, percent_increase, marker='o', label=str(year))
    
    # config plot
    ax.set_title(f'{airport}')
    ax.set_xlabel('Mes')
    ax.set_ylabel('Incremento Porcentual (%)')
    ax.legend(title='Año')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, linestyle='--', alpha=0.7)

plt.show()

