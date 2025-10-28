document.addEventListener("DOMContentLoaded", function () {
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.display = "none";
        }, 5000);
    });

    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener("change", function () {
            const label = this.nextElementSibling;
            if (this.files.length > 0) {
                label.textContent = this.files[0].name;
            }
        });
    });

    const modal = document.getElementById("authModal");
    const openBtn = document.getElementById("openModal");
    const closeBtn = document.querySelector(".close");

    openBtn.onclick = () => {
        modal.style.display = "block";
    };

    closeBtn.onclick = () => {
        modal.style.display = "none";
    };

    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };

});
