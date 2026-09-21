import json

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Project


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")
        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))
        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

class ProjectPageTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Sortify",
            description="Designing a simpler way to recognize waste.",
            thumbnail="sortify-card.png",
        )
        self.url = reverse("main:show_projects")

    def test_projects_url_is_accessible(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")

    def test_project_data_is_displayed(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.description)
        self.assertContains(response, 'src="/static/img/projects/sortify-card.png"')
        self.assertNotContains(response, "No projects have been added yet.")

    def test_empty_projects_page(self):
        Project.objects.all().delete()
        response = self.client.get(self.url)
        self.assertContains(response, "No projects have been added yet.")

    def test_navbar_links_to_projects_page(self):
        for page in ("main:show_main", "main:show_experience", "main:show_projects"):
            with self.subTest(page=page):
                response = self.client.get(reverse(page))
                self.assertContains(response, f'href="{self.url}"')


class ProjectFormAndApiTest(TestCase):
    """Fitur Tutorial 03: form tambah, data JSON, pencarian, dan hapus proyek."""

    def setUp(self):
        self.project = Project.objects.create(
            title="Sortify",
            description="Designing a simpler way to recognize waste.",
            thumbnail="sortify-card.png",
        )
        # Semua form hanya boleh dipakai pemilik portofolio, jadi test ini login lebih dulu.
        self.owner = User.objects.create_superuser("ira", password="owner-pass")
        self.client.force_login(self.owner)
        self.create_url = reverse("main:create_project")
        self.json_url = reverse("main:get_projects_json")
        self.delete_url = reverse("main:delete_project", args=[self.project.id])

    def test_create_page_renders_form_with_csrf_token(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "entry_form.html")
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_create_project_with_valid_data(self):
        response = self.client.post(
            self.create_url,
            {
                "title": "Sheltra",
                "description": "A women's safety platform.",
                "thumbnail": "sheltra-card.png",
            },
            follow=True,
        )
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(Project.objects.filter(title="Sheltra").exists())
        self.assertContains(response, "Project added successfully.")

    def test_create_rejects_missing_image(self):
        response = self.client.post(
            self.create_url,
            {"title": "Broken", "description": "No image.", "thumbnail": "does-not-exist.png"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Project.objects.filter(title="Broken").exists())
        self.assertContains(response, "No image named does-not-exist.png")

    def test_create_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.owner)
        response = csrf_client.post(
            self.create_url,
            {"title": "No token", "description": "Should fail.", "thumbnail": "sortify-card.png"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Project.objects.filter(title="No token").exists())

    def test_projects_json(self):
        response = self.client.get(self.json_url)
        self.assertEqual(response["Content-Type"], "application/json")
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["model"], "main.project")
        self.assertEqual(data[0]["fields"]["title"], "Sortify")

    def test_projects_json_filters_by_title(self):
        Project.objects.create(title="Sheltra", description="Safety.", thumbnail="sheltra-card.png")
        data = json.loads(self.client.get(self.json_url, {"title": "shel"}).content)
        self.assertEqual([item["fields"]["title"] for item in data], ["Sheltra"])

    def test_search_without_match_shows_message(self):
        response = self.client.get(reverse("main:show_projects"), {"title": "zzz"})
        self.assertNotContains(response, 'class="work-card"')
        self.assertContains(response, "No projects match")

    def test_delete_project_with_post(self):
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_get_request_does_not_delete(self):
        self.client.get(self.delete_url)
        self.assertTrue(Project.objects.filter(pk=self.project.id).exists())


class ExperienceCrudTest(TestCase):
    """Tugas 3: ExperienceForm, JSON experience, serta tambah, ubah, dan hapus experience."""

    def setUp(self):
        self.ongoing = Experience.objects.create(
            title="Staff of Community Service Department",
            description="Leading an outreach program.",
            category="volunteer",
        )
        self.finished = Experience.objects.create(
            title="UI/UX Design Intern",
            description="Designed learning interfaces.",
            category="internship",
            ended_at=timezone.make_aware(timezone.datetime(2025, 11, 30)),
        )
        # Semua form hanya boleh dipakai pemilik portofolio, jadi test ini login lebih dulu.
        self.owner = User.objects.create_superuser("ira", password="owner-pass")
        self.client.force_login(self.owner)

    def test_experience_json_lists_ongoing_first(self):
        response = self.client.get(reverse("main:get_experience_json"))
        self.assertEqual(response["Content-Type"], "application/json")
        titles = [item["fields"]["title"] for item in json.loads(response.content)]
        self.assertEqual(titles, [self.ongoing.title, self.finished.title])

    def test_experience_page_shows_deserialized_data(self):
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, self.ongoing.title)
        self.assertContains(response, "Selesai &middot; Nov 2025")

    def test_create_experience(self):
        response = self.client.post(
            reverse("main:create_experience"),
            {
                "title": "Programming & AI Intern",
                "description": "Worked with ROS2 and PX4.",
                "category": "internship",
                "thumbnail": "",
                "ended_at": "2026-02-28",
            },
        )
        self.assertRedirects(response, reverse("main:show_experience"))
        created = Experience.objects.get(title="Programming & AI Intern")
        self.assertFalse(created.is_ongoing)

    def test_create_experience_rejects_unknown_category(self):
        response = self.client.post(
            reverse("main:create_experience"),
            {"title": "X", "description": "Y", "category": "hobby", "thumbnail": "", "ended_at": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Experience.objects.filter(title="X").exists())

    def test_edit_page_is_prefilled(self):
        response = self.client.get(reverse("main:edit_experience", args=[self.finished.id]))
        self.assertTemplateUsed(response, "entry_form.html")
        self.assertContains(response, 'value="UI/UX Design Intern"')
        self.assertContains(response, 'value="2025-11-30"')

    def test_edit_experience_updates_same_row(self):
        url = reverse("main:edit_experience", args=[self.ongoing.id])
        self.client.post(
            url,
            {
                "title": "Staff of Community Service",
                "description": "Updated.",
                "category": "volunteer",
                "thumbnail": "",
                "ended_at": "2026-12-31",
            },
        )
        self.ongoing.refresh_from_db()
        self.assertEqual(self.ongoing.title, "Staff of Community Service")
        self.assertFalse(self.ongoing.is_ongoing)
        self.assertEqual(Experience.objects.count(), 2)

    def test_delete_experience_only_on_post(self):
        url = reverse("main:delete_experience", args=[self.finished.id])
        self.client.get(url)
        self.assertTrue(Experience.objects.filter(pk=self.finished.id).exists())
        self.client.post(url)
        self.assertFalse(Experience.objects.filter(pk=self.finished.id).exists())

    def test_edit_project_updates_same_row(self):
        project = Project.objects.create(
            title="Sortify", description="Old.", thumbnail="sortify-card.png"
        )
        self.client.post(
            reverse("main:edit_project", args=[project.id]),
            {"title": "Sortify v2", "description": "New.", "thumbnail": "sortify-card.png"},
        )
        project.refresh_from_db()
        self.assertEqual(project.title, "Sortify v2")
        self.assertEqual(Project.objects.count(), 1)


class AuthTest(TestCase):
    """Bagian 1 dan 2 Tutorial 04: register, login, logout, dan cookie last_login."""

    def test_register_creates_account(self):
        response = self.client.post(
            reverse("main:register"),
            {"username": "pengunjung", "password1": "kataSandi!2026", "password2": "kataSandi!2026"},
        )
        self.assertRedirects(response, reverse("main:login"))
        self.assertTrue(User.objects.filter(username="pengunjung").exists())

    def test_register_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("main:register"),
            {"username": "pengunjung", "password1": "kataSandi!2026", "password2": "beda!2026"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="pengunjung").exists())

    def test_login_sets_session_and_last_login_cookie(self):
        User.objects.create_user("pengunjung", password="kataSandi!2026")
        response = self.client.post(
            reverse("main:login"), {"username": "pengunjung", "password": "kataSandi!2026"}
        )
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertIn("last_login", response.cookies)
        self.assertContains(self.client.get(reverse("main:show_main")), "Sesi terakhir login")

    def test_login_with_wrong_password_shows_error(self):
        User.objects.create_user("pengunjung", password="kataSandi!2026")
        response = self.client.post(
            reverse("main:login"), {"username": "pengunjung", "password": "salah"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_navbar_shows_username_after_login(self):
        user = User.objects.create_user("pengunjung", password="kataSandi!2026")
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, "Register")

        self.client.force_login(user)
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, "pengunjung")
        self.assertContains(response, "Logout")

    def test_logout_clears_last_login_cookie(self):
        user = User.objects.create_user("pengunjung", password="kataSandi!2026")
        self.client.force_login(user)
        response = self.client.get(reverse("main:logout"))
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertEqual(response.cookies["last_login"].value, "")


