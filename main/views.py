from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
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


def get_projects_json(request):
    """Kirim data proyek sebagai JSON. ?title=... menyaring berdasarkan judul."""
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")


def show_projects(request):
    """Halaman proyek tidak membaca basis data langsung: datanya diambil dari JSON
    get_projects_json, lalu di-deserialize kembali menjadi objek Project."""
    json_response = get_projects_json(request)
    project_list = [
        item.object
        for item in serializers.deserialize("json", json_response.content.decode("utf-8"))
    ]
    context = {
        **SITE_OWNER,
        "project_list": project_list,
        "title_query": request.GET.get("title", "").strip(),
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


def delete_project(request, project_id):
    """Hapus proyek hanya lewat POST dari form konfirmasi. Request GET, misalnya
    karena alamatnya dibuka langsung, tidak menghapus apa pun."""
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, f"{project.title} was deleted.")
    return redirect("main:show_projects")