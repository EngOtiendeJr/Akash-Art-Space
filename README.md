# Akash Art Space (Django)

## Run locally

1. Create and activate a Python virtual environment. For detailed local error pages, set `DJANGO_DEBUG=true` in your shell before starting Django.
2. Install Django: `python -m pip install Django`
3. From this folder, run `python manage.py migrate`.
4. Start the development server with `python manage.py runserver`.
5. Open `http://127.0.0.1:8000/`.

## Gallery administration

1. Create an administrator account with `python manage.py createsuperuser`.
2. Start the server and open `http://127.0.0.1:8000/admin/`.
3. Use the Artists and Exhibitions sections to add and manage gallery records. Current and upcoming exhibitions appear on the homepage and exhibition pages; artist records appear on the Artists page.

The homepage and existing About, Contact, Exhibitions, and Archive pages are routed through Django. Static files are served from `Static/` during development.

## Deployment configuration

Set `DJANGO_SECRET_KEY` to a private random value, `DJANGO_DEBUG=false`, and `DJANGO_ALLOWED_HOSTS` to a comma-separated list of the deployment hostnames. Configure a production email backend and static file hosting before enabling email features or deploying.

The default email backend is Django's console backend for local development. The database uses SQLite and starts empty; migrations initialize Django's built-in tables.

