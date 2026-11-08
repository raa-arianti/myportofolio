import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience, Project


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.project = Project.objects.create(
            title="Portfolio", description="My website", thumbnail="sortify-card.png",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        # thumbnail harus nama berkas yang benar-benar ada di static/img/projects/.
        self.payload = {
            "title": "New project", "description": "A useful app",
            "thumbnail": "sheltra-card.png",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(self.list_url, self.payload, format="json").status_code, 403
            )
            self.assertEqual(
                self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code,
                403,
            )
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"thumbnail": "../settings.py"}, "thumbnail"),
            ({"thumbnail": "does-not-exist.png"}, "thumbnail"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Changed")
        self.assertEqual(self.project.description, "My website")

        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(
            self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        # The Browsable API form renders a real CSRF token into the response.
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ExperienceAPITest(APITestCase):
    """Tugas 6: API Experience dengan empat peran dari Tugas 4.

    Setiap test penolakan memeriksa isi database juga, bukan hanya status HTTP-nya,
    supaya ketahuan kalau view sempat menyimpan data sebelum menolak."""

    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.member = User.objects.create_user(
            username="member", password="test-password", email="member@example.com",
        )
        self.editor = User.objects.create_user(username="editor", password="test-password")
        # Database pengujian selalu kosong, jadi grup Editor dibuat di sini.
        self.editor.groups.add(Group.objects.create(name="Editor"))

        self.experience = Experience.objects.create(
            title="UI/UX Design Intern", description="Designed learning interfaces.",
            category="internship",
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.id])
        self.star_url = reverse("api:experience-star", args=[self.experience.id])
        self.payload = {
            "title": "Teaching Assistant", "description": "Guiding lab sessions.",
            "category": "part-time", "thumbnail": "", "ended_at": None,
        }

    def assert_unchanged(self):
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "UI/UX Design Intern")

    # --- Membaca --------------------------------------------------------------------

    def test_anyone_can_read_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.data[0]
        self.assertEqual(item["id"], str(self.experience.id))
        self.assertEqual(item["category_label"], "Internship")
        self.assertTrue(item["is_ongoing"])
        self.assertFalse(item["is_starred"])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_category_filter(self):
        Experience.objects.create(title="Volunteer Mentor", description="d", category="volunteer")

        def titles(params):
            return [item["title"] for item in self.client.get(self.list_url, params).data]

        self.assertEqual(titles({"title": "intern"}), ["UI/UX Design Intern"])
        self.assertEqual(titles({"category": "volunteer"}), ["Volunteer Mentor"])
        self.assertEqual(titles({"title": "intern", "category": "volunteer"}), [])

    def test_missing_experience_returns_404(self):
        url = reverse("api:experience-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_no_sensitive_account_data_is_exposed(self):
        self.experience.starred_by.add(self.member)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.data["starred_by_names"], "member")
        body = response.content.decode()
        self.assertNotIn("member@example.com", body)
        self.assertNotIn("pbkdf2", body)
        self.assertNotIn('"starred_by"', body)

    def test_list_query_count_does_not_grow_with_rows(self):
        """prefetch_related + starred_by.all() di serializer: dua query untuk berapa pun
        jumlah experience (satu untuk Experience, satu untuk semua user pemberi star)."""
        for i in range(5):
            Experience.objects.create(title=f"E{i}", description="d").starred_by.add(self.member)
        with self.assertNumQueries(2):
            self.client.get(self.list_url)

    # --- Peran: pengunjung dan pengguna biasa ----------------------------------------

    def test_guest_and_member_cannot_write(self):
        for user in (None, self.member):
            with self.subTest(user=user):
                self.client.force_authenticate(user=user)
                responses = [
                    self.client.post(self.list_url, self.payload, format="json"),
                    self.client.put(self.detail_url, self.payload, format="json"),
                    self.client.patch(self.detail_url, {"title": "Hacked"}, format="json"),
                    self.client.delete(self.detail_url),
                ]
                for response in responses:
                    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.assert_unchanged()

    # --- Peran: Editor ---------------------------------------------------------------

    def test_editor_can_patch_and_put(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"title": "Design Intern"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Design Intern")
        self.assertEqual(self.experience.category, "internship")  # field lain tidak berubah

        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Teaching Assistant")

    def test_put_requires_every_required_field(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.put(self.detail_url, {"title": "Only title"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assert_unchanged()

    def test_editor_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_unchanged()

    # --- Peran: pemilik --------------------------------------------------------------

    def test_owner_can_create_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Experience.objects.get(pk=response.data["id"])
        self.assertEqual(created.title, "Teaching Assistant")

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())

    # --- Validasi --------------------------------------------------------------------

    def test_validation_rejects_bad_input(self):
        self.client.force_authenticate(user=self.owner)
        cases = [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"description": "<script></script>"}, "description"),
            ({"category": "astronaut"}, "category"),
            ({"thumbnail": "javascript:alert(1)"}, "thumbnail"),
            ({"ended_at": "bukan tanggal"}, "ended_at"),
        ]
        for changes, field in cases:
            with self.subTest(field=field, changes=changes):
                response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
        self.assert_unchanged()

    def test_tags_are_stripped_but_text_is_kept(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url, {**self.payload, "title": "<b>Teaching</b> Assistant"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Teaching Assistant")

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True, "is_ongoing": False,
            "starred_by_names": "forged", "started_at": "2000-01-01T00:00:00Z",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertTrue(response.data["is_ongoing"])
        self.assertFalse(response.data["started_at"].startswith("2000"))

    # --- Star ------------------------------------------------------------------------

    def test_guest_cannot_star(self):
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_member_can_star_and_unstar(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(response.data["starred_by_names"], "member")
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_star_always_uses_request_user(self):
        """Body yang mencoba menyebut akun lain diabaikan."""
        self.client.force_authenticate(user=self.member)
        self.client.post(self.star_url, {"user": self.owner.id}, format="json")
        self.assertEqual(list(self.experience.starred_by.all()), [self.member])

    def test_star_on_missing_experience_returns_404(self):
        self.client.force_authenticate(user=self.member)
        url = reverse("api:experience-star", args=[uuid.uuid4()])
        self.assertEqual(self.client.post(url).status_code, status.HTTP_404_NOT_FOUND)

    # --- CSRF ------------------------------------------------------------------------

    def test_session_write_without_csrf_is_rejected(self):
        """force_authenticate melewati SessionAuthentication, jadi CSRF tidak ikut diuji.
        Di sini login sungguhan lewat .login() supaya pemeriksaan CSRF benar-benar jalan."""
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("CSRF", str(response.data["detail"]))
        response = client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_unchanged()

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="member", password="test-password")
        # Halaman Experience menyetel cookie csrftoken lewat {% csrf_token %}.
        client.get(reverse("main:show_experience"))
        token = client.cookies["csrftoken"].value
        response = client.post(self.star_url, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
