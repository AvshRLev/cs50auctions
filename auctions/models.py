from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listing_owner")
    listing_title = models.CharField(max_length=64, unique=True)
    listing_description = models.CharField(max_length=256)
    starting_bid = models.IntegerField()
    current_bid = models.IntegerField()
    listing_image_url = models.URLField(blank=True, null=True)
    listing_category = models.CharField(blank=True, max_length=32, null=True)
    active = models.BooleanField(blank=True, null=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="listing_winner")
    highest_bidder = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="highest_bidder")
    def __str__(self):
        return f"{self.listing_title} By {self.user}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid_on_listing")
    amount = models.IntegerField()

    def __str__(self):
        return f"A Bid for {self.amount} By {self.user} on {self.listing}"

    