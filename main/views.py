from django.db.models import F
from django.shortcuts import get_object_or_404, render

from .models import AboutPage, Artist, Artwork, Exhibition, ExploreTopic, HomeBanner


def home(request):
    return render(request, "home.html", {
        "home_banners": HomeBanner.objects.filter(is_active=True),
    })


def about(request):
    about_page = AboutPage.objects.get(pk=1)
    artists = list(Artist.objects.all())
    has_gallery_works = Artwork.objects.exists()
    for artist in artists:
        artist.has_gallery_works = has_gallery_works
    return render(request, "about-us.html", {
        "about_page": about_page,
        "artists": artists,
        "explore_topics": ExploreTopic.objects.filter(is_visible=True),
    })


def contact(request):
    return render(request, "contact-us.html", {"artist": Artist.objects.first()})


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




def explore_topic(request, topic_slug):
    topic = get_object_or_404(ExploreTopic, slug=topic_slug, is_visible=True)
    topic_artworks = topic.uploaded_artworks.all().order_by("-year", "display_order", "title")
    return render(request, "explore-topic.html", {
        "topic": topic,
        "topic_artworks": topic_artworks,
    })
