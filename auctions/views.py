from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required


from .models import User, Listing, Bid, Comment, Category, Watchlist
from .forms import CreateListingForm



def index(request):
    return render(request, "auctions/index.html",{
        "listings":Listing.objects.all()
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
        form = CreateListingForm(request.POST)
        
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            bid = form.cleaned_data["bid"]
            if form.cleaned_data["image_url"]:
                image_url = form.cleaned_data["image_url"]
            else:
                image_url = "https://upload.wikimedia.org/wikipedia/commons/0/0a/No-image-available.png"
            user = request.user
            category_id = Category.objects.get(id=request.POST["categories"])
            Listing.objects.create(user = user, title = title, description = description, 
            price = bid, image_url = image_url, category = category_id)
        
        else:
            return render(request, "auctions/create.html", { 
                "message": "Invalid entry.",
                "listing_form": CreateListingForm(),
                "categories": Category.objects.all().order_by('category')
        })
    
        return HttpResponseRedirect(reverse('index'))
    else:
        # Opcionalmente, se puede ver como resulta el flujo de información a partir de usar una forma custom
        # cambiando abajo 'create' por 'create2'
        return render(request, "auctions/create.html", { 
            "listing_form": CreateListingForm(),
            "categories": Category.objects.all().order_by('category')
        })
    


def listing_info(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    category = Category.objects.get(category=listing.category)
    comments = Comment.objects.filter(listing=listing.id)
    user = request.user
    if request.user.is_authenticated:
        is_owner = True if listing.user == user else False
        watching = Watchlist.objects.filter(user = user, listing = listing)
        if watching:
            watching = Watchlist.objects.get(user = user, listing = listing)
        return listing, user, is_owner, category, comments, watching
    else:
        return listing, user, category, comments


def listing(request, listing_id):
    if request.user.is_authenticated:
        info = listing_info(request, listing_id)
        listing, user, is_owner, category = info[0], info[1], info[2], info[3]
        if request.method == "POST":
            comment = request.POST["comment"]
            if comment != "":
                Comment.objects.create(user = user, listing = listing, comment = comment)
        
        if listing.sold:
            winner = Bid.objects.get(price = listing.price, listing = listing).user
            is_winner = user.id == winner.id
        else: is_winner = False

        return render(request, "auctions/listing.html", {
        "listing": listing,
        "category": category,
        "is_owner": is_owner,
        "comments":Comment.objects.filter(listing=listing.id), 
        "watching": Watchlist.objects.filter(user = user, listing = listing).values('watching'), 
        "is_winner": is_winner
    })

    else:
        info_unauth = listing_info(request, listing_id)
        listing, user, category = info_unauth[0], info_unauth[1], info_unauth[2]

    

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "category": category,
        "comments":Comment.objects.filter(listing=listing.id), 
    })


@login_required
def bidding(request, listing_id):
    info = listing_info(request, listing_id)
    listing, user, is_owner, category, comments, watch = info[0], info[1], info[2], info[3], info[4], info[5]
    if request.method == "POST":
        bid = request.POST["bid"]
        listing.price = float(bid)
        listing.save()
        Bid.objects.create(user = user, price = bid, listing = listing)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "category": category,
        "comments": comments, 
        "watching": watch, 
        "is_owner": is_owner
    })


@login_required
def close_bidding(request, listing_id):
    info = listing_info(request, listing_id)
    listing, user, is_owner, category, comments, watch = info[0], info[1], info[2], info[3], info[4], info[5]
    listing.sold = True
    listing.save()
    winner = Bid.objects.get(price = listing.price, listing = listing).user
    is_winner = user.id == winner.id

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "category": category,
        "comments": comments, 
        "watching": watch, 
        "is_owner": is_owner,
        "is_winner": is_winner
    })





@login_required
def add_to_watchlist(request,listing_id):
    info = listing_info(request, listing_id)
    listing, user, is_owner, category, comments = info[0], info[1], info[2], info[3], info[4]
    watch = Watchlist.objects.filter(user = user, listing = listing)
    if watch:
        watch = Watchlist.objects.get(user = user, listing = listing)
        watch.watching = True
        watch.save()
    else:
        Watchlist.objects.create(user = user, listing = listing, watching = True)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "category": category,
        "comments": comments, 
        "watching": Watchlist.objects.get(user = user, listing = listing).watching, 
        "is_owner": is_owner
    })

@login_required
def remove_watchlist(request,listing_id):
    info = listing_info(request, listing_id)
    listing, user, is_owner, category, comments, watch = info[0], info[1], info[2], info[3], info[4], info[5]
    watch.watching = False
    watch.save()

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "category": category,
        "comments": comments, 
        "watching": Watchlist.objects.get(user = user, listing = listing).watching, 
        "is_owner": is_owner
    })

@login_required
def watchlist(request, user_id):
    listing_ids = Watchlist.objects.filter(user = request.user, watching=True).values('listing')
    listing = Listing.objects.filter(id__in = listing_ids)
    return render(request, "auctions/watchlist.html", {
        "listings": listing
    })





def category(request):
    listings = None
    category = None
    if request.method == "POST":
        category = request.POST["categories"]
        listings = Listing.objects.filter(category = category)
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all(),
        "category": Category.objects.get(id = category).category if category is not None else "",
        "listings": listings
    })
