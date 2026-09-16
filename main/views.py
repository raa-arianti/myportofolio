from django.contrib import messages
from django.core import serializers
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project
from main.owner import SESSION_KEY, is_owner, owner_lock_enabled, owner_required, secret_matches

# name dan brand_name untuk navbar, footer, dan judul tab dikirim oleh
# main.context_processors.site ke semua template, jadi view tidak perlu mengirimnya.


def show_main(request):
    context = {
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


def get_experience_json(request):
    """Kirim data experience sebagai JSON. Yang masih berlangsung (ended_at kosong) di atas,
    lalu yang paling baru selesai, sama seperti urutan linimasa di rancangan. Kalau tanggal
    selesainya sama, yang lebih dulu dimasukkan tampil lebih dulu."""
    experiences = Experience.objects.order_by(
        F("ended_at").desc(nulls_first=True), "started_at"
    )
    experiences_json = serializers.serialize("json", experiences)
    return HttpResponse(experiences_json, content_type="application/json")


def show_experience(request):
    """Seperti halaman proyek, data diambil dari JSON lalu di-deserialize."""
    json_response = get_experience_json(request)
    experience_list = [
        item.object
        for item in serializers.deserialize("json", json_response.content.decode("utf-8"))
    ]
    context = {
        "experience_list": experience_list,
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
        "project_list": project_list,
        "title_query": request.GET.get("title", "").strip(),
    }
    return render(request, "projects.html", context)


def render_entry_form(request, form, *, page_title, submit_label, cancel_url_name):
    """Satu halaman form untuk semua aksi tambah dan ubah data (proyek maupun experience)."""
    context = {
        "form": form,
        "page_title": page_title,
        "submit_label": submit_label,
        "cancel_url": reverse(cancel_url_name),
    }
    return render(request, "entry_form.html", context)


@owner_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project added successfully.")
        return redirect("main:show_projects")

    return render_entry_form(
        request,
        form,
        page_title="Add Project",
        submit_label="Add project",
        cancel_url_name="main:show_projects",
    )


@owner_required
def edit_project(request, project_id):
    """Form ubah = form tambah yang diisi data lama lewat instance=project, lalu
    form.save() memperbarui baris yang sama, bukan membuat baris baru."""
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{project.title} was updated.")
        return redirect("main:show_projects")

    return render_entry_form(
        request,
        form,
        page_title="Edit Project",
        submit_label="Save changes",
        cancel_url_name="main:show_projects",
    )


@owner_required
def delete_project(request, project_id):
    """Hapus proyek hanya lewat POST dari form konfirmasi. Request GET, misalnya
    karena alamatnya dibuka langsung, tidak menghapus apa pun."""
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, f"{project.title} was deleted.")
    return redirect("main:show_projects")



@owner_required
def create_experience(request):
    form = ExperienceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience added successfully.")
        return redirect("main:show_experience")

    return render_entry_form(
        request,
        form,
        page_title="Add Experience",
        submit_label="Add experience",
        cancel_url_name="main:show_experience",
    )


@owner_required
def edit_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{experience.title} was updated.")
        return redirect("main:show_experience")

    return render_entry_form(
        request,
        form,
        page_title="Edit Experience",
        submit_label="Save changes",
        cancel_url_name="main:show_experience",
    )


@owner_required
def delete_experience(request, experience_id):
    """Sama seperti delete_project: hanya POST yang menghapus."""
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == "POST":
        experience.delete()
        messages.success(request, f"{experience.title} was deleted.")
    return redirect("main:show_experience")


def owner_login(request):
    """Halaman masuk mode pemilik. Tidak ditautkan dari mana pun, dibuka lewat /owner/."""
    if not owner_lock_enabled() or is_owner(request):
        return redirect("main:show_projects")

    error = ""
    if request.method == "POST":
        if secret_matches(request.POST.get("secret", "")):
            # Ganti ID sesi setelah berhasil masuk, supaya ID sesi lama tidak bisa dipakai ulang.
            request.session.cycle_key()
            request.session[SESSION_KEY] = True
            messages.success(request, "Owner mode is on.")
            return redirect("main:show_projects")
        error = "That secret is not correct."

    return render(request, "owner_login.html", {"error": error})


@require_POST
def owner_logout(request):
    request.session.pop(SESSION_KEY, None)
    messages.success(request, "Owner mode is off.")
    return redirect("main:show_main")