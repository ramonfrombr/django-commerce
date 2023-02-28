from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.category, name="category"),
    path("listings/<int:listing_id>/bid", views.bid, name="bid"),
    path("listings/<int:listing_id>/add_watchlist", views.add_watchlist, name="add_watchlist"),
    path("listings/<int:listing_id>/remove_watchlist", views.remove_watchlist, name="remove_watchlist"),
    path("listings/<int:listing_id>", views.listing, name="listing"),
    path("my_listings", views.my_listings, name="my_listings"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("close_auction/<int:listing_id>", views.close_auction, name="close_auction"),
    path("watchlist", views.watchlist, name="watchlist"),
]
