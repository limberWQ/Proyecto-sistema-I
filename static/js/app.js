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
