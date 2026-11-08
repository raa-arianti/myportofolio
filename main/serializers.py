from rest_framework import serializers

from main.forms import check_project_thumbnail, strip_html
from main.models import Experience, Project


class ProjectSerializer(serializers.ModelSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "title", "description", "thumbnail",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    # Serializer tidak menjalankan clean_<field> milik ProjectForm, jadi aturan yang
    # sama dipanggil ulang di sini. DRF mengubah ValidationError milik Django menjadi
    # error 400 per field.
    def validate_title(self, value):
        return strip_html(value, "title")

    def validate_description(self, value):
        return strip_html(value, "description")

    def validate_thumbnail(self, value):
        return check_project_thumbnail(value)

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class ExperienceSerializer(serializers.ModelSerializer):
    """Representasi Experience untuk /api/v1/experience/.

    Field star dihitung dari starred_by.all() (bukan .count() atau .filter()) supaya
    memakai hasil prefetch_related di view. Dengan begitu daftar berisi N experience
    tetap hanya butuh dua query, bukan 1 + 2N. Yang dikirim hanya username, tidak
    pernah email, id, atau password hash pengguna."""

    category_label = serializers.CharField(source="get_category_display", read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = [
            "id", "title", "description", "category", "category_label",
            "thumbnail", "started_at", "ended_at", "is_ongoing",
            "star_count", "is_starred", "starred_by_names",
        ]
        # started_at diisi otomatis (auto_now_add), jadi hanya bisa dibaca.
        read_only_fields = ["id", "started_at"]

    # Aturan yang sama dengan clean_title dan clean_description milik ExperienceForm.
    def validate_title(self, value):
        return strip_html(value, "title")

    def validate_description(self, value):
        return strip_html(value, "description")

    def _starred_users(self, obj):
        return obj.starred_by.all()

    def get_star_count(self, obj):
        return len(self._starred_users(obj))

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return any(user.pk == request.user.pk for user in self._starred_users(obj))

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in self._starred_users(obj))
