"""
Django settings for eurowiki project.

Generated by 'django-admin startproject' using Django 2.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

from eurowiki.private import *
import django
DJANGO_VERSION = django.VERSION[0]
HAS_DMUC = False
HAS_MEETING = True
HAS_SAML2 = False

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = '4g+k(d00j5%n#$7_4ny)2!bczn%q496@ojdh1hh8m3(z9&g%7q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

"""
if IS_LINUX:
    ALLOWED_HOSTS = ['*']
    # PROTOCOL = 'https'
else:
    ALLOWED_HOSTS = ["localhost",]
    PROTOCOL = 'http'
"""
# Application definition

INSTALLED_APPS = [
    'haystack',
    'suit',
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # added
    'django_comments',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django_extensions',
    'mptt',
    'hierarchical_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.linkedin_oauth2',
    'django_dag',
    'django_messages',
    'queryset_sequence',
    'dal',
    'dal_select2',
    'dal_queryset_sequence',
    'dal_select2_queryset_sequence',
    'tinymce',
    'menu',
    # 'taggit',
    # 'taggit_labels',
    'tagging',
	# ...
    'rest_framework',
    'datatrans',

    'commons',
    'roles',
     'zinnia',
	 'pybb',
    'actstream',
	# ...
    'rdflib_django',
    'crispy_forms',
    'eurowiki',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    # 'commons.middleware.ActiveUserMiddleware',
    # 'pybb.middleware.PybbMiddleware',
 ]

ROOT_URLCONF = 'eurowiki.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "eurowiki", "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'eurowiki.context_processors.processor',
            ],
        },
    },
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

WSGI_APPLICATION = 'eurowiki.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
"""

ACCOUNT_AUTHENTICATION_METHOD = "email" # "username"
ACCOUNT_USERNAME_REQUIRED = False # True
ACCOUNT_EMAIL_REQUIRED = True # False
ACCOUNT_EMAIL_VERIFICATION = "mandatory" # "optional"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True # False
SOCIALACCOUNT_EMAIL_VERIFICATION = "none" # ACCOUNT_EMAIL_VERIFICATION

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'VERSION': 'v2.12',
    },
    'linkedin_oauth2': { # added 180826
        'SCOPE': [
            'r_emailaddress',
            'r_basicprofile',
        ],
        'PROFILE_FIELDS': [
            'id',
            'first-name',
            'last-name',
            'email-address',
        ],
    },
}

# --------- HIERARCHICAL GROUPS ----------------
AUTHENTICATION_BACKENDS = (
    'hierarchical_auth.backends.HierarchicalModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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

# project membership

EURO_PROJECT_SLUG = "university-4-europe-european-national-identities-profiles-towards-euroforge"
EURO_PROJECT_ID = 334
# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en'
LANGUAGES = (
    (u'en', u'English'),
    (u'it', u'Italiano'),
)
LANGUAGE_CODES = [l[0] for l in LANGUAGES]

# TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TIME_ZONE = 'Europe/Rome'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
if IS_LINUX:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'eurowiki/static')
    LOCALE_PATHS = (os.path.join(BASE_DIR, 'eurowiki/locale'),)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SITE_ID = 1
# SITE_ID = 2
SITE_NAME = 'EuroIdentities'

PROJECT_ROOT = os.path.dirname(__file__)
PARENT_ROOT = os.path.dirname(PROJECT_ROOT)

USE_HAYSTACK = True
INDEXABLE_PREDICATES = ('label', 'PUE2',)
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
SEARCH_BACKEND = "whoosh"
if SEARCH_BACKEND == 'whoosh':
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
            'PATH': os.path.join(PARENT_ROOT, 'whoosh_index'),
            'EXCLUDED_INDEXES': [
                 'commons.search_indexes.UserProfileIndex',
                 'commons.search_indexes.ProjectIndex',
                 'commons.search_indexes.RepoIndex',
                 'commons.search_indexes.OERIndex',
                 'commons.search_indexes.LearningPathIndex',
                 'commons.search_indexes.FlatPageIndex',
             ],
        },
    }

