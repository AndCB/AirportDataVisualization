# Visualización de Operaciones Mensuales en Aeropuertos

Este proyecto tiene como objetivo visualizar las operaciones mensuales en aeropuertos de Costa Rica a partir de los datos obtenidos de la API proporcionada por ARESEP. El análisis se centra en los datos desde 2020 en adelante, y la visualización se realiza mostrando el porcentaje de incremento en las operaciones mes a mes para cada año.

## Requisitos

Para ejecutar este proyecto, se necesita tener instalado:

- Python 3.x
- Las siguientes bibliotecas de Python:
  - `requests`
  - `matplotlib`
  - `numpy`

Pueden instalarlas ejecutando:

```bash
pip install requests matplotlib numpy
```

# Descripcion

## Obtencion de datos de la API

Se realiza un GET a la API del ARESEP para obtener datos historicos de las operaciones de los aeropuertos internacionales de Costa Rica. La URL es la siguiente:

```python
URL = "https://datos.aresep.go.cr/ws.datosabiertos/Services/IT/Aeropuerto.svc/ObtenerHistoricoOperativoOperacion"
```

La api no provee la opcion de parametrizacion en el url o cuerpo por lo que se deben recibir los datos de todos los años desde el 2009 y procesarlos segun se necesite.

## Filtrado y ordenado de datos

Una vez se obtienen los datos, se filtran para capturar solo los años del 2020 en adelante. Los datos sse ordenan por mes para cada año y se calculas los incrementos porcentuales mensuales en las operaciones mes a mes.

## Visualizacion

Se utiliza matplotlib para la generacion de una grafica de lineas donde cada año se representa por una linea distinta. En la grafica se muestra el increment porcentual de las operaciones.

## Ejecucion del codigo

Simplemente se debe ejecutar el script de python. El codigo generara una visualizacion que muestra como han cambiado las operaciones de mes a mes por cada año desde el 2020 para los diferentes aeropuertos.

# Instrucciones de uso

1. Ejecutar el script: Al ejecutar el script se realizara una solicitud a la API, se procesaran los datos y se generara la grafica.
2. Interpretacion de la grafica: La gráfica mostrará el porcentaje de incremento de operaciones para cada mes, permitiendo comparar cómo variaron las operaciones mes a mes para cada año.
3. Modificar el codigo: Se se desean analizar otros datos o cambiar el enfoque del analisis se debera de modificar el codigo.

# Ejemplo de uso

Al ejecutar el codigo, se generara una grafica como la siguiente:
![image](https://github.com/user-attachments/assets/908cc909-a699-443f-b1e1-dc7a3aa4f8aa)





