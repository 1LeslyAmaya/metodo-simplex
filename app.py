from contextlib import redirect_stdout
from io import StringIO

from flask import Flask, render_template, request
from index import resolver_simplex

app = Flask(__name__)


def convertir_datos(objetivo, restricciones):
    """Convierte los datos del formulario en listas numéricas."""
    try:
        c = [float(numero) for numero in objetivo.split()]
    except ValueError:
        raise ValueError(
            "Los valores de la función objetivo deben ser números."
        )

    if not c:
        raise ValueError("Ingrese los valores de la función objetivo.")

    a = []
    b = []

    for numero, linea in enumerate(restricciones.splitlines(), start=1):
        linea = linea.strip()

        if not linea:
            continue

        partes = linea.replace("≤", "<=").split("<=")

        if len(partes) != 2:
            raise ValueError(
                f"Restricción {numero}: formato incorrecto."
            )

        try:
            coeficientes = [
                float(valor)
                for valor in partes[0].split()
            ]

            lado_derecho = float(partes[1].strip())

        except ValueError:
            raise ValueError(
                f"Restricción {numero}: revise los números ingresados."
            )

        if len(coeficientes) != len(c):
            raise ValueError(
                f"Restricción {numero}: debe tener "
                f"{len(c)} valores, uno por variable."
            )

        a.append(coeficientes)
        b.append(lado_derecho)

    if not a:
        raise ValueError("Ingrese al menos una restricción.")

    return c, a, b


@app.route("/", methods=["GET", "POST"])
def inicio():
    # Al abrir la página, el formulario comienza vacío.
    objetivo = ""
    restricciones = ""

    resultado = None
    procedimiento = ""
    error = None

    if request.method == "POST":
        objetivo = request.form.get("objetivo", "")
        restricciones = request.form.get("restricciones", "")

        try:
            c, a, b = convertir_datos(objetivo, restricciones)

            # Captura las tablas para mostrarlas en la página.
            salida = StringIO()

            with redirect_stdout(salida):
                resultado = resolver_simplex(
                    c,
                    a,
                    b,
                    mostrar=True
                )

            procedimiento = salida.getvalue()

        except (ValueError, ArithmeticError) as problema:
            error = str(problema)

    return render_template(
        "inicio.html",
        objetivo=objetivo,
        restricciones=restricciones,
        resultado=resultado,
        procedimiento=procedimiento,
        error=error,
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=False,
    )