python manage.py makemigrations
python manage.py migrate
DJANGO_SETTINGS_MODULE={{ django_project_name }}.settings_render gunicorn blog.wsgi:application
