import flickrapi
from django.conf import settings
#http://stuvel.eu/projects/flickrapi
from flickr.models import Photo
import time


from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT UNIX_TIMESTAMP( MAX(  `date_posted` ) ) FROM flickr_photo")
row = cursor.fetchone()

min_upload_date = row[0] # Will get the last one again, but that's ok

    
# check latest 
# SELECT UNIX_TIMESTAMP( MAX(  `date_posted` ) ) 
# FROM flickr_photo

flickr = flickrapi.FlickrAPI(settings.FLICKR_API_KEY, format='etree')
rsp = flickr.photos_search(
    user_id=settings.FLICKR_USER_ID,
    extras='date_taken,tags',
    per_page=200,
    min_upload_date=min_upload_date,
    machine_tags=settings.FLICKR_MACHINETAG,
    )
assert rsp.attrib['stat'] == 'ok'

photos = rsp.find('photos')
for photo in photos:
    photo_id = photo.attrib['id']
    print photo_id
    photo_rsp = flickr.photos_getInfo(photo_id=photo_id)
    assert photo_rsp.attrib['stat'] == 'ok'
    
    photo = photo_rsp.find('photo')
    
    #Now, finally insert the photo to db.
    
    photodates = photo.find('dates')     
                       
    p = Photo(
        photo_id=photo_id,
        server=photo.attrib['server'],
        farm=photo.attrib['farm'],
        secret=photo.attrib['secret'],
        originalsecret=photo.attrib['originalsecret'],
        originalformat=photo.attrib['originalformat'],
        media=photo.attrib['media'],
        title=photo.find('title').text,
        description=photo.find('description').text,
        comment_count=photo.find('comments').text,
        date_posted=time.strftime('%Y-%m-%d %H:%M', time.gmtime(float(photodates.attrib['posted']))),
        date_taken=photodates.attrib['taken'],
        date_updated=time.strftime('%Y-%m-%d %H:%M', time.gmtime(float(photodates.attrib['lastupdate']))),
    )
    
    p.save()