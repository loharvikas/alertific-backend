release: python manage.py migrate
web: gunicorn alertific.wsgi
worker: celery -A alertific worker -loglevel info
beat: celery -A alertific beat 