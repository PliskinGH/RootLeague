release: python manage.py compilemessages -i .heroku --no-input && python manage.py migrate  --no-input
web: gunicorn RootLeagueProject.wsgi