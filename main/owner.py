"""Mode pemilik: hanya pemilik portofolio yang boleh menambah, mengubah, dan menghapus data.

Kuncinya adalah OWNER_SECRET dari environment variable. Setelah pemilik memasukkan kata
sandi yang benar di /owner/, sesi browsernya ditandai sebagai pemilik.

Kalau OWNER_SECRET tidak diatur (misalnya proyek dijalankan asisten dosen di laptopnya),
kunci dinonaktifkan dan semua orang dianggap pemilik, supaya seluruh fitur form tetap bisa
diuji tanpa perlu mengetahui kata sandi.
"""

import hmac
from functools import wraps

from django.conf import settings
from django.core.exceptions import PermissionDenied

SESSION_KEY = "is_owner"


def owner_lock_enabled():
    return bool(settings.OWNER_SECRET)


def is_owner(request):
    if not owner_lock_enabled():
        return True
    return request.session.get(SESSION_KEY, False)


def secret_matches(candidate):
    """Bandingkan dengan compare_digest agar lama waktu pengecekan tidak membocorkan
    berapa karakter kata sandi yang sudah benar."""
    if not owner_lock_enabled():
        return False
    return hmac.compare_digest(candidate.encode(), settings.OWNER_SECRET.encode())


def owner_required(view):
    """Tolak dengan 403 siapa pun yang bukan pemilik, baik lewat tombol maupun URL langsung."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not is_owner(request):
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapper
