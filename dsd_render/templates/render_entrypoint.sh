python manage.py makemigrations
python manage.py migrate
gunicorn blog.wsgi
