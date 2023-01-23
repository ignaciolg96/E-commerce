from django.contrib import admin
from .models import Comment, Bid, Listing, Category, Watchlist

class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "comment", "listing")


# Register your models here.
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid)
admin.site.register(Listing)
admin.site.register(Category)
admin.site.register(Watchlist)

