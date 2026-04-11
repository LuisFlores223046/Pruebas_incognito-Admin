/**
 * confirmar.js — Confirmación de acciones destructivas
 * usando el modal nativo o un confirm() de respaldo.
 *
 * Uso: agrega data-confirmar="¿Mensaje?" a cualquier
 * botón submit o enlace para requerir confirmación.
 */
document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    var modal = document.getElementById('modal-confirmar');
    var modalMensaje = document.getElementById('modal-mensaje');
    var btnAceptar = document.getElementById('modal-aceptar');
    var btnCancelar = document.getElementById('modal-cancelar');
    var pendingButton = null;

    /**
     * Muestra el modal de confirmación si está disponible,
     * de lo contrario usa confirm() nativo.
     */
    function confirmar(elemento, mensaje) {
        if (modal) {
            pendingButton = elemento;
            modalMensaje.textContent = mensaje;
            modal.removeAttribute('hidden');
        } else {
            if (window.confirm(mensaje)) {
                ejecutar(elemento);
            }
        }
    }

    /**
     * Ejecuta la acción del elemento (submit del form padre
     * o navegación si es un enlace).
     */
    function ejecutar(elemento) {
        if (elemento.tagName === 'A') {
            window.location.href = elemento.href;
        } else if (elemento.tagName === 'BUTTON') {
            var form = elemento.closest('form');
            if (form) {
                elemento.removeAttribute('data-confirmar');
                form.submit();
            }
        }
    }

    // Interceptar botones y enlaces con data-confirmar
    document.addEventListener('click', function (e) {
        var target = e.target.closest('[data-confirmar]');
        if (!target) { return; }
        e.preventDefault();
        var mensaje = target.getAttribute('data-confirmar');
        confirmar(target, mensaje);
    });

    // Botones del modal
    if (btnAceptar) {
        btnAceptar.addEventListener('click', function () {
            modal.setAttribute('hidden', '');
            if (pendingButton) {
                ejecutar(pendingButton);
                pendingButton = null;
            }
        });
    }

    if (btnCancelar) {
        btnCancelar.addEventListener('click', function () {
            modal.setAttribute('hidden', '');
            pendingButton = null;
        });
    }

    // Cerrar al hacer clic fuera del modal
    if (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                modal.setAttribute('hidden', '');
                pendingButton = null;
            }
        });
    }
});
