from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path("instructor/create/", create_instructor, name='create_instructor' )
]