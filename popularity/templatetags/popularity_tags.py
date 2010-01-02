# This file is part of django-popularity.
# 
# django-popularity: A generic view- and popularity tracking pluggable for Django. 
# Copyright (C) 2008-2009 Mathijs de Bruin
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django import template
from django.db.models import get_model

from popularity.models import ViewTracker
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.filter
def viewtrack(value):
    ''' Add reference to script for adding a view to an object's tracker. 
        Usage: {{ object|viewtrack }}
        This will be substituted by: 'add_view_for(content_type_id, object_id)'
    '''
    ct = ContentType.objects.get_for_model(value)
    return 'add_view_for(%d,%d)' % (ct.pk, value.pk)

def validate_template_tag_params(bits, arguments_count, keyword_positions):
    '''
        Raises exception if passed params (`bits`) do not match signature.
        Signature is defined by `bits_len` (acceptible number of params) and
        keyword_positions (dictionary with positions in keys and keywords in values,
        for ex. {2:'by', 4:'of', 5:'type', 7:'as'}).            
    '''    
    
    if len(bits) != arguments_count+1:
        raise template.TemplateSyntaxError("'%s' tag takes %d arguments" % (bits[0], arguments_count,))
    
    for pos in keyword_positions:
        value = keyword_positions[pos]
        if bits[pos] != value:
            raise template.TemplateSyntaxError("argument #%d to '%s' tag must be '%s'" % (pos, bits[0], value))

# Nodes

class ViewsForObjectNode(template.Node):
    def __init__(self, object, context_var):
        self.object = object
        self.context_var = context_var

    def render(self, context):
        try:
            object = template.resolve_variable(self.object, context)
        except template.VariableDoesNotExist:
            return ''
        context[self.context_var] = ViewTracker.get_views_for(object)
        return ''

class ViewsForObjectsNode(template.Node):
    def __init__(self, objects, var_name):
        self.objects = objects
        self.var_name = var_name

    def render(self, context):
        try:
            objects = template.resolve_variable(self.objects, context)
        except template.VariableDoesNotExist:
            return ''

        queryset = ViewTracker.objects.get_for_objects(objects)
        view_dict = {}
        for row in queryset:
            view_dict[row.object_id] = row.views
        for object in objects:
            object.__setattr__(self.var_name, view_dict.get(object.id,0))
        return ''

class MostPopularForModelNode(template.Node):
    def __init__(self, model, context_var, limit=None):
        self.model = model
        self.context_var = context_var
        self.limit = limit

    def render(self, context):
        model = get_model(*self.model.split('.'))
        if model is None:
            raise TemplateSyntaxError('most_popular_for_model tag was given an invalid model: %s' % self.model)
        context[self.context_var] = ViewTracker.objects.get_for_model(model=model).get_most_popular(limit=self.limit)
        return ''

class MostViewedForModelNode(template.Node):
    def __init__(self, model, context_var, limit=None):
        self.model = model
        self.context_var = context_var
        self.limit = limit

    def render(self, context):
        model = get_model(*self.model.split('.'))
        if model is None:
            raise TemplateSyntaxError('most_viewed_for_model tag was given an invalid model: %s' % self.model)
        context[self.context_var] = ViewTracker.objects.get_for_model(model=model).get_most_viewed(limit=self.limit)
        return ''

class RecentlyViewedForModelNode(template.Node):
    def __init__(self, model, context_var, limit=None):
        self.model = model
        self.context_var = context_var
        self.limit = limit

    def render(self, context):
        model = get_model(*self.model.split('.'))
        if model is None:
            raise TemplateSyntaxError('recently_viewed_for_model tag was given an invalid model: %s' % self.model)
        context[self.context_var] = ViewTracker.objects.get_for_model(model=model).get_recently_viewed(limit=self.limit)
        return ''

