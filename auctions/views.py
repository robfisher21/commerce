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

from .models import Category, User, Listing, Bid, Watchlist, Comments

# Index View: enables users to view active listings:

def index(request):
    listings = Listing.objects.values().exclude(state=False).order_by('dateadded').reverse()
    if request.GET.get("SortBy") == "Ended":
            listings = Listing.objects.values().exclude(state=True).order_by('dateadded').reverse()
            
    listingView = []
 # Interrogate the current price for each listing
    for i in range (len(listings)):
        listing_id = listings[i]["id"]
        price = GetCurrentPrice (request, listing_id)
        watchliststatus = GetWatchlistStatus (request,listing_id)
        
        listingView.append (
            {
                "id": listings[i]["id"],
                "title": listings[i]["title"],
                "description": listings[i]["description"],
                "imageurl": listings[i]["imageurl"],
                "price" : price,
                "watchliststatus": watchliststatus                
            }
 
        )
    return render(request, "auctions/index.html", {
    "listing" : listingView,
    "index":True
    })

# Category View: return a listings matching category name:
def category(request,category_id):
    category = Category.objects.get(id=category_id)

    return render(request, "auctions/category.html",{
    "category" : category

    })
    
# New Commment Form: describes a new comment form:
class NewCommmentForm (forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':70}), label=False )

# Commment Handler: enables users to create and vote on an comment:
def CommentHandler (request,listing_id):
    ListingCommments = None
    # Check to test whether listing has comments:
    if request.method =="POST" and request.POST.get("vote") is None:
            form = NewCommmentForm(request.POST)
            if form.is_valid():
                user = request.user
                title = Listing.objects.get(id=listing_id)
                comment = form.cleaned_data['comment']
                datetime=timezone.now()
                c = Comments(user=user, title=title, comment=comment, datetime=datetime)
                c.save()

            return HttpResponseRedirect(reverse("listing", args=[listing_id]))
    #Handler for Comment Voting:
    elif request.method =="POST" and request.POST.get("vote") is not None:
            if request.POST.get("vote") =="+":
                comment_id = request.POST.get("comment_id")
                Comment = Comments.objects.get(id=comment_id)
                Comment.votes += 1
                Comment.save()
        #Else condition assumes that the vote must be negative given Boolean state:
            else: 
                comment_id = request.POST.get("comment_id")
                Comment = Comments.objects.get(id=comment_id)
                Comment.votes -= 1
                Comment.save()

            return HttpResponseRedirect(reverse("listing", args=[listing_id]))
        
    return ListingCommments

#Current Price Handler: returns max bid or starting price, whichever is greater
def GetCurrentPrice (request,listing_id):
    try:
        AllItemBids = Bid.objects.filter(item=listing_id)
        MaxBidDic = AllItemBids.order_by('-bid')[0]
        CurrentPrice = MaxBidDic.bid
    except:
        CurrentPrice =Listing.objects.get(id=listing_id).startingbid
 
    return CurrentPrice

# Listing View: generates context for the listing's page.
def listing(request,listing_id):
    listing = Listing.objects.get(id=listing_id)
    categories = listing.category_set.all()
    startingbid= listing.startingbid
    AllItemBids = Bid.objects.filter(item=listing_id)
    MaxBidDic = ""
    MaxBid = ""
    IsSeller =  False
    IsBidder = False
    watchliststatus = GetWatchlistStatus (request, listing_id)
    ListingCommments = None
    CommentSortOrder = True

    if request.user == listing.seller:
                        IsSeller = True

    try:
        # Conditions to test whether listing has bids:
            MaxBidDic = AllItemBids.order_by('-bid')[0]
            MaxBid = MaxBidDic.bid
            # If there is a previous bid, increment next bid by £0.01:
            BidValue = round(MaxBid + (Decimal.from_float(0.01)),2)
            Bidcount = len(AllItemBids)

        #Condiditions to test the status of the user:
            if request.user == MaxBidDic.bidder:
                        IsBidder = True

    except:
            #Handler if there are No bids on listing:
            MaxBid = ""
            # If there is NOT a previous bid, set next bid equal to starting bid:
            BidValue = startingbid
            Bidcount = ""
    try:
        #Returns a QuerySet of comments ordered by most recent:
            ListingCommments = Comments.objects.filter(title_id=listing_id).order_by('-datetime')
    
    except:
        pass

    # Sort Order handler: Returns Most Popular Or Most Recently added comments:
    if request.GET.get("SortBy") is not None:
        if request.GET.get("SortBy") == "Most_Popular":
            ListingCommments = Comments.objects.filter(title_id=listing_id).order_by('-votes')
            CommentSortOrder = False

        elif request.GET.get("SortBy") == "Most_Recent":
            ListingCommments = Comments.objects.filter(title_id=listing_id).order_by('-datetime')
            CommentSortOrder = True


    class BidsForm (forms.Form):
            BidEntered = forms.DecimalField(decimal_places=2,label="Enter Your Bid", initial=BidValue, min_value=BidValue)

   # Bid Handler: enables users to bid on a listing:
    if request.method =="POST" and request.POST.get("statechange") is None:
        # create a form instance and populate it with data from the request:
            form = BidsForm (request.POST)
            if form.is_valid():
                bidder = request.user
                # Because Item is modelled as a ForeignKey to the Listing, you let Django identify the Listing Object by passing it the context to identify the object. i.e. you logic item = listing.title doesn't provide sufficient context!
                item = Listing.objects.get(id=listing_id)
                bid = form.cleaned_data['BidEntered']
                b = Bid(item=item,bidder=bidder, bid=bid, datetime=timezone.now())
                b.save()
                return HttpResponseRedirect(reverse("listing", args=[listing_id]))
            
    # Close Bid Handler: enables the seller to end the auction  :
    elif request.user == listing.seller and request.method =="POST" and request.POST.get("statechange") is not None:
                l = Listing.objects.get(id=listing_id)
                l.state = False
                l.save()
                return HttpResponseRedirect(reverse("listing", args=[listing_id]))

    # Bid Handler: enables users to bid on a listing:
    if request.method =="POST" and request.POST.get("delete"):
            Listing.objects.get(id=listing_id).delete()
            return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/listing.html", {
            "listing" : listing,
            "bid" : MaxBid,
            "bidcount" : Bidcount,
            "IsSeller": IsSeller,
            "IsBidder": IsBidder,
            "bidform" : BidsForm,
            "MaxBidDic" : MaxBidDic,
            "watchliststatus" : watchliststatus,
            "categories": categories,
            "commentform":NewCommmentForm,
            "comments":ListingCommments,
            "CommentSortOrder":CommentSortOrder    
            })

