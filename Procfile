release: python manage.py migrate
web: gunicorn alertific.wsgi
worker: celery -A [nameOfYourApp] worker --beat