class AuthorizationTest(TestCase):
    """Bagian 3 Tutorial 04: pengunjung, pengguna terdaftar, dan pemilik punya hak berbeda."""

    def setUp(self):
        self.owner = User.objects.create_superuser("ira", password="owner-pass")
        self.member = User.objects.create_user("pengunjung", password="kataSandi!2026")
        self.project = Project.objects.create(
            title="Sortify", description="Waste sorting.", thumbnail="sortify-card.png"
        )
        self.protected_urls = [
            reverse("main:create_project"),
            reverse("main:edit_project", args=[self.project.id]),
            reverse("main:delete_project", args=[self.project.id]),
            reverse("main:create_experience"),
        ]

    def test_visitor_is_redirected_to_login(self):
        for url in self.protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f"/login/?next={url}")

    def test_registered_user_is_forbidden(self):
        self.client.force_login(self.member)
        for url in self.protected_urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)
        self.assertTrue(Project.objects.filter(pk=self.project.id).exists())

    def test_owner_may_open_the_forms(self):
        self.client.force_login(self.owner)
        for url in self.protected_urls[:2]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_owner_controls_are_hidden_from_others(self):
        response = self.client.get(reverse("main:show_projects"))
        self.assertNotContains(response, "Add project")

        self.client.force_login(self.member)
        self.assertNotContains(self.client.get(reverse("main:show_projects")), "Add project")

        self.client.force_login(self.owner)
        self.assertContains(self.client.get(reverse("main:show_projects")), "Add project")


class StarTest(TestCase):
    """Bagian 3 Tutorial 04: pengguna terdaftar boleh memberi dan membatalkan star."""

    def setUp(self):
        self.member = User.objects.create_user("pengunjung", password="kataSandi!2026")
        self.project = Project.objects.create(
            title="Sortify", description="Waste sorting.", thumbnail="sortify-card.png"
        )
        self.star_url = reverse("main:toggle_star", args=[self.project.id])

    def test_visitor_is_redirected_to_login(self):
        self.assertRedirects(
            self.client.post(self.star_url), f"/login/?next={self.star_url}"
        )
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_member_can_star_and_unstar(self):
        self.client.force_login(self.member)
        self.client.post(self.star_url)
        self.assertIn(self.member, self.project.starred_by.all())

        self.client.post(self.star_url)
        self.assertNotIn(self.member, self.project.starred_by.all())

    def test_get_request_does_not_change_stars(self):
        self.client.force_login(self.member)
        self.client.get(self.star_url)
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_json_shows_usernames_instead_of_ids(self):
        self.project.starred_by.add(self.member)
        data = json.loads(self.client.get(reverse("main:get_projects_json")).content)
        self.assertEqual(data[0]["fields"]["starred_by"], [["pengunjung"]])