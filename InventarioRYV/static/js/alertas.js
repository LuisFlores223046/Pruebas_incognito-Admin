/**
 * alertas.js — Auto-cierre y cierre manual de mensajes Django.
 */
document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    /**
     * Cierra y remueve un mensaje del DOM.
     */
    function cerrarMensaje(mensaje) {
        mensaje.style.opacity = '0';
        mensaje.style.transition = 'opacity 0.3s';
        setTimeout(function () {
            if (mensaje.parentNode) {
                mensaje.parentNode.removeChild(mensaje);
            }
        }, 300);
    }

    // Cierre manual con el botón ×
    var botonesCerrar = document.querySelectorAll('.mensaje-cerrar');
    botonesCerrar.forEach(function (btn) {
        btn.addEventListener('click', function () {
            var mensaje = btn.closest('.mensaje');
            if (mensaje) { cerrarMensaje(mensaje); }
        });
    });

    // Auto-cierre de mensajes de éxito después de 5 segundos
    var mensajesExito = document.querySelectorAll(
        '.mensaje--success, .mensaje--info'
    );
    mensajesExito.forEach(function (mensaje) {
        setTimeout(function () {
            cerrarMensaje(mensaje);
        }, 5000);
    });
});
