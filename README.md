# Akash Art Space Repaired

## Image uploads on Render

Django Admin keeps the normal image file picker. To store uploaded images
durably without a Render disk, set `CLOUDINARY_URL` in the Render web service's
Environment settings. Copy the API environment variable from the Cloudinary
Console; keep it private and do not commit it to this repository. Render will
redeploy after the variable is saved. No Render disk mount is needed.

When `CLOUDINARY_URL` is present, new image uploads from Admin are saved to
Cloudinary and served from its CDN. Without it, local development uses the
project's `media/` directory. Files previously saved on Render's temporary
filesystem are not copied automatically; upload those images again in Admin
after Cloudinary is configured.

## Django Admin account limit

The project allows at most two staff accounts with access to Django Admin.
The Admin interface does not allow adding users, blocks promotion of a third
staff account, and the `create_admin` deployment command enforces the same
limit. Existing accounts are left unchanged; remove staff access from any
extra account before creating or promoting another one.
