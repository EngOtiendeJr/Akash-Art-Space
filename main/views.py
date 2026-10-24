from django.db.models import F
from django.shortcuts import render

from .models import AboutPage, Artist, Artwork, Exhibition


def home(request):
    exhibitions = (
        Exhibition.objects.all()
        .order_by(F("start_date").desc(nulls_last=True), "title")[:3]
    )
    return render(request, "home.html", {"featured_exhibitions": exhibitions})


def about(request):
    about_page = AboutPage.objects.get(pk=1)
    artists = list(Artist.objects.all())
    has_gallery_works = Artwork.objects.exists()
    for artist in artists:
        artist.has_gallery_works = has_gallery_works
    return render(request, "about-us.html", {"about_page": about_page, "artists": artists})


def contact(request):
    return render(request, "contact-us.html")


def exhibitions(request):
    exhibitions = Exhibition.objects.order_by(
        F("start_date").desc(nulls_last=True), "title"
    )
    return render(request, "exhibitions.html", {"exhibitions": exhibitions})


def information_page(request, page_title):
    return render(request, "information.html", {"page_title": page_title})


def gallery(request):
    artworks = Artwork.objects.all()
    artworks = artworks.order_by(
        "-year",
        "display_order",
        "title",
    )
    return render(request, "gallery.html", {
        "artworks": artworks,
        "artist_profile": Artist.objects.first(),
    })


