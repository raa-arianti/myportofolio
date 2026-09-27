"""Peran pengguna di portofolio ini.

Peran Editor tidak ditulis di kode, melainkan berupa grup bernama "Editor" yang
dibuat lewat Django Admin. Berkas ini hanya menyediakan pemeriksaannya, supaya
view dan template memakai aturan yang sama persis.
"""


def is_editor(user):
    return user.is_authenticated and user.groups.filter(name="Editor").exists()


def can_change_content(user):
    """Boleh mengubah data yang sudah ada: pemilik portofolio atau Editor.
    Menambah dan menghapus tetap hanya untuk pemilik (user.is_superuser)."""
    return user.is_superuser or is_editor(user)