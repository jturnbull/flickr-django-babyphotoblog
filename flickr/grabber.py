import flickrapi
from django.conf import settings
#http://stuvel.eu/projects/flickrapi
from flickr.models import Photo
import time

# check latest 
# SELECT UNIX_TIMESTAMP( MAX(  `date_posted` ) ) 
# FROM flickr_photo

flickr = flickrapi.FlickrAPI(settings.FLICKR_API_KEY, format='etree')
rsp = flickr.photos_search(user_id=settings.FLICKR_USER_ID,extras='date_taken,tags',per_page=200,min_upload_date="1228496880")

assert rsp.attrib['stat'] == 'ok'

photos = rsp.find('photos')
for photo in photos:
    photo_id = photo.attrib['id']
    print photo_id
    
    context_rsp = flickr.photos_getAllContexts(photo_id=photo_id)
    assert context_rsp.attrib['stat'] == 'ok'
    sets = context_rsp.findall('set')
    if sets:
        foundset = False
        for flickrset in sets:
            if flickrset.attrib['id'] == settings.FLICKR_SETFILTER:
                foundset = True
                #FIXME: log other sets this photo is in so we can link.
        if foundset:
            photo_rsp = flickr.photos_getInfo(photo_id=photo_id)
            assert photo_rsp.attrib['stat'] == 'ok'
            
            photo = photo_rsp.find('photo')
            
            #Now, finally insert the phot o to db.
            
            photodates = photo.find('dates')     
                               
            p = Photo(
                photo_id=photo_id,
                server=photo.attrib['server'],
                farm=photo.attrib['farm'],
                secret=photo.attrib['secret'],
                originalsecret=photo.attrib['originalsecret'],
                originalformat=photo.attrib['originalformat'],
                title=photo.find('title').text,
                description=photo.find('description').text,
                comment_count=photo.find('comments').text,
                date_posted=time.strftime('%Y-%m-%d %H:%M', time.gmtime(float(photodates.attrib['posted']))),
                date_taken=photodates.attrib['taken'],
                date_updated=time.strftime('%Y-%m-%d %H:%M', time.gmtime(float(photodates.attrib['lastupdate']))),
            )
            
            p.save()