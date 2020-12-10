release: python manage.py migrate
web: gunicorn Tweetproject.wsgi:application --log-file - --log-level debug
