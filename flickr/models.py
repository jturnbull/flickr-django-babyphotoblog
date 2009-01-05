from django.db import models
from django.template.defaultfilters import slugify
from lib.AutoSlugField import AutoSlugField

#http://www.paragiraffe.com/posts/2008/sep/23/rewriting-my-flickr-importer/

class Photo(models.Model):
    
    # Key Flickr info
    photo_id    = models.CharField(unique=True, primary_key=True, max_length=50)
    server   = models.PositiveSmallIntegerField()
    farm   = models.PositiveSmallIntegerField()
    secret      = models.CharField(max_length=30, blank=True)
    originalsecret = models.CharField(max_length=30, blank=True)
    originalformat = models.CharField(max_length=3, blank=True)
        
    # Main metadata
    title           = models.CharField(max_length=250)
    slug            = AutoSlugField(max_length=127,populate_from="title",help_text='This will be automatically generated from the name', editable=True, blank=True, unique=True)
    description     = models.TextField(blank=True,null=True)
    comment_count   = models.PositiveIntegerField(max_length=5, default=0)
    
    # Date metadata
    date_posted = models.DateTimeField(blank=True, null=True)
    date_taken = models.DateTimeField(blank=True, null=True)
    date_updated  = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering=("-date_taken",)
    
    def __unicode__(self):
        return self.title
    
    def url(self):
        return "http://www.flickr.com/photos/%s/%s/" % (self.taken_by, self.photo_id)
    url = property(url)
    
    
    def timestamp(self):
        return self.date_uploaded
    timestamp = property(timestamp)
    
    def get_absolute_url(self):
        return ('detail_photo', (), {
                'slug': self.slug,
                })
    get_absolute_url = models.permalink(get_absolute_url)
    
    ### Image URLs ###
    
    def get_image_url(self, size=None):
        if size == "o":
            return "http://farm%s.static.flickr.com/%s/%s_%s_%s.%s" % (self.farm, self.server, self.photo_id, self.originalsecret, size, self.originalformat)
        elif size in list('mstb'):
            return "http://farm%s.static.flickr.com/%s/%s_%s_%s.jpg" % (self.farm, self.server, self.photo_id, self.secret, size)
        else:
            return "http://farm%s.static.flickr.com/%s/%s_%s.jpg" % (self.farm, self.server, self.photo_id, self.secret)
    
    image_url       = property(lambda self: self.get_image_url())
    square_url      = property(lambda self: self.get_image_url('s'))
    thumbnail_url   = property(lambda self: self.get_image_url('t'))
    small_url       = property(lambda self: self.get_image_url('m'))
    large_url       = property(lambda self: self.get_image_url('b'))
    original_url    = property(lambda self: self.get_image_url('o'))
    
    def resized_image(self, size=(740,987)):
    	from PIL import Image, ImageOps
    	import urllib
    	import os
    	from django.conf import settings

    	if not os.path.exists('%s/images/resized/%s.jpg' % (settings.MEDIA_ROOT, self.slug)):
    		newimage = urllib.urlretrieve(str(self.original_url))
    		newimage = Image.open(newimage[0]) 
    		newimage.thumbnail(size, Image.ANTIALIAS)
    		newimage = newimage.convert("RGB") # Apparently PIL may throw errors without this
    		newimage.save('%s/images/resized/%s.jpg' % (settings.MEDIA_ROOT, self.slug), 'jpeg') 
    		
    	return '%s/images/resized/%s.jpg' % (settings.MEDIA_URL, self.slug)
    
