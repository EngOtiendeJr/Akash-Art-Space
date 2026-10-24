from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("exhibitions/", views.exhibitions, name="exhibitions"),
    path("exhibitions/archive/", RedirectView.as_view(pattern_name="main:exhibitions", permanent=True), name="exhibition_archive"),
    path("exhibitions/up-coming-exhibitions/", RedirectView.as_view(pattern_name="main:exhibitions", permanent=True), name="upcoming_exhibitions"),
    path("exhibitions/current-exhibitions/", RedirectView.as_view(pattern_name="main:exhibitions", permanent=True), name="current_exhibitions"),
    path("exhibitions/<slug:exhibition_slug>/", RedirectView.as_view(pattern_name="main:exhibitions", permanent=True), name="exhibition_detail"),
    path("artists/", RedirectView.as_view(pattern_name="main:about", permanent=True), name="artists"),
    path("gallery/", views.gallery, name="gallery"),
]
