release: python manage.py migrate
web: gunicorn alertific.wsgi
worker: celery -A alertific worker --beat -l INFO
