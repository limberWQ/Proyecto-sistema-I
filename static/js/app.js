// === Selección de viaje y asientos en el formulario de venta ===
document.addEventListener("DOMContentLoaded", function () {
    const selectViaje = document.getElementById("id_viaje");
    const seatMap = document.getElementById("seat-map");
    const precioInfo = document.getElementById("precio-info");
    const totalInfo = document.getElementById("total-info");
    const montoPagado = document.getElementById("monto_pagado");
    const cambioInfo = document.getElementById("cambio-info");

    if (!selectViaje || !seatMap) return;

    let precioUnitario = 0;
    let asientosSeleccionados = new Set();

    function actualizarTotales() {
        const total = precioUnitario * asientosSeleccionados.size;
        totalInfo.textContent = "Bs " + total.toFixed(2);
        totalInfo.dataset.total = total.toFixed(2);
        calcularCambio();
    }

    function calcularCambio() {
        const total = parseFloat(totalInfo.dataset.total || "0");
        const pagado = parseFloat(montoPagado.value || "0");
        const cambio = pagado - total;
        if (isNaN(pagado)) {
            cambioInfo.textContent = "Bs 0.00";
            cambioInfo.className = "";
            return;
        }
        cambioInfo.textContent = "Bs " + cambio.toFixed(2);
        cambioInfo.className = cambio < 0 ? "text-danger" : "text-success";
    }

    function cargarAsientos(idViaje) {
        seatMap.innerHTML = '<p class="text-muted">Cargando asientos...</p>';
        asientosSeleccionados.clear();
        actualizarTotales();

        fetch("/ventas/asientos/" + idViaje)
            .then((resp) => resp.json())
            .then((data) => {
                precioUnitario = data.precio;
                precioInfo.textContent = "Bs " + precioUnitario.toFixed(2);

                seatMap.innerHTML = "";
                data.asientos.forEach((asiento) => {
                    const div = document.createElement("div");
                    div.classList.add("seat");
                    div.textContent = asiento.numero;
                    div.dataset.id = asiento.id_viaje_asiento;

                    if (asiento.ocupado) {
                        div.classList.add("ocupado");
                        div.title = "Asiento ocupado";
                    } else {
                        div.classList.add("disponible");
                        div.addEventListener("click", function () {
                            toggleAsiento(div, asiento.id_viaje_asiento);
                        });
                    }
                    seatMap.appendChild(div);
                });

                actualizarTotales();
            })
            .catch(() => {
                seatMap.innerHTML = '<p class="text-muted">No se pudieron cargar los asientos.</p>';
            });
    }

    function toggleAsiento(div, idViajeAsiento) {
        if (div.classList.contains("seleccionado")) {
            div.classList.remove("seleccionado");
            asientosSeleccionados.delete(idViajeAsiento);

            // Eliminar input hidden
            const input = document.querySelector('input[name="asientos"][value="' + idViajeAsiento + '"]');
            if (input) input.remove();
        } else {
            div.classList.add("seleccionado");
            asientosSeleccionados.add(idViajeAsiento);

            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "asientos";
            input.value = idViajeAsiento;
            document.getElementById("form-venta").appendChild(input);
        }
        actualizarTotales();
    }

    selectViaje.addEventListener("change", function () {
        if (this.value) {
            cargarAsientos(this.value);
        } else {
            seatMap.innerHTML = '<p class="text-muted">Selecciona un viaje para ver los asientos.</p>';
            precioInfo.textContent = "Bs 0.00";
            asientosSeleccionados.clear();
            actualizarTotales();
        }
    });

    if (montoPagado) {
        montoPagado.addEventListener("input", calcularCambio);
    }

    // Si ya hay un viaje seleccionado al cargar (por ejemplo, tras un error de validación)
    if (selectViaje.value) {
        cargarAsientos(selectViaje.value);
    }
});

// === Confirmaciones para acciones destructivas ===
function confirmarAccion(mensaje) {
    return confirm(mensaje || "¿Estás seguro de realizar esta acción?");
}

// === Disponibilidad de bus y chofer al crear/editar un viaje ===
// Un bus/chofer solo puede tener un viaje por día (ver viaje_service.py).
// Esto deshabilita en el formulario las opciones ya ocupadas en la fecha
// elegida, para que el usuario no pueda ni seleccionarlas; la validación
// real (por si el usuario manipula el HTML) sigue viviendo en el servidor.
document.addEventListener("DOMContentLoaded", function () {
    const fechaInput = document.getElementById("fecha_viaje");
    const selectBus = document.getElementById("id_bus");
    const selectChofer = document.getElementById("id_chofer");

    if (!fechaInput || !selectBus || !selectChofer) return;

    const excluirIdViaje = fechaInput.dataset.excluirIdViaje || "";

    function guardarTextoOriginal(select) {
        Array.from(select.options).forEach(function (opt) {
            if (opt.value && !opt.dataset.textoOriginal) {
                opt.dataset.textoOriginal = opt.textContent;
            }
        });
    }
    guardarTextoOriginal(selectBus);
    guardarTextoOriginal(selectChofer);

    function aplicarOcupados(select, idsOcupados) {
        let seleccionInvalidada = false;
        Array.from(select.options).forEach(function (opt) {
            if (!opt.value) return;
            const ocupado = idsOcupados.indexOf(parseInt(opt.value, 10)) !== -1;
            opt.disabled = ocupado;
            opt.textContent = ocupado
                ? opt.dataset.textoOriginal + " — ocupado esta fecha"
                : opt.dataset.textoOriginal;
            if (ocupado && opt.selected) {
                seleccionInvalidada = true;
            }
        });
        if (seleccionInvalidada) {
            select.value = "";
        }
    }

    function actualizarDisponibilidad() {
        const fecha = fechaInput.value;
        if (!fecha) return;

        let url = "/viajes/disponibilidad?fecha=" + encodeURIComponent(fecha);
        if (excluirIdViaje) {
            url += "&excluir_id_viaje=" + encodeURIComponent(excluirIdViaje);
        }

        fetch(url)
            .then(function (resp) { return resp.json(); })
            .then(function (data) {
                aplicarOcupados(selectBus, data.buses_ocupados || []);
                aplicarOcupados(selectChofer, data.choferes_ocupados || []);
            })
            .catch(function () {
                // Si falla la consulta no bloqueamos el formulario: el
                // servidor igual valida al guardar.
            });
    }

    fechaInput.addEventListener("change", actualizarDisponibilidad);

    // Si el formulario ya trae una fecha precargada (edición), consultar de una vez
    if (fechaInput.value) {
        actualizarDisponibilidad();
    }
});
