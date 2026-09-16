from django import forms
from django.contrib.staticfiles import finders

from main.models import Project


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
