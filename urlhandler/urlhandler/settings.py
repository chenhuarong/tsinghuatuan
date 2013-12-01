"""
Django settings for urlhandler project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
#import MySQLdb
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'o)0t4jx3l*b^syx4w78wrv_9laa=f9i+0$ynntqzvny$m#w4#9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'urlhandler'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urlhandler.urls'

WSGI_APPLICATION = 'urlhandler.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
if 'SERVER_SOFTWARE' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'NYenZfWMVWuqtUGNuQsI',
            'USER': '6jIVijhGUVreXBNI6jYzZGlt',
            'PASSWORD': 'AxB1w67ddB4cwkCLw3gQSoBjGUcICUL3',
            'HOST': 'sqld.duapp.com',
            'PORT': '4050',
            }
    }
    #con = MySQLdb.Connect(host = "sqld.duapp.com",
   #                       port = 4050,
   #                       user = "6jIVijhGUVreXBNI6jYzZGlt",
   #                       passwd = "AxB1w67ddB4cwkCLw3gQSoBjGUcICUL3",
    #                      db = "NYenZfWMVWuqtUGNuQsI")
   # con.ping(True)
   #cur = con.cursor()
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'tsinghuatuan',
            'USER': 'root',
            'PASSWORD': 'root',
            'HOST': '127.0.0.1',
            'PORT': '3306',
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'zh-CN'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = False

USE_L10N = False

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

#STATIC_ROOT = os.path.join(BASE_DIR, 'static').replace('\\', '/')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'userpage/static').replace('\\', '/'),
    os.path.join(BASE_DIR, 'adminpage/static').replace('\\', '/'),
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'userpage/templates').replace('\\', '/'),
    os.path.join(BASE_DIR, 'adminpage/templates').replace('\\', '/'),
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

