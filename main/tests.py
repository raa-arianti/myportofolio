import json

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
        self.create_url = reverse("main:create_project")
        self.json_url = reverse("main:get_projects_json")
        self.delete_url = reverse("main:delete_project", args=[self.project.id])

    def test_create_page_renders_form_with_csrf_token(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")
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