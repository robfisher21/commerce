from django.contrib import admin

from .models import Comments, Listing
from .models import Category
from .models import Bid
from .models import Watchlist
from .models import Comments

# Register your models here.
class ListingAdmin (admin.ModelAdmin):
    filter_horizontal = ("Listing")

admin.site.register(Listing)
admin.site.register(Category)
admin.site.register(Bid)
admin.site.register(Watchlist)
admin.site.register(Comments)