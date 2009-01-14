from models import Photo
from django.contrib import admin

class PhotoOptions(admin.ModelAdmin):

    list_display = ('title','photo_id', 'slug','media','date_posted', 'date_taken','comment_count')
    search_fields = ('title', 'slug', 'description',)
    date_hierarchy = 'date_taken'

admin.site.register(Photo, PhotoOptions)

