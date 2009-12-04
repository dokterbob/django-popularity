=================
Django Popularity
=================
Generic view- and popularity tracking pluggable for Django
----------------------------------------------------------

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
This app is currently being used in several small-scale production environments.
However, it is probably that it still has a few kinks here and there and a fair bit
of functionality is still undocumented. 

Requirements
============
Short answer: MySQL >= 4.1.1, Django >= 1.1

Long answer:
Currently, this has only beentested for MySQL, thought it might work for Postgres and others as well (though SQLite might make some trouble out of it). If you do manage to get it to work (with or without modifications), please let me know so other users can profit from it as well.

In time, I am planning to migrate most of the functionality to pure-Django QuerySet babble. Sadly enough, the required functionality in the Django API
is as of now not yet mature enough.

Installation
============
#)  Change into some suitable directory and get the latest version from 
    GitHub by doing::
    
	git clone git://github.com/dokterbob/django-popularity.git
    
    (In case you don't have or like Git, get the latest tarball from
    http://github.com/dokterbob/django-popularity/tarball/master.)
    
#)  Link the popularity directory to your application tree::
    
	ln -s django-popularity/popularity $PROJECT_DIR/popularity
    
    (Here `$PROJECT_DIR` is your project root directory.)
    
#)  Add popularity to `INSTALLED_APPS` in settings.py::

	INSTALLED_APPS = (
	    ...
	    'popularity',
	    ...
	)
    
    Optionally, use the variable `POPULARITY_CHARAGE` to the characteristic 
    number of seconds after which an object grows 'twice as old'.
    
    There is also a configuration variable `POPULARITY_LISTSIZE` to set the
    default number of 'popular' items returned.
    
#)  Create required data structure::
    
	cd $PROJECT_DIR
	./manage.py syncdb
    
#)  Run the tests to see if it all works::
    
	./manage.py test
    
    If this fails, please contact me!
    If it doesn't: that's a good sign, chap! Go on to the next step.
    
#)  Register the model you want to track by placing the following code 
    somewhere, preferably in `models.py`::
    
	import popularity
	popularity.register(<mymodel>)
    
    This will assure that a ViewTracker gets created for each object that is 
    created and that it is deleted when that particular object is deleted as
    well. Also, this keeps track of add dates of objects.
    
#)  Next, make sure that for every method where you view an object you add the 
    following code (replace <viewed_object> by whatever you are viewing)::
    
	from popularity.models import ViewTracker
	...
	ViewTracker.add_view_for(<viewed_object>)
    
    If you want to make sure that your application also works when
    django_popularity is not present, use the example code in 
    `demo/testapp/views.py`.
    
    **Alternatively**, you can also use signals to register the viewing of 
    instances::
    
	from popularity.signals import view
	...
	view.send(<myinstance>)
    
    As there are multiple methods to do this, just pick one. They should be 
    equally good. If you have a preference for either one, please let me know
    because two options to do exactly the same sounds like overhead to me.
    
    **Lastly**, django-popularity has recently been extended with a beautiful AJAX way
    to register views for an object. This is useful for interactive scripted
    ways of viewing objects, for instance for registering views of movies. As of now it
    is still very much a work in progress but it seems to work quite well.
    (But are, however, much welcomed by the author.)
    
    To use this, add the following to your `urls.py`::
    
	urlpatterns += patterns('',
	    ...
	    (r'^viewtracker/', include('popularity.urls')),
	    ...
	)
    
    You can now register views by requesting the url `/viewtracker/<content_type_id>/<object_id>/`
    which is facilitated by two lines of JavaScript::
    
	function add_view_for(content_type_id, object_id) {
	    $.get('/viewtracker/' + content_type_id + '/' + object_id+'/')
	}
    
    To facilitate the useage of this there is a template tag::
    
	{% load popularity_tags %}
	...
	<img onclick="{{ object|viewtrack }}" />
	
    This will render as::
    
	<img onclick="add_view_for(<nn>,<nn>)" />
    
    **WARNING**: If you use the latter method, please be aware that it becomes tremendously easier for anyone on
    the web to register 'fake' views for objects. Hence, this might be considered a security
    risk.
    
#)  Now if you want to use the information you've just gathered, the easiest
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

    A second way is to use template tags.  As with all sets of custom tags you must 
    first call {% load popularity_tags %} in your template.  There 6 template tags you 
    can use which are described below.
    
    :Tag: views_for_object
    :Usage: `{% views_for_object widget as views %}`
    :Description: Retrieves the number of views for and stores them in a context variable.
    
    :Tag: views_for_objects
    :Usage: `{% views_for_objects widget_list as view_count %}`
    :Description: Retrieves the number of views for each object and stores them in an attribute.
        After using this tag the views for each widget in the widget_list can be accessed 
        through widget_list.view_count.

    :Tag: most_popular_for_model
    :Usage: `{% most_popular_for_model main.model_name as popular_models %}` or
        `{% most_popular_for_model main.model_name as popular_models limit 20 %}`
    :Description: Retrieves the ViewTrackers for the most popular instances of the given model.
        If the limit is not given it will use settings.POPULARITY_LISTSIZE.  The model should be
        given by the app name followed by the model name such as comments.Comment or auth.User.

    :Tag: most_viewed_for_model
    :Usage: `{% most_viewed_for_model main.model_name as viewed_models %}` or
        `{% most_viewed_for_model main.model_name as viewed_models limit 20 %}`
    :Description: Retrieves the ViewTrackers for the most viewed instances of the given model.
        If the limit is not given it will use settings.POPULARITY_LISTSIZE.  The model should be
        given by the app name followed by the model name such as comments.Comment or auth.User.

    :Tag: recently_viewed_for_model
    :Usage: `{% recently_viewed_for_model main.model_name as recent_models %}` or
        `{% recently_viewed_for_model main.model_name as recent_models limit 20 %}`
    :Description: Retrieves the ViewTrackers for the most recently viewed instances of the given model.
        If the limit is not given it will use settings.POPULARITY_LISTSIZE.  The model should be
        given by the app name followed by the model name such as comments.Comment or auth.User.
    
    :Tag: recently_added_for_model
    :Usage: `{% recently_added_for_model main.model_name as recent_models %}` or
        `{% recently_added_for_model main.model_name as recent_models limit 20 %}`
    :Description: Retrieves the ViewTrackers for the most recently added instances of the given model.
        If the limit is not given it will use settings.POPULARITY_LISTSIZE.  The model should be
        given by the app name followed by the model name such as comments.Comment or auth.User.
    
#)  Now you're done. Go have beer. Or a whiskey. Or coffee. Suit yourself.
    If you're still not done learning, try reading through the many methods
    described in `popularity/models.py` as they are to be documented later.

Credits
=======
Django-popularity was initially developed by Mathijs de Bruin <mathijs@mathijsfietst.nl> while
working for Visualspace <info@visualspace.nl>.

Major and minor contributions to this project were made by:

- Daniel Nordberg <dnordberg@gmail.com>
- Mark Lavin <markdlavin@gmail.com>

License
=======
This application is released 
under the GPL version 3.
