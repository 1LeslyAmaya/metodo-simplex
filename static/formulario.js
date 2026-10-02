const formulario = document.getElementById("formulario-simplex");
const objetivoOculto = document.getElementById("objetivo");
const restriccionesOcultas = document.getElementById("restricciones");

const contenedorVariables = document.getElementById("variables");

const contenedorRestricciones =
    document.getElementById("lista-restricciones");

const aviso = document.getElementById("aviso");


// Recupera los datos después de resolver.
// Si no existen, comienza con dos variables vacías.
let coeficientes = objetivoOculto.value.trim()
    ? objetivoOculto.value.trim().split(/\s+/)
    : ["", ""];

let filas = [];
let limites = [];

restriccionesOcultas.value.split("\n").forEach(function (linea) {
    if (!linea.trim()) {
        return;
    }

    const partes = linea.replace("≤", "<=").split("<=");

    if (partes.length === 2) {
        const valores = partes[0].trim()
            ? partes[0].trim().split(/\s+/)
            : [];

        filas.push(
            coeficientes.map(function (_, columna) {
                return valores[columna] ?? "";
            })
        );

        limites.push(partes[1].trim());
    }
});

// Al abrir por primera vez, muestra una restricción vacía.
if (filas.length === 0) {
    filas = [coeficientes.map(() => "")];
    limites = [""];
}


function ocultarResultado() {
    const resultado = document.getElementById("resultados");
    const error = document.querySelector(".error");

    if (resultado) {
        resultado.hidden = true;
    }

    if (error) {
        error.hidden = true;
    }

    aviso.textContent = "";
}


function esNumeroValido(texto) {
    const patron =
        /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/;

    return patron.test(texto.trim())
        && Number.isFinite(Number(texto));
}


function validarNumero(input, noNegativo = false) {
    const texto = input.value.trim();
    let mensaje = "";

    if (texto === "") {
        mensaje = "Completa esta casilla.";

    } else if (!esNumeroValido(texto)) {
        mensaje = "Escribe un número válido. Usa punto decimal.";

    } else if (noNegativo && Number(texto) < 0) {
        mensaje = "El lado derecho debe ser mayor o igual a cero.";
    }

    input.setCustomValidity(mensaje);
}


function crearCampo(
    id,
    etiqueta,
    valor,
    cambiar,
    noNegativo = false
) {
    const grupo = document.createElement("div");
    grupo.className = "campo";

    const label = document.createElement("label");
    label.htmlFor = id;
    label.textContent = etiqueta;

    const input = document.createElement("input");
    input.type = "text";
    input.id = id;
    input.value = valor;
    input.required = true;
    input.placeholder = "Escribe un número";

    validarNumero(input, noNegativo);

    input.addEventListener("input", function () {
        validarNumero(input, noNegativo);
        cambiar(input.value);
        ocultarResultado();
        actualizarVista();
    });

    grupo.append(label, input);

    return grupo;
}


function actualizarVista() {
    let expresion = "";

    coeficientes.forEach(function (texto, indice) {
        const valido = esNumeroValido(texto);
        const numero = valido ? Number(texto) : null;
        const negativo = valido && numero < 0;

        const valor = valido ? Math.abs(numero) : "?";
        const termino = valor + "x" + (indice + 1);

        if (indice === 0) {
            expresion = (negativo ? "−" : "") + termino;
        } else {
            expresion += (negativo ? " − " : " + ") + termino;
        }
    });

    document.getElementById("vista-funcion").textContent =
        "Maximizar Z = " + expresion;
}


function dibujarFormulario() {
    contenedorVariables.replaceChildren();
    contenedorRestricciones.replaceChildren();

    // Función objetivo: una casilla por variable.
    coeficientes.forEach(function (valor, columna) {
        const campo = crearCampo(
            "objetivo-" + columna,
            "Número que multiplica a x" + (columna + 1),
            valor,
            function (nuevoValor) {
                coeficientes[columna] = nuevoValor;
            }
        );

        contenedorVariables.appendChild(campo);
    });

    // Restricciones: todos sus campos se muestran verticalmente.
    filas.forEach(function (fila, numeroFila) {
        const bloque = document.createElement("fieldset");
        bloque.className = "restriccion";

        const titulo = document.createElement("legend");
        titulo.textContent = "Restricción " + (numeroFila + 1);

        bloque.appendChild(titulo);

        coeficientes.forEach(function (_, columna) {
            const campo = crearCampo(
                "restriccion-" + numeroFila + "-" + columna,
                "Número que multiplica a x" + (columna + 1),
                fila[columna] ?? "",
                function (nuevoValor) {
                    filas[numeroFila][columna] = nuevoValor;
                }
            );

            bloque.appendChild(campo);
        });

        const relacion = document.createElement("p");
        relacion.className = "relacion";
        relacion.textContent = "Relación: menor o igual que (≤)";

        bloque.appendChild(relacion);

        const campoLimite = crearCampo(
            "limite-" + numeroFila,
            "Lado derecho",
            limites[numeroFila],
            function (nuevoValor) {
                limites[numeroFila] = nuevoValor;
            },
            true
        );

        bloque.appendChild(campoLimite);

        const quitar = document.createElement("button");
        quitar.type = "button";
        quitar.textContent = "Quitar esta restricción";
        quitar.disabled = filas.length <= 1;

        quitar.addEventListener("click", function () {
            filas.splice(numeroFila, 1);
            limites.splice(numeroFila, 1);

            ocultarResultado();
            dibujarFormulario();
        });

        bloque.appendChild(quitar);
        contenedorRestricciones.appendChild(bloque);
    });

    document.getElementById("quitar-variable").disabled =
        coeficientes.length <= 1;

    actualizarVista();
}


document.getElementById("agregar-variable").addEventListener(
    "click",
    function () {
        coeficientes.push("");

        filas.forEach(function (fila) {
            fila.push("");
        });

        ocultarResultado();
        dibujarFormulario();

        aviso.textContent =
            "Completa la nueva variable en la función objetivo " +
            "y en cada restricción.";

        document.getElementById(
            "objetivo-" + (coeficientes.length - 1)
        ).focus();
    }
);


document.getElementById("quitar-variable").addEventListener(
    "click",
    function () {
        if (coeficientes.length <= 1) {
            return;
        }

        coeficientes.pop();

        filas.forEach(function (fila) {
            fila.pop();
        });

        ocultarResultado();
        dibujarFormulario();
    }
);


document.getElementById("agregar-restriccion").addEventListener(
    "click",
    function () {
        filas.push(coeficientes.map(() => ""));
        limites.push("");

        ocultarResultado();
        dibujarFormulario();

        document.getElementById(
            "restriccion-" + (filas.length - 1) + "-0"
        ).focus();
    }
);


document.getElementById("limpiar-formulario").addEventListener(
    "click",
    function () {
        coeficientes = ["", ""];
        filas = [["", ""]];
        limites = [""];

        objetivoOculto.value = "";
        restriccionesOcultas.value = "";

        ocultarResultado();
        dibujarFormulario();

        document.getElementById("objetivo-0").focus();
    }
);


formulario.addEventListener("submit", function (evento) {
    if (!formulario.reportValidity()) {
        evento.preventDefault();
        return;
    }

    // Convierte las casillas al formato que recibe Python.
    objetivoOculto.value = coeficientes
        .map(valor => valor.trim())
        .join(" ");

    restriccionesOcultas.value = filas
        .map(function (fila, indice) {
            return fila.map(valor => valor.trim()).join(" ")
                + " <= "
                + limites[indice].trim();
        })
        .join("\n");
});


// Crear las casillas al abrir la página.
dibujarFormulario();