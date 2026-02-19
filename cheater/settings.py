

"""
Django settings for cheater project (producción Railway).
"""

from pathlib import Path

# -------------------------
# Paths
# -------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------
# Seguridad
# -------------------------
SECRET_KEY = "django-insecure-1^pagal2tm&(yhx+!$^)60q*2y2a$e6-5m&_hxc-@as2+8@s3_"
DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".railway.app",
    ".feuoir.com",
    "www.feuoir.com",
]

# -------------------------
# Aplicaciones
# -------------------------
INSTALLED_APPS = [
    "unfold",
    "ciscoapp",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "corsheaders",
]

# -------------------------
# Middleware
# -------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cheater.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "cheater.wsgi.application"

# -------------------------
# Base de datos (Railway)
# -------------------------
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": "railway",
#         "USER": "postgres",
#         "PASSWORD": "nRamsrsRdKFwIzoKzQpfaOvOzZXrvNYB",
#         "HOST": "caboose.proxy.rlwy.net",
#         "PORT": "45374",
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cisco_cheater_db',
        'USER': 'postgres',
        'PASSWORD': 'odoo',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
# -------------------------
# Validación de contraseñas
# -------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------
# Internacionalización
# -------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Guayaquil"
USE_I18N = True
USE_TZ = True

# -------------------------
# Archivos estáticos
# -------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -------------------------
# Configuración CORS
# -------------------------
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# CORS_ALLOWED_ORIGINS = [
#     "https://*.railway.app",
# ]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]
CORS_ALLOWED_HEADERS = [
    "accept", "accept-encoding", "authorization", "content-type",
    "dnt", "origin", "user-agent", "x-csrftoken", "x-requested-with",
]

# -------------------------
# Seguridad CSRF / Cookies
# -------------------------
CSRF_TRUSTED_ORIGINS = [
    "https://*.railway.app",
]
CSRF_ALLOWED_ORIGINS = [
    "https://*.railway.app",
]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# -------------------------
# Default primary key
# -------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static

UNFOLD = {
    "SITE_TITLE": "cisco-cheater admin",
    "SITE_HEADER": "cisco cheater",
    "SITE_SUBHEADER": "renata xd",
    "SITE_URL": "/",
    "SITE_SYMBOL": "bolt",  # Relámpago - súper cool
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": False,
    "THEME": "light",  # Tema claro
    "BORDER_RADIUS": "8px",
    "COLORS": {
        "primary": {
            "50": "#fefae0",   # fefae0 - crema claro
            "100": "#faedcd",  # faedcd - beige claro
            "200": "#e9edc9",  # e9edc9 - verde menta claro
            "300": "#ccd5ae",  # ccd5ae - verde menta
            "400": "#d4a373",  # d4a373 - marrón dorado
            "500": "#d4a373",  # d4a373 - marrón dorado (principal)
            "600": "#b8956a",  # versión más oscura
            "700": "#9c7a5a",  # versión más oscura
            "800": "#80604a",  # versión más oscura
            "900": "#64453a",  # versión más oscura
            "950": "#482a2a",  # versión más oscura
        },
        "base": {
            "50": "#fefae0",   # fefae0 - crema claro
            "100": "#faedcd",  # faedcd - beige claro
            "200": "#e9edc9",  # e9edc9 - verde menta claro
            "300": "#ccd5ae",  # ccd5ae - verde menta
            "400": "#d4a373",  # d4a373 - marrón dorado
            "500": "#d4a373",  # d4a373 - marrón dorado
            "600": "#b8956a",  # versión más oscura
            "700": "#9c7a5a",  # versión más oscura
            "800": "#80604a",  # versión más oscura
            "900": "#64453a",  # versión más oscura
            "950": "#482a2a",  # versión más oscura
        },
        "font": {
            "subtle-light": "var(--color-base-600)",
            "subtle-dark": "var(--color-base-400)",
            "default-light": "var(--color-base-700)",
            "default-dark": "var(--color-base-300)",
            "important-light": "var(--color-base-900)",
            "important-dark": "var(--color-base-100)",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Dashboard"),
                "separator": True,
                "items": [
                    {
                        "title": _("Overview"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": _("Exámenes"),
                "separator": True,
                "items": [
                    {
                        "title": _("Exámenes"),
                        "icon": "quiz",
                        "link": reverse_lazy("admin:ciscoapp_exam_changelist"),
                    },
                    {
                        "title": _("Preguntas"),
                        "icon": "help",
                        "link": reverse_lazy("admin:ciscoapp_question_changelist"),
                    },
                    {
                        "title": _("Respuestas"),
                        "icon": "check_circle",
                        "link": reverse_lazy("admin:ciscoapp_answer_changelist"),
                    },
                ],
            },
            {
                "title": _("Activation Keys"),
                "separator": True,
                "items": [
                    {
                        "title": _("All Keys"),
                        "icon": "key",
                        "link": reverse_lazy("admin:ciscoapp_activationkey_changelist"),
                    },
                ],
            },
            {
                "title": _("User Management"),
                "separator": True,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "people",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "groups",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
            {
                "title": _("Site"),
                "separator": True,
                "items": [
                    {
                        "title": _("Home Page"),
                        "icon": "home",
                        "link": "/",
                    },
                ],
            },
        ],
    },
    "LOGIN": {
        "redirect_after": lambda request: reverse_lazy("admin:index"),
    },
    "STYLES": [
        lambda request: static("admin/custom.css"),
    ],
}

