from django.shortcuts import render

from main.models import Experience


def show_main(request):
    context = {
        "name": "Ira Arianti Alawiah",
        "brand_name": "Ira Arianti",
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
        "name": "Ira Arianti Alawiah",
        "brand_name": "Ira Arianti",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)