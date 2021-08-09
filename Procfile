release: python manage.py migrate
web: gunicorn alertific.wsgi
worker: celery -A alertific worker -l INFO
beat: celery -A alertific beat 