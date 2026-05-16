# colab-nbchecker

Verificador automático de ejercicios de Pandas para el mini proyecto de KPIs.

## Instalación en Google Colab

```python
!pip install -qq git+https://github.com/OrlandoREMI/colab-nbchecker.git
```

## Uso

```python
from nbchecker import Checker

# Inicializar con el DataFrame original (sales_data, sin modificar)
checker = Checker(df)

# Verificar cada ejercicio
checker.verificar_1(precio_promedio, producto_frecuente)
checker.verificar_2(df_con_total)
checker.verificar_3(ordenes_top)
checker.verificar_4(ingresos_por_producto)
checker.verificar_5(resumen_productos)
checker.verificar_6(ventas_mensuales)
```

## Qué valida cada ejercicio

| Método | Valida |
|---|---|
| `verificar_1` | Promedio de precio (float) y producto más frecuente (str) |
| `verificar_2` | DataFrame con columna `total = price × quantity` |
| `verificar_3` | DataFrame filtrado: filas donde `total > mean(total)` |
| `verificar_4` | Serie de ingresos por producto, ordenada descendente |
| `verificar_5` | DataFrame con agg múltiple: suma, conteo y promedio por producto |
| `verificar_6` | Serie de ventas mensuales con índice DatetimeIndex |
