from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("inactive", views.inactive, name="inactive"),
    path("categories", views.categories, name="categories"),
    path("watchlist_view", views.watchlist_view, name="watchlist_view"),
    path("category_view/<str:category>", views.category_view, name="category_view"),
    path("category_view", views.category_view, name="category_view"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("<str:listing>", views.listing, name="listing"),
    path("bid/<str:listing>", views.bid, name="bid_listing"),
    path("bid", views.bid, name="bid"),
    path("close/<str:listing>", views.close_auction, name="close_auction"),
    path("watchlist/<str:listing>", views.watchlist, name="watchlist"),
    path("comment/<str:listing>", views.comment, name="comment")
    

]
