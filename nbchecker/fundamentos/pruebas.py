"""
Lógica de comprobación de la Tarea 1 — Fundamentos de Python.

Este módulo es la ÚNICA fuente de verdad de las pruebas. Lo usan:
  - CheckerFundamentos (el alumno lo ejecuta en Colab)
  - calificar.py (calificación automática por CLI / GitHub Actions)

Cada prueba recibe los objetos del alumno y regresa True (pasó) o False (no pasó).
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
TOTAL_PEDIDO = 185
ES_FRECUENTE = True

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

def _ref_nivel(puntos):
    if puntos < 100:
        return "Bronce"
    elif puntos < 300:
        return "Plata"
    elif puntos < 600:
        return "Oro"
    return "Platino"


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


# ─────────────────────────────────────────────────────────────────────────────
# Pruebas por ejercicio
# ─────────────────────────────────────────────────────────────────────────────

@_seguro
def prueba_1(total_a_pagar):
    """Descuento de 10% si es cliente frecuente Y el total es >= 150."""
    esperado = TOTAL_PEDIDO * 0.9 if (ES_FRECUENTE and TOTAL_PEDIDO >= 150) else TOTAL_PEDIDO
    return _num_igual(total_a_pagar, esperado)


@_seguro
def prueba_2(nivel_lealtad):
    """Función con if/elif/else; se prueba en los límites de cada nivel."""
    if not callable(nivel_lealtad):
        return False
    casos = [0, 50, 99, 100, 250, 299, 300, 450, 599, 600, 1500]
    return all(
        _llamar_con_limite(nivel_lealtad, p) == _ref_nivel(p) for p in casos
    )


@_seguro
def prueba_3(venta_lunes, venta_domingo, fin_de_semana):
    return (
        venta_lunes == VENTAS_SEMANA[0]
        and venta_domingo == VENTAS_SEMANA[-1]
        and isinstance(fin_de_semana, list)
        and fin_de_semana == VENTAS_SEMANA[-2:]
    )


@_seguro
def prueba_4(total_semana, promedio_diario):
    total = sum(VENTAS_SEMANA)
    return _num_igual(total_semana, total) and _num_igual(
        promedio_diario, total / len(VENTAS_SEMANA)
    )


@_seguro
def prueba_5(dias_buenos, mejor_dia):
    esperado_buenos = [d for d, v in zip(DIAS, VENTAS_SEMANA) if v >= 1500]
    esperado_mejor = DIAS[VENTAS_SEMANA.index(max(VENTAS_SEMANA))]
    return (
        isinstance(dias_buenos, list)
        and dias_buenos == esperado_buenos
        and mejor_dia == esperado_mejor
    )


@_seguro
def prueba_6(precio_capuchino, menu_actualizado):
    esperado = dict(MENU)
    esperado["Americano"] = 38
    esperado["Té matcha"] = 55
    del esperado["Frappé"]
    return (
        precio_capuchino == MENU["Capuchino"]
        and isinstance(menu_actualizado, dict)
        and menu_actualizado == esperado
    )


@_seguro
def prueba_7(por_reabastecer, total_unidades):
    esperado = [k for k, v in INVENTARIO.items() if v < 5]
    return (
        isinstance(por_reabastecer, list)
        and sorted(por_reabastecer) == sorted(esperado)
        and len(por_reabastecer) == len(esperado)
        and total_unidades == sum(INVENTARIO.values())
    )


@_seguro
def prueba_8(meses_para_meta):
    if not callable(meses_para_meta):
        return False
    casos = [
        (18000, 1500), (1000, 300), (500, 500), (0, 200),
        (100, 250), (7000, 1200), (12345, 1000), (1, 1),
    ]
    return all(
        _llamar_con_limite(meses_para_meta, m, a) == _ref_meses(m, a)
        for m, a in casos
    )


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
    if not callable(calcular_ticket):
        return False
    for pedido, menu in _CASOS_TICKET:
        p, m = copy.deepcopy(pedido), copy.deepcopy(menu)
        resultado = _llamar_con_limite(calcular_ticket, p, m)
        if not _num_igual(resultado, _ref_ticket(pedido, menu)):
            return False
        if p != pedido or m != menu:  # no debe modificar lo que recibe
            return False
    return True


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
    if not callable(resumen_pedidos):
        return False
    for pedidos, menu in _CASOS_RESUMEN:
        p, m = copy.deepcopy(pedidos), copy.deepcopy(menu)
        r = _llamar_con_limite(resumen_pedidos, p, m)
        e = _ref_resumen(pedidos, menu)
        if not isinstance(r, dict):
            return False
        if set(r.keys()) != set(e.keys()):
            return False
        if r["num_pedidos"] != e["num_pedidos"]:
            return False
        if not _num_igual(r["total_vendido"], e["total_vendido"]):
            return False
        if r["cliente_top"] != e["cliente_top"]:
            return False
        if p != pedidos or m != menu:
            return False
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Registro: número → (título, nombres de variables/funciones, prueba)
# El calificador automático busca estos nombres en el notebook del alumno.
# ─────────────────────────────────────────────────────────────────────────────

EJERCICIOS = {
    1: ("Descuento para clientes frecuentes", ["total_a_pagar"], prueba_1),
    2: ("Nivel de lealtad", ["nivel_lealtad"], prueba_2),
    3: ("Ventas de la semana (listas)", ["venta_lunes", "venta_domingo", "fin_de_semana"], prueba_3),
    4: ("Total y promedio con for", ["total_semana", "promedio_diario"], prueba_4),
    5: ("Días buenos y mejor día", ["dias_buenos", "mejor_dia"], prueba_5),
    6: ("Actualizar el menú (diccionarios)", ["precio_capuchino", "menu_actualizado"], prueba_6),
    7: ("Revisión de inventario", ["por_reabastecer", "total_unidades"], prueba_7),
    8: ("Meta de ahorro con while", ["meses_para_meta"], prueba_8),
    9: ("Calcular un ticket", ["calcular_ticket"], prueba_9),
    10: ("Resumen de pedidos", ["resumen_pedidos"], prueba_10),
}
