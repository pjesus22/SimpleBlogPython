from django.contrib import admin

from .models import Admin, Author, AuthorProfile, SocialAccount

# Register your models here.
admin.site.register(Author)
admin.site.register(Admin)
admin.site.register(AuthorProfile)
admin.site.register(SocialAccount)
