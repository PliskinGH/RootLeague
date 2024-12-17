release: python manage.py migrate  --no-input
web: gunicorn RootLeagueProject.wsgi
worker: python manage.py runmailer_pg