# Number of seconds of inactivity before a user is marked offline
USER_ONLINE_TIMEOUT = 300
# Number of seconds that we will keep track of inactive users for before 
# their last seen is removed from the cache
USER_LASTSEEN_TIMEOUT = 60 * 60 * 24 * 7

CRISPY_TEMPLATE_PACK = 'bootstrap4'

TINYMCE_DEFAULT_CONFIG = {
    'schema': "html5",
    'resize' : "both",
    'height': 350,
    'branding': False,
    # 'plugins': "advlist charmap textcolor colorpicker table link anchor image media visualblocks code fullscreen preview",
    'plugins': "paste lists advlist charmap textcolor colorpicker table link anchor image visualblocks code fullscreen preview",
    # 'toolbar': 'undo redo | formatselect bold italic underline | alignleft aligncenter alignright alignjustify | forecolor backcolor subscript superscript charmap | bullist numlist outdent indent | table link unlink anchor image media | cut copy paste removeformat | visualblocks code fullscreen preview',
    'toolbar': 'undo redo | formatselect styleselect bold italic underline | alignleft aligncenter alignright alignjustify | forecolor backcolor subscript superscript charmap | bullist numlist outdent indent | table link unlink anchor image | cut copy paste removeformat | visualblocks code fullscreen preview',
    'content_css' : os.path.join(STATIC_URL,"tinymce/mycontent.css"),
    'style_formats': [
      {'title': '10px', 'inline': 'span', 'styles': {'font-size': '10px'}},
      {'title': '11px', 'inline': 'span', 'styles': {'font-size': '11px'}},
      {'title': '12px', 'inline': 'span', 'styles': {'font-size': '12px'}},
      {'title': '13px', 'inline': 'span', 'styles': {'font-size': '13px'}},
      {'title': '14px', 'inline': 'span', 'styles': {'font-size': '14px'}},
      {'title': '15px', 'inline': 'span', 'styles': {'font-size': '15px'}},
      {'title': '16px', 'inline': 'span', 'styles': {'font-size': '16px'}},
      {'title': '17px', 'inline': 'span', 'styles': {'font-size': '17px'}},
      {'title': '18px', 'inline': 'span', 'styles': {'font-size': '18px'}},
      {'title': 'clear floats', 'block': 'div', 'styles': {'clear': 'both'}},
    ],
    'plugin_preview_width' : 800,
    'plugin_preview_height' : 600,
    'advlist_class_list' : [
        {'title': 'select', 'value': ''},
        {'title': 'image responsive', 'value': 'img-responsive-basic center-block'},
        {'title': 'image responsive left', 'value': 'img-responsive-basic pull-left'},
        {'title': 'image responsive right', 'value': 'img-responsive-basic pull-right'}],
    'image_advtab' : True,
    'image_caption': False,
    'image_class_list' : [
        {'title': 'select', 'value': ''},
        {'title': 'image responsive', 'value': 'img-responsive-basic center-block'},
        {'title': 'image responsive left', 'value': 'img-responsive-basic pull-left marginR10'},
        {'title': 'image responsive right', 'value': 'img-responsive-basic pull-right marginL10'}],
    'paste_data_images': True,
    'table_class_list': [
        {'title': 'select', 'value': ''},
        {'title': 'table responsive', 'value': 'table-responsive'},
        {'title': 'table responsive width 100%', 'value': 'table-responsive width-full'},],
    'file_browser_callback_types': 'image',
    'paste_as_text': True,
    # URL settings
    # 'convert_urls' : False,
    'relative_urls' : False,
}

DATATRANS_TRANSLATE_MAP = {
    'flatpage': ('/admin/flatpages/flatpage/%s/', 'pk', 'title', 'commons.forms.FlatPageForm',),
}

from eurowiki.resources import * # EXTERNAL_SOURCES an EXTERNAL_RESOURCES, complementing rdflib store
