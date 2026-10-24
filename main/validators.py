from django.core.exceptions import ValidationError


MAX_GALLERY_IMAGE_SIZE = 10 * 1024 * 1024
IMAGE_SIGNATURES = (
    ("JPEG", lambda data: data.startswith(b"\xff\xd8\xff")),
    ("PNG", lambda data: data.startswith(b"\x89PNG\r\n\x1a\n")),
    ("GIF", lambda data: data.startswith((b"GIF87a", b"GIF89a"))),
    ("WEBP", lambda data: data.startswith(b"RIFF") and data[8:12] == b"WEBP"),
)


def validate_gallery_image(upload):
    """Accept common web image formats and keep gallery uploads manageable."""
    if upload.size > MAX_GALLERY_IMAGE_SIZE:
        raise ValidationError("Choose an image smaller than 10 MB.")

    try:
        signature = upload.read(16)
        upload.seek(0)
    except (AttributeError, OSError):
        raise ValidationError("Choose a valid JPG, PNG, WEBP or GIF image.") from None

    if not any(matches(signature) for _name, matches in IMAGE_SIGNATURES):
        raise ValidationError("This file does not appear to be a valid JPG, PNG, WEBP or GIF image.")
