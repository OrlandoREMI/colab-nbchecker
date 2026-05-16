import pandas as pd
import numpy as np


class Checker:
    """
    Verificador automático de ejercicios — Mini Proyecto KPIs con Pandas.

    Uso:
        from nbchecker import Checker
        checker = Checker(df)          # df = sales_data original, sin modificar
        checker.verificar_1(precio_promedio, producto_frecuente)
        checker.verificar_2(df_con_total)
        ...
    """

    _REQUIRED = {"order_id", "customer_id", "product", "price", "quantity", "date"}

    def __init__(self, df: pd.DataFrame):
        missing = self._REQUIRED - set(df.columns)
        if missing:
            raise ValueError(
                f"❌ Al DataFrame le faltan las columnas requeridas: {missing}\n"
                "   Asegúrate de pasar el DataFrame original de sales_data."
            )
        self.df = df.copy()
        self.df["date"] = pd.to_datetime(self.df["date"])

        # DataFrame con columna 'total' precalculada para validaciones
        self._dft = self.df.copy()
        self._dft["total"] = self._dft["price"] * self._dft["quantity"]

        print("✅ Checker inicializado. ¡Listo para verificar tus ejercicios!")

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers internos
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _ok(msg: str):
        print(f"  ✅ {msg}")

    @staticmethod
    def _fail(msg: str, hint: str = ""):
        print(f"  ❌ {msg}")
        if hint:
            print(f"     💡 Pista: {hint}")

    @staticmethod
    def _describe(obj) -> str:
        """Descripción corta de un objeto para mensajes de error."""
        if isinstance(obj, pd.DataFrame):
            return f"DataFrame con forma {obj.shape} y columnas {list(obj.columns)}"
        if isinstance(obj, pd.Series):
            return (
                f"Series con {len(obj)} elementos, "
                f"dtype={obj.dtype}, nombre='{obj.name}'"
            )
        return f"{type(obj).__name__}: {repr(obj)[:60]}"

    def _header(self, n: int, titulo: str):
        print(f"\n{'─'*50}")
        print(f"  Ejercicio {n}: {titulo}")
        print(f"{'─'*50}")

    # ─────────────────────────────────────────────────────────────────────────
    # Ejercicio 1 — Estadística descriptiva
    # ─────────────────────────────────────────────────────────────────────────

    def verificar_1(self, precio_promedio, producto_frecuente):
        """
        Valida:
          - precio_promedio  → float con el promedio de la columna 'price'
          - producto_frecuente → str con el nombre del producto más frecuente
        """
        self._header(1, "Estadística Descriptiva")
        ok = True

        # ── precio_promedio ──────────────────────────────────────────────────
        expected_precio = self.df["price"].mean()

        if not isinstance(precio_promedio, (int, float, np.floating)):
            self._fail(
                f"'precio_promedio' debe ser un número. "
                f"Recibiste: {type(precio_promedio).__name__}",
                "Usa df['price'].mean() y guarda el resultado directamente.",
            )
            ok = False
        elif not np.isclose(float(precio_promedio), expected_precio, rtol=1e-3):
            self._fail(
                f"'precio_promedio' incorrecto. "
                f"Esperado ≈ {expected_precio:.4f}, recibiste {precio_promedio}.",
            )
            ok = False
        else:
            self._ok(f"precio_promedio correcto ({precio_promedio:.4f})")

        # ── producto_frecuente ───────────────────────────────────────────────
        expected_prod = self.df["product"].value_counts().index[0]

        if not isinstance(producto_frecuente, str):
            self._fail(
                f"'producto_frecuente' debe ser un string. "
                f"Recibiste: {type(producto_frecuente).__name__}",
                "Usa df['product'].value_counts().index[0] para obtener el nombre.",
            )
            ok = False
        elif producto_frecuente != expected_prod:
            self._fail(
                f"'producto_frecuente' incorrecto. "
                f"Esperado: '{expected_prod}', recibiste: '{producto_frecuente}'.",
            )
            ok = False
        else:
            self._ok(f"producto_frecuente correcto ('{producto_frecuente}')")

        print("\n🎉 ¡Ejercicio 1 completado!" if ok else "\n⚠️  Revisa los puntos marcados con ❌.")

    # ─────────────────────────────────────────────────────────────────────────
    # Ejercicio 2 — Columna derivada
    # ─────────────────────────────────────────────────────────────────────────

    def verificar_2(self, df_resultado):
        """
        Valida que df_resultado sea el DataFrame original con la columna
        'total' = price × quantity correctamente calculada.
        """
        self._header(2, "Columna Derivada")
        ok = True

        if not isinstance(df_resultado, pd.DataFrame):
            self._fail(
                f"Se esperaba un DataFrame. "
                f"Recibiste: {self._describe(df_resultado)}",
                "Guarda el DataFrame completo (con la nueva columna) en la variable.",
            )
            print("\n⚠️  Revisa los puntos marcados con ❌.")
            return

        # Número de filas
        if len(df_resultado) != len(self.df):
            self._fail(
                f"El DataFrame tiene {len(df_resultado)} filas; "
                f"se esperaban {len(self.df)}. No elimines filas.",
            )
            ok = False

        # Existencia de columna 'total'
        if "total" not in df_resultado.columns:
            self._fail(
                "El DataFrame no contiene la columna 'total'.",
                "Crea la columna con: df['total'] = df['price'] * df['quantity']",
            )
            ok = False
        else:
            expected_total = self.df["price"] * self.df["quantity"]
            if not np.allclose(
                df_resultado["total"].values, expected_total.values, rtol=1e-4
            ):
                self._fail(
                    "Los valores de 'total' no coinciden con price × quantity.",
                    "Verifica la operación: df['total'] = df['price'] * df['quantity']",
                )
                ok = False
            else:
                self._ok("Columna 'total' correcta (price × quantity ✓)")

        print("\n🎉 ¡Ejercicio 2 completado!" if ok else "\n⚠️  Revisa los puntos marcados con ❌.")

    # ─────────────────────────────────────────────────────────────────────────
    # Ejercicio 3 — Filtrado con query
    # ─────────────────────────────────────────────────────────────────────────

    def verificar_3(self, df_filtrado):
        """
        Valida que df_filtrado contenga solo las filas donde
        total > promedio(total).
        """
        self._header(3, "Filtrado con query()")
        ok = True

        if not isinstance(df_filtrado, pd.DataFrame):
            self._fail(
                f"Se esperaba un DataFrame. "
                f"Recibiste: {self._describe(df_filtrado)}",
                "Usa df.query('total > @umbral') o df[df['total'] > umbral].",
            )
            print("\n⚠️  Revisa los puntos marcados con ❌.")
            return

        if "total" not in df_filtrado.columns:
            self._fail(
                "El DataFrame filtrado debe conservar la columna 'total'.",
                "No elimines columnas al filtrar.",
            )
            print("\n⚠️  Revisa los puntos marcados con ❌.")
            return

        umbral = self._dft["total"].mean()
        expected = self._dft[self._dft["total"] > umbral]

        # Número de filas
        if len(df_filtrado) != len(expected):
            self._fail(
                f"Número de filas incorrecto. "
                f"Esperadas: {len(expected)}, recibidas: {len(df_filtrado)}.",
                f"El umbral es el promedio de 'total' ≈ {umbral:.2f}. Usa '>' estricto.",
            )
            ok = False
        else:
            # Todas las filas cumplen la condición
            if not (df_filtrado["total"] > umbral).all():
                self._fail(
                    "Algunas filas no cumplen la condición total > promedio.",
                    "Asegúrate de usar '>' y no '>='.",
                )
                ok = False
            else:
                self._ok(
                    f"Filtro correcto — {len(df_filtrado)} filas "
                    f"con total > {umbral:.2f} ✓"
                )

        print("\n🎉 ¡Ejercicio 3 completado!" if ok else "\n⚠️  Revisa los puntos marcados con ❌.")

    # ─────────────────────────────────────────────────────────────────────────
    # Ejercicio 4 — Groupby simple
    # ─────────────────────────────────────────────────────────────────────────

    def verificar_4(self, resultado):
        """
        Valida que resultado sea una Serie con ingresos totales por producto,
        ordenada de mayor a menor.
        """
        self._header(4, "Agrupación Simple (groupby)")
        ok = True

        # Aceptar DataFrame de 1 columna y convertirlo a Serie
        if isinstance(resultado, pd.DataFrame):
            if resultado.shape[1] == 1:
                resultado = resultado.iloc[:, 0]
            else:
                self._fail(
                    f"Se esperaba una Serie (o DataFrame de 1 columna). "
                    f"Recibiste {self._describe(resultado)}.",
                    "Selecciona solo la columna 'total' después del groupby: "
                    "groupby('product')['total'].sum()",
                )
                print("\n⚠️  Revisa los puntos marcados con ❌.")
                return

        if not isinstance(resultado, pd.Series):
            self._fail(
                f"Se esperaba una Series. Recibiste: {self._describe(resultado)}",
            )
            print("\n⚠️  Revisa los puntos marcados con ❌.")
            return

        expected = (
            self._dft.groupby("product")["total"]
            .sum()
            .sort_values(ascending=False)
        )

        # Índice
        if set(resultado.index) != set(expected.index):
            extra = set(resultado.index) - set(expected.index)
            missing = set(expected.index) - set(resultado.index)
            self._fail(
                f"El índice no coincide con los productos esperados. "
                f"Extra: {extra}  Faltantes: {missing}",
                "Agrupa por la columna 'product'.",
            )
            ok = False
        else:
            self._ok("Índice de productos correcto.")

        # Valores
        if ok:
            reindexed = resultado.reindex(expected.index)
            if not np.allclose(reindexed.values, expected.values, rtol=1e-3):
                self._fail(
                    "Los valores de ingreso por producto no son correctos.",
                    "Asegúrate de sumar la columna 'total' (price × quantity).",
                )
                ok = False
            else:
                self._ok("Valores de ingresos por producto correctos.")

        # Orden
        if not resultado.is_monotonic_decreasing:
            self._fail(
                "La Serie no está ordenada de mayor a menor.",
                "Agrega .sort_values(ascending=False) al final.",
            )
            ok = False
        else:
            self._ok("Orden descendente correcto.")

        print("\n🎉 ¡Ejercicio 4 completado!" if ok else "\n⚠️  Revisa los puntos marcados con ❌.")

    # ─────────────────────────────────────────────────────────────────────────
    # Ejercicio 5 — Agregación múltiple con .agg()
    # ─────────────────────────────────────────────────────────────────────────

    def verificar_5(self, resultado):
        """
        Valida que resultado sea un DataFrame con agrupación por producto
        que incluya al menos: suma de total, conteo de órdenes y promedio de price.
        """
        self._header(5, "Agregación Múltiple (.agg())")
        ok = True

        if not isinstance(resultado, pd.DataFrame):
            self._fail(
                f"Se esperaba un DataFrame. Recibiste: {self._describe(resultado)}",
                "Usa .agg() después del groupby para obtener un DataFrame.",
            )
            print("\n⚠️  Revisa los puntos marcados con ❌.")
            return

        # Índice = productos
        expected_index = set(self._dft["product"].unique())
        if set(resultado.index) != expected_index:
            self._fail(
                "El índice del DataFrame debe ser la columna 'product'.",
                "Asegúrate de agrupar por 'product'.",
            )
            ok = False
        else:
            self._ok("Índice de productos correcto.")

        # Mínimo 3 columnas numéricas
        num_cols = resultado.select_dtypes(include="number").columns.tolist()
        if len(num_cols) < 3:
            self._fail(
                f"Se esperaban al menos 3 columnas numéricas (suma, conteo, promedio). "
                f"Encontradas: {len(num_cols)} → {num_cols}",
                "Incluye sum, count y mean en tu .agg().",
            )
            ok = False
        else:
            self._ok(f"3+ columnas numéricas encontradas: {num_cols}")

        # Validar que exista una columna con la suma de total
        expected_sum = self._dft.groupby("product")["total"].sum()
        expected_count = self._dft.groupby("product")["order_id"].count()
        expected_mean = self.df.groupby("product")["price"].mean()

        found_sum = found_count = found_mean = False
        for col in num_cols:
            vals = resultado[col].reindex(expected_sum.index)
            if not found_sum and np.allclose(vals.values, expected_sum.values, rtol=1e-2):
                self._ok(f"Suma de ingresos correcta (columna '{col}').")
                found_sum = True
            if not found_count and np.allclose(vals.values, expected_count.values, rtol=1e-2):
                self._ok(f"Conteo de órdenes correcto (columna '{col}').")
                found_count = True
            if not found_mean and np.allclose(vals.values, expected_mean.values, rtol=1e-2):
                self._ok(f"Promedio de precio correcto (columna '{col}').")
                found_mean = True

        if not found_sum:
            self._fail(
                "No se encontró una columna con la suma correcta de ingresos.",
                "Incluye: ('total', 'sum') en tu .agg().",
            )
            ok = False
        if not found_count:
            self._fail(
                "No se encontró una columna con el conteo correcto de órdenes.",
                "Incluye: ('order_id', 'count') en tu .agg().",
            )
            ok = False
        if not found_mean:
            self._fail(
                "No se encontró una columna con el promedio correcto de precio.",
                "Incluye: ('price', 'mean') en tu .agg().",
            )
            ok = False

        print("\n🎉 ¡Ejercicio 5 completado!" if ok else "\n⚠️  Revisa los puntos marcados con ❌.")

    # ─────────────────────────────────────────────────────────────────────────
    # Ejercicio 6 — Resample + visualización
    # ─────────────────────────────────────────────────────────────────────────

    def verificar_6(self, ventas_mensuales):
        """
        Valida que ventas_mensuales sea una Serie con ventas totales
        agrupadas por mes, con índice DatetimeIndex.
        """
        self._header(6, "Tendencia Temporal (resample)")
        ok = True

        if not isinstance(ventas_mensuales, pd.Series):
            self._fail(
                f"Se esperaba una Series. Recibiste: {self._describe(ventas_mensuales)}",
                "Guarda el resultado del resample ANTES de llamar a .plot().\n"
                "     Ej: ventas_mensuales = df.resample('ME', on='date')['total'].sum()",
            )
            print("\n⚠️  Revisa los puntos marcados con ❌.")
            return

        # Índice DatetimeIndex
        if not isinstance(ventas_mensuales.index, pd.DatetimeIndex):
            self._fail(
                "El índice de la Serie debe ser un DatetimeIndex.",
                "Verifica que la columna 'date' esté convertida con pd.to_datetime() "
                "y que uses resample() sobre ella.",
            )
            ok = False
        else:
            self._ok("Índice DatetimeIndex correcto.")

        # Calcular expected con ambas frecuencias (pandas <2.2 y >=2.2)
        dft_idx = self._dft.set_index("date")
        try:
            expected = dft_idx["total"].resample("ME").sum()
        except Exception:
            expected = dft_idx["total"].resample("M").sum()

        # Número de períodos
        if len(ventas_mensuales) != len(expected):
            self._fail(
                f"Número de períodos incorrecto. "
                f"Esperados: {len(expected)}, recibidos: {len(ventas_mensuales)}.",
                "Usa resample('ME') o resample('M') para agrupar por mes.",
            )
            ok = False
        else:
            self._ok(f"{len(ventas_mensuales)} meses encontrados.")

        # Suma total (tolerante a diferencias de fin de mes vs inicio de mes)
        if abs(ventas_mensuales.sum() - expected.sum()) / expected.sum() > 0.01:
            self._fail(
                f"La suma total de ventas mensuales no coincide. "
                f"Esperado ≈ {expected.sum():.2f}, recibido: {ventas_mensuales.sum():.2f}.",
                "Asegúrate de sumar la columna 'total' con .sum().",
            )
            ok = False
        else:
            self._ok(f"Suma total de ventas correcta ({ventas_mensuales.sum():.2f}).")

        print("\n🎉 ¡Ejercicio 6 completado!" if ok else "\n⚠️  Revisa los puntos marcados con ❌.")
