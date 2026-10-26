"""
Calificador automático de la Tarea 1 — Fundamentos de Python.

Contrato (para el workflow de GitHub Actions):
    python -m nbchecker.fundamentos.calificar --notebook ENTREGA.ipynb [--config CONFIG.json]

  - Lee el notebook del alumno (.ipynb ya descargado).
  - Ejecuta sus celdas de código en un proceso aparte, con límite de tiempo
    por celda (protege contra while infinitos) y sin las celdas del checker.
  - Corre las mismas pruebas que ve el alumno (nbchecker.fundamentos.pruebas).
  - Imprime UN solo objeto JSON en stdout:
        {"grade": 80.0, "feedback": "...", "aprobados": 8, "total": 10,
         "detalle": {"1": true, ...}}

CONFIG.json (opcional, todos los campos opcionales):
    {"max_grade": 100, "timeout_celda": 10, "timeout_total": 180}
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

_RAIZ_PAQUETE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_CONFIG_DEFECTO = {"max_grade": 100, "timeout_celda": 10, "timeout_total": 180}

# Celdas que pertenecen al checker (instalación, inicialización y verificación):
# no se ejecutan durante la calificación.
_PATRON_CELDA_CHECKER = re.compile(r"\bchecker\b|nbchecker|CheckerFundamentos")


# ─────────────────────────────────────────────────────────────────────────────
# Lectura del notebook
# ─────────────────────────────────────────────────────────────────────────────

def _celdas_de_codigo(ruta_notebook):
    with open(ruta_notebook, encoding="utf-8") as f:
        nb = json.load(f)
    celdas = []
    for celda in nb.get("cells", []):
        if celda.get("cell_type") != "code":
            continue
        fuente = celda.get("source", "")
        if isinstance(fuente, list):
            fuente = "".join(fuente)
        if _PATRON_CELDA_CHECKER.search(fuente):
            continue
        # quitar comandos de shell (!pip ...) y magics (%time ...) de Colab
        lineas = [
            l for l in fuente.splitlines()
            if not l.lstrip().startswith(("!", "%"))
        ]
        codigo = "\n".join(lineas).strip()
        if codigo:
            celdas.append(codigo)
    return celdas


# ─────────────────────────────────────────────────────────────────────────────
# Proceso hijo: ejecuta el código del alumno y corre las pruebas
# ─────────────────────────────────────────────────────────────────────────────

def _hijo(ruta_notebook, ruta_salida, timeout_celda):
    import builtins
    import signal

    from nbchecker.fundamentos import pruebas

    def _sin_input(*_a, **_k):
        raise RuntimeError("input() no está permitido en la tarea")

    builtins.input = _sin_input

    class _Tiempo(Exception):
        pass

    def _alarma(signum, frame):
        raise _Tiempo()

    espacio = {"__name__": "__main__"}
    errores = 0
    for codigo in _celdas_de_codigo(ruta_notebook):
        signal.signal(signal.SIGALRM, _alarma)
        signal.alarm(int(timeout_celda))
        try:
            exec(compile(codigo, "<celda>", "exec"), espacio)
        except BaseException:
            errores += 1
        finally:
            signal.alarm(0)

    detalle = {}
    for n, (_, nombres, prueba) in pruebas.EJERCICIOS.items():
        if not all(nombre in espacio for nombre in nombres):
            detalle[n] = False
            continue
        detalle[n] = prueba(*(espacio[nombre] for nombre in nombres))

    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump({"detalle": detalle, "errores_celdas": errores}, f)


# ─────────────────────────────────────────────────────────────────────────────
# Proceso principal
# ─────────────────────────────────────────────────────────────────────────────

def calificar(ruta_notebook, config=None):
    from nbchecker.fundamentos import pruebas

    cfg = dict(_CONFIG_DEFECTO)
    cfg.update(config or {})
    total = len(pruebas.EJERCICIOS)

    def _resultado(detalle, nota_extra=None):
        aprobados = sum(1 for v in detalle.values() if v)
        lineas = []
        for n, (titulo, _, _) in pruebas.EJERCICIOS.items():
            marca = "✅ pasó" if detalle.get(n) else "❌ no pasó"
            lineas.append(f"Ejercicio {n} ({titulo}): {marca}")
        lineas.append(f"Ejercicios aprobados: {aprobados}/{total}")
        if nota_extra:
            lineas.append(nota_extra)
        return {
            "grade": round(cfg["max_grade"] * aprobados / total, 2),
            "feedback": "\n".join(lineas),
            "aprobados": aprobados,
            "total": total,
            "detalle": {str(k): bool(v) for k, v in detalle.items()},
        }

    vacio = {n: False for n in pruebas.EJERCICIOS}

    try:
        _celdas_de_codigo(ruta_notebook)
    except Exception:
        return _resultado(vacio, "No se pudo leer el notebook entregado.")

    with tempfile.TemporaryDirectory() as tmp:
        salida = os.path.join(tmp, "resultado.json")
        lanzador = (
            "import sys; sys.path.insert(0, sys.argv[1]); "
            "from nbchecker.fundamentos.calificar import _hijo; "
            "_hijo(sys.argv[2], sys.argv[3], sys.argv[4])"
        )
        try:
            subprocess.run(
                [sys.executable, "-c", lanzador, _RAIZ_PAQUETE,
                 os.path.abspath(ruta_notebook), salida, str(cfg["timeout_celda"])],
                cwd=tmp,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=cfg["timeout_total"],
            )
        except subprocess.TimeoutExpired:
            return _resultado(vacio, "La ejecución del notebook excedió el tiempo límite.")

        if not os.path.exists(salida):
            return _resultado(vacio, "El notebook no pudo ejecutarse.")
        with open(salida, encoding="utf-8") as f:
            datos = json.load(f)

    detalle = {int(k): v for k, v in datos["detalle"].items()}
    return _resultado(detalle)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Califica la Tarea 1 — Fundamentos de Python")
    parser.add_argument("--notebook", required=True, help="Ruta al .ipynb entregado")
    parser.add_argument("--config", help="Ruta a un JSON de configuración (opcional)")
    args = parser.parse_args(argv)

    config = {}
    if args.config:
        with open(args.config, encoding="utf-8") as f:
            config = json.load(f)

    print(json.dumps(calificar(args.notebook, config), ensure_ascii=False))


if __name__ == "__main__":
    main()
