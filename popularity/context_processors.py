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

from models import ViewTracker

def most_popular(request):
    return {'most_popular' : ViewTracker.objects.get_most_popular() }

def recently_added(request):
    return {'recently_added' : ViewTracker.objects.get_recently_added() }

def recently_viewed(request):
    return {'recently_viewed' : ViewTracker.objects.get_recently_viewed() }

def most_viewed(request):
    return {'most_viewed' : ViewTracker.objects.get_most_viewed() }
