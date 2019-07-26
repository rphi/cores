"""
Django settings for cores project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import ldap
from django_auth_ldap.config import LDAPSearch

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG') == "True"

ALLOWED_HOSTS = ['localhost', 'nginx', os.getenv('HOSTNAME')]

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'polymorphic',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_auth_kerberos',
    'django_filters',
    'bootstrap4',
    'netfields',
    'booking',
    'inventory',
    'api',
    'reports',
    'notices',
    'live',
    'loans',
    'impersonate'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'impersonate.middleware.ImpersonateMiddleware'
]

ROOT_URLCONF = 'cores.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['cores/templates'],
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

WSGI_APPLICATION = 'cores.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-GB'

TIME_ZONE = 'GB'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = '../static'

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    'cores/static'
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/account/login'

# Django REST Framwork config
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissions'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'EXCEPTION_HANDLER': 'api.utils.cores_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination'
}

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cores',
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST')
    }
}

if os.getenv('SMTP_SERVER'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('SMTP_SERVER')
    EMAIL_PORT = int(os.getenv('SMTP_PORT'))
    EMAIL_FROM = os.getenv('SMTP_FROM')

if os.getenv('LDAP_AUTH') == "True":
    AUTHENTICATION_BACKENDS = [
        "django_auth_ldap.backend.LDAPBackend",
        "django.contrib.auth.backends.ModelBackend",
    ]

    AUTH_LDAP_SERVER_URI = os.getenv('LDAP_URI')
    AUTH_LDAP_BIND_DN = os.getenv('LDAP_BIND_DN')
    AUTH_LDAP_BIND_PASSWORD = os.getenv('LDAP_BIND_PASS')
    AUTH_LDAP_USER_ATTR_MAP = {"first_name": "givenName", "last_name": "sn", "email": "mail"}
    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        os.getenv('LDAP_SEARCH_PATH'), ldap.SCOPE_SUBTREE, "(CN=%(user)s)"
    )
elif os.getenv('LDAP_AUTH_DIRECT') == "True":
    # we're going for direct binding
    AUTHENTICATION_BACKENDS = [
        "django_auth_ldap.backend.LDAPBackend",
        "django.contrib.auth.backends.ModelBackend",
    ]
    
    AUTH_LDAP_SERVER_URI = os.getenv('LDAP_URI')
    AUTH_LDAP_USER_DN_TEMPLATE = "CN=%(user)s," + os.getenv('LDAP_SEARCH_PATH')
elif os.getenv('KERBEROS_AUTH') == "True":
    # kerberos realm and service
    KRB5_REALM = os.getenv('KERBEROS_REALM')
    KRB5_SERVICE = os.getenv('KERBEROS_SERVICE')

    # Enabled KDC verification defending against rogue KDC responses
    # by validating the ticket against the local keytab.
    KRB5_VERIFY_KDC = False

    # Enable case-sensitive matching between Kerberos and database user names
    KRB5_USERNAME_MATCH_IEXACT = True

    # enable kerberos auth backends
    AUTHENTICATION_BACKENDS = (
        'django_auth_kerberos.backends.KrbBackend',
    )

if os.getenv('LDAP_LOGGING') == "True":
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "loggers": {"django_auth_ldap": {"level": "DEBUG", "handlers": ["console"]}},
    }

    KRB5_DEBUG = True
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "loggers": {"django_auth_kerberos": {"level": "DEBUG", "handlers": ["console"]}},
    }