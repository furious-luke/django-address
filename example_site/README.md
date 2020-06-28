# Overview
This is a django demonstration project that shows how `django-address` can be used to geocode manually entered postal addresses.

**The Landing Page**

<img alt="Screenshot of landing page" src="https://user-images.githubusercontent.com/1409710/81486802-50bc4500-920c-11ea-901e-2579e7ce93b2.png" width="450">

**The Admin View**

<img alt="Screenshot of django admin" src="https://user-images.githubusercontent.com/1409710/81486803-52860880-920c-11ea-8938-b5e216d29c40.png" width="450">

## The person app and Person model
The person app is a simple implementation of a model called Person that includes an `AddressField`
and a first_name. When you geocode an address using the main landing page of this app, it saves
the name in an object with a blank first_name.

You can use Django Admin to view the saved Person objects and add a first name if you like.

### Use of `null=true` on `address` of the Person model 
Note that the Person model uses Address field with `null=true`.

By default, `django-address` uses Cascade delete on AddressField. 

This means if you for some reason delete an Address that is related to a Person or some other 
model, it will also delete the Person.

By setting `null=True`, deleting the Address associated with a Person will keep the Person 
object instance and set `address` to null.

# Setup
## Create virtual environment
   * `virtualenv env`
   * `source env/bin/activate`

## Install python requirements
   * `pip install -r requirements.txt`

## Add Google Maps requirements
Create a Google Cloud Platform project and API Key
   * Instructions for setting up an API key here: [Google Maps API Key]
   * This requires the set up of a billing with Google
   * The key will belong to a "project" in Google Cloud Platform 
 
### Enable (activate) required Google Maps services for the project your key belongs to 
This is hidden under Google Cloud Platform's console menu, under 
**Other Google Solutions** > **Google Maps** > **APIs**. ([screenshot](https://user-images.githubusercontent.com/1409710/81484071-9d495580-91f7-11ea-891e-850fd5a225de.png))
   * Google Maps _Javascript API_ 
   * Google Maps _Places API_ 

### Update this example_site django project's [settings.py].
   * Add your key to `GOOGLE_API_KEY` 

## Migrate
   * `python manage.py migrate`

## Create a super admin to see results in Django Admin
   * `python manage.py createsuperuser`

## Run server
   * `python manage.py runserver`
   
# The Project
The page shows a simple form entry field 
### Troubleshooting Google Maps
Check the browser console on the page for javascript errors. ([Screenshot of an error](https://user-images.githubusercontent.com/1409710/81484063-90c4fd00-91f7-11ea-8833-80a346c77f89.png))
   * `ApiTargetBlockedMapError`: Your API key [needs authorization](https://developers.google.com/maps/documentation/javascript/error-messages#api-target-blocked-map-error) to use the above services.
   * `ApiNotActivatedMapError`: Your API key [needs Google Maps services](https://developers.google.com/maps/documentation/javascript/error-messages#api-target-blocked-map-error) to use the above services.
   
   ***NOTE:** There is up to a several minute delay in making changes to project and api key settings. New keys can also take several minutes to be recognized. 


[Google Maps API Key]: https://developers.google.com/maps/documentation/javascript/get-api-key
[settings.py]: example_site/settings.py
