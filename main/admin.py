from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import Group
from django import forms
from django.http import HttpResponseRedirect
from django.db import models
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode

from .constants import MAX_ADMIN_USERS
from .models import Artist, Artwork, Exhibition, ExploreArtwork, ExploreTopic, HomeBanner


class AkashAdminSite(admin.AdminSite):
    site_header = "Akash Art Space Administration"
    site_title = "Akash Art Space Admin"
    index_title = "Manage gallery content"
    index_template = "admin/index.html"

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        if app_label not in (None, "main") or not request.user.has_perm("main.change_exploretopic"):
            return app_list

        upload_links = []
        for topic in ExploreTopic.objects.order_by("display_order", "name"):
            topic_filter = urlencode({"topic__id__exact": topic.pk})
            upload_links.append({
                "name": f"{topic.name} uploads",
                "object_name": f"ExploreTopicUpload{topic.pk}",
                "admin_url": reverse("admin:main_exploreartwork_changelist") + "?" + topic_filter,
                "add_url": reverse("admin:main_exploreartwork_add") + "?" + topic_filter,
                "view_only": False,
            })
        if upload_links:
            app_list.append({
                "name": "Explore page uploads",
                "app_label": "explore_uploads",
                "app_url": reverse("admin:main_exploretopic_changelist"),
                "has_module_perms": True,
                "models": upload_links,
            })
            app_list.sort(key=lambda app: app["name"].lower())
        return app_list

    def index(self, request, extra_context=None):
        can_view_artists = request.user.has_perm("main.view_artist")
        can_manage_artists = any(
            request.user.has_perm(f"main.{action}_artist")
            for action in ("view", "add", "change")
        )
        can_view_exhibitions = request.user.has_perm("main.view_exhibition")
        can_view_artworks = request.user.has_perm("main.view_artwork")
        can_view_homebanners = request.user.has_perm("main.view_homebanner")
        can_view_explore_topics = request.user.has_perm("main.view_exploretopic")
        can_view_users = request.user.has_perm("auth.view_user")
        context = {
            "can_view_artists": can_view_artists,
            "artist_profile": Artist.objects.first() if can_manage_artists else None,
            "can_view_exhibitions": can_view_exhibitions,
            "exhibition_count": Exhibition.objects.count() if can_view_exhibitions else None,
            "artwork_count": Artwork.objects.count() if can_view_artworks else None,
            "can_view_homebanners": can_view_homebanners,
            "homebanner_count": HomeBanner.objects.count() if can_view_homebanners else None,
            "can_view_explore_topics": can_view_explore_topics,
            "explore_topics": ExploreTopic.objects.all() if can_view_explore_topics else (),
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
            "fields": ("instagram_url", "facebook_url", "whatsapp_url", "tiktok_url"),
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
        if artist.has_portrait_image:
            return format_html(
                '<img src="{}" alt="" class="admin-portrait-thumbnail">',
                artist.portrait_image.url,
            )
        if artist.portrait_url:
            return format_html(
                '<img src="{}" alt="" class="admin-portrait-thumbnail">',
                artist.portrait_url,
            )
        if artist.portrait_image:
            return "Uploaded portrait file is missing. Upload it again."
        return "—"

    @admin.display(description="Current portrait")
    def portrait_preview_large(self, artist):
        if artist and artist.has_portrait_image:
            return format_html(
                '<img src="{}" alt="Current portrait of {}" class="admin-portrait-preview">',
                artist.portrait_image.url,
                artist.name,
            )
        if artist and artist.portrait_url:
            return format_html(
                '<img src="{}" alt="Hosted portrait of {}" class="admin-portrait-preview">',
                artist.portrait_url,
                artist.name,
            )
        if artist and artist.portrait_image:
            return "The stored portrait file is missing. Upload it again or add a hosted portrait URL."
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


@admin.register(HomeBanner, site=akash_admin_site)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ("image_thumbnail", "label", "is_active", "display_order", "updated_at")
    list_display_links = ("image_thumbnail",)
    list_editable = ("is_active", "display_order")
    list_filter = ("is_active",)
    search_fields = ("label",)
    list_per_page = 25
    ordering = ("display_order", "pk")
    save_on_top = True
    formfield_overrides = ArtistAdmin.formfield_overrides
    readonly_fields = ("created_at", "updated_at", "image_preview")
    fieldsets = (
        ("Banner image", {
            "description": "Upload an image for the rotating homepage background. The optional label is only shown in this admin.",
            "fields": ("label", "image", "image_preview"),
        }),
        ("Homepage display", {
            "description": "Active banners rotate on the homepage in display order. Deactivate a banner to hide it without deleting it.",
            "fields": ("is_active", "display_order"),
        }),
        ("Record dates", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Image")
    def image_thumbnail(self, banner):
        if banner.image:
            return format_html(
                '<img src="{}" alt="" loading="lazy" class="admin-image-thumbnail">',
                banner.image.url,
            )
        return "—"

    @admin.display(description="Current banner image")
    def image_preview(self, banner):
        if banner and banner.image:
            return format_html(
                '<img src="{}" alt="Current homepage banner" class="admin-artwork-preview">',
                banner.image.url,
            )
        return "Save an uploaded image to preview it here."


@admin.register(ExploreTopic, site=akash_admin_site)
class ExploreTopicAdmin(admin.ModelAdmin):
    list_display = ("name", "is_visible", "display_order", "artwork_count", "updated_at")
    list_filter = ("is_visible",)
    list_editable = ("is_visible", "display_order")
    search_fields = ("name",)
    list_display_links = ("name",)
    list_per_page = 25
    save_on_top = True
    readonly_fields = ("slug", "created_at", "updated_at")
    fieldsets = (
        ("Explore topic", {
            "description": "Each topic automatically gets its own gallery-style page. Choose visibility to show or hide its About page link and public page.",
            "fields": ("name", "slug", "is_visible", "display_order"),
        }),
        ("Record dates", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Artworks")
    def artwork_count(self, topic):
        return topic.uploaded_artworks.count()


@admin.register(ExploreArtwork, site=akash_admin_site)
class ExploreArtworkAdmin(admin.ModelAdmin):
    list_display = ("image_thumbnail", "title", "topic", "year", "status", "display_order")
    list_filter = ("status",)
    search_fields = ("title", "year", "description", "topic__name")
    list_per_page = 25
    list_display_links = ("title",)
    ordering = ("-year", "display_order", "title")
    save_on_top = True
    formfield_overrides = ArtistAdmin.formfield_overrides
    readonly_fields = ("created_at", "updated_at", "image_preview")
    fieldsets = (
        ("Artwork information", {
            "description": "This artwork belongs only to the selected Explore topic collection.",
            "fields": ("topic", "title", "year", "description"),
        }),
        ("Artwork image", {
            "description": "Upload the image to display on this topic's page.",
            "fields": ("image", "image_preview"),
        }),
        ("Availability and enquiries", {
            "description": "Available, Sold or Not for Sale is shown to visitors. Available works require a WhatsApp number.",
            "fields": ("status", "whatsapp_number", "display_order"),
        }),
        ("Record dates", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        topic_id = request.GET.get("topic__id__exact")
        if topic_id and topic_id.isdigit():
            queryset = queryset.filter(topic_id=topic_id)
        return queryset

    def changelist_view(self, request, extra_context=None):
        topic_id = request.GET.get("topic__id__exact")
        if topic_id and topic_id.isdigit() and ExploreTopic.objects.filter(pk=topic_id).exists():
            request.session["explore_artwork_upload_topic"] = topic_id
        return super().changelist_view(request, extra_context)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        topic_id = request.GET.get("topic__id__exact") or request.session.get("explore_artwork_upload_topic")
        if topic_id and str(topic_id).isdigit() and ExploreTopic.objects.filter(pk=topic_id).exists():
            initial["topic"] = topic_id
        return initial

    def _topic_changelist_url(self, topic_id):
        query = urlencode({"topic__id__exact": topic_id})
        return f"{reverse('admin:main_exploreartwork_changelist')}?{query}"

    def response_add(self, request, obj, post_url_continue=None):
        if "_continue" in request.POST:
            return super().response_add(request, obj, post_url_continue)
        if "_addanother" in request.POST:
            add_url = reverse("admin:main_exploreartwork_add")
            return HttpResponseRedirect(f"{add_url}?{urlencode({'topic__id__exact': obj.topic_id})}")
        return HttpResponseRedirect(self._topic_changelist_url(obj.topic_id))

    def response_change(self, request, obj):
        if "_continue" in request.POST:
            return super().response_change(request, obj)
        return HttpResponseRedirect(self._topic_changelist_url(obj.topic_id))

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

    class ChangeForm(UserChangeForm):
        def clean_is_staff(self):
            is_staff = self.cleaned_data["is_staff"]
            if is_staff and not self.instance.is_staff:
                staff_users = get_user_model().objects.filter(is_staff=True).count()
                if staff_users >= MAX_ADMIN_USERS:
                    raise forms.ValidationError(
                        f"Only {MAX_ADMIN_USERS} Django Admin accounts are allowed."
                    )
            return is_staff

    form = ChangeForm

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
