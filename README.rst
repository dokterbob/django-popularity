=================
Django Popularity
=================

What is it?
===========
The pluggable django-popularity makes it very easy to track the amount of
views for objects, and generate (generic) popularity listings based upon that.

Right now it has a measure for view counts, relative view counts, novelty and
popularity for ''all'' possible objects. The latter is still to be tested. Soon to be expected: randomness
and the ability to sort by a combination of novelty, view counts, randomness
and view count.

Status
======
We are nearing production stage, let's call it an early alpha. ;)
Also, please note that as of now we have about zero documentation.

Requirements
============
Short answer: MySQL >= 4.1.1, Django >= 

Long answer:
Currently, this has only beentested for MySQL, thought it might work for Postgres and others as well (though SQLite might make some trouble out of it). If you do manage to get it to work (with or without modifications), please let me know so other users can profit from it as well.

In time, I am planning to migrate most of the functionality to pure-Django QuerySet babble. Sadly enough, the required functionality in the Django API
is as of now not yet mature enough.

Installation
============
1)  Change into some suitable directory and get the latest version from 
    GitHub by doing::
    
	git clone git://github.com/dokterbob/django-popularity.git
    
    (In case you don't have or like Git, get the latest tarball from
    http://github.com/dokterbob/django-popularity/tarball/master.)
    
2)  Configure a test database in `demo/settings.py` and run the unit tests
    to see if you are to expect any trouble. If you're a fool, safely ignore 
    this step::
    
	cd demo
	./manage.py test
    
    If this fails, please contact me!
    If it doesn't: that's a good sign, chap! Go on to the next step.
    
3)  Link the popularity directory to your application tree::
    
	ln -s django-popularity/popularity $PROJECT_DIR/popularity
    
    (Here `$PROJECT_DIR` is your project root directory.)
    
4)  Add popularity to `INSTALLED_APPS` in settings.py::

	INSTALLED_APPS = (
	    ...
	    'popularity',
	    ...
	)
    
    Optionally, use the variable `POPULARITY_CHARAGE` to the characteristic 
    number of seconds after which an object grows 'twice as old'.
    
    There is also a configuration variable `POPULARITY_LISTSIZE` to set the
    default number of 'popular' items returned.
    
5)  Create required data structure::

	cd $PROJECT_DIR
	./manage.py syncdb

6)  Register the model you want to track by placing the following code 
    somewhere, preferably in `models.py`::
    
	import popularity
	popularity.register(<myobject>)
    
    This will assure that a ViewTracker gets created for each object that is 
    created and that it is deleted when that particular object is deleted as
    well. Also, this keeps track of add dates of objects.
    
7)  Next, make sure that for every method where you view an object you add the 
    following code (replace <viewed_object> by whatever you are viewing)::
    
	from popularity.models import ViewTracker
	...
	ViewTracker.add_view_for(<viewed_object>)
    
    If you want to make sure that your application also works when
    django_popularity is not present, use the example code in 
    `demo/testapp/views.py`.
    
    Alternatively, you can also use signals to register the viewing of 
    instances::
    
	from popularity.signals import view
	...
	view.send(myinstance)
    
    As there are multiple methods to do this, just pick one. They should be 
    equally good. If you have a preference for either one, please let me know
    because two options to do exactly the same sounds like overhead to me.

8)  Now if you want to use the information you've just gathered, the easiest
    way is to use the included RequestContextProcessors. To do this, include
    the following in your `settings.py`::
    
	TEMPLATE_CONTEXT_PROCESSORS = (
	    ...
	    'popularity.context_processors.most_popular',
	    'popularity.context_processors.most_viewed',
	    'popularity.context_processors.recently_viewed',
	    'popularity.context_processors.recently_added',
	)
    
    Here, the first processors are Django's default. The latter respectively
    add `most_popular`, `most_viewed`, `recently_viewed` and `recently_added`
    to the RequestContext.
    
    (If you don't know what a RequestContext is, do not pity yourself.
    Visit http://docs.djangoproject.com/en/dev/ref/templates/api/#id1.)
    
9)  Now you're done. Go have beer. Or a whiskey. Or coffee. Suit yourself.
    If you're still not done learning, try reading through the many methods
    described in `popularity/models.py` as they are to be documented later.

License
=======
This application is released 
under the GPL version 3.
