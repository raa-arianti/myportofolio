import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import PermissionDenied
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project
from main.roles import can_change_content

# name dan brand_name untuk navbar, footer, dan judul tab dikirim oleh
# main.context_processors.site ke semua template, jadi view tidak perlu mengirimnya.


def show_main(request):
    # Cookie last_login dikirim browser di setiap request setelah login.
    last_login = request.COOKIES.get("last_login", "Belum ada sesi login")
    context = {
        "last_login": last_login,
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
    """Kirim data experience sebagai JSON. ?title=... menyaring berdasarkan judul.

    Urutan: yang masih berlangsung (ended_at kosong) di atas, lalu yang paling baru
    selesai. Kalau tanggal selesainya sama, yang lebih dulu dimasukkan tampil lebih dulu.

    JSON dirakit manual dengan alasan yang sama seperti get_projects_json: status star
    bergantung pada akun yang sedang login. Hanya username yang dikirim, bukan id."""
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.prefetch_related("starred_by").order_by(
        F("ended_at").desc(nulls_first=True), "started_at"
    )
    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    data = []
    for experience in experiences:
        starred_users = list(experience.starred_by.all())
        data.append(
            {
                "pk": str(experience.id),
                "fields": {
                    "title": experience.title,
                    "description": experience.description,
                    # Label yang dibaca manusia ("Part-Time"), bukan kodenya ("part-time").
                    "category": experience.get_category_display(),
                    "thumbnail": experience.thumbnail,
                    # None berarti masih berlangsung.
                    "ended_at": experience.ended_at,
                    "star_count": len(starred_users),
                    "is_starred": request.user in starred_users,
                    "starred_by_names": ", ".join(user.username for user in starred_users),
                },
            }
        )
    return JsonResponse(data, safe=False)


def show_experience(request):
    # Sementara masih merender daftar di server. Tahap berikutnya halaman ini
    # hanya mengirim kerangka dan datanya diambil lewat AJAX.
    experience_list = Experience.objects.order_by(
        F("ended_at").desc(nulls_first=True), "started_at"
    )
    return render(request, "experience.html", {"experience_list": experience_list})

def get_projects_json(request):
    """Kirim data proyek sebagai JSON. ?title=... menyaring berdasarkan judul.

    JSON dirakit manual, bukan lewat serializers.serialize, karena status star
    bergantung pada akun yang sedang login dan serializer bawaan tidak
    mengetahuinya. Hanya username yang dikirim, bukan id pengguna."""
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related("starred_by").all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)

    data = []
    for project in projects:
        starred_users = list(project.starred_by.all())
        data.append(
            {
                "pk": str(project.id),
                "fields": {
                    "title": project.title,
                    "description": project.description,
                    "thumbnail": project.thumbnail,
                    "star_count": len(starred_users),
                    "is_starred": request.user in starred_users,
                    "starred_by_names": ", ".join(user.username for user in starred_users),
                },
            }
        )
    return JsonResponse(data, safe=False)


def show_projects(request):
    """Halaman ini hanya mengirim kerangkanya. Daftar proyeknya diambil browser
    sendiri lewat AJAX ke get_projects_json. ProjectForm kosong dikirim untuk
    mengisi modal tambah proyek."""
    context = {
        "title_query": request.GET.get("title", "").strip(),
        "form": ProjectForm(),
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


@login_required(login_url="/login/")
def create_project(request):
    # Hanya pemilik portofolio (superuser) yang boleh mengubah isi situs.
    if not request.user.is_superuser:
        raise PermissionDenied

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


@require_POST
def create_project_ajax(request):
    """Versi AJAX dari create_project. Jawabannya selalu JSON supaya bisa dibaca fetch.

    Tidak memakai @login_required karena dekorator itu membalas dengan redirect ke
    halaman login, dan fetch akan mengikutinya lalu menerima HTML berstatus 200
    sehingga JavaScript mengira permintaannya berhasil. AnonymousUser juga bernilai
    False pada is_superuser, jadi satu pemeriksaan di bawah sudah menolak pengunjung
    maupun pengguna biasa."""
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Only the portfolio owner can add a project."}, status=403
        )

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Project added successfully.", "pk": str(project.id)}, status=201
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@login_required(login_url="/login/")
def edit_project(request, project_id):
    """Form ubah = form tambah yang diisi data lama lewat instance=project, lalu
    form.save() memperbarui baris yang sama, bukan membuat baris baru."""
    # Hanya pemilik portofolio (superuser) yang boleh mengubah isi situs.
    if not can_change_content(request.user):
        raise PermissionDenied

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


@login_required(login_url="/login/")
def delete_project(request, project_id):
    """Hapus proyek hanya lewat POST dari form konfirmasi. Request GET, misalnya
    karena alamatnya dibuka langsung, tidak menghapus apa pun."""
    # Hanya pemilik portofolio (superuser) yang boleh mengubah isi situs.
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, f"{project.title} was deleted.")
    return redirect("main:show_projects")


@login_required(login_url="/login/")
def create_experience(request):
    # Hanya pemilik portofolio (superuser) yang boleh mengubah isi situs.
    if not request.user.is_superuser:
        raise PermissionDenied

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


@login_required(login_url="/login/")
def edit_experience(request, experience_id):
    # Mengubah data boleh dilakukan pemilik portofolio maupun Editor.
    if not can_change_content(request.user):
        raise PermissionDenied

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


@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    """Sama seperti delete_project: hanya POST yang menghapus."""
    # Hanya pemilik portofolio (superuser) yang boleh mengubah isi situs.
    if not request.user.is_superuser:
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == "POST":
        experience.delete()
        messages.success(request, f"{experience.title} was deleted.")
    return redirect("main:show_experience")



# Tanpa cek is_superuser: semua akun yang sudah login boleh memberi star.
@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)
    return redirect("main:show_projects")


def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    return render(request, "register.html", {"form": form})


def login_user(request):
    """Dinamai login_user supaya tidak menimpa fungsi login() yang diimpor di atas."""
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        response = redirect("main:show_main")
        response.set_cookie(
            "last_login", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        return response

    return render(request, "login.html", {"form": form})


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response


@login_required(login_url="/login/")
def toggle_star_experience(request, experience_id):
    """Sama seperti toggle_star milik proyek: semua akun yang sudah login boleh
    memberi atau membatalkan star, dan hanya POST yang mengubah data."""
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == "POST":
        if request.user in experience.starred_by.all():
            experience.starred_by.remove(request.user)
        else:
            experience.starred_by.add(request.user)
    return redirect("main:show_experience")