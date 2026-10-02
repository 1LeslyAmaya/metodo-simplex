"""
Método Simplex tabular - Prototipo 1.0

Resuelve:
    Maximizar Z = c*x
    Sujeto a A*x <= b
    Con x >= 0 y b >= 0

Solo utiliza la biblioteca estándar de Python.
"""

import math

TOLERANCIA = 1e-9
MAX_ITERACIONES = 1000


def validar_modelo(c, a, b):
    """Comprueba que los datos tengan dimensiones y valores válidos."""
    if not c or not a or len(a) != len(b):
        raise ValueError(
            "Se necesita una función objetivo y al menos una restricción."
        )

    if any(len(fila) != len(c) for fila in a):
        raise ValueError(
            "Cada restricción debe tener un coeficiente por variable."
        )

    datos = c + b + [valor for fila in a for valor in fila]

    if not all(math.isfinite(valor) for valor in datos):
        raise ValueError("Todos los datos deben ser números finitos.")

    if any(valor < 0 for valor in b):
        raise ValueError(
            "Los lados derechos deben ser mayores o iguales a cero."
        )


def crear_tabla(c, a, b):
    """Construye la tabla inicial y agrega las variables de holgura."""
    n = len(c)
    m = len(a)
    tabla = []

    for i in range(m):
        holguras = [
            1.0 if i == j else 0.0
            for j in range(m)
        ]

        fila = (
            [float(valor) for valor in a[i]]
            + holguras
            + [float(b[i])]
        )

        tabla.append(fila)

    # Convención: Z - c1*x1 - c2*x2 - ... = 0.
    fila_z = [-float(valor) for valor in c] + [0.0] * (m + 1)
    tabla.append(fila_z)

    # Al inicio, las variables básicas son las holguras.
    base = list(range(n, n + m))

    nombres = (
        [f"x{i + 1}" for i in range(n)]
        + [f"s{i + 1}" for i in range(m)]
    )

    return tabla, base, nombres


def mostrar_tabla(tabla, base, nombres):
    """Imprime la tabla con cuatro decimales."""
    encabezado = ["Base"] + nombres + ["LD"]
    filas = []

    for i, fila in enumerate(tabla):
        etiqueta = nombres[base[i]] if i < len(base) else "Z"

        valores = [
            f"{valor:.4f}" if abs(valor) > TOLERANCIA else "0.0000"
            for valor in fila
        ]

        filas.append([etiqueta] + valores)

    anchos = [
        max(len(fila[j]) for fila in [encabezado] + filas) + 2
        for j in range(len(encabezado))
    ]

    for fila in [encabezado] + filas:
        print(
            "".join(
                valor.rjust(ancho)
                for valor, ancho in zip(fila, anchos)
            )
        )


def encontrar_columna_pivote(tabla):
    """
    Selecciona la primera columna negativa de la fila Z.
    Corresponde al criterio de entrada de la regla de Bland.
    """
    for j, valor in enumerate(tabla[-1][:-1]):
        if valor < -TOLERANCIA:
            return j

    return None


def encontrar_fila_pivote(tabla, base, columna):
    """
    Aplica la prueba del cociente mínimo.
    Solo considera coeficientes positivos de la columna pivote.

    En empates exactos, sale la variable básica de menor índice.
    """
    candidatos = []

    for i in range(len(base)):
        coeficiente = tabla[i][columna]

        if coeficiente > TOLERANCIA:
            cociente = tabla[i][-1] / coeficiente
            candidatos.append((cociente, base[i], i))

    if not candidatos:
        return None

    return min(candidatos)[2]


def actualizar_tabla(tabla, fila, columna):
    """Aplica Gauss-Jordan para actualizar la tabla."""
    pivote = tabla[fila][columna]

    # Convertir el pivote en 1.
    tabla[fila] = [
        valor / pivote
        for valor in tabla[fila]
    ]

    # Convertir los demás elementos de la columna pivote en 0.
    for i in range(len(tabla)):
        if i != fila:
            factor = tabla[i][columna]

            tabla[i] = [
                valor - factor * referencia
                for valor, referencia in zip(tabla[i], tabla[fila])
            ]

    if not all(
        math.isfinite(valor)
        for renglon in tabla
        for valor in renglon
    ):
        raise ArithmeticError(
            "Se excedió la capacidad numérica. Revise la escala de los datos."
        )


