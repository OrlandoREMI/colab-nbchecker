"""
Lógica de comprobación de la Tarea 1 — Fundamentos de Python.

Este módulo es la ÚNICA fuente de verdad de las pruebas. Lo usan:
  - CheckerFundamentos (el alumno lo ejecuta en Colab)
  - calificar.py (calificación automática por CLI / GitHub Actions)

Todos los ejercicios son funciones: cada prueba llama a la función del alumno
con varios casos (incluidos casos que el alumno no ve) y la compara contra una
solución de referencia. Además verifica que la función no modifique lo que recibe.

Cada prueba recibe la función del alumno y regresa True (pasó) o False (no pasó).
Nunca lanza excepciones hacia afuera: cualquier error del código del alumno cuenta
como "no pasó".
"""

import copy
import math
import signal
import threading

# ─────────────────────────────────────────────────────────────────────────────
# Datos de la tarea (deben coincidir con la celda de datos del notebook)
# ─────────────────────────────────────────────────────────────────────────────

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
VENTAS_SEMANA = [1250, 980, 1430, 870, 1610, 2100, 1890]
MENU = {
    "Americano": 35,
    "Latte": 50,
    "Capuchino": 48,
    "Té chai": 45,
    "Frappé": 62,
    "Pan dulce": 22,
}
INVENTARIO = {
    "Café en grano": 3,
    "Leche": 12,
    "Azúcar": 1,
    "Vasos": 40,
    "Canela": 0,
    "Chocolate": 7,
}

TIEMPO_MAXIMO_FUNCION = 3  # segundos por llamada a una función del alumno


# ─────────────────────────────────────────────────────────────────────────────
# Utilidades
# ─────────────────────────────────────────────────────────────────────────────

class _TiempoAgotado(Exception):
    pass


def _llamar_con_limite(func, *args, segundos=TIEMPO_MAXIMO_FUNCION):
    """Llama a func(*args) cortándola si tarda demasiado (p. ej. un while infinito).
    Usa SIGALRM cuando está disponible (Linux/Colab, hilo principal)."""
    puede_cortar = (
        hasattr(signal, "SIGALRM")
        and threading.current_thread() is threading.main_thread()
    )
    if not puede_cortar:
        return func(*args)

    def _alarma(signum, frame):
        raise _TiempoAgotado()

    anterior = signal.signal(signal.SIGALRM, _alarma)
    signal.alarm(segundos)
    try:
        return func(*args)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, anterior)


