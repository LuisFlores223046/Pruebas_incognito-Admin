/**
 * filtros.js — Auto-submit de formularios de filtro
 * al cambiar un select.
 */
document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    var formFiltros = document.getElementById('form-filtros');
    if (!formFiltros) { return; }

    var selects = formFiltros.querySelectorAll('select');
    selects.forEach(function (select) {
        select.addEventListener('change', function () {
            formFiltros.submit();
        });
    });
});
