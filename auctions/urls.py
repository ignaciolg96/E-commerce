from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"), 
    path("listing/<str:listing_id>", views.listing, name="listing"),
    path("bidding/<str:listing_id>", views.bidding, name="bidding"),
    path("close_bidding/<str:listing_id>", views.close_bidding, name="close_bidding"),
    path("categories", views.category, name="categories"), 
    path("watch_list/<str:user_id>", views.watchlist, name="watchlist"),
    path("add_to_watchlist/<str:listing_id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("remove_watchlist/<str:listing_id>", views.remove_watchlist, name="remove_watchlist"),



]
