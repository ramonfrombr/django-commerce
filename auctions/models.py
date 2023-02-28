from django.contrib.auth.models import AbstractUser
from django.db import models

class Category(models.Model):
    title = models.CharField(max_length=100)

class User(AbstractUser):
    listing_watchlist = models.ManyToManyField(
        "Listing",
        through='Watchlist',
        through_fields=('user', 'listing'),
    )

class Listing(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    image_url = models.CharField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings", null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    starting_bid = models.FloatField(default=0)
    current_bid = models.ForeignKey("Bid", on_delete=models.CASCADE, null=True, related_name="current_bid")
    last_bid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings_bid", null=True)
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

class Watchlist(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    value = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    content = models.CharField(max_length=200, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    datetime = models.DateTimeField(auto_now_add=True)
