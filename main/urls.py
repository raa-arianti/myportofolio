from django.urls import path

from main.views import (
    create_project,
    delete_project,
    edit_project,
    get_experience_json,
    get_projects_json,
    owner_login,
    owner_logout,
    show_experience,
    show_main,
    show_projects,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/<uuid:project_id>/edit/", edit_project, name="edit_project"),
    path("projects/<uuid:project_id>/delete/", delete_project, name="delete_project"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("owner/", owner_login, name="owner_login"),
    path("owner/logout/", owner_logout, name="owner_logout"),
]