class RecentlyAddedForModelNode(template.Node):
    def __init__(self, model, context_var, limit=None):
        self.model = model
        self.context_var = context_var
        self.limit = limit

    def render(self, context):
        model = get_model(*self.model.split('.'))
        if model is None:
            raise TemplateSyntaxError('recently_added_for_model tag was given an invalid model: %s' % self.model)
        context[self.context_var] = ViewTracker.objects.get_for_model(model=model).get_recently_added(limit=self.limit)
        return ''

# Tags
@register.tag
def views_for_object(parser, token):
    """
    Retrieves the number of views and stores them in a context variable.

    Example usage::

        {% views_for_object widget as views %}

    """
    bits = token.contents.split()
    validate_template_tag_params(bits, 3, {2:'as'})

    return ViewsForObjectNode(bits[1], bits[3])

@register.tag
def views_for_objects(parser, token):
    """
    Retrieves the number of views for each object and stores them in an attribute.

    Example usage::

        {% views_for_objects widget_list as view_count %}
        {% for object in widget_list %}
            Object Id {{object.id}} - Views {{object.view_count}}
        {% endfor %}
    """
    bits = token.contents.split()
    validate_template_tag_params(bits, 3, {2:'as'})

    return ViewsForObjectsNode(bits[1], bits[3])

@register.tag
def most_popular_for_model(parser, token):
    """
    Retrieves the ViewTrackers for the most popular instances of the given model.
    If the limit is not given it will use settings.POPULARITY_LISTSIZE

    Example usage::

        {% most_popular_for_model main.model_name as popular_models %}
        {% most_popular_for_model main.model_name as popular_models limit 20 %}

    """
    bits = token.contents.split()
    if len(bits) > 4:
        validate_template_tag_params(bits, 5, {2:'as', 4:'limit'})
        return MostPopularForModelNode(bits[1], bits[3], bits[5])
    else:
        validate_template_tag_params(bits, 3, {2:'as'})
        return MostPopularForModelNode(bits[1], bits[3])

@register.tag
def most_viewed_for_model(parser, token):
    """
    Retrieves the ViewTrackers for the most viewed instances of the given model.
    If the limit is not given it will use settings.POPULARITY_LISTSIZE

    Example usage::

        {% most_viewed_for_model main.model_name as viewed_models %}
        {% most_viewed_for_model main.model_name as viewed_models limit 20 %}

    """
    bits = token.contents.split()
    if len(bits) > 4:
        validate_template_tag_params(bits, 5, {2:'as', 4:'limit'})
        return MostViewedForModelNode(bits[1], bits[3], bits[5])
    else:
        validate_template_tag_params(bits, 3, {2:'as'})
        return MostViewedForModelNode(bits[1], bits[3])

@register.tag
def recently_viewed_for_model(parser, token):
    """
    Retrieves the ViewTrackers for the most recently viewed instances of the given model.
    If the limit is not given it will use settings.POPULARITY_LISTSIZE

    Example usage::

        {% recently_viewed_for_model main.model_name as recent_models %}
        {% recently_viewed_for_model main.model_name as recent_models limit 20 %}

    """
    bits = token.contents.split()
    if len(bits) > 4:
        validate_template_tag_params(bits, 5, {2:'as', 4:'limit'})
        return RecentlyViewedForModelNode(bits[1], bits[3], bits[5])
    else:
        validate_template_tag_params(bits, 3, {2:'as'})
        return RecentlyViewedForModelNode(bits[1], bits[3])

@register.tag
def recently_added_for_model(parser, token):
    """
    Retrieves the ViewTrackers for the most recently added instances of the given model.
    If the limit is not given it will use settings.POPULARITY_LISTSIZE

    Example usage::

        {% recently_added_for_model main.model_name as recent_models %}
        {% recently_added_for_model main.model_name as recent_models limit 20 %}

    """
    bits = token.contents.split()
    if len(bits) > 4:
        validate_template_tag_params(bits, 5, {2:'as', 4:'limit'})
        return RecentlyAddedForModelNode(bits[1], bits[3], bits[5])
    else:
        validate_template_tag_params(bits, 3, {2:'as'})
        return RecentlyAddedForModelNode(bits[1], bits[3])