# Watchlist Status Handler: tests whether a item is on a users Watchlist:
def GetWatchlistStatus (request,listing_id):
    try:
        user = User.objects.get(username=request.user)
        watchlist = Watchlist.objects.get(user=user)
        watchlist.items.get(id=listing_id)
        watchliststatus= "Remove from Watchlist"
 
    except: 
        watchliststatus="Add to Watchlist"

    return watchliststatus

#Watchlist View: returns items on a users Watchlist
def watchlist(request):
    user = User.objects.get(username=request.user)
    watchlist=""
    
    # Create a Watchlist for new users
    try:
        watchlist = Watchlist.objects.get(user=user)
    
    except:
        Watchlist(user=user).save()
        watchlist = Watchlist.objects.get(user=user)
   
    # Watchlist handler: enables items to be added/removed from Watchlist:
        #from Listings page:
    if request.method =="POST" and request.POST.get("ReturnURL") is None:
        listing_id=request.POST['listing_id']
        watchlistitem = Listing.objects.get(id=listing_id)

        try:
            watchlistitem = watchlist.items.get(id=listing_id)
            watchlist.items.remove(watchlistitem)
        
        except: 
            watchlist.items.add(watchlistitem)

        return HttpResponseRedirect(reverse("listing", args=[listing_id]))    
        
        #from other pages, e.g. Watchlist: 
    elif request.method =="POST" and request.POST.get("ReturnURL") is not None:
        ReturnURL=request.POST.get("ReturnURL")
        listing_id=request.POST['listing_id']
        watchlistitem = Listing.objects.get(id=listing_id)

        try:
            watchlistitem = watchlist.items.get(id=listing_id)
            watchlist.items.remove(watchlistitem)
        
        except: 
            watchlist.items.add(watchlistitem)    
        
        return HttpResponseRedirect(reverse(ReturnURL))

    return render(request, "auctions/watchlist.html",{
        "watchlist":watchlist

    })



# Log in view: enable users to sign in  
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

# Log out view: enable users to log out
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# Register view: enable new users to create an account:
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


#New Listing Form: class describing a new listing object:
class NewEntryForm (forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput (attrs={
        'class':'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':2, 'cols':50,  'class':'form-control'}), label="Description")
    startingbid = forms.DecimalField(decimal_places=2,label="Starting price (£)", initial='0.00', min_value=0, widget=forms.NumberInput (attrs={
        'class':'form-control'}))
    imageurl = forms.CharField(label="Image URL", initial='http://',widget=forms.TextInput (attrs={
        'class':'form-control'}))


# Create Listing View: enables users to create a new listing:
def create (request):
    categories = Category.objects.all()
    if request.method =="POST":
    # create a form instance and populate it with data from the request:
        form = NewEntryForm(request.POST)
        if form.is_valid():
            seller = request.user
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            startingbid = form.cleaned_data['startingbid']
            imageurl = form.cleaned_data['imageurl']
            category = Category.objects.get(id=request.POST["category"])
            l = Listing(seller=seller, title=title, description=description,startingbid=startingbid, imageurl=imageurl, dateadded=timezone.now())
            l.save()
            listing_id = Listing.objects.aggregate(Max('id')).get('id__max')
            category.cat_items.add(listing_id) 

            return HttpResponseRedirect(reverse("listing", args=[listing_id]))
        else:
            return render(request, "auctions/create.html", {
        "form": form,
        "categories": categories,
        "create":True
        })

    return render(request, "auctions/create.html", {
        "form": NewEntryForm(),
        "categories": categories,
        "create":True
        })

