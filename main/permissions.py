from rest_framework.permissions import SAFE_METHODS, BasePermission

from main.roles import is_editor


class IsPortfolioOwnerOrReadOnly(BasePermission):
    message = "Only the portfolio owner can change projects."

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_superuser


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    """Untuk bagian pilihan tugas (Experience): Editor boleh mengubah (PUT/PATCH),
    tetapi menambah dan menghapus tetap hanya untuk pemilik. Memakai is_editor dari
    main/roles.py supaya aturannya sama dengan halaman HTML."""

    message = "Only the portfolio owner can add or delete. Editors may only edit."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
        return request.method in ("PUT", "PATCH") and is_editor(request.user)
