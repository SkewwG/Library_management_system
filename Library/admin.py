from django.contrib import admin
from Library.models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Book)
admin.site.register(BorrowBook)
admin.site.register(ReturnBook)
admin.site.register(LackBook)
admin.site.register(subscribeBook)