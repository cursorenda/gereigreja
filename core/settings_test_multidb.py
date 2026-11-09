from .settings_test import *  # noqa: F403

DATABASES = {
    **DATABASES,  # noqa: F405
    "secondary": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
}
