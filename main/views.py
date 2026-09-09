from django.shortcuts import render

from main.models import Experience


def show_main(request):
    context = {
        "name": "Ira Arianti Alawiah",
        "brand_name": "Ira Arianti",
        "npm": "2506551775",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "CS student at Universitas Indonesia, curious about AI, "
            "Machine Learning, and Robotics. I build, experiment, "
            "and occasionally wonder why my code stopped working."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Ira Arianti Alawiah",
        "brand_name": "Ira Arianti",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)