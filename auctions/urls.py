from django.urls import path

from . import views

import debug_toolbar
from django.conf import settings
from django.urls import include, path


urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.create, name="create"),
    path("listing/<int:listing_id>",views.listing, name="listing"),
    path("login", views.login_view, name="login"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("category/<int:category_id>", views.category, name="category"),
    path("logout", views.logout_view, name="logout"),
    path("comment/<int:listing_id>", views.CommentHandler, name="comment"),
    path("register", views.register, name="register"),
    path('__debug__/', include(debug_toolbar.urls))
]
