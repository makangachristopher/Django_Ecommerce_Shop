from .base import *
import dj_database_url

DEBUG = config('DEBUG', cast=bool)
ALLOWED_HOSTS = ['ip-address', 'https://django-ecommerce-shop.onrender.com']

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('seeds_j7uu'),
        'USER': config('seeds_j7uu_user'),
        'PASSWORD': config('19nBFOlYoK1t6fHaaqm8KQIWyjA0J9j7'),
        'HOST': config('dpg-coad35n79t8c73eg1m00-a'),
        'PORT': '5432'
    }
}

STRIPE_PUBLIC_KEY = config('STRIPE_LIVE_PUBLIC_KEY')
STRIPE_SECRET_KEY = config('STRIPE_LIVE_SECRET_KEY')
