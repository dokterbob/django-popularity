=================
Django Popularity
=================

What is it?
===========
The pluggable django-popularity makes it very easy to track the amount of
views for objects, and generate popularity listings based upon that.

Right now it has a measure for view counts, relative view counts, novelty and
popularity. The latter is still to be tested. Soon to be expected: randomness
and the ability to sort by a combination of novelty, view counts, randomness
and view count.

Status
======
We are nearing production stage, let's call it an early alpha. ;)
Also, please note that as of now we have about zero documentation.

Requirements
============
Currently, this is only tested for MySQL. It should also work for PostgresSQL
and Oracle though, but some alterations to the custom SQL might be needed. Please
let me know if you do make them.

Installation
============
1)  Get the latest version from the repository::

	git clone git://github.com/dokterbob/django-popularity.git
    
2)  Copy the popularity and testapp directories to your application tree::

	cd django-popularity
	cp -r popularity $APPDIR/
	cp -r demo/testapp $APPDIR/
    
    (Here `$APPDIR` is wherever you throw the applications belonging to your    
    project).
    
3)  Add popularity and testapp to `INSTALLED_APPS` in settings.py.

    Optionally, use the variable `CHARAGE` to the characteristic number of 
    seconds after which an object grows 'twice as old'.
    
4)  Create required data structure::

	cd $APPDIR
	./manage.py syncdb
    
5)  Run the unittests to see if it all makes sense::

	./manage.py test
	(If this fucks up, please contact me!)
    
6)  Make sure that for every method where you view an object you add the 
    following code (replace <viewed_object> by whatever you are viewing)::
    
	from popularity.models import ViewTracker
	ViewTracker.add_view_for(<viewed_object>)
    
7)  You're done! Views should be tracked from now! Go whiiiiiiiiiiiiiiii!

    :D

Usage
=====
You can use the view information in several different ways. Best is to look at
models.py in the popularity folder and in tests.py in testapp. But I'll give
some examples here.

ViewTracker.objects.select_age().order_by('age').limit(10)
	This yields the 10 newest objects on your site, meaning the 10 objects
	which have the most recent first view. Each element in the QuerySet has an
	extra field 'age' with the difference between the first and the last view
	of the object.


ViewTracker.get_recently_viewed(limit=10)
	This yields the 10 most recently viewed objects.


ViewTracker.get_most_popular(limit=10)
	This yields the 10 most popular objects of all time.


ViewTracker.get_for_model(<mymodel>), ViewTracker.get_for_models(*<mymodels>)
	This filters out the views for ``<mymodel>`` respectively the list ``*<mymodels>``.


Other functions will only become interesting at a later stage in development,
but you can already start logging now and choose to use them later.

License
=======
The django-agenda app is released 
under the GPL version 3.
