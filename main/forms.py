from django import forms
from django.contrib.staticfiles import finders

from main.models import Experience, Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "thumbnail"]
        labels = {
            "title": "Project title",
            "description": "Description",
            "thumbnail": "Card image",
        }
        help_texts = {
            "thumbnail": "File name inside static/img/projects/, for example sortify-card.png.",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Sortify"}),
            "description": forms.Textarea(
                attrs={"placeholder": "What is this project about?", "rows": 4}
            ),
            "thumbnail": forms.TextInput(attrs={"placeholder": "sortify-card.png"}),
        }

    def clean_thumbnail(self):
        """Tolak nama file yang tidak ada, supaya kartu tidak tampil dengan gambar rusak."""
        name = self.cleaned_data["thumbnail"].strip()
        if "/" in name or "\\" in name:
            raise forms.ValidationError("Enter only the file name, without a folder.")
        if not finders.find(f"img/projects/{name}"):
            raise forms.ValidationError(
                f"No image named {name} was found in static/img/projects/."
            )
        return name


class ExperienceForm(forms.ModelForm):
    """id dan started_at (auto_now_add) tidak dimasukkan karena diisi otomatis.
    ended_at tetap dimasukkan karena diisi pemilik untuk menandai pengalaman selesai."""

    class Meta:
        model = Experience
        fields = ["title", "description", "category", "thumbnail", "ended_at"]
        labels = {
            "title": "Role or activity",
            "description": "Description",
            "category": "Category",
            "thumbnail": "Image URL",
            "ended_at": "End date",
        }
        help_texts = {
            "thumbnail": "Optional. A direct link to an image.",
            "ended_at": "Leave empty if this experience is still ongoing.",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Staff of Community Service Department"}
            ),
            "description": forms.Textarea(
                attrs={"placeholder": "What did you do and learn?", "rows": 4}
            ),
            # DateTimeField ditampilkan sebagai pemilih tanggal saja. format wajib sama
            # dengan yang dibaca <input type="date">, supaya tanggal tersimpan ikut
            # muncul saat form ubah data dibuka.
            "ended_at": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }
