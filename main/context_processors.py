def site(request):
    """Data pemilik portofolio yang dipakai base.html di setiap halaman, termasuk halaman
    403, jadi tidak perlu dikirim ulang dari tiap view."""
    return {
        "name": "Ira Arianti Alawiah",
        "brand_name": "Ira Arianti",
    }
