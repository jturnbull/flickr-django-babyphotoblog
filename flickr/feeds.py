from django.contrib.sites.models import Site
from django.contrib.syndication.feeds import Feed
from models import Photo

class PhotoFeed(Feed):
    _site = Site.objects.get_current()
    title = '%s' % _site.name
    link = "/feed/"
    description = ""

    def items(self):
        return Photo.objects.order_by('-date_taken')[:15]

    def item_pubdate(self, item):
        return item.date_taken

