document.addEventListener("DOMContentLoaded", function () {
    // Авто‑скрытие alert
    document.querySelectorAll(".alert").forEach(a => setTimeout(() => a.style.display = "none", 5000));

    // Файловые инпуты
    document.querySelectorAll('input[type="file"]').forEach(input => {
        input.addEventListener("change", function () {
            let label = this.nextElementSibling;
            if (!label || label.tagName.toLowerCase() !== 'label') {
                label = this.parentElement ? this.parentElement.querySelector('label') : null;
            }
            if (label) label.textContent = this.files && this.files.length ? this.files[0].name : 'Выберите файл';
        });
    });

    // Универсальная логика модалок по data-modal-target
    document.querySelectorAll('[data-modal-target]').forEach(btn => {
        const selector = btn.getAttribute('data-modal-target');
        const modal = document.querySelector(selector);
        if (!modal) return;
        btn.addEventListener('click', () => modal.style.display = 'block');
    });

    // Закрытие модалок по элементам с классом close внутри .modal
    document.querySelectorAll('.modal .close').forEach(btn => {
        const modal = btn.closest('.modal');
        if (!modal) return;
        btn.addEventListener('click', () => modal.style.display = 'none');
    });

    // Закрытие при клике вне содержимого
    window.addEventListener('click', (e) => {
        document.querySelectorAll('.modal').forEach(modal => {
            if (e.target === modal) modal.style.display = 'none';
        });
    });
});
