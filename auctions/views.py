from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator 
from django import forms

from .models import User, Category, Listing, Comment, Watchlist, Bid


class NewListingForm(forms.Form):
    title = forms.CharField(label="Title", max_length=200)
    description = forms.CharField(label="Description", max_length=500)
    starting_bid = forms.FloatField(label="Starting bid (in US Dollars)")
    image_url = forms.CharField(label="Image URL", max_length=500, required=False)
    category = forms.ChoiceField(choices=[(c.id, c.title) for c in Category.objects.all()], required=False)

class BiddingForm(forms.Form):

    value = forms.FloatField(label="Bidding value")

    def __init__(self, *args, **kwargs):

        min_bid = kwargs.pop('min_bid')
        
        super(BiddingForm, self).__init__(*args, **kwargs)

        self.fields['value'].widget.attrs['min'] = min_bid

        self.fields['value'].validators=[MinValueValidator(min_bid)]

class CommentForm(forms.Form):
    content = forms.CharField(max_length=200, label="")

def index(request):
    listings = Listing.objects.filter(active=True)
    return render(request, 'auctions/index.html', {"listings": listings})

@login_required
def my_listings(request):
    return render(request, 'auctions/my_listings.html')

def listing(request, listing_id):

    comment_form = CommentForm()
    
    listing = Listing.objects.get(id=listing_id)

    if listing.current_bid:
        bidding_form = BiddingForm(min_bid=listing.current_bid.value+1)
    else:
        bidding_form = BiddingForm(min_bid=listing.starting_bid)

    if request.method == "POST":

        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():

            comment = Comment(content=comment_form.cleaned_data["content"], user=request.user, listing=listing)

            comment.save()

    comments = Comment.objects.filter(listing=listing)
    
    return render(request, 'auctions/listing.html', {"listing": listing, "comment_form": comment_form, "comments": comments, "bidding_form": bidding_form})

@login_required
def close_auction(request, listing_id):

    listing = Listing.objects.get(id=listing_id)

    if listing.created_by == request.user:
        listing.active = False
        listing.save()

    return HttpResponseRedirect(reverse("my_listings"))

@login_required
def bid(request, listing_id):

    listing = Listing.objects.get(id=listing_id)
 
    if request.method == "POST":

        listing = Listing.objects.get(id=listing_id)

        if listing.current_bid:
            bidding_form = BiddingForm(request.POST, min_bid=listing.current_bid.value+1)
        else:
            bidding_form = BiddingForm(request.POST, min_bid=listing.starting_bid)

        if bidding_form.is_valid():

            bid = Bid(value=bidding_form.cleaned_data["value"], listing=listing, user=request.user)
            bid.save()

            listing.current_bid = bid
            listing.last_bid_by = request.user
            listing.save()

            return HttpResponseRedirect(reverse("listing", args=[listing.id]))
        else:
            print("Invalid")
            return HttpResponseRedirect(reverse("listing", args=[listing.id], kwargs=[{"message": "message"}]))

@login_required
def watchlist(request):
    watchlist = request.user.listing_watchlist.all()
    return render(request, "auctions/watchlist.html", {"watchlist": watchlist})

@login_required
def add_watchlist(request, listing_id):

    listing = Listing.objects.get(id=listing_id)

    if len(Watchlist.objects.filter(listing=listing, user=request.user)) != 0:
        print("Already in watchlist")
    else:
        watchlist_item = Watchlist(listing=listing, user=request.user)

        watchlist_item.save()

    return HttpResponseRedirect(reverse("listing", args=[listing.id]))

@login_required
def remove_watchlist(request, listing_id):

    listing = Listing.objects.get(id=listing_id)

    watchlist_item = Watchlist.objects.filter(listing=listing, user=request.user)

    watchlist_item.delete()

    return HttpResponseRedirect(reverse("listing", args=[listing.id]))

@login_required
def create_listing(request):

    form = NewListingForm()

    if request.method == 'POST':

        form = NewListingForm(request.POST)

        if form.is_valid():

            listing = Listing(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                starting_bid=form.cleaned_data["starting_bid"],
                image_url=form.cleaned_data["image_url"],
                created_by=request.user,
            )

            if form.cleaned_data["category"]:
                category = Category.objects.get(id=form.cleaned_data["category"])
                listing.category = category

            listing.save()

            return HttpResponseRedirect(reverse("listing", args=[listing.id]))

    return render(request, "auctions/create_listing.html", {"form": form})

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {"categories": categories})

def category(request, category):

    category = Category.objects.get(title=category)
    listings = category.listings.filter(active=True)
    return render(
        request,
        "auctions/category.html",
        {"category": category, "listings": listings}
    )

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

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

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
