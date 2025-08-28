# Copilot Instructions for Gereigreja

## Project Overview
- **Gereigreja** is a Django-based web application for church management, with modular apps for finance, events, communication, configuration, and member management.
- The project uses a classic Django structure: each app (e.g., `financeiro`, `eventos`, `contas`, `configuracao`, `secretaria`) contains its own `models.py`, `views.py`, `forms.py`, `urls.py`, and `templates/`.
- The main settings and routing are in `core/settings.py` and `core/urls.py`.

## Key Patterns & Conventions
- **App Structure:** Each app is self-contained. Templates are namespaced under `templates/<app_name>/`.
- **Database:** Uses SQLite by default (`db.sqlite3`). Backups are stored in `/backup/`.
- **Media & Static:** User-uploaded files are in `/media/`; static assets are in `/static/`, `/staticfiles/`, and `/staticfiles_production/`.
- **Custom Utilities:** Shared logic is often placed in `utils.py` within each app.
- **Signals:** Some apps (e.g., `financeiro`, `comunicacao`) use Django signals for side effects.
- **Templatetags:** Custom template tags are in `<app>/templatetags/`.

## Developer Workflows
- **Run Server:** `python manage.py runserver`
- **Migrations:** `python manage.py makemigrations` and `python manage.py migrate`
- **Create Superuser:** `python manage.py createsuperuser`
- **Testing:** Run tests with `python manage.py test <app>` (e.g., `python manage.py test financeiro`)
- **Static Files:** Collect with `python manage.py collectstatic`
- **Backups:** Manual backups are stored in `/backup/` (see backup scripts if present).

## Integration Points
- **Forms:** Each app uses Django forms for validation and admin interfaces.
- **Admin:** Custom admin logic per app in `admin.py`.
- **Cross-App Communication:** Use Django signals or shared utilities for cross-app logic.
- **External Dependencies:** All Python dependencies are listed in `requirements.txt`.

## Project-Specific Notes
- **Error Logging:** Logs are written to `logs/django_errors.log` and `erros.log`.
- **Data Dumps:** JSON data dumps are in the project root (e.g., `datadump.json`).
- **Backup Naming:** Backups are timestamped for traceability.
- **Debugging:** Use `debug.log` for custom debug output.

## Examples
- To add a new finance feature, create a model in `financeiro/models.py`, register it in `financeiro/admin.py`, and add views/templates as needed.
- For custom template logic, add a templatetag in `financeiro/templatetags/` and load it in your template.

---

**For AI agents:**
- Respect the modular app structure—keep logic within the relevant app unless cross-cutting concerns require otherwise.
- When updating models, always create and apply migrations.
- Use existing utility and signal patterns for shared or side-effect logic.
- Reference backup and logging conventions for any data or error handling features.
