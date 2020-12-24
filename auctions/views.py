from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, models
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing


class NewListingForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control'}))
    starting_bid = forms.IntegerField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    image_url = forms.URLField(required=False, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    category = forms.CharField(required=False, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    active = forms.BooleanField(required=False, widget=forms.HiddenInput(), initial=True)

class NewBid(forms.Form):
    # current_bid = forms.IntegerField(widget=forms.HiddenInput())
    bid = forms.IntegerField(widget=forms.TextInput(attrs={'class' : 'form-control'}))



def index(request):
    return render(request, "auctions/index.html", {
        "active_listings": [listing for listing in Listing.objects.all().filter(active=True) ]
    })


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

@login_required
def create(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            user = request.user
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            starting_bid = form.cleaned_data['starting_bid']
            current_bid = form.cleaned_data['starting_bid']
            image_url = form.cleaned_data['image_url']
            category = form.cleaned_data['category']
            active = form.cleaned_data['active']
            if Listing.objects.filter(listing_title=title).exists():
                return render(request, "auctions/create.html", {
                    "form": form,
                    "message": "A Listing with that name already exists, try naming it differently."
                })
            else:
                listing = Listing(user= user, listing_title= title, listing_description= description, starting_bid= starting_bid, listing_image_url= image_url, listing_category= category, active= active, current_bid=current_bid)
                listing.save()
                return render(request, "auctions/index.html", {
                    "active_listings": [listing for listing in Listing.objects.all().filter(active=True) ]
                })
    return render(request, "auctions/create.html",{
        "form": NewListingForm()
    })


@login_required
def listing(request, listing):
    listing = Listing.objects.get(listing_title=listing)
    return render(request, "auctions/listing.html", {
        "listing": listing
    })

def bid(request, listing):
    listin = Listing.objects.get(listing_title=listing)
    current_bid = listin.current_bid
    if request.method == "POST":
        form = NewBid(request.POST)
        if form.is_valid():
            new_bid = form.cleaned_data['bid']
            if new_bid <= current_bid:
                message = "Bid must be higher than starting bid or highest bid!"
                return render(request, "auctions/bid.html", {
                    "message": message,
                    "form": form
                })
    return render(request, "auctions/bid.html", {
        "current_bid": current_bid,
        "form": NewBid()
    })

# def new_bid(request, current_bid):
#     if request.method == "POST":
#         form = NewBid(request.POST)
#         if form.is_valid():
#             new_bid = form.cleaned_data['bid']
#             if new_bid <= current_bid:
#                 message = "Bid must be higher than starting bid or highest bid!"
#                 return render(request, "auctions/bid.html", {
#                     "message": message,
#                     "form": form
#                 })

