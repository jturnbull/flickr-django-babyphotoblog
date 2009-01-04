from django.conf  import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from models import *
from django.views.generic.list_detail import object_detail, object_list
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import comments


def list_photos(request, extra_context = None):
    context = RequestContext(request)
    if extra_context != None:
        context.update(extra_context)
    
    context['photos'] = Photo.objects.all()
    
    return render_to_response('flickr/list.html', 
                              context)

def detail_photo(request, slug, extra_context = None):
    context = RequestContext(request)
    if extra_context != None:
        context.update(extra_context)
    
    context['photo'] = get_object_or_404(Photo, slug=slug)
    
    return render_to_response('flickr/detail.html', 
                              context)

def wrapped_comment_was_posted(request, extra_context=None, context_processors=None):
    
    comment = None
    if 'c' in request.GET:
        try:
            comment = comments.get_model().objects.get(pk=request.GET['c'])
            return HttpResponseRedirect(comment.get_absolute_url())
        except ObjectDoesNotExist:
            return HttpResponseRedirect("/")
            pass