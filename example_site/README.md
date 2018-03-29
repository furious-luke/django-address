Quickstart
==========

Get a [Google Maps API Key] and update `GOOGLE_API_KEY` in [settings.py].

```bash
# Set up virtual environment
virtualenv env
source env/bin/activate

# Install requirements
pip install -r requirements.txt

# Migrate
python manage.py migrate

# Create a super admin to see results in Django Admin
python manage.py createsuperuser

# Run server
python manage.py runserver
```

[Google Maps API Key]: https://developers.google.com/maps/documentation/javascript/get-api-key
[settings.py]: example_site/settings.py