def resolver_simplex(
    c, a, b, mostrar=True, max_iteraciones=MAX_ITERACIONES
):
    """Controla las iteraciones y devuelve el resultado del modelo."""
    validar_modelo(c, a, b)

    tabla, base, nombres = crear_tabla(c, a, b)

    if mostrar:
        print("\nTabla inicial (LD = lado derecho):")
        mostrar_tabla(tabla, base, nombres)

    iteracion = 0

    while True:
        columna = encontrar_columna_pivote(tabla)

        # Si no quedan negativos en Z, se alcanzó el óptimo.
        if columna is None:
            valores = [0.0] * len(nombres)

            for i, variable in enumerate(base):
                valores[variable] = tabla[i][-1]

            resultado = {
                "estado": "optimo",
                "x": valores[:len(c)],
                "z": tabla[-1][-1],
                "holguras": valores[len(c):],
                "iteraciones": iteracion,
                "tabla": tabla,
            }

            if mostrar:
                print("\nSolución óptima encontrada:")

                for i, valor in enumerate(resultado["x"]):
                    print(f"x{i + 1} = {valor:.6g}")

                print(f"Z máximo = {resultado['z']:.6g}")

                for i, valor in enumerate(resultado["holguras"]):
                    print(f"Holgura s{i + 1} = {valor:.6g}")

            return resultado

        fila = encontrar_fila_pivote(tabla, base, columna)

        if fila is None:
            if mostrar:
                print("\nProblema no acotado: Z puede crecer sin límite.")

            return {
                "estado": "no_acotado",
                "iteraciones": iteracion,
                "tabla": tabla,
            }

        if iteracion >= max_iteraciones:
            if mostrar:
                print(
                    "\nLímite de iteraciones alcanzado. "
                    "No se confirma una solución óptima."
                )

            return {
                "estado": "limite_iteraciones",
                "iteraciones": iteracion,
                "tabla": tabla,
            }

        iteracion += 1

        if mostrar:
            print(
                f"\nIteración {iteracion}: "
                f"entra {nombres[columna]}, "
                f"sale {nombres[base[fila]]}."
            )

            cociente = tabla[fila][-1] / tabla[fila][columna]

            print(
                f"Pivote = {tabla[fila][columna]:.6g}; "
                f"cociente = {cociente:.6g}"
            )

        actualizar_tabla(tabla, fila, columna)
        base[fila] = columna

        if mostrar:
            mostrar_tabla(tabla, base, nombres)


def leer_entero(mensaje):
    """Solicita un entero positivo."""
    while True:
        try:
            valor = int(input(mensaje))

            if valor > 0:
                return valor

        except ValueError:
            pass

        print("Ingrese un número entero mayor que cero.")


def leer_numeros(mensaje, cantidad, no_negativos=False):
    """Solicita una cantidad determinada de números."""
    while True:
        try:
            valores = [
                float(valor)
                for valor in input(mensaje).split()
            ]

            if len(valores) != cantidad:
                raise ValueError

            if not all(math.isfinite(valor) for valor in valores):
                raise ValueError

            if no_negativos and any(valor < 0 for valor in valores):
                raise ValueError

            return valores

        except ValueError:
            extra = (
                ", mayores o iguales a cero"
                if no_negativos
                else ""
            )

            print(
                f"Ingrese {cantidad} número(s) finito(s){extra}, "
                "separados por espacios. Use punto decimal."
            )


def ingresar_modelo():
    """Lee los coeficientes de la función objetivo y restricciones."""
    n = leer_entero("Cantidad de variables: ")
    m = leer_entero("Cantidad de restricciones: ")

    c = leer_numeros(
        "Coeficientes de Z, separados por espacios: ", n
    )

    a = []
    b = []

    for i in range(m):
        print(f"Restricción {i + 1} (tipo <=):")

        a.append(leer_numeros("Coeficientes: ", n))

        lado_derecho = leer_numeros(
            "Lado derecho: ", 1, no_negativos=True
        )[0]

        b.append(lado_derecho)

    return c, a, b


def main():
    print("MÉTODO SIMPLEX - PROTOTIPO 1.0")
    print(
        "Maximización, restricciones <=, "
        "variables y lados derechos >= 0."
    )

    while True:
        print("\n1. Ingresar modelo")
        print("2. Ejemplo 1")
        print("3. Ejemplo 2")
        print("0. Salir")

        opcion = input("Opción: ").strip()

        try:
            if opcion == "0":
                break

            if opcion == "1":
                modelo = ingresar_modelo()

            elif opcion == "2":
                print("\nMax Z = 3x1 + 5x2")
                print("x1 <= 4")
                print("2x2 <= 12")
                print("3x1 + 2x2 <= 18")

                modelo = (
                    [3, 5],
                    [[1, 0], [0, 2], [3, 2]],
                    [4, 12, 18],
                )

            elif opcion == "3":
                print("\nMax Z = 4x1 + 3x2")
                print("2x1 + x2 <= 8")
                print("x1 + 2x2 <= 8")

                modelo = (
                    [4, 3],
                    [[2, 1], [1, 2]],
                    [8, 8],
                )

            else:
                print("Opción no válida.")
                continue

            resolver_simplex(*modelo)

        except (ValueError, ArithmeticError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma finalizado.")