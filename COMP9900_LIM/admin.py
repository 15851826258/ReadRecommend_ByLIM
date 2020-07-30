from django.contrib import admin
from .models import *

# Register your models here.
# Every table that wanna be managed by admin should config here
# admin.site.register(TABLENAME) --xinchen

admin.site.register(User)
admin.site.register(Book)
admin.site.register(Collection)
admin.site.register(Review)
admin.site.register(CoBk)
admin.site.register(Rating)
admin.site.register(Goals)
