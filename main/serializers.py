from rest_framework import serializers

from main.forms import check_project_thumbnail, strip_html
from main.models import Project


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
