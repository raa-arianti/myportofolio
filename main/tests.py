import json

from django.test import Client, TestCase, override_settings
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


@override_settings(OWNER_SECRET="test-owner-secret")
class OwnerModeTest(TestCase):
    """Dengan OWNER_SECRET aktif, hanya sesi pemilik yang boleh menambah dan menghapus."""

    def setUp(self):
        self.project = Project.objects.create(
            title="Sortify",
            description="Designing a simpler way to recognize waste.",
            thumbnail="sortify-card.png",
        )
        self.login_url = reverse("main:owner_login")
        self.projects_url = reverse("main:show_projects")

    def log_in(self):
        return self.client.post(self.login_url, {"secret": "test-owner-secret"})

    def test_visitor_does_not_see_owner_controls(self):
        response = self.client.get(self.projects_url)
        self.assertContains(response, self.project.title)
        self.assertNotContains(response, "Add project")
        self.assertNotContains(response, 'class="card-action"')
        self.assertNotContains(response, "Owner mode")

    def test_visitor_is_forbidden_from_protected_views(self):
        response = self.client.get(reverse("main:create_project"))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")

        response = self.client.post(reverse("main:delete_project", args=[self.project.id]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.filter(pk=self.project.id).exists())

    def test_wrong_secret_keeps_site_locked(self):
        response = self.client.post(self.login_url, {"secret": "guess"})
        self.assertContains(response, "That secret is not correct.")
        self.assertEqual(self.client.get(reverse("main:create_project")).status_code, 403)

    def test_correct_secret_unlocks_owner_controls(self):
        self.assertRedirects(self.log_in(), self.projects_url)
        self.assertEqual(self.client.get(reverse("main:create_project")).status_code, 200)

        response = self.client.get(self.projects_url)
        self.assertContains(response, "Add project")
        self.assertContains(response, 'class="card-action"')
        self.assertContains(response, "Owner mode")

    def test_logout_locks_site_again(self):
        self.log_in()
        self.assertEqual(self.client.get(reverse("main:owner_logout")).status_code, 405)
        self.client.post(reverse("main:owner_logout"))
        self.assertEqual(self.client.get(reverse("main:create_project")).status_code, 403)


class OwnerLockDisabledTest(TestCase):
    """Tanpa OWNER_SECRET, kunci nonaktif sehingga fitur form bisa diuji siapa pun."""

    @override_settings(OWNER_SECRET="")
    def test_everyone_is_owner_without_secret(self):
        self.assertEqual(self.client.get(reverse("main:create_project")).status_code, 200)
        self.assertRedirects(
            self.client.get(reverse("main:owner_login")), reverse("main:show_projects")
        )


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

    @override_settings(OWNER_SECRET="test-owner-secret")
    def test_experience_forms_are_owner_only(self):
        urls = [
            reverse("main:create_experience"),
            reverse("main:edit_experience", args=[self.ongoing.id]),
            reverse("main:delete_experience", args=[self.ongoing.id]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.post(url).status_code, 403)
        self.assertEqual(Experience.objects.count(), 2)