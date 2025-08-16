document.addEventListener('DOMContentLoaded', function () {
    // --- ИНИЦИАЛИЗАЦИЯ МОДАЛЬНЫХ ОКОН ---
    const mainModalEl = document.getElementById('modal-container');
    const deleteModalEl = document.getElementById('delete-confirm-modal');
    
    if (!mainModalEl || !deleteModalEl) return;
    
    const mainModal = new bootstrap.Modal(mainModalEl);
    const deleteModal = new bootstrap.Modal(deleteModalEl);

    mainModalEl.addEventListener('hidden.bs.modal', function () {
        mainModalEl.querySelector('.modal-content').innerHTML = '';
    });

    // --- ФУНКЦИЯ ДЛЯ ИНИЦИАЛИЗАЦИИ SELECT2 ---
    // Мы выносим это в отдельную функцию, чтобы вызывать ее в разных местах
    function initializeSelect2(context) {
        // Находим все селекты внутри указанного контекста (например, модального окна)
        const selects = $(context).find('select');
        if (selects.length === 0) return;

        selects.each(function() {
            const select = $(this);
            // Если у селекта много опций, включаем поиск. Иначе - отключаем.
            const hasSearch = select.find('option').length > 7;

            select.select2({
                theme: 'bootstrap-5',
                // Важно: привязываем выпадающий список к родительскому элементу модального окна
                dropdownParent: $(mainModalEl),
                placeholder: select.find('option[disabled]').text() || '-- Выберите --',
                minimumResultsForSearch: hasSearch ? 0 : Infinity
            });
        });
    }

    // --- ОТКРЫТИЕ ГЛАВНОГО МОДАЛЬНОГО ОКНА ---
    document.body.addEventListener('click', function (event) {
        const modalTrigger = event.target.closest('[data-bs-toggle="modal"][data-bs-target="#modal-container"]');
        if (!modalTrigger) return;

        event.preventDefault();
        const url = modalTrigger.getAttribute('href');
        if (!url) return;
        
        const modalContent = mainModalEl.querySelector('.modal-content');
        modalContent.innerHTML = '<div class="text-center p-4"><div class="spinner-border" role="status"><span class="visually-hidden">Загрузка...</span></div></div>';
        
        fetch(url, { 
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.ok ? response.text() : Promise.reject(`HTTP error! status: ${response.status}`))
        .then(html => {
            modalContent.innerHTML = html;
            // === КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Вызываем нашу функцию после вставки HTML ===
            initializeSelect2(modalContent);
            mainModal.show();
        })
        .catch(error => {
            modalContent.innerHTML = `<div class="modal-header"><h5 class="modal-title">Ошибка</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body"><div class="alert alert-danger">Произошла ошибка при загрузке: ${error.message}</div></div>`;
            mainModal.show();
        });
    });

    // --- ОТПРАВКА ФОРМ В ГЛАВНОМ МОДАЛЬНОМ ОКНЕ ---
    mainModalEl.addEventListener('submit', function (event) {
        const form = event.target.closest('form');
        if (!form) return;
        event.preventDefault();

        if (!form.checkValidity()) {
            event.stopPropagation();
            form.classList.add('was-validated');
            return;
        }

        const submitButton = form.querySelector('[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Сохранение...';
        }
        
        // Перед отправкой "убиваем" все экземпляры Select2, чтобы форма отправилась корректно
        $(form).find('select').select2('destroy');

        fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => {
            if (response.status === 204) {
                window.location.reload();
                return;
            }
            return response.text().then(html => {
                mainModalEl.querySelector('.modal-content').innerHTML = html;
                // === КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: И здесь тоже вызываем нашу функцию, если сервер вернул форму с ошибкой ===
                initializeSelect2(mainModalEl.querySelector('.modal-content'));
            });
        })
        .catch(error => {
            console.error('Ошибка:', error);
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = 'Сохранить изменения';
            }
            alert('Произошла ошибка: ' + error.message);
        });
    });

    // --- ЛОГИКА ДЛЯ ОКНА ПОДТВЕРЖДЕНИЯ УДАЛЕНИЯ (остается без изменений) ---
    // ... (ваш код для deleteModalEl) ...

    let triggerButtonFromMainModal = null;

    deleteModalEl.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        deleteModalEl.querySelector('.modal-body p:first-of-type').innerHTML = `Вы уверены, что хотите удалить: <strong>${button.dataset.itemName}</strong>?`;
        deleteModalEl.querySelector('#delete-form').action = button.dataset.deleteUrl;
        
        if (mainModalEl.contains(button)) {
            triggerButtonFromMainModal = button;
            mainModal.hide();
        }
    });
    
    deleteModalEl.addEventListener('hidden.bs.modal', function() {
        if (triggerButtonFromMainModal) {
            mainModal.show();
            triggerButtonFromMainModal = null;
        }
    });

    deleteModalEl.querySelector('#delete-form').addEventListener('submit', function(event) {
        event.preventDefault();
        
        fetch(this.action, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => {
            deleteModal.hide();
            
            if (triggerButtonFromMainModal) { // Если удаление было из главного окна
                return response.text().then(html => {
                     mainModalEl.querySelector('.modal-content').innerHTML = html;
                });
            } else { // Если удаление было с основной страницы
                deleteModalEl.addEventListener('hidden.bs.modal', () => window.location.reload(), { once: true });
            }
        });
    });
});