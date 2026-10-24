from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django import forms
from django.db import models
from django.utils.html import format_html

from .models import Artist, Artwork, Exhibition


class AkashAdminSite(admin.AdminSite):
    site_header = "Akash Art Space Administration"
    site_title = "Akash Art Space Admin"
    index_title = "Manage gallery content"
    index_template = "admin/index.html"

    def index(self, request, extra_context=None):
        can_view_artists = request.user.has_perm("main.view_artist")
        can_manage_artists = any(
            request.user.has_perm(f"main.{action}_artist")
            for action in ("view", "add", "change")
        )
        can_view_exhibitions = request.user.has_perm("main.view_exhibition")
        can_view_artworks = request.user.has_perm("main.view_artwork")
        can_view_users = request.user.has_perm("auth.view_user")
        context = {
            "can_view_artists": can_view_artists,
            "artist_profile": Artist.objects.first() if can_manage_artists else None,
            "can_view_exhibitions": can_view_exhibitions,
            "exhibition_count": Exhibition.objects.count() if can_view_exhibitions else None,
            "artwork_count": Artwork.objects.count() if can_view_artworks else None,
            "recent_exhibitions": (
                Exhibition.objects.order_by(models.F("start_date").desc(nulls_last=True), "title")[:5]
                if can_view_exhibitions else ()
            ),
            "can_view_users": can_view_users,
            "user_count": get_user_model().objects.count() if can_view_users else None,
        }
        context.update(extra_context or {})
        return super().index(request, extra_context=context)


akash_admin_site = AkashAdminSite(name="admin")


@admin.register(Artist, site=akash_admin_site)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("portrait_preview", "name", "phone", "email", "updated_at")
    search_fields = ("name", "phone", "email", "biography")
    list_per_page = 25
    save_on_top = True
    formfield_overrides = {
        models.FileField: {
            "widget": forms.ClearableFileInput(attrs={
                "accept": "image/jpeg,image/png,image/webp,image/gif",
                "class": "vFileField",
            }),
        },
    }
    readonly_fields = ("created_at", "updated_at", "portrait_preview_large")
    ordering = ("display_order", "name")
    fieldsets = (
        ("About the artist", {
            "description": "Manage the artist profile displayed on the About page.",
            "fields": ("name", "phone", "email", "biography"),
        }),
        ("Social links", {
            "description": "Add any public profiles the artist wants visitors to find. Only provided links appear on the website.",
            "fields": ("facebook_url", "whatsapp_url", "tiktok_url"),
        }),
        ("Portrait and website", {
            "description": "Upload the portrait shown on the About page. You can optionally provide a hosted image link as a fallback.",
            "fields": ("portrait_image", "portrait_preview_large", "portrait_url", "website"),
        }),
        ("Record dates", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )

    def has_add_permission(self, request):
        return not Artist.objects.exists() and super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Portrait")
    def portrait_preview(self, artist):
        if artist.portrait_image:
            return format_html(
                '<img src="{}" alt="" class="admin-portrait-thumbnail">',
                artist.portrait_image.url,
            )
        return "—"

    @admin.display(description="Current portrait")
    def portrait_preview_large(self, artist):
        if artist and artist.portrait_image:
            return format_html(
                '<img src="{}" alt="Current portrait of {}" class="admin-portrait-preview">',
                artist.portrait_image.url,
                artist.name,
            )
        return "Save an uploaded portrait to preview it here."


@admin.register(Exhibition, site=akash_admin_site)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "description_preview")
    search_fields = ("title", "description")
    list_per_page = 20
    save_on_top = True
    date_hierarchy = "start_date"
    ordering = ("-start_date", "title")
    list_display_links = ("title",)
    fieldsets = (
        ("Exhibition information", {
            "description": "Add the exhibition title and date. A description is optional.",
            "fields": ("title", "start_date", "description"),
        }),
    )

    @admin.display(description="Description")
    def description_preview(self, exhibition):
        return exhibition.description[:100] + ("…" if len(exhibition.description) > 100 else "") or "—"


@admin.register(Artwork, site=akash_admin_site)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ("image_thumbnail", "title", "year", "status", "display_order")
    list_filter = ("status",)
    list_editable = ("status", "display_order")
    search_fields = ("title", "year", "description")
    list_per_page = 25
    list_display_links = ("title",)
    ordering = ("-year", "display_order", "title")
    save_on_top = True
    formfield_overrides = ArtistAdmin.formfield_overrides
    readonly_fields = ("created_at", "updated_at", "image_preview")
    fieldsets = (
        ("Artwork information", {
            "description": "Add the work's title, year and optional description.",
            "fields": ("title", "year", "description"),
        }),
        ("Artwork image", {
            "description": "Upload the artwork image. This image appears on the public Gallery page.",
            "fields": ("image", "image_preview"),
        }),
        ("Availability and enquiries", {
            "description": "For Available works, enter a WhatsApp number with country code. Visitors can select the Available label to start a chat.",
            "fields": ("status", "whatsapp_number", "display_order"),
        }),
        ("Record dates", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Image")
    def image_thumbnail(self, artwork):
        return format_html(
            '<img src="{}" alt="" loading="lazy" class="admin-image-thumbnail">',
            artwork.image.url,
        )

    @admin.display(description="Current artwork image")
    def image_preview(self, artwork):
        if artwork and artwork.image:
            return format_html(
                '<img src="{}" alt="" class="admin-artwork-preview">',
                artwork.image.url,
            )
        return "Save an uploaded image to preview it here."


@admin.register(get_user_model(), site=akash_admin_site)
class GalleryUserAdmin(UserAdmin):
    """Use Django's secure account and password forms on the gallery admin site."""

    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)
    list_per_page = 25
    save_on_top = True
    fieldsets = (
        ("Sign-in details", {"fields": ("username", "password")}),
        ("Personal details", {"fields": ("first_name", "last_name", "email")}),
        ("Access to the gallery admin", {
            "description": "Staff accounts can manage gallery content. Only give people the access they need.",
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        ("Account dates", {"classes": ("collapse",), "fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        ("Create a sign-in", {
            "classes": ("wide",),
            "description": "Create an account for a trusted gallery team member. Set a temporary password and share it with them securely.",
            "fields": ("username", "email", "first_name", "last_name", "password1", "password2", "is_active", "is_staff"),
        }),
    )

    def has_add_permission(self, request):
        return False


@admin.register(Group, site=akash_admin_site)
class GalleryGroupAdmin(GroupAdmin):
    """Allow managers to assign reusable role-based access to staff."""
