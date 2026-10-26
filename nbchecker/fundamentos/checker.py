"""
Checker que el alumno ejecuta dentro de Colab.

Solo informa si cada ejercicio pasó o no pasó las comprobaciones.
No revela respuestas esperadas ni da pistas.

Uso:
    from nbchecker import CheckerFundamentos
    checker = CheckerFundamentos()
    checker.verificar_1(total_a_pagar)
    ...
    checker.resumen()
"""

from . import pruebas


class CheckerFundamentos:

    def __init__(self):
        self._resultados = {}
        print("✅ Checker listo. Ya puedes empezar con los ejercicios.")

    # ── interno ──────────────────────────────────────────────────────────────

    def _registrar(self, n, *args):
        titulo, _, prueba = pruebas.EJERCICIOS[n]
        paso = prueba(*args)
        self._resultados[n] = paso
        if paso:
            print(f"✅ Ejercicio {n} — {titulo}: pasó las comprobaciones.")
        else:
            print(f"❌ Ejercicio {n} — {titulo}: no pasó las comprobaciones.")

    # ── un método por ejercicio ─────────────────────────────────────────────

    def verificar_1(self, total_a_pagar):
        self._registrar(1, total_a_pagar)

    def verificar_2(self, nivel_lealtad):
        self._registrar(2, nivel_lealtad)

    def verificar_3(self, venta_lunes, venta_domingo, fin_de_semana):
        self._registrar(3, venta_lunes, venta_domingo, fin_de_semana)

    def verificar_4(self, total_semana, promedio_diario):
        self._registrar(4, total_semana, promedio_diario)

    def verificar_5(self, dias_buenos, mejor_dia):
        self._registrar(5, dias_buenos, mejor_dia)

    def verificar_6(self, precio_capuchino, menu_actualizado):
        self._registrar(6, precio_capuchino, menu_actualizado)

    def verificar_7(self, por_reabastecer, total_unidades):
        self._registrar(7, por_reabastecer, total_unidades)

    def verificar_8(self, meses_para_meta):
        self._registrar(8, meses_para_meta)

    def verificar_9(self, calcular_ticket):
        self._registrar(9, calcular_ticket)

    def verificar_10(self, resumen_pedidos):
        self._registrar(10, resumen_pedidos)

    # ── resumen ──────────────────────────────────────────────────────────────

    def resumen(self):
        total = len(pruebas.EJERCICIOS)
        aprobados = sum(1 for v in self._resultados.values() if v)
        print("─" * 50)
        for n, (titulo, _, _) in pruebas.EJERCICIOS.items():
            if n not in self._resultados:
                marca = "⬜ sin verificar"
            elif self._resultados[n]:
                marca = "✅ pasó"
            else:
                marca = "❌ no pasó"
            print(f"  {n:>2}. {titulo:<38} {marca}")
        print("─" * 50)
        print(f"  Ejercicios aprobados: {aprobados}/{total}")
        if aprobados == total:
            print("  🎉 ¡Tarea completa!")
