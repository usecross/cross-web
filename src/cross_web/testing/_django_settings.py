SECRET_KEY = "test-secret-key"
DEBUG = True
DEFAULT_CHARSET = "utf-8"
USE_TZ = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
]

MIDDLEWARE = []
ROOT_URLCONF = "cross_web.testing._django_urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
