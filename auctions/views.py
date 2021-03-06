from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, models
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Listing, Bid, Watchlist, Comment


class NewListingForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control'}))
    starting_bid = forms.IntegerField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    image_url = forms.URLField(required=False, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    category = forms.CharField(required=False, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    active = forms.BooleanField(required=False, widget=forms.HiddenInput(), initial=True)

class NewBid(forms.Form):
    bid = forms.IntegerField(widget=forms.TextInput(attrs={'class' : 'form-control'}))

class NewComment(forms.Form):
    your_comment = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control'}))


def index(request):
    '''Gives back all the active listings in the database'''
    return render(request, "auctions/index.html", {
        "active_listings": [listing for listing in Listing.objects.all().filter(active=True) ]
    })


def inactive(request):
    '''Gives back all the inactive listings in the database '''
    return render(request, "auctions/inactive.html", {
        "inactive_listings": [listing for listing in Listing.objects.all().filter(active=False) ]
    })



def categories(request):
    """
    A function that displays links to all listing categories avaliable 
    """
    categories = Listing.objects.values('listing_category').distinct().exclude(listing_category__exact='')
    return render(request, "auctions/categories.html", {
    "categories": categories
})  


def category_view(request, category):
    '''
    A function that returns a list of all listings under a specific category    
    '''
    return render(request, "auctions/category_view.html", {
        "category": category, 
        "category_listings": [listing for listing in Listing.objects.all().filter(listing_category=category) ]
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
    ''' A function to create a new listing '''

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
            highest_bidder = user
            if Listing.objects.filter(listing_title=title).exists():
                return render(request, "auctions/create.html", {
                    "form": form,
                    "message": "A Listing with that name already exists, try naming it differently."
                })
            else:
                listing = Listing(user= user, listing_title= title, listing_description= description, starting_bid= starting_bid, listing_image_url= image_url, listing_category= category, active= active, current_bid=current_bid, highest_bidder=highest_bidder)
                listing.save()
                return render(request, "auctions/index.html", {
                    "active_listings": [listing for listing in Listing.objects.all().filter(active=True) ]
                })
    return render(request, "auctions/create.html",{
        "form": NewListingForm()
    })



def listing(request, listing):
    '''A function used to present a certain listing'''
    user = request.user
    listing = Listing.objects.get(listing_title=listing)
    comments = Comment.objects.all().filter(listing=listing)
    if not user.is_authenticated:
        return render(request, "auctions/listing_no_login.html", {
            "listing": listing,
            "comments": comments
        })
    else:
        
        watchlist = Watchlist.objects.all().filter(user=user, listing=listing)
        
        if watchlist:
            on_watchlist_id = watchlist[0].id
            on_watchlist = Watchlist.objects.get(id=on_watchlist_id)
        else:
            watchlist = Watchlist.create(user, listing, False)
            watchlist.save()
            watchlist = Watchlist.objects.all().filter(user=user, listing=listing)
            on_watchlist_id = watchlist[0].id
            on_watchlist = Watchlist.objects.get(id=on_watchlist_id)
            
        Listing.refresh_from_db(listing)  
        if listing.winner == user:
            message = "Congratulations you are the winner of this auction"
            return render(request, "auctions/listing.html", {
            "listing": listing,
            "user": user,
            "message": message,
            "on_watchlist": on_watchlist.on_watchlist,
            "comments": comments,
            })
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "user": user,
            "on_watchlist": on_watchlist.on_watchlist,
            "comments": comments,
        })

@login_required
def bid(request, listing):
    '''A function used to place a bid '''

    listing = Listing.objects.get(listing_title=listing)
    current_bid = listing.current_bid
    if request.method == "POST":
        form = NewBid(request.POST)
        if form.is_valid():
            new_bid = form.cleaned_data['bid']
            # Check that the bid placed is higher than the current bid
            if new_bid < current_bid:
                message = "Bid must be higher than current bid."
                return render(request, "auctions/bid.html", {
                    "listing": listing,
                    "form": NewBid(),
                    "current_bid": current_bid,
                    "message": message
                })
            # In case the bid is higher we save the bid and update the database of the new highest bid    
            else:
                user = request.user
                bid_to_save = Bid(user=user, listing=listing, amount=new_bid)
                bid_to_save.save()
                update_listing = Listing.objects.get(listing_title=listing.listing_title)
                update_listing.current_bid = new_bid
                update_listing.highest_bidder = user
                update_listing.save()
                Listing.refresh_from_db(listing)
                return redirect('listing', listing=listing.listing_title)
    
    Listing.refresh_from_db(listing)            
    return render(request, "auctions/bid.html", {
        "listing": listing,
        "form": NewBid(),
        "current_bid": current_bid
    })


def comment(request, listing):
    '''A function used to add comments to a listing '''

    listing = Listing.objects.get(listing_title=listing)
    if request.method == "POST":
        form = NewComment(request.POST)
        if form.is_valid():
            comment = form.cleaned_data['your_comment']
            user = request.user
            comment_to_save = Comment(user=user, listing=listing, comment=comment)
            comment_to_save.save()
            return redirect('listing', listing=listing.listing_title)

    else:   
        return render(request, "auctions/comment.html", {
            "listing":listing,
            "form": NewComment()
        })


def close_auction(request, listing):
    ''' A function used to close an auction and declare a winner '''
    listing = Listing.objects.get(listing_title=listing)
    update_listing = Listing.objects.get(listing_title=listing.listing_title)
    update_listing.winner = listing.highest_bidder
    update_listing.active = False
    update_listing.save()
    Listing.refresh_from_db(listing)  
    return redirect('index')

def watchlist(request, listing):
    '''A function that adds or removes a listing from a user's watchlist '''
    the_listing = Listing.objects.get(listing_title=listing)
    user = request.user
    watchlist = Watchlist.objects.all().filter(listing=the_listing, user=user)
    on_watchlist_id = watchlist[0].id
    on_watchlist = Watchlist.objects.get(id=on_watchlist_id)

    # If the listing is on the user's watchlist we remove it
    if on_watchlist.on_watchlist == True:
        on_watchlist.on_watchlist = False
        on_watchlist.save()

    # If it is not on the user's watchlist we add it
    elif on_watchlist.on_watchlist == False:
        on_watchlist.on_watchlist = True
        on_watchlist.save()

    return redirect('listing', listing=listing)


def watchlist_view(request):
    """
    A view that shows all of the items on the current user's watchlist
    """
    user = request.user
    listed_in_watchlist = Watchlist.objects.all().filter(user=user, on_watchlist=True).values_list('listing', flat=True)
    return render(request, "auctions/watchlist_view.html", {
        "watchlist": [listing for listing in Listing.objects.all().filter(id__in=listed_in_watchlist)]
        
    })




