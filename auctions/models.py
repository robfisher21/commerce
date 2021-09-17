from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date
from django.utils import timezone


class User(AbstractUser):
    pass

class Listing (models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    title = models.CharField(max_length=64, blank = False, null = False)
    description = models.CharField(max_length=1000, blank = False, null = False)
    startingbid = models.DecimalField(max_digits=6, decimal_places=2, blank = False, null = False)
    imageurl = models.URLField(max_length=1000, blank = False, null = False)
    dateadded = models.DateTimeField(default=timezone.now)
    state = models.BooleanField (default=True)

    def __str__(self):
        return f"{self.title} ({self.seller})"

class Category (models.Model):
    cat_name = models.CharField(max_length=64, default="Misc")
    cat_items = models.ManyToManyField(Listing, null=True, blank=True)

    def __str__(self):
        return f"{self.cat_name}"

class Bid (models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="item")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    bid = models.DecimalField(max_digits=6, decimal_places=2)
    datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.item}:{self.bidder} bid {self.bid}"


class Watchlist (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Listing)
    datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['datetime']
    
    def __str__(self):
        return f"{self.user}'s Watchlist'"


class Comments (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="commenttitle")
    comment = models.CharField(max_length=1000)
    datetime = models.DateTimeField(default=timezone.now)
    votes = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
        ordering = ['datetime']
    
    def __str__(self):
        return f"{self.user}:{self.comment}'"