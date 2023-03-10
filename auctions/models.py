from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.category}"

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)    # Usuario que postea
    title = models.CharField(max_length=64)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=8)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listing_category", blank=True)
    categories = models.ManyToManyField(Category, blank=True, related_name="select_category") # Varios objetos <--> varias categorias
    image_url = models.URLField(default='google.com', blank=True)
    sold = models.BooleanField(default=False)

    def __str__(self): 
        return f"{self.title} by {self.user}"

class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2, max_digits=8)

    def __str__(self):
        return f"Bid item:{self.listing} by {self.user} with price {self.price}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self): 
        return f"{self.comment} - {self.user}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    watching = models.BooleanField(default=False)


