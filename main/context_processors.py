from main.roles import can_change_content, is_editor


def site(request):
    """Data pemilik portofolio yang dipakai base.html di setiap halaman, termasuk halaman
    403, ditambah peran pengguna yang sedang membuka halaman supaya template bisa
    menyembunyikan tombol yang tidak boleh dipakai."""
    return {
        "name": "Ira Arianti Alawiah",
        "brand_name": "Ira Arianti",
        "is_editor": is_editor(request.user),
        "can_change_content": can_change_content(request.user),
    }