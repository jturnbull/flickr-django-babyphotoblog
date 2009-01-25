from django.conf.urls.defaults import *
from django.conf  import settings
import os
from flickr.feeds import PhotoFeed
from django.http import HttpResponseRedirect

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    (r'^admin/(.*)', admin.site.root),
    (r'^comments/posted/', 'flickr.views.wrapped_comment_was_posted'),
    (r'^comments/', include('django.contrib.comments.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^client_media/(?P<path>.*)$', 'django.views.static.serve', 
         {'document_root': os.path.join(os.path.dirname(__file__), "client_media")}),
         url(r'^404/$', 'django.views.generic.simple.direct_to_template', {'template': '404.html'}),
         url(r'^500/$', 'django.views.generic.simple.direct_to_template', {'template': '500.html'}),
         
    )

feeds = {
    'feed': PhotoFeed,
}

#FEED rewrites

def redirect_to_feed():
    def inner(request, *args):
        return HttpResponseRedirect("/feed/")
    return inner

urlpatterns += patterns('',
    url(r'^wp-rss.php$', redirect_to_feed()),
    url(r'^wp-rss2.php$', redirect_to_feed()),
    url(r'^wp-rdf.php$', redirect_to_feed()),
    url(r'^wp-atom.php$', redirect_to_feed()),
    url(r'^feed/(.+)/$', redirect_to_feed()),
    )

urlpatterns += patterns('',
    (r'^(?P<url>feed)/$', 'django.contrib.syndication.views.feed',{'feed_dict': feeds}),
    url(r'^(?P<slug>[a-z0-9_-]+)/$', 'flickr.views.detail_photo', name="detail_photo"),
    (r'^/?$', 'flickr.views.list_photos', ),
    
)

