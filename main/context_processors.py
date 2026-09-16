from main.owner import is_owner, owner_lock_enabled


def site(request):
    """Data yang dibutuhkan base.html di setiap halaman, termasuk halaman 403, jadi tidak
    perlu dikirim ulang dari tiap view."""
    return {
        "name": "Ira Arianti Alawiah",
        "brand_name": "Ira Arianti",
        "is_owner": is_owner(request),
        "owner_lock_enabled": owner_lock_enabled(),
    }
