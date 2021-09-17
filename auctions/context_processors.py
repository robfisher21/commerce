from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max
from django import forms
from datetime import datetime
from django.utils import timezone
from decimal import Decimal


from .models import Category, User, Listing, Bid, Watchlist

def getcategories (request):
    allcategories = Category.objects.all().order_by('cat_name')
    
    return {
        "allcategories": allcategories,
    
    }


def watchlist_count (request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        watchlist = Watchlist.objects.get(user=user)
        wl_count = watchlist.items.all().count()

    else: wl_count = 0

    return {
            "watchlist_count":wl_count
                }