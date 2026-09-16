from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from main.forms import ProjectForm
from main.models import Experience, Project

# Dipakai base.html (navbar, footer, judul tab) di setiap halaman, jadi ditulis sekali
# di sini lalu disebarkan ke context tiap view dengan **SITE_OWNER.
SITE_OWNER = {
    "name": "Ira Arianti Alawiah",
    "brand_name": "Ira Arianti",
}


def show_main(request):
    context = {
        **SITE_OWNER,
        "nickname": "Ira",
        "npm": "2506551775",
        "role": "CS Student at Universitas Indonesia",
        "bio": (
            "I enjoy learning deeply,\n"
            "turning complex ideas into clear solutions,\n"
            "building with purpose and care."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        **SITE_OWNER,
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


def show_projects(request):
    context = {
        **SITE_OWNER,
        "project_list": Project.objects.all(),
    }
    return render(request, "projects.html", context)


def create_project(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project added successfully.")
        return redirect("main:show_projects")

    context = {
        **SITE_OWNER,
        "form": form,
        "page_title": "Add Project",
        "submit_label": "Add project",
        "cancel_url": reverse("main:show_projects"),
    }
    return render(request, "projects_form.html", context)