document.addEventListener("DOMContentLoaded", function() {
    // Tunggu hingga dokumen selesai dimuat

    const taskManager = document.getElementById("task-manager");

    // Fungsi untuk menjalankan animasi slide in dan fade in
    function runAnimation() {
        taskManager.style.animation = "slideIn 2s forwards";
        taskManager.style.opacity = "1";
    }

    // Panggil fungsi animasi setelah 500ms (0.5 detik)
    setTimeout(runAnimation, 100);
});