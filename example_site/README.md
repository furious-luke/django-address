# Overview

This is a django demonstration project that shows how `django-address` can be used to geocode manually entered postal
addresses.

## The Landing Page

<img alt="Screenshot of landing page"
src="https://user-images.githubusercontent.com/1409710/81486802-50bc4500-920c-11ea-901e-2579e7ce93b2.png" width="450">

## The Admin View

<img alt="Screenshot of django admin"
src="https://user-images.githubusercontent.com/1409710/81486803-52860880-920c-11ea-8938-b5e216d29c40.png" width="450">

## The person app and Person model

The person app is a simple implementation of a model called Person that includes an `AddressField` and a
first_name. When you geocode an address using the main landing page of this app, it saves the name in an object with a
blank first_name.

You can use Django Admin to view the saved Person objects and add a first name if you like.

### Use of `null=True` on `address` of the Person model

Note that the Person model uses Address field with `null=True`.

By default, `django-address` uses Cascade delete on AddressField. 

This means if you for some reason delete an Address that is related to a Person or some other 
model, it will also delete the Person.

By setting `null=True`, deleting the Address associated with a Person will keep the Person 
object instance and set `address` to null.

# Setup

If not already installed, [please install Docker](https://docs.docker.com/get-docker/).

Before building the example site, you will need to export three items into your environment:

```bash
export USER_ID=`id -u`
export GROUP_ID=`id -g`
export GOOGLE_API_KEY=<your-api-key>
```

The first two are used by Docker to ensure any files created are owned by your current user. The last is required to
make your Google Maps API key available to the example site. Instructions for setting up an API key here: [Google Maps
API Key]. Please note that this requires the set up of a billing account with Google.

## Enable (activate) required Google Maps services for the project your key belongs to 

This is hidden under Google Cloud Platform's console menu, under **Other Google Solutions** > **Google Maps** >
**APIs**. ([screenshot](https://user-images.githubusercontent.com/1409710/81484071-9d495580-91f7-11ea-891e-850fd5a225de.png))
   * Google Maps _Javascript API_ 
   * Google Maps _Places API_ 
   
## Launch the server

To run the example site, simply run:

```bash
docker-compose up
```

This will take care of launching a database, the server, and migrating the database.

## Create a super admin to see results in Django Admin

```bash
docker-compose run --rm server python manage.py createsuperuser
```
   
# The Project

The page shows a simple form entry field.

### Troubleshooting Google Maps

Check the browser console on the page for javascript errors. ([Screenshot of an error](https://user-images.githubusercontent.com/1409710/81484063-90c4fd00-91f7-11ea-8833-80a346c77f89.png))
   * `ApiTargetBlockedMapError`: Your API key [needs authorization](https://developers.google.com/maps/documentation/javascript/error-messages#api-target-blocked-map-error) to use the above services.
   * `ApiNotActivatedMapError`: Your API key [needs Google Maps services](https://developers.google.com/maps/documentation/javascript/error-messages#api-target-blocked-map-error) to use the above services.
   
   ***NOTE:** There is up to a several minute delay in making changes to project and api key settings. New keys can also take several minutes to be recognized. 

[Google Maps API Key]: https://developers.google.com/maps/documentation/javascript/get-api-key
[settings.py]: example_site/settings.py
