import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file (sits next to manage.py)
load_dotenv(BASE_DIR / '.env')

# ─────────────────────────────────────────────────────────────────────────────
# SECURITY — All secrets are loaded from .env (never hardcode these!)
# ─────────────────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom apps
    'authentication.apps.AuthenticationConfig',
    'core.apps.CoreConfig',
    'resume.apps.ResumeConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bluenova_erp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Look for templates in root directory or app folders
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bluenova_erp.wsgi.application'

# Database Setup - SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom User Auth Settings
AUTH_USER_MODEL = 'authentication.User'

# ─────────────────────────────────────────────────────────────────────────────
# SESSION & COOKIE SECURITY
# ─────────────────────────────────────────────────────────────────────────────

# Store sessions in the database (default, backed by django.contrib.sessions)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Session lifetime: 30 minutes of inactivity
SESSION_COOKIE_AGE = 1800  # seconds

# Extend session on every request so active users aren't logged out mid-work
SESSION_SAVE_EVERY_REQUEST = True

# Destroy session when browser closes (additional safety net)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Prevent JavaScript from reading the session cookie (mitigates XSS theft)
SESSION_COOKIE_HTTPONLY = True

# SameSite=Lax blocks CSRF via cross-site navigation while allowing normal links
SESSION_COOKIE_SAMESITE = 'Lax'

# Set to True in production when serving over HTTPS
# SESSION_COOKIE_SECURE = True  # Uncomment for HTTPS/production

# ─────────────────────────────────────────────────────────────────────────────
# CSRF PROTECTION
# ─────────────────────────────────────────────────────────────────────────────
CSRF_COOKIE_HTTPONLY = False   # Must be False so JS can read the token for AJAX
CSRF_COOKIE_SAMESITE = 'Lax'  # Consistent with session cookie policy
# CSRF_COOKIE_SECURE = True    # Uncomment for HTTPS/production

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media Files (User Resumes, Avatars, ZIP uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Resume Builder — output directory for generated PDFs
RESUME_OUTPUT_DIR = os.path.join(BASE_DIR, 'media', 'resumes', 'generated')

# Security Headers Configuration
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Custom Authentication redirect target
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/erp/dashboard/'
LOGOUT_REDIRECT_URL = '/'