def _es_numero(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _num_igual(a, b, tol=0.01):
    return _es_numero(a) and math.isclose(float(a), float(b), abs_tol=tol)


def _seguro(prueba):
    """Convierte cualquier excepción en 'no pasó'."""
    def envoltura(*args):
        try:
            return bool(prueba(*args))
        except BaseException as e:  # incluye _TiempoAgotado y SystemExit
            if isinstance(e, KeyboardInterrupt):
                raise
            return False
    envoltura.__name__ = prueba.__name__
    envoltura.__doc__ = prueba.__doc__
    return envoltura


# ─────────────────────────────────────────────────────────────────────────────
# Soluciones de referencia (privadas)
# ─────────────────────────────────────────────────────────────────────────────

def _ref_total_a_pagar(total_pedido, es_frecuente):
    if es_frecuente and total_pedido >= 150:
        return total_pedido * 0.9
    return total_pedido


def _ref_nivel(puntos):
    if puntos < 100:
        return "Bronce"
    elif puntos < 300:
        return "Plata"
    elif puntos < 600:
        return "Oro"
    return "Platino"


def _ref_resumen_semana(ventas):
    return {"primera": ventas[0], "ultima": ventas[-1], "fin_de_semana": ventas[-2:]}


def _ref_promedio(ventas):
    if len(ventas) == 0:
        return 0
    total = 0
    for v in ventas:
        total += v
    return total / len(ventas)


def _ref_dias_buenos(dias, ventas, minimo):
    return [dias[i] for i in range(len(dias)) if ventas[i] >= minimo]


def _ref_actualizar_menu(menu, producto, nuevo_precio):
    nuevo = dict(menu)
    if nuevo_precio == 0:
        if producto in nuevo:
            del nuevo[producto]
    else:
        nuevo[producto] = nuevo_precio
    return nuevo


def _ref_reabastecer(inventario, minimo):
    return [k for k, v in inventario.items() if v < minimo]


def _ref_meses(meta, ahorro_mensual):
    ahorrado, meses = 0, 0
    while ahorrado < meta:
        ahorrado += ahorro_mensual
        meses += 1
    return meses


def _ref_ticket(pedido, menu):
    total = 0
    for producto, cantidad in pedido.items():
        if producto in menu:
            total += menu[producto] * cantidad
    if total >= 200:
        total = total * 0.95
    return total


def _ref_resumen(pedidos, menu):
    por_cliente = {}
    total = 0
    for p in pedidos:
        monto = _ref_ticket(p["productos"], menu)
        total += monto
        por_cliente[p["cliente"]] = por_cliente.get(p["cliente"], 0) + monto
    top = max(por_cliente, key=por_cliente.get) if por_cliente else None
    return {"num_pedidos": len(pedidos), "total_vendido": total, "cliente_top": top}


def _probar(func, casos, comparar):
    """Llama func con cada caso (copias profundas), compara contra la referencia
    y verifica que la función no modifique lo que recibe."""
    if not callable(func):
        return False
    for args, esperado in casos:
        copia = copy.deepcopy(args)
        resultado = _llamar_con_limite(func, *copia)
        if not comparar(resultado, esperado):
            return False
        if copia != args:
            return False
    return True


def _igual(a, b):
    return type(a) is type(b) and a == b if isinstance(b, (list, dict)) else a == b


# ─────────────────────────────────────────────────────────────────────────────
# Pruebas por ejercicio
# ─────────────────────────────────────────────────────────────────────────────

@_seguro
def prueba_1(total_a_pagar):
    """if con dos condiciones (and); límite exacto en 150."""
    entradas = [
        (185, True), (185, False), (150, True), (149.99, True),
        (150, False), (0, True), (1000, True), (90, False),
    ]
    casos = [(e, _ref_total_a_pagar(*e)) for e in entradas]
    return _probar(total_a_pagar, casos, _num_igual)


@_seguro
def prueba_2(nivel_lealtad):
    """if/elif/else; se prueba en los límites de cada nivel."""
    entradas = [0, 50, 99, 100, 250, 299, 300, 450, 599, 600, 1500]
    casos = [((p,), _ref_nivel(p)) for p in entradas]
    return _probar(nivel_lealtad, casos, lambda r, e: r == e)


@_seguro
def prueba_3(resumen_semana):
    """Índices positivos, negativos y slicing."""
    entradas = [
        VENTAS_SEMANA,
        [100, 200],
        [5, 4, 3, 2, 1],
        [700, 700, 900, 300, 1200, 50],
    ]
    casos = [((list(v),), _ref_resumen_semana(v)) for v in entradas]

    def comparar(r, e):
        return (
            isinstance(r, dict)
            and set(r.keys()) == set(e.keys())
            and r["primera"] == e["primera"]
            and r["ultima"] == e["ultima"]
            and _igual(r["fin_de_semana"], e["fin_de_semana"])
        )
    return _probar(resumen_semana, casos, comparar)


@_seguro
def prueba_4(promedio_ventas):
    """for con acumulador; lista vacía regresa 0."""
    entradas = [VENTAS_SEMANA, [100], [10, 20, 30, 45], [], [0, 0, 0], [999, 1]]
    casos = [((list(v),), _ref_promedio(v)) for v in entradas]
    return _probar(promedio_ventas, casos, _num_igual)


@_seguro
def prueba_5(dias_buenos):
    """for + if recorriendo dos listas en paralelo; respeta el orden."""
    entradas = [
        (DIAS, VENTAS_SEMANA, 1500),
        (DIAS, VENTAS_SEMANA, 1430),       # límite exacto (>=)
        (DIAS, VENTAS_SEMANA, 5000),       # ninguno
        (DIAS, VENTAS_SEMANA, 0),          # todos
        (["Ene", "Feb", "Mar"], [10, 50, 30], 30),
        ([], [], 100),
    ]
    casos = [((list(d), list(v), m), _ref_dias_buenos(d, v, m)) for d, v, m in entradas]
    return _probar(dias_buenos, casos, _igual)


@_seguro
def prueba_6(actualizar_menu):
    """Leer, cambiar, agregar y eliminar llaves; regresa un menú nuevo."""
    entradas = [
        (MENU, "Americano", 38),           # cambiar precio
        (MENU, "Té matcha", 55),           # agregar
        (MENU, "Frappé", 0),               # eliminar
        (MENU, "Malteada", 0),             # eliminar algo que no existe
        ({}, "Latte", 50),                 # menú vacío
        ({"Té": 20}, "Té", 0),             # queda vacío
    ]
    casos = [((dict(m), p, n), _ref_actualizar_menu(m, p, n)) for m, p, n in entradas]
    return _probar(actualizar_menu, casos, _igual)


@_seguro
def prueba_7(por_reabastecer):
    """for sobre .items() + if; el orden de la lista no importa."""
    entradas = [
        (INVENTARIO, 5),
        (INVENTARIO, 1),                   # límite: solo los que tienen 0
        (INVENTARIO, 100),                 # todos
        (INVENTARIO, 0),                   # ninguno
        ({"Leche": 4, "Vasos": 4, "Tapas": 5}, 5),
        ({}, 10),
    ]
    casos = [((dict(i), m), _ref_reabastecer(i, m)) for i, m in entradas]

    def comparar(r, e):
        return isinstance(r, list) and len(r) == len(e) and sorted(r) == sorted(e)
    return _probar(por_reabastecer, casos, comparar)


@_seguro
def prueba_8(meses_para_meta):
    """while; incluye meta 0 y metas exactas."""
    entradas = [
        (18000, 1500), (1000, 300), (500, 500), (0, 200),
        (100, 250), (7000, 1200), (12345, 1000), (1, 1),
    ]
    casos = [(e, _ref_meses(*e)) for e in entradas]
    return _probar(meses_para_meta, casos, lambda r, e: r == e)


_MENU_PRUEBA = {"Té": 20, "Galleta": 15, "Malteada": 70}

_CASOS_TICKET = [
    ({"Latte": 2, "Pan dulce": 1}, MENU),           # sin descuento
    ({}, MENU),                                     # pedido vacío
    ({"Frappé": 3, "Americano": 1}, MENU),          # con descuento
    ({"Latte": 4}, MENU),                           # exactamente 200
    ({"Latte": 1, "Galleta": 3}, MENU),             # producto fuera del menú
    ({"Té": 2, "Galleta": 1}, _MENU_PRUEBA),        # otro menú
    ({"Malteada": 3, "Pizza": 2}, _MENU_PRUEBA),    # otro menú + desc + ignorar
    ({"Capuchino": 0, "Té chai": 4}, MENU),         # cantidad cero
]


@_seguro
def prueba_9(calcular_ticket):
    """Recorre el pedido, ignora productos fuera del menú, descuento en >= 200."""
    casos = [((dict(p), dict(m)), _ref_ticket(p, m)) for p, m in _CASOS_TICKET]
    return _probar(calcular_ticket, casos, _num_igual)


_CASOS_RESUMEN = [
    (
        [
            {"cliente": "Ana", "productos": {"Latte": 2, "Pan dulce": 1}},
            {"cliente": "Luis", "productos": {"Frappé": 3, "Americano": 1}},
            {"cliente": "Ana", "productos": {"Capuchino": 2}},
        ],
        MENU,
    ),
    (
        [
            {"cliente": "Sofía", "productos": {"Té": 1}},
            {"cliente": "Marco", "productos": {"Malteada": 1, "Galleta": 2}},
            {"cliente": "Sofía", "productos": {"Galleta": 1, "Hot dog": 3}},
            {"cliente": "Sofía", "productos": {"Té": 2}},
        ],
        _MENU_PRUEBA,
    ),
    ([{"cliente": "Iván", "productos": {"Americano": 6}}], MENU),
    ([], MENU),
]


@_seguro
def prueba_10(resumen_pedidos):
    """Integrador: lista de diccionarios, acumulado por cliente."""
    casos = [((copy.deepcopy(p), dict(m)), _ref_resumen(p, m)) for p, m in _CASOS_RESUMEN]

    def comparar(r, e):
        return (
            isinstance(r, dict)
            and set(r.keys()) == set(e.keys())
            and r["num_pedidos"] == e["num_pedidos"]
            and _num_igual(r["total_vendido"], e["total_vendido"])
            and r["cliente_top"] == e["cliente_top"]
        )
    return _probar(resumen_pedidos, casos, comparar)


# ─────────────────────────────────────────────────────────────────────────────
# Registro: número → (título, nombres de variables/funciones, prueba)
# El calificador automático busca estos nombres en el notebook del alumno.
# ─────────────────────────────────────────────────────────────────────────────

EJERCICIOS = {
    1: ("Descuento para clientes frecuentes", ["total_a_pagar"], prueba_1),
    2: ("Nivel de lealtad", ["nivel_lealtad"], prueba_2),
    3: ("Resumen de la semana (listas)", ["resumen_semana"], prueba_3),
    4: ("Promedio de ventas con for", ["promedio_ventas"], prueba_4),
    5: ("Días buenos", ["dias_buenos"], prueba_5),
    6: ("Actualizar el menú (diccionarios)", ["actualizar_menu"], prueba_6),
    7: ("Insumos por reabastecer", ["por_reabastecer"], prueba_7),
    8: ("Meta de ahorro con while", ["meses_para_meta"], prueba_8),
    9: ("Calcular un ticket", ["calcular_ticket"], prueba_9),
    10: ("Resumen de pedidos", ["resumen_pedidos"], prueba_10),
}
