// Fungsi kecil yang dipakai bersama oleh skrip halaman (Projects, Experience).
// Dimuat di <head> base.html supaya sudah tersedia sebelum skrip halaman berjalan.

// Django tidak meng-escape data yang kartunya dirakit di browser.
// Tanpa fungsi ini, teks berisi tag HTML akan dijalankan sebagai kode (XSS).
function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

// Token CSRF dibaca dari cookie lalu dikirim lewat header X-CSRFToken.
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        for (const rawCookie of document.cookie.split(";")) {
            const cookie = rawCookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}