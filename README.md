# colab-nbchecker

Verificadores automáticos de ejercicios para Google Colab:

- `Checker` — Mini proyecto de KPIs con Pandas.
- `CheckerFundamentos` — Tarea 1: fundamentos de Python (if, for, while, listas, diccionarios, funciones).

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

---

## Tarea 1 — Fundamentos de Python (`CheckerFundamentos`)

### Uso en Colab (alumno)

```python
from nbchecker import CheckerFundamentos
checker = CheckerFundamentos()

# cada ejercicio es una función; se pasa la función, sin paréntesis
checker.verificar_1(total_a_pagar)
checker.verificar_2(nivel_lealtad)
checker.verificar_3(resumen_semana)
checker.verificar_4(promedio_ventas)
checker.verificar_5(dias_buenos)
checker.verificar_6(actualizar_menu)
checker.verificar_7(por_reabastecer)
checker.verificar_8(meses_para_meta)
checker.verificar_9(calcular_ticket)
checker.verificar_10(resumen_pedidos)
checker.resumen()
```

El feedback solo indica si cada ejercicio **pasó** o **no pasó** las comprobaciones.
Los 10 ejercicios son funciones: cada una se prueba con varios casos (incluidos casos límite que
el alumno no ve) contra una solución de referencia, y se verifica que no modifique las listas o
diccionarios que recibe. Cada llamada se corta a los 3 segundos para proteger contra ciclos infinitos.

### Calificación automática (CLI)

```bash
python -m nbchecker.fundamentos.calificar --notebook entrega.ipynb --config config.json
```

Imprime un único JSON en stdout:

```json
{"grade": 80.0, "feedback": "Ejercicio 1 (...): ✅ pasó\n...", "aprobados": 8, "total": 10,
 "detalle": {"1": true, "2": false, "...": true}}
```

`config.json` es opcional: `{"max_grade": 100, "timeout_celda": 10, "timeout_total": 180}`.

El calificador ejecuta las celdas de código del alumno en un proceso aparte (sin las celdas del
checker ni los comandos `!`/`%`), con límite de tiempo por celda, y corre exactamente las mismas
pruebas que ve el alumno (`nbchecker/fundamentos/pruebas.py`).
