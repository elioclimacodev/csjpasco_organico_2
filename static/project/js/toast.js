window.addEventListener('load', () => {
    
    document.body.addEventListener('show_toast', function(evt) {
        const { type, message } = evt.detail;
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const typeMap = {
            success: 'text-bg-success',
            error: 'text-bg-danger',
            warning: 'text-bg-warning',
            info: 'text-bg-info',
        };

        const toastId = 'toast-' + Math.floor(Math.random() * 1000000);
        const bgClass = typeMap[type] || 'text-bg-info';

        const toastHtml = `
        <div 
            id="${toastId}"
            class="toast border-0 ${bgClass}" 
            role="alert" 
            aria-live="assertive" 
            aria-atomic="true" 
            data-bs-autohide="true"
            data-bs-toggle="toast">
            <div class="d-flex align-items-center">
                <div
                    id="toastBody" 
                    class="toast-body flex-grow-1">
                    ${message}
                </div>
                <button type="button" class="ms-2 btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>            
        `;

        container.insertAdjacentHTML('beforeend', toastHtml);
        const toastElem = document.getElementById(toastId);

        // --- LÓGICA DE DETECCIÓN DE BOOTSTRAP EN TABLER ---
        // Intentamos encontrar el constructor de Toast en diferentes objetos
        const ToastConstructor = window.bootstrap?.Toast || window.tabler?.Toast;

        if (ToastConstructor) {
            const toastInstance = new ToastConstructor(toastElem, {
                delay: 3000,
                autohide: true
            });
            toastInstance.show();
            
            toastElem.addEventListener('hidden.bs.toast', () => toastElem.remove());
        } else {
            // FALLBACK MANUAL (Si nada de lo anterior existe)
            // Agregamos la clase de Bootstrap para mostrarlo
            setTimeout(() => {
                toastElem.classList.add('show');
                // Programamos la desaparición manual
                setTimeout(() => {
                    toastElem.classList.remove('show');
                    setTimeout(() => toastElem.remove(), 500);
                }, 3000);
            }, 100);
        }
    });
});

// // document.body.addEventListener('show_toast', function(e) {
// //     const {type, message} = e.detail;

// //     const toastEl = document.getElementById('liveToast');
// //     const toastBody = document.getElementById('toastBody');

// //     // Limpia los estilos previos.
// //     toastEl.classList.remove(
// //         'text-bg-success',
// //         'text-bg-danger',
// //         'text-bg-warning',
// //         'text-bg-info'
// //     );

// //     const typeMap = {
// //         success: 'text-bg-success',
// //         error: 'text-bg-danger',
// //         warning: 'text-bg-warning',
// //         info: 'text-bg-info',
// //     };

// //     toastEl.classList.add(typeMap[type] ?? 'text-bg-info');
// //     toastBody.textContent = message;

// //     const toast = new tabler.Toast(toastEl, {
// //         delay: 4000,
// //         autohide: true,
// //     });

// //     toast.show();
// // });


// document.body.addEventListener('show_toast', function(evt) {
//     // HTMX pone los datos en evt.detail
//     const type = evt.detail.type || 'info';
//     const message = evt.detail.message || '';

//     const toastEl = document.getElementById('liveToast'); // Asegúrate que el ID coincida en tu HTML
//     const toastBody = document.getElementById('toastBody');

//     if (!toastEl || !toastBody) return;

//     // Limpia clases
//     toastEl.classList.remove('text-bg-success', 'text-bg-danger', 'text-bg-warning', 'text-bg-info');

//     const typeMap = {
//         success: 'text-bg-success',
//         error: 'text-bg-danger',
//         warning: 'text-bg-warning',
//         info: 'text-bg-info',
//     };

//     toastEl.classList.add(typeMap[type]);
//     toastBody.textContent = message;

//     // Usar bootstrap.Toast porque Tabler usa Bootstrap internamente
//     // Si 'bootstrap' no está definido, probamos con la instancia global de Tabler
//     try {
//         const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
//         toast.show();
//     } catch (e) {
//         // Fallback si Bootstrap no está global (algunas versiones de Tabler)
//         toastEl.classList.add('show');
//         setTimeout(() => toastEl.classList.remove('show'), 4000);
//     }
// });