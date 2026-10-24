from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.text import slugify
from .validators import validate_gallery_image


class Artist(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    phone = models.CharField(max_length=32, blank=True, help_text="Optional public contact number for this artist.")
    email = models.EmailField(blank=True, help_text="Optional public email address.")
    facebook_url = models.URLField("Facebook link", blank=True)
    whatsapp_url = models.URLField("WhatsApp link", blank=True, help_text="Use a WhatsApp chat link, for example https://wa.me/2547XXXXXXXX.")
    tiktok_url = models.URLField("TikTok link", blank=True)
    biography = models.TextField(blank=True)
    portrait_url = models.URLField(blank=True)
    portrait_image = models.FileField(
        "Portrait image",
        upload_to="artists/portraits/",
        blank=True,
        validators=[FileExtensionValidator(("jpg", "jpeg", "png", "webp", "gif")), validate_gallery_image],
        help_text="Choose a JPG, PNG, WEBP or GIF image up to 10 MB. This portrait appears on the About page.",
    )
    website = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_order", "name")
        verbose_name = "artist profile"
        verbose_name_plural = "artist profile"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def phone_uri(self):
        digits = "".join(character for character in self.phone if character.isdigit())
        return f"+{digits}" if self.phone.strip().startswith("+") else digits

    def __str__(self):
        return self.name


class Exhibition(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField(
        null=True,
        help_text="Exhibitions are listed with the latest date first.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-start_date", "title")

    def __str__(self):
        return self.title


class Artwork(models.Model):
    class Status(models.TextChoices):
        NOT_FOR_SALE = "not_for_sale", "Not for Sale"
        AVAILABLE = "available", "Available"
        SOLD = "sold", "Sold"

    title = models.CharField(max_length=180)
    year = models.CharField(max_length=32)
    description = models.TextField(
        blank=True,
        help_text="Optional. Visitors can open the artwork information control to read this.",
    )
    image = models.FileField(
        "Artwork image",
        upload_to="gallery/artworks/",
        validators=[FileExtensionValidator(("jpg", "jpeg", "png", "webp", "gif")), validate_gallery_image],
        help_text="Upload a JPG, PNG, WEBP or GIF image up to 10 MB.",
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.AVAILABLE,
        help_text="Choose whether this work is available, sold, or not for sale.",
    )
    whatsapp_number = models.CharField(
        max_length=32,
        blank=True,
        help_text="Required for Available works. Enter the full international number, including country code.",
    )
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-year", "display_order", "title")
        verbose_name = "Gallery artwork"
        verbose_name_plural = "Gallery artworks"

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        digits = "".join(character for character in self.whatsapp_number if character.isdigit())
        if self.status == self.Status.AVAILABLE:
            if not digits:
                raise ValidationError({"whatsapp_number": "Add a WhatsApp number for an available artwork."})
            if not 8 <= len(digits) <= 15:
                raise ValidationError({"whatsapp_number": "Enter a valid international WhatsApp number with 8 to 15 digits."})

    @property
    def whatsapp_uri(self):
        digits = "".join(character for character in self.whatsapp_number if character.isdigit())
        return f"https://wa.me/{digits}" if digits else ""


class AboutPage(models.Model):
    intro_label = models.CharField(max_length=100, default="Get to know us")
    title = models.CharField(max_length=180, default="About The Akash Art Space")
    intro_text = models.TextField(default="A welcoming space for creativity, visual expression, and the many ways art connects people with ideas and experiences.")
    space_label = models.CharField(max_length=100, default="Our space")
    space_heading = models.CharField(max_length=180, default="A place to encounter art")
    space_text = models.TextField(default="The Akash Art Space is dedicated to showcasing art, encouraging imagination, and making room for creative expression. Art can communicate ideas, express identity, explore different perspectives, and connect people through visual experiences.\n\nWe celebrate artistic creativity and invite people to discover, experience, and appreciate the diversity of art.")
    explore_heading = models.CharField(max_length=180, default="What you can explore")
    explore_items = models.TextField(default="Paintings\nSculpture\nMixed Media Crafts\nMosaics\nGuided Meditation", help_text="Enter one item per line.")
    vision_heading = models.CharField(max_length=180, default="Our creative vision")
    vision_text = models.TextField(default="We believe art can inspire curiosity, encourage exploration, and help us see the world from fresh perspectives.\n\nWhether you are an artist, student, collector, or discovering art for the first time, you are welcome to explore and enjoy creative expression here.")
    visit_label = models.CharField(max_length=100, default="Plan ahead")
    visit_heading = models.CharField(max_length=180, default="Planning a visit?")
    visit_text = models.TextField(default="Please contact the artist before visiting studio.")
    visit_button_text = models.CharField(max_length=80, default="Contact Artist")
    experience_label = models.CharField(max_length=100, default="Look closer")
    experience_heading = models.CharField(max_length=180, default="Make the experience your own")
    experience_text = models.TextField(default="Art can communicate emotions, tell stories, challenge perspectives, and inspire new ideas. Take time to notice colour, composition, texture, shape, and meaning; each visitor brings a perspective that makes the experience personal.\n\nYou do not need to be an artist or an art expert. Explore, observe, reflect, and discover what the work means to you.")
    exhibitions_button_text = models.CharField(max_length=80, default="Explore exhibitions")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About page"
        verbose_name_plural = "About page"

    @property
    def explore_item_list(self):
        return [item.strip() for item in self.explore_items.splitlines() if item.strip()]

    def __str__(self):
        return "About page content"
