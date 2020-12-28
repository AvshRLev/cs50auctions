from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("inactive", views.inactive, name="inactive"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("<str:listing>", views.listing, name="listing"),
    path("bid/<str:listing>", views.bid, name="bid_listing"),
    path("bid", views.bid, name="bid"),
    path("close/<str:listing>", views.close_auction, name="close_auction"),
    path("watchlist/<str:listing>", views.close_auction, name="watchlist"),

]
