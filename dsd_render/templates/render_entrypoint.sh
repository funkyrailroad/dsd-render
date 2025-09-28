python manage.py makemigrations
python manage.py migrate
# TODO: blog will need to use templated project name
DJANGO_SETTINGS_MODULE=blog.settings_prod gunicorn blog.wsgi:application
