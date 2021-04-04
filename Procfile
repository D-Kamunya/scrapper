web: gunicorn scrapper.wsgi --log-file -
worker: celery -A scrapper  worker -B -l info --concurrency 2