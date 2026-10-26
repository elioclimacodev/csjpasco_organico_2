document.addEventListener('DOMContentLoaded', () => {
    const modalElem = document.getElementById('modal_htmx');

    // 1. CERRAR MODAL (Cuando Django envía 'object_created')
    ['object_created', 'object_updated'].forEach(event => {
        document.body.addEventListener(event, () => {
            const closeButton = modalElem.querySelector('[data-bs-dismiss="modal"]');
            if (closeButton) closeButton.click();
        });
    });

    // 2. FOCO AUTOMÁTICO (Para "Guardar y Añadir Otro")
    document.body.addEventListener('update_object_list', () => {
        // SOLUCIÓN AL ERROR: Forzamos que el modal no esté oculto para A11Y antes de dar foco
        modalElem.setAttribute('aria-hidden', 'false');
        
        setTimeout(() => {
            const firstInput = modalElem.querySelector('input:not([type=hidden]):not([disabled]), select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        }, 150); 
    });

    // 3. LIMPIEZA DE FOCO AL CERRAR
    // Este evento es disparado por Tabler/Bootstrap automáticamente
    modalElem.addEventListener('hide.bs.modal', () => {
        // Antes de que se oculte, quitamos el foco del elemento activo
        if (document.activeElement) {
            document.activeElement.blur();
        }
    });

    modalElem.addEventListener('hidden.bs.modal', () => {
        document.getElementById('modal_content').innerHTML = '';
    